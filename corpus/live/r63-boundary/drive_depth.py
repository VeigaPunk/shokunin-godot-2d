#!/usr/bin/env python3
"""r63-boundary driver 2/2: multi-depth descendant pipe-EOF recon (scratch).

Question (lane brief): does the r62 pipe-EOF wait extend transitively? A
depth-1 holder blocks communicate() past the child's death (r62 pinned
`min(bound, max(child_exit, last_fd_EOF))`). Untested: depth >= 2 — a
grandchild / great-grandchild holding the captured pipes after EVERY
intermediate ancestor has died, and whether a signature forged at depth 2
is still accepted on the signature axis.

Two evidence layers per arm (r62-critic discipline):

  verdict  — verbatim `run_process` + `classify_process` ast-extracted from
             the tracked run_battery.py and exec'd (production code path).
  timeline — a Popen+communicate replica of the POSIX timeout shape with a
             monitor thread: proc.poll() reap time, transitive /proc
             children discovery (children of godot -> intermediate -> gc ->
             ggc), per-pid ppid/state transition log, and pipe-inode holder
             scans (which pids hold OUR captured pipes, whatever their
             genealogy — the fd-level truth behind the EOF wait).

Shell level files are generated into arms/ at runtime (receipts); the
fixture executes `sh <out>/<arm>.sh` as the intermediate (depth 1).

Writes depth-verdicts.json + depth-timeline.json + raw captures.
No tracked files touched; all spawned descendants are self-terminating
sleeps <= 7s and a final hygiene sweep SIGKILLs any straggler.
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
import threading
import time
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
RUNNER = (HERE.parent.parent / "fixtures" / "run_battery.py").resolve()
GODOT = "godot"
PROJ = HERE / "proj"
RAW = HERE / "raw"
ARMS = HERE / "arms"

MARKER = "DEPTH_PROBE: expected signature"
BOUND = 3.0

# --------------------------------------------------------------------------
# Arm level files. @ARMS@ -> arms dir, @OUT@ -> outlived-file path.
# Gate idiom (same as the tracked fixture's ppid gate): poll /proc/self/stat
# field 4 until it flips off the recorded parent pid => provably post-parent
# -death. At depth >= 2 that makes the write provably post-ANCESTOR death.
# --------------------------------------------------------------------------

GATE = "while read -r _ _ _ pp _ < /proc/self/stat && [ \"$pp\" = \"$ANC\" ]; do sleep 0.05; done"

ARMSPEC = {
    # godot exits ~0.4s; intermediate exits +0.6s; gc gates on its own
    # reparent (post both deaths) then holds pipes ~4s more -> TIMEOUT.
    "d2_hold": {
        "godot_args": [],
        "files": {
            "d2_hold.sh": (
                "sh @ARMS@/d2_hold_gc.sh &\n"
                "echo \"INTERMEDIATE pid=$$ gc_pid=$!\"\n"
                "sleep 0.6\n"
                "echo \"INTERMEDIATE_EXIT\"\n"
            ),
            "d2_hold_gc.sh": (
                "ANC=$PPID\n"
                + GATE + "\n"
                "read -r _ _ _ PP _ < /proc/self/stat\n"                "echo \"GC_ORPHANED pid=$$ ppid_now=$PP\"\n"
                "sleep 4.0\n"
                "echo d2_hold-gc-outlived > @OUT@\n"
            ),
        },
        "outlived": "d2_hold.gc-outlived",
        "expect": "TIMEOUT; gc (depth2) alone holds pipes at bound",
    },

    # godot exits ~0.4s; intermediate +0.6s; gc releases at ~+1.6s total ->
    # clean exit-0 return at ~1.9s: EOF tracked through TWO dead generations.
    "d2_release": {
        "godot_args": [],
        "files": {
            "d2_release.sh": (
                "sh @ARMS@/d2_release_gc.sh &\n"
                "echo \"INTERMEDIATE pid=$$ gc_pid=$!\"\n"
                "sleep 0.6\n"
                "echo \"INTERMEDIATE_EXIT\"\n"
            ),
            "d2_release_gc.sh": (
                "ANC=$PPID\n"
                + GATE + "\n"
                "read -r _ _ _ PP _ < /proc/self/stat\n"                "echo \"GC_ORPHANED pid=$$ ppid_now=$PP\"\n"
                "sleep 1.0\n"
                "echo \"GC_RELEASED\"\n"
            ),
        },
        "expect": "exit 0 True at ~1.9s; return > intermediate death by ~1s",
    },

    # godot prints NO signature; gc emits the signature only after its own
    # reparent gate fires (post godot AND post intermediate death), releases
    # ~1.4s -> the depth-2 forged PASS on the signature axis.
    "d2_spoof": {
        "godot_args": ["--no-signature"],
        "files": {
            "d2_spoof.sh": (
                "sh @ARMS@/d2_spoof_gc.sh &\n"
                "echo \"INTERMEDIATE pid=$$ gc_pid=$!\"\n"
                "sleep 0.5\n"
                "echo \"INTERMEDIATE_EXIT\"\n"
            ),
            "d2_spoof_gc.sh": (
                "ANC=$PPID\n"
                + GATE + "\n"
                "read -r _ _ _ PP _ < /proc/self/stat\n"                "echo \"GC_ORPHANED pid=$$ ppid_now=$PP\"\n"
                "echo \"" + MARKER + "\"\n"
                "sleep 0.6\n"
                "echo \"GC_RELEASED\"\n"
            ),
        },
        "expect": "exit 0, marker True, classify True — forged depth-2 pass",
    },

    # same forgery but gc keeps holding past the bound: the forged signature
    # lands INSIDE a TIMEOUT record's partial output.
    "d2_spoof_hold": {
        "godot_args": ["--no-signature"],
        "files": {
            "d2_spoof_hold.sh": (
                "sh @ARMS@/d2_spoof_hold_gc.sh &\n"
                "echo \"INTERMEDIATE pid=$$ gc_pid=$!\"\n"
                "sleep 0.5\n"
                "echo \"INTERMEDIATE_EXIT\"\n"
            ),
            "d2_spoof_hold_gc.sh": (
                "ANC=$PPID\n"
                + GATE + "\n"
                "read -r _ _ _ PP _ < /proc/self/stat\n"                "echo \"GC_ORPHANED pid=$$ ppid_now=$PP\"\n"
                "echo \"" + MARKER + "\"\n"
                "sleep 4.0\n"
                "echo d2_spoof_hold-gc-outlived > @OUT@\n"
            ),
        },
        "outlived": "d2_spoof_hold.gc-outlived",
        "expect": "TIMEOUT w/ forged signature in partial output; False",
    },

    # live-child bound: godot --hang, intermediate exits +0.6s, gc holds.
    # SIGKILL reaches godot only; gc orphaned at depth 2.
    "d2_hang": {
        "godot_args": ["--hang"],
        "files": {
            "d2_hang.sh": (
                "sh @ARMS@/d2_hang_gc.sh &\n"
                "echo \"INTERMEDIATE pid=$$ gc_pid=$!\"\n"
                "sleep 0.6\n"
                "echo \"INTERMEDIATE_EXIT\"\n"
            ),
            "d2_hang_gc.sh": (
                "ANC=$PPID\n"
                + GATE + "\n"
                "read -r _ _ _ PP _ < /proc/self/stat\n"                "echo \"GC_ORPHANED pid=$$ ppid_now=$PP\"\n"
                "sleep 3.5\n"
                "echo d2_hang-gc-outlived > @OUT@\n"
            ),
        },
        "outlived": "d2_hang.gc-outlived",
        "expect": "TIMEOUT; godot killed; gc orphaned alive at depth 2",
    },

    # depth-2 silent leak: gc fully detached (stdio->/dev/null), sleeps 6.
    "d2_detach": {
        "godot_args": [],
        "files": {
            "d2_detach.sh": (
                "sh @ARMS@/d2_detach_gc.sh </dev/null >/dev/null 2>&1 &\n"
                "echo \"INTERMEDIATE pid=$$ gc_pid=$!\"\n"
                "sleep 0.3\n"
                "echo \"INTERMEDIATE_EXIT\"\n"
            ),
            "d2_detach_gc.sh": (
                "sleep 6\n"
                "echo d2_detach-gc-outlived > @OUT@\n"
            ),
        },
        "outlived": "d2_detach.gc-outlived",
        "expect": "clean exit 0 True at ~0.7s; depth-2 process silently leaked",
    },

    # intermediate ITSELF holds pipes to ~1.5s while its gc is detached:
    # return gated by the depth-1 holder; leaked gc invisible anyway.
    "d2_mixed": {
        "godot_args": [],
        "files": {
            "d2_mixed.sh": (
                "sh @ARMS@/d2_mixed_gc.sh </dev/null >/dev/null 2>&1 &\n"
                "echo \"INTERMEDIATE pid=$$ gc_pid=$!\"\n"
                "sleep 1.5\n"
                "echo \"INTERMEDIATE_EXIT\"\n"
            ),
            "d2_mixed_gc.sh": (
                "sleep 6\n"
                "echo d2_mixed-gc-outlived > @OUT@\n"
            ),
        },
        "outlived": "d2_mixed.gc-outlived",
        "expect": "exit 0 True at ~1.9s (intermediate hold); gc leaked invisibly",
    },

    # re-adoption: intermediate exits while godot (--linger 1.2) is still
    # alive -> gc's ppid becomes GODOT's pid (a pipe-holder re-adopted as a
    # DIRECT child), then 1573 when godot exits. Genealogy-irrelevant wait.
    "d2_reparent": {
        "godot_args": ["--linger=1.2"],
        "files": {
            "d2_reparent.sh": (
                "sh @ARMS@/d2_reparent_gc.sh &\n"
                "echo \"INTERMEDIATE pid=$$ gc_pid=$!\"\n"
                "sleep 0.15\n"
                "echo \"INTERMEDIATE_EXIT\"\n"
            ),
            "d2_reparent_gc.sh": (
                "sleep 3.8\n"
                "echo d2_reparent-gc-outlived > @OUT@\n"
            ),
        },
        "outlived": "d2_reparent.gc-outlived",
        "expect": "TIMEOUT; gc ppid path intermediate -> godot -> subreaper",
    },

    # depth 3: intermediate -> gc -> ggc; only ggc holds pipes (~4.5s).
    "d3_hold": {
        "godot_args": [],
        "files": {
            "d3_hold.sh": (
                "sh @ARMS@/d3_hold_gc.sh &\n"
                "echo \"INTERMEDIATE pid=$$ gc_pid=$!\"\n"
                "sleep 0.4\n"
                "echo \"INTERMEDIATE_EXIT\"\n"
            ),
            "d3_hold_gc.sh": (
                "sh @ARMS@/d3_hold_ggc.sh &\n"
                "echo \"GC pid=$$ ggc_pid=$!\"\n"
                "sleep 0.4\n"
                "echo \"GC_EXIT\"\n"
            ),
            "d3_hold_ggc.sh": (
                "ANC=$PPID\n"
                + GATE + "\n"
                "read -r _ _ _ PP _ < /proc/self/stat\n"                "echo \"GGC_ORPHANED pid=$$ ppid_now=$PP\"\n"
                "sleep 4.0\n"
                "echo d3_hold-ggc-outlived > @OUT@\n"
            ),
        },
        "outlived": "d3_hold.ggc-outlived",
        "expect": "TIMEOUT; depth-3 holder alone blocks EOF",
    },
}


def extract_runner_functions(runner_path):
    src = runner_path.read_text()
    tree = ast.parse(src)
    segs = {}

    def walk(node):
        for child in ast.iter_child_nodes(node):
            if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)) and child.name in (
                "run_process",
                "classify_process",
            ):
                seg = ast.get_source_segment(src, child)
                assert seg, f"no source segment for {child.name}"
                segs[child.name] = seg
            walk(child)

    walk(tree)
    assert set(segs) == {"run_process", "classify_process"}, segs.keys()
    ns = {"subprocess": subprocess}
    exec(segs["run_process"], ns)
    exec(segs["classify_process"], ns)
    return ns["run_process"], ns["classify_process"], segs


def proc_identity(pid):
    if pid is None or pid <= 0:
        return None
    try:
        stat = Path(f"/proc/{pid}/stat").read_text()
        rest = stat[stat.rindex(")") + 2:].split()
        cmd = (Path(f"/proc/{pid}/cmdline").read_bytes()
               .replace(b"\0", b" ").decode(errors="replace").strip())
        return {"state": rest[0], "ppid": int(rest[1]), "pgid": int(rest[2]),
                "sid": int(rest[3]), "cmdline": cmd}
    except (OSError, ValueError, IndexError):
        return None


def proc_alive(pid):
    found = proc_identity(pid)
    return None if found is None else found["state"] not in ("Z", "X")


def children_of(ppid):
    found = []
    for ent in os.listdir("/proc"):
        if not ent.isdigit():
            continue
        try:
            text = Path(f"/proc/{ent}/stat").read_text()
            rest = text[text.rindex(")") + 2:].split()
            if int(rest[1]) == ppid:
                found.append(int(ent))
        except (OSError, ValueError, IndexError):
            continue
    return found


def pipe_inodes(proc):
    inos = {}
    for name, stream in (("stdout", proc.stdout), ("stderr", proc.stderr)):
        if stream is None:
            continue
        try:
            link = os.readlink(f"/proc/self/fd/{stream.fileno()}")
        except OSError:
            continue
        m = re.fullmatch(r"pipe:\[(\d+)\]", link)
        if m:
            inos[f"pipe:[{m.group(1)}]"] = name
    return inos


def pipe_holders(ino_names, exclude_pids):
    """Pids holding any of our captured-pipe inodes, with which stream."""
    holders = []
    for entry in Path("/proc").iterdir():
        if not entry.name.isdigit():
            continue
        pid = int(entry.name)
        if pid in exclude_pids:
            continue
        try:
            held = set()
            for fd in (entry / "fd").iterdir():
                try:
                    tgt = os.readlink(fd)
                except OSError:
                    continue
                if tgt in ino_names:
                    held.add(ino_names[tgt])
            if held:
                ident = proc_identity(pid) or {}
                holders.append({"pid": pid, "streams": sorted(held),
                                "ppid": ident.get("ppid"),
                                "state": ident.get("state"),
                                "cmdline": ident.get("cmdline")})
        except (OSError, PermissionError):
            continue
    return holders


def parse_pid(output, name):
    m = re.search(rf"{re.escape(name)}\s*(\d+)", output or "")
    return int(m.group(1)) if m else None


def command_for(spec):
    return [GODOT, "--headless", "--path", str(PROJ), "--script",
            "res://depth_probe.gd", "--", *spec["godot_args"],
            f"--script-file={spec['main']}", f"--out-dir={ARMS}"]


def run_verdict_arm(run_process, classify_process, arm, spec):
    outlived_rel = spec.get("outlived")
    if outlived_rel:
        (ARMS / outlived_rel).unlink(missing_ok=True)
    command = command_for(spec)
    started = time.monotonic()
    output, code, error = run_process(command, BOUND)
    elapsed = time.monotonic() - started
    (RAW / f"{arm}.stdout").write_text(output or "")
    record = {
        "arm": arm, "expect": spec["expect"], "command": command,
        "bound_seconds": BOUND, "actual_exit": code, "error": error,
        "elapsed_seconds": round(elapsed, 3),
        "signature_observed": MARKER in (output or ""),
        "godot_suppressed_signature": "--no-signature" in spec["godot_args"],
        "inner_classification": classify_process(code, error, output or "",
                                                 0, MARKER),
        "godot_pid": parse_pid(output, "godot_pid="),
        "intermediate_pid": parse_pid(output, "spawned_pid="),
        "gc_pid_announced": parse_pid(output, "gc_pid="),
        "ggc_pid_announced": parse_pid(output, "ggc_pid="),
        "gc_orphaned_line": "GC_ORPHANED" in (output or ""),
        "ggc_orphaned_line": "GGC_ORPHANED" in (output or ""),
    }
    for key in ("godot_pid", "intermediate_pid", "gc_pid_announced",
                "ggc_pid_announced"):
        pid = record[key]
        ident = proc_identity(pid)
        record[f"{key}_alive_at_return"] = proc_alive(pid)
        record[f"{key}_ppid_at_return"] = ident["ppid"] if ident else None
    if outlived_rel:
        deadline = time.monotonic() + 9.0
        landed = False
        while time.monotonic() < deadline:
            if (ARMS / outlived_rel).exists():
                landed = True
                break
            time.sleep(0.2)
        record["descendant_outlived_file_landed"] = landed
    print(f"{arm}: exit={code} err={error!r} "
          f"elapsed={record['elapsed_seconds']}s "
          f"sig={record['signature_observed']} "
          f"classify={record['inner_classification']}",
          flush=True)
    return record


def run_timeline_arm(arm, spec):
    """Popen+communicate replica with /proc monitor thread."""
    command = command_for(spec)
    proc = subprocess.Popen(command, stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE, text=True, bufsize=1)
    t0 = time.monotonic()
    inos = pipe_inodes(proc)
    tl = {"arm": arm, "bound_seconds": BOUND, "godot_pid": proc.pid,
          "pipe_inodes": inos, "child_reaped_at_s": None,
          "child_returncode": None, "communicate_ended_at_s": None,
          "timed_out": None, "kill_sent_at_s": None,
          "pids": {}, "holder_samples": [],
          "signature_in_output": None}
    comm_result = {}

    def comm_worker():
        try:
            out, err = proc.communicate(timeout=BOUND)
            comm_result.update(out=out, err=err, timeout=False)
        except subprocess.TimeoutExpired as exc:
            comm_result.update(timeout=True, exc=exc)
        comm_result["ended_at"] = time.monotonic() - t0

    worker = threading.Thread(target=comm_worker, daemon=True)
    worker.start()

    seen = set()
    last_states = {}
    last_holder_sig = None

    def note(pid, tnow):
        if str(pid) not in tl["pids"]:
            tl["pids"][str(pid)] = {"first_seen_s": round(tnow, 3),
                                    "transitions": []}
        ident = proc_identity(pid)
        if ident:
            key = (ident["ppid"], ident["state"])
            if last_states.get(pid) != key:
                tl["pids"][str(pid)]["transitions"].append(
                    {"t_s": round(tnow, 3), "ppid": ident["ppid"],
                     "state": ident["state"]})
                last_states[pid] = key
            tl["pids"][str(pid)]["last_alive_s"] = round(tnow, 3)
            tl["pids"][str(pid)].setdefault("cmdline", ident.get("cmdline"))
        return ident

    while worker.is_alive():
        tnow = time.monotonic() - t0
        rc = proc.poll()
        if tl["child_reaped_at_s"] is None and rc is not None:
            tl["child_reaped_at_s"] = round(tnow, 3)
            tl["child_returncode"] = rc
        # transitive discovery: children of godot and of every seen pid
        for base in [proc.pid, *sorted(seen)]:
            for p in children_of(base):
                if p not in seen:
                    seen.add(p)
                    note(p, tnow)
        for p in sorted(seen):
            note(p, tnow)
        holders = pipe_holders(inos, {os.getpid(), proc.pid})
        sig = frozenset((h["pid"], tuple(h["streams"])) for h in holders)
        if sig != last_holder_sig:
            tl["holder_samples"].append({"t_s": round(tnow, 3),
                                         "holders": holders})
            last_holder_sig = sig
        time.sleep(0.02)

    worker.join(timeout=2)
    tl["communicate_ended_at_s"] = round(comm_result.get("ended_at", -1), 3)
    tl["timed_out"] = comm_result.get("timeout")
    tl["holders_at_return"] = pipe_holders(inos, {os.getpid(), proc.pid})

    if comm_result.get("timeout"):
        tl["kill_sent_at_s"] = round(time.monotonic() - t0, 3)
        if proc.poll() is None:
            proc.kill()
        proc.wait()
        exc = comm_result["exc"]
        out = exc.stdout or ""
        if isinstance(out, bytes):
            out = out.decode(errors="replace")
        tl["signature_in_output"] = MARKER in out
        tl["partial_output_lines"] = len(out.splitlines())
        (RAW / f"{arm}.timeline.stdout").write_text(out)
    else:
        out = comm_result.get("out") or ""
        tl["signature_in_output"] = MARKER in out
        tl["final_returncode"] = proc.returncode
        (RAW / f"{arm}.timeline.stdout").write_text(out)

    for p in sorted(seen):
        ident = proc_identity(p)
        tl["pids"][str(p)]["alive_at_return"] = proc_alive(p)
        if ident:
            tl["pids"][str(p)]["ppid_at_return"] = ident["ppid"]
            tl["pids"][str(p)]["state_at_return"] = ident["state"]
    if proc.stdout:
        proc.stdout.close()
    if proc.stderr:
        proc.stderr.close()
    # record but do not kill: descendants self-exit; hygiene sweep at end
    tl["seen_pids"] = sorted(seen)
    print(f"{arm} [timeline]: reaped={tl['child_reaped_at_s']} "
          f"end={tl['communicate_ended_at_s']} to={tl['timed_out']} "
          f"seen={tl['seen_pids']}", flush=True)
    return tl, seen


def write_arm_files():
    ARMS.mkdir(parents=True, exist_ok=True)
    for arm, spec in ARMSPEC.items():
        spec["main"] = f"{arm}.sh"
        out_path = ARMS / spec["outlived"] if spec.get("outlived") else ARMS / f"{arm}.out"
        for fname, body in spec["files"].items():
            body = body.replace("@ARMS@", str(ARMS)).replace("@OUT@", str(out_path))
            (ARMS / fname).write_text(body)


def main():
    RAW.mkdir(parents=True, exist_ok=True)
    write_arm_files()
    runner_sha = hashlib.sha256(RUNNER.read_bytes()).hexdigest()
    run_process, classify_process, segs = extract_runner_functions(RUNNER)

    env = {
        "godot_version": subprocess.run(
            [GODOT, "--version"], capture_output=True, text=True
        ).stdout.strip(),
        "python": sys.version.split()[0],
        "platform": subprocess.run(
            ["uname", "-srvm"], capture_output=True, text=True
        ).stdout.strip(),
        "runner": str(RUNNER),
        "runner_sha256": runner_sha,
        "started_utc": datetime.now(timezone.utc).isoformat(),
        "subreaper_hint": "pid 1573 = systemd --user on this host (r61/r62)",
    }
    print(json.dumps(env, indent=2), flush=True)

    verdicts, timelines, all_seen = [], [], set()
    for arm, spec in ARMSPEC.items():
        verdicts.append(run_verdict_arm(run_process, classify_process, arm, spec))
    for arm, spec in ARMSPEC.items():
        tl, seen = run_timeline_arm(arm, spec)
        timelines.append(tl)
        all_seen |= seen

    # hygiene: SIGKILL any spawned descendant still alive at driver end
    stragglers = [p for p in sorted(all_seen) if proc_alive(p)]
    for p in stragglers:
        try:
            os.kill(p, signal.SIGKILL)
        except OSError:
            pass

    (HERE / "depth-verdicts.json").write_text(json.dumps({
        "mode": "multi_depth_descendant_verdicts",
        "mechanism": "verbatim run_process (subprocess.run capture_output+timeout)",
        "environment": env, "arm_scripts_dir": str(ARMS),
        "results": verdicts,
    }, indent=2) + "\n")
    (HERE / "depth-timeline.json").write_text(json.dumps({
        "mode": "multi_depth_descendant_timelines",
        "mechanism": ("Popen+communicate replica of subprocess.run POSIX "
                      "timeout shape; monitor thread: poll()/transitive "
                      "children/pipe-inode holders at 20ms"),
        "environment": env,
        "results": timelines,
        "hygiene_killed": stragglers,
    }, indent=2) + "\n")
    print("done", flush=True)


if __name__ == "__main__":
    main()
