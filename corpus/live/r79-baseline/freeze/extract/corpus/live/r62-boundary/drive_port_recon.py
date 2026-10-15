#!/usr/bin/env python3
"""r62-boundary port recon driver (scratch only).

Recon for porting game-dev-3d's verified tree-timeout mechanism
(`probe_tree_timeout` in game-dev-3d/corpus/fixtures/run_battery.py:
Popen(start_new_session=True) -> communicate(timeout) -> on TimeoutExpired
verify one identified descendant, os.killpg(child group) -> kill verified
witness BEFORE draining pipes) into the 2d runner's run_process.

Questions measured, not assumed:
  Q1  Does 3d's approach kill the descendant GROUP? (i.e. does
      os.killpg(child_pgid) reach a Godot OS.create_process descendant?)
  Q2  Does the port change classification of the r61 pipe-holding mutant
      (child exits cleanly, descendant holds inherited stdout/stderr)?

Runners under test:
  V0_stock        - verbatim ast-extracted 2d run_process (baseline re-measure)
  V1_groupkill    - minimal port: Popen(start_new_session=True) +
                    communicate(bound); on TimeoutExpired killpg child group,
                    then bounded second communicate drain. No witness logic.
  V2_pipeholders  - V1 + on timeout discover & SIGKILL every live holder of
                    OUR captured pipe inodes (scan /proc/*/fd), then drain.
                    No fixture cooperation: identity = "holds our pipe".
  V3_attributed   - V2 + attributed return: actual_exit = child's real
                    returncode even when it pre-exited; error string names
                    pipe-held-vs-child-alive. Classification measured under
                    both `error=<attributed>` and hypothetical `error=None`.

Each run records child/descendant pid+pgid+sid+ppid+state via /proc, whether
killpg reached the descendant, whether 3d's witness rule (ppid==child,
pgid==self) would verify, elapsed, and the verbatim classify_process verdict.
Writes port-recon-verdicts.json + raw/<variant>-<arm>.stdout. No tracked files.
"""
import ast
import hashlib
import json
import os
import re
import resource
import signal
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
RUNNER = (HERE.parent.parent / "fixtures" / "run_battery.py").resolve()
RUNNER_3D = Path(
    "~/Projects/shokunin/game-dev-3d-shokunin/corpus/fixtures/run_battery.py"
).expanduser().resolve()
GODOT = "godot"
PROJ = HERE / "proj"
RAW = HERE / "raw"
MARKER = "TREE_PROBE: expected signature"
BOUND = 3.0
DRAIN_GRACE = 2.0

ARMS = {
    "clean": [],
    "hold": ["--spawn-hold"],
    "detach": ["--spawn-detach"],
    "hang": ["--spawn-hang"],
}
OUTLIVED = {
    "hold": "hold.descendant-outlived",
    "detach": "detach.descendant-outlived",
    "hang": "hang.descendant-outlived",
}


def extract(runner_path):
    src = runner_path.read_text()
    tree = ast.parse(src)
    segs = {}

    def walk(node):
        for child in ast.iter_child_nodes(node):
            if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)) and child.name in (
                "run_process", "classify_process",
            ):
                seg = ast.get_source_segment(src, child)
                assert seg, f"no segment for {child.name}"
                segs[child.name] = seg
            walk(child)

    walk(tree)
    assert set(segs) == {"run_process", "classify_process"}, segs.keys()
    ns = {"subprocess": subprocess}
    exec(segs["run_process"], ns)
    exec(segs["classify_process"], ns)
    return ns["run_process"], ns["classify_process"]


def proc_identity(pid):
    """state, ppid, pgid, sid, starttime, cmdline from /proc (None if gone)."""
    if pid is None or pid <= 0:
        return None
    try:
        stat = Path(f"/proc/{pid}/stat").read_text()
        rest = stat[stat.rindex(")") + 2:].split()
        cmd = (Path(f"/proc/{pid}/cmdline").read_bytes()
               .replace(b"\0", b" ").decode(errors="replace").strip())
        return {"state": rest[0], "ppid": int(rest[1]), "pgid": int(rest[2]),
                "sid": int(rest[3]), "starttime": int(rest[19]), "cmdline": cmd}
    except (OSError, ValueError, IndexError):
        return None


def proc_alive(pid):
    found = proc_identity(pid)
    return None if found is None else found["state"] not in ("Z", "X")


