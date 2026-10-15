#!/usr/bin/env python3
"""r62-verifier independent descendant pipe-EOF driver (scratch only).

Replays the COMMITTED fixture's --spawn-hold arm and my instrumented variant
arms under a Popen+communicate(bound) harness shaped like the committed r62
meta block, while a sampler thread records KERNEL-side evidence from /proc:
the godot child's /proc/<pid> state and the descendant's ppid as it flips at
kernel reparenting. The descendant's own self-report lands in the trace log;
the sampler's log is harness-side and cannot be forged by the descendant.

Arms:
  committed_hold       committed descendant_pipe_probe.gd --spawn-hold
  gate_trace_d500      verifier_pipe_probe --gate-trace --parent-delay-ms=500
  gate_trace_d0        verifier_pipe_probe --gate-trace (real committed timing)
  forge_d2000          --forge-immediate --parent-delay-ms=2000
                       (deterministic PRE-exit write, pipes still held)
  forge_d0             --forge-immediate (stripped gate, real timing)
  forge_detach         --forge-detach --parent-delay-ms=300
                       (marker captured, pipes NOT held -> no timeout)

Writes scratch/verifier-drive-verdicts.json + scratch/raw/<arm>.stdout.
"""
import ast
import json
import os
import re
import signal
import subprocess
import threading
import time
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]  # game-dev-2d-shokunin
RUNNER = REPO / "corpus" / "fixtures" / "run_battery.py"
PROJ = HERE / "proj"
RAW = HERE / "raw"
TRACE = HERE / "ppid_trace.log"
GODOT = "/usr/bin/godot"
BOUND = 3.0
MARKER = "DESCENDANT_PIPE_PROBE: expected signature"
POST_EXIT_WRITE = "DESCENDANT_PIPE_AFTER_EXIT_WRITE"

# classify_process extracted verbatim from the COMMITTED runner.
src = RUNNER.read_text()
tree = ast.parse(src)
seg = None
for n in ast.walk(tree):
    if isinstance(n, ast.FunctionDef) and n.name == "classify_process":
        seg = ast.get_source_segment(src, n)
        break
assert seg
ns = {}
exec(seg, ns)
classify_process = ns["classify_process"]


def proc_stat_fields(pid):
    try:
        data = Path(f"/proc/{pid}/stat").read_text()
    except OSError:
        return None
    # pid (comm) state ppid ... ; comm can contain spaces -> split after ')'.
    rparen = data.rfind(")")
    rest = data[rparen + 2:].split()
    return {"state": rest[0], "ppid": int(rest[1])}


def pid_alive(pid):
    if pid is None or pid <= 0:
        return None
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    except PermissionError:
        return True
    except OSError:
        return False
    return True


def find_child_of(ppid):
    """Return a live direct child pid of ppid by scanning /proc, or None."""
    for entry in os.listdir("/proc"):
        if not entry.isdigit():
            continue
        st = proc_stat_fields(int(entry))
        if st and st["ppid"] == ppid and st["state"] != "Z":
            return int(entry)
    return None