def pipe_inodes(proc):
    """pipe:[ino] tokens for the parent's read ends of proc stdout/stderr."""
    inos = set()
    for stream in (proc.stdout, proc.stderr):
        if stream is None:
            continue
        try:
            link = os.readlink(f"/proc/self/fd/{stream.fileno()}")
        except OSError:
            continue
        m = re.fullmatch(r"pipe:\[(\d+)\]", link)
        if m:
            inos.add(f"pipe:[{m.group(1)}]")
    return inos


def pipe_holders(inos, exclude_pids):
    """Pids with an open fd on any of our pipe inodes (other than excluded)."""
    holders = []
    for entry in Path("/proc").iterdir():
        if not entry.name.isdigit():
            continue
        pid = int(entry.name)
        if pid in exclude_pids:
            continue
        fd_dir = entry / "fd"
        try:
            for fd in fd_dir.iterdir():
                try:
                    if os.readlink(fd) in inos:
                        ident = proc_identity(pid) or {}
                        holders.append({"pid": pid,
                                        "cmdline": ident.get("cmdline"),
                                        "ppid": ident.get("ppid"),
                                        "pgid": ident.get("pgid"),
                                        "sid": ident.get("sid"),
                                        "state": ident.get("state")})
                        break
                except OSError:
                    continue
        except (OSError, PermissionError):
            continue
    return holders


def verify_3d_rule(child_pid, desc_pid, identity_token):
    """Replicates probe_tree_timeout's witness check (3d run_battery.py:484-488):
    live, ppid == child pid, pgid == witness pid, cmdline carries tokens."""
    found = proc_identity(desc_pid)
    if found is None:
        return False, "descendant gone", None
    reasons = []
    if found["state"] in ("Z", "X"):
        reasons.append("state zombie/dead")
    if found["ppid"] != child_pid:
        reasons.append(f"ppid {found['ppid']} != child {child_pid}")
    if found["pgid"] != desc_pid:
        reasons.append(f"pgid {found['pgid']} != own pid {desc_pid}")
    if identity_token not in (found["cmdline"] or ""):
        reasons.append("cmdline token absent")
    return (not reasons, ";".join(reasons) or "verified", found)


def run_v0(run_process, command):
    started = time.monotonic()
    output, code, error = run_process(command, BOUND)
    return {"output": output or "", "code": code, "error": error,
            "elapsed": round(time.monotonic() - started, 3),
            "child_alive_at_timeout": None, "killpg_sent": False,
            "killpg_error": None, "pipe_holders": [], "pipe_holders_killed": [],
            "child_pgid_at_spawn": None, "drain_elapsed": None,
            "cleanup_exit": None, "child_precipitated_exit": None,
            "attributed_error": None}


def run_popen_variant(command, kill_pipeholders, attributed):
    """start_new_session port variants. Returns shaped like run_v0 + extras."""
    rec = {"output": "", "code": None, "error": None, "elapsed": None,
           "child_alive_at_timeout": None, "killpg_sent": False,
           "killpg_error": None, "pipe_holders": [], "pipe_holders_killed": [],
           "child_pgid_at_spawn": None, "drain_elapsed": None,
           "cleanup_exit": None, "child_precipitated_exit": None,
           "attributed_error": None}
    started = time.monotonic()
    proc = subprocess.Popen(command, stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE, text=True,
                            start_new_session=True)
    try:
        rec["child_pgid_at_spawn"] = os.getpgid(proc.pid)
    except OSError as exc:
        rec["child_pgid_at_spawn"] = f"unreadable: {exc}"
    try:
        out, err = proc.communicate(timeout=BOUND)
        rec["output"] = (out or "") + (err or "")
        rec["code"] = proc.returncode
        rec["elapsed"] = round(time.monotonic() - started, 3)
        return proc, rec
    except subprocess.TimeoutExpired as exc:
        out = exc.stdout or ""
        err = exc.stderr or ""
        if isinstance(out, bytes):
            out = out.decode(errors="replace")
        if isinstance(err, bytes):
            err = err.decode(errors="replace")
        rec["output"] = out + err
        rec["error"] = f"TIMEOUT after {BOUND} seconds"
        rec["child_precipitated_exit"] = proc.poll()
        rec["child_alive_at_timeout"] = proc.poll() is None
        if rec["child_alive_at_timeout"]:
            try:
                os.killpg(proc.pid, signal.SIGKILL)
                rec["killpg_sent"] = True
            except OSError as exc2:
                rec["killpg_error"] = str(exc2)
        # Always record who still holds our pipes; kill only under the
        # pipe-holder variants so V1 evidences the survivor it would orphan.
        for holder in pipe_holders(pipe_inodes(proc), {os.getpid(), proc.pid}):
            rec["pipe_holders"].append(holder)
            if kill_pipeholders:
                try:
                    os.kill(holder["pid"], signal.SIGKILL)
                    rec["pipe_holders_killed"].append(holder["pid"])
                except OSError as exc2:
                    holder["kill_error"] = str(exc2)
        drain_start = time.monotonic()
        try:
            out2, err2 = proc.communicate(timeout=DRAIN_GRACE)
            rec["cleanup_exit"] = proc.returncode
            rec["output"] += (out2 or "") + (err2 or "")
        except subprocess.TimeoutExpired:
            rec["error"] += f"; drain exceeded {DRAIN_GRACE}s"
            # Release the parent's ends so a surviving holder does not pin us.
            for stream in (proc.stdout, proc.stderr):
                try:
                    stream.close()
                except OSError:
                    pass
        rec["drain_elapsed"] = round(time.monotonic() - drain_start, 3)
        rec["elapsed"] = round(time.monotonic() - started, 3)
        if attributed:
            if rec["child_precipitated_exit"] is not None:
                rec["attributed_error"] = (
                    f"TIMEOUT (pipe held after child exit "
                    f"{rec['child_precipitated_exit']})")
            else:
                rec["attributed_error"] = "TIMEOUT (child alive at bound; group killed)"
            rec["code"] = rec["child_precipitated_exit"] if (
                rec["child_precipitated_exit"] is not None
            ) else proc.returncode
            rec["error"] = rec["attributed_error"]
        else:
            rec["code"] = proc.returncode
        return proc, rec


def parse_pid(output, name):
    m = re.search(rf"{name}=(\d+)", output or "")
    return int(m.group(1)) if m else None


def run_arm(variant, arm, run_process, classify_process):
    command = [GODOT, "--headless", "--path", str(PROJ), "--script",
               "res://tree_probe.gd", "--", *ARMS[arm], f"--out-dir={HERE}"]
    fname = OUTLIVED.get(arm)
    if fname:
        (HERE / fname).unlink(missing_ok=True)
    identity_token = f"--out-dir={HERE}"

    started = time.monotonic()
    if variant == "V0_stock":
        core = run_v0(run_process, command)
        proc = None
    elif variant == "V1_groupkill":
        proc, core = run_popen_variant(command, kill_pipeholders=False,
                                       attributed=False)
    elif variant == "V2_pipeholders":
        proc, core = run_popen_variant(command, kill_pipeholders=True,
                                       attributed=False)
    elif variant == "V3_attributed":
        proc, core = run_popen_variant(command, kill_pipeholders=True,
                                       attributed=True)
    else:
        raise ValueError(variant)
    elapsed = time.monotonic() - started

    output = core["output"]
    godot_pid = parse_pid(output, "TREE_PROBE godot_pid")
    desc_pid = parse_pid(output, "TREE_PROBE spawned_pid")
    desc_at_return = proc_identity(desc_pid)
    godot_at_return = proc_identity(godot_pid)

    # Would 3d's witness rule have verified this descendant at return time?
    verify_ok, verify_detail, verify_found = (None, "no descendant", None)
    if desc_pid is not None:
        child_for_check = godot_pid if godot_pid is not None else -1
        verify_ok, verify_detail, verify_found = verify_3d_rule(
            child_for_check, desc_pid, identity_token)

    classification = classify_process(core["code"], core["error"], output, 0, MARKER)
    record = {
        "variant": variant, "arm": arm, "command": command, "bound": BOUND,
        "elapsed_seconds": round(elapsed, 3),
        "actual_exit": core["code"], "error": core["error"],
        "attributed_error": core.get("attributed_error"),
        "marker_observed": MARKER in output,
        "descendant_pipe_write_captured": "TREE_DESC_AFTER_PARENT_WRITE" in output,
        "inner_classification": classification,
        "godot_pid": godot_pid,
        "godot_pgid_at_spawn": core.get("child_pgid_at_spawn"),
        "driver_pgid": os.getpgid(0),
        "child_alive_at_timeout": core["child_alive_at_timeout"],
        "child_precipitated_exit": core.get("child_precipitated_exit"),
        "killpg_sent": core["killpg_sent"], "killpg_error": core["killpg_error"],
        "pipe_holders": core.get("pipe_holders"),
        "pipe_holders_killed": core.get("pipe_holders_killed"),
        "cleanup_exit": core["cleanup_exit"],
        "drain_elapsed_seconds": core["drain_elapsed"],
        "godot_alive_at_return": (None if godot_at_return is None
                                  else godot_at_return["state"] not in ("Z", "X")),
        "descendant_pid": desc_pid,
        "descendant_at_return": desc_at_return,
        "descendant_alive_at_return": (None if desc_at_return is None
                                       else desc_at_return["state"] not in ("Z", "X")),
        "witness_verify_3d_rule": verify_ok,
        "witness_verify_detail": verify_detail,
        "descendant_file": fname, "descendant_file_landed": False,
        "descendant_file_delay_after_return_s": None,
        "descendant_alive_after_file": None,
    }
    # Hypothetical classification if an attributed port returned error=None for
    # a child that had already exited cleanly with its marker emitted.
    if variant == "V3_attributed" and core.get("child_precipitated_exit") is not None:
        record["classification_if_error_none"] = classify_process(
            core["code"], None, output, 0, MARKER)

    if fname:
        deadline = time.monotonic() + 14.0
        while time.monotonic() < deadline:
            if (HERE / fname).exists():
                record["descendant_file_landed"] = True
                record["descendant_file_delay_after_return_s"] = round(
                    time.monotonic() - started - elapsed, 3)
                break
            time.sleep(0.25)
        record["descendant_alive_after_file"] = proc_alive(desc_pid)
    (RAW / f"{variant}-{arm}.stdout").write_text(output)
    print(f"{variant}/{arm}: exit={core['code']} err={core['error']!r} "
          f"elapsed={record['elapsed_seconds']}s classify={classification} "
          f"desc={desc_pid} desc_alive={record['descendant_alive_at_return']} "
          f"desc_pgid={None if desc_at_return is None else desc_at_return['pgid']} "
          f"verify3d={verify_ok} killpg={core['killpg_sent']} "
          f"holders={core.get('pipe_holders_killed')} "
          f"file={record['descendant_file_landed']}", flush=True)
    return record