def run_arm(name, script, flags, trace_path):
    """Popen+communicate(BOUND) harness mirroring the committed meta block,
    plus a harness-side /proc sampler thread (15ms cadence)."""
    samples = []
    stop = threading.Event()
    rec = {"case": name, "script": script, "flags": flags,
           "bound_seconds": BOUND, "timed_out": False,
           "child_exit_at_timeout": None, "actual_exit": None, "error": None,
           "marker_observed": False, "post_exit_write_captured": False,
           "godot_pid": None, "descendant_pid": None,
           "godot_alive_at_return": None, "descendant_alive_at_return": None,
           "inner_classification": None}
    proc = subprocess.Popen(
        [GODOT, "--headless", "--path", str(PROJ), "--script",
         f"res://{script}", "--"] + flags,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, bufsize=1)
    godot_pid = proc.pid
    rec["godot_pid"] = godot_pid
    started = time.monotonic()

    def sampler():
        desc = None
        while not stop.is_set():
            t = round(time.monotonic() - started, 4)
            gs = proc_stat_fields(godot_pid)
            if desc is None:
                desc = find_child_of(godot_pid)
                if desc is not None:
                    rec["descendant_pid_sighted"] = desc
            ds = proc_stat_fields(desc) if desc else None
            samples.append({"t": t,
                            "godot_state": gs["state"] if gs else "gone",
                            "desc_ppid": ds["ppid"] if ds else None,
                            "desc_state": ds["state"] if ds else None})
            time.sleep(0.015)

    th = threading.Thread(target=sampler, daemon=True)
    th.start()
    text = ""
    try:
        out, err = proc.communicate(timeout=BOUND)
        text = (out or "") + (err or "")
        rec["actual_exit"] = proc.returncode
    except subprocess.TimeoutExpired as exc:
        rec["timed_out"] = True
        rec["child_exit_at_timeout"] = proc.poll()
        out = exc.stdout.decode(errors="replace") if isinstance(exc.stdout, bytes) else (exc.stdout or "")
        err = exc.stderr.decode(errors="replace") if isinstance(exc.stderr, bytes) else (exc.stderr or "")
        text = out + err
        rec["error"] = f"TIMEOUT after {BOUND} seconds"
        for stream in (proc.stdout, proc.stderr):
            try:
                stream.close()
            except OSError:
                pass
        try:
            proc.wait(timeout=3)
        except subprocess.TimeoutExpired:
            proc.kill()
            try:
                proc.wait(timeout=3)
            except subprocess.TimeoutExpired:
                rec["error"] += "; post-kill wait timed out"
    finally:
        if proc.poll() is None:
            proc.kill()
            try:
                proc.wait(timeout=3)
            except subprocess.TimeoutExpired:
                rec["error"] = (rec["error"] or "") + "; forced cleanup timed out"
    stop.set()
    th.join(timeout=2)
    rec["elapsed_seconds"] = round(time.monotonic() - started, 3)
    rec["marker_observed"] = MARKER in text
    rec["post_exit_write_captured"] = POST_EXIT_WRITE in text
    m = re.search(r"DESCENDANT_PIPE spawned_pid=(\d+)", text)
    rec["descendant_pid"] = int(m.group(1)) if m else rec.get("descendant_pid_sighted")
    rec["godot_alive_at_return"] = pid_alive(godot_pid)
    rec["descendant_alive_at_return"] = pid_alive(rec["descendant_pid"])
    rec["inner_classification"] = classify_process(
        rec["actual_exit"], rec["error"], text, 0, MARKER)
    # Distill the kernel-side timeline: godot death + descendant ppid flip.
    flip = next((s for s in samples
                 if s["desc_ppid"] is not None and s["desc_ppid"] != godot_pid), None)
    death = next((s for s in samples if s["godot_state"] in ("Z", "gone")), None)
    rec["sampler"] = {
        "samples": len(samples),
        "first_desc_ppid": next((s["desc_ppid"] for s in samples
                                 if s["desc_ppid"] is not None), None),
        "ppid_flip_observation": flip,
        "godot_dead_observation": death,
        "descendant_sighted": rec.get("descendant_pid_sighted"),
    }
    rec["output_lines"] = text.strip().splitlines()
    (RAW / f"{name}.stdout").write_text(text)
    # Hygiene: reap the bounded orphan.
    if pid_alive(rec["descendant_pid"]):
        try:
            os.kill(rec["descendant_pid"], signal.SIGKILL)
        except OSError:
            pass
    return rec


def read_trace():
    if not TRACE.exists():
        return []
    lines = TRACE.read_text().splitlines()
    TRACE.unlink()
    return lines


def main():
    results = []
    arms = [
        ("committed_hold", "descendant_pipe_probe.gd", ["--spawn-hold"]),
        ("gate_trace_d500", "verifier_pipe_probe.gd",
         ["--gate-trace", f"--trace-log={TRACE}", "--parent-delay-ms=500"]),
        ("gate_trace_d0", "verifier_pipe_probe.gd",
         ["--gate-trace", f"--trace-log={TRACE}"]),
        ("forge_d2000", "verifier_pipe_probe.gd",
         ["--forge-immediate", f"--trace-log={TRACE}", "--parent-delay-ms=2000"]),
        ("forge_d0", "verifier_pipe_probe.gd",
         ["--forge-immediate", f"--trace-log={TRACE}"]),
        ("forge_detach", "verifier_pipe_probe.gd",
         ["--forge-detach", f"--trace-log={TRACE}", "--parent-delay-ms=300"]),
    ]
    for name, script, flags in arms:
        t0 = datetime.now(timezone.utc).isoformat()
        rec = run_arm(name, script, flags, TRACE)
        rec["arm_started_utc"] = t0
        rec["descendant_trace_lines"] = read_trace()
        results.append(rec)
        print(f"{name}: timed_out={rec['timed_out']} "
              f"child_exit_at_timeout={rec['child_exit_at_timeout']} "
              f"actual_exit={rec['actual_exit']} "
              f"post_write={rec['post_exit_write_captured']} "
              f"inner={rec['inner_classification']} "
              f"desc_alive={rec['descendant_alive_at_return']}")
    out = {
        "mode": "r62_verifier_independent_descendant_pipe_eof",
        "godot": subprocess.check_output([GODOT, "--version"], text=True).strip(),
        "runner_sha256_note": "classify_process ast-extracted from committed corpus/fixtures/run_battery.py @81a100c",
        "bound_seconds": BOUND,
        "results": results,
    }
    dest = HERE / "verifier-drive-verdicts.json"
    dest.write_text(json.dumps(out, indent=1))
    print("wrote", dest)


if __name__ == "__main__":
    main()