def main():
    RAW.mkdir(parents=True, exist_ok=True)
    runner_sha = hashlib.sha256(RUNNER.read_bytes()).hexdigest()
    runner3d_sha = hashlib.sha256(RUNNER_3D.read_bytes()).hexdigest()
    run_process, classify_process = extract(RUNNER)
    env = {
        "godot_version": subprocess.run([GODOT, "--version"],
                                        capture_output=True, text=True).stdout.strip(),
        "python": sys.version.split()[0],
        "platform": subprocess.run(["uname", "-srvm"], capture_output=True,
                                   text=True).stdout.strip(),
        "runner_2d": str(RUNNER), "runner_2d_sha256": runner_sha,
        "runner_3d": str(RUNNER_3D), "runner_3d_sha256": runner3d_sha,
        "driver_pgid": os.getpgid(0), "driver_pid": os.getpid(),
        "rlimit_core": list(resource.getrlimit(resource.RLIMIT_CORE)),
        "started_utc": datetime.now(timezone.utc).isoformat(),
    }
    print(json.dumps(env, indent=2), flush=True)

    # S0 safety control: WITHOUT start_new_session, the Godot child's process
    # group IS the driver's group -> a killpg port without setsid self-kills.
    s0 = subprocess.Popen([GODOT, "--headless", "--path", str(PROJ), "--script",
                           "res://tree_probe.gd", "--", f"--out-dir={HERE}"],
                          stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                          text=True)
    try:
        s0_child_pgid = os.getpgid(s0.pid)
    except OSError:
        s0_child_pgid = None
    s0_out, s0_err = s0.communicate(timeout=8)
    s0_record = {"child_pid": s0.pid, "child_pgid": s0_child_pgid,
                 "driver_pgid": os.getpgid(0),
                 "child_group_equals_driver_group": s0_child_pgid == os.getpgid(0),
                 "exit": s0.returncode}
    print(f"S0: child_pgid={s0_child_pgid} driver_pgid={os.getpgid(0)} "
          f"equal={s0_record['child_group_equals_driver_group']}", flush=True)

    only = None
    for arg in sys.argv[1:]:
        if arg.startswith("--only="):
            only = arg.split("=", 1)[1].split(",")
    variants = ["V0_stock", "V1_groupkill", "V2_pipeholders", "V3_attributed"]
    arms = list(ARMS)
    if only:
        combos = [tuple(x.split("/", 1)) for x in only]
    else:
        combos = [(v, a) for v in variants for a in arms]
    records = []
    for variant, arm in combos:
        records.append(run_arm(variant, arm, run_process, classify_process))
    payload = {"mode": "port_recon_tree_timeout", "bound": BOUND,
               "drain_grace": DRAIN_GRACE, "environment": env,
               "s0_no_new_session": s0_record, "results": records}
    (HERE / "port-recon-verdicts.json").write_text(json.dumps(payload, indent=2) + "\n")
    print("done", flush=True)


if __name__ == "__main__":
    main()
