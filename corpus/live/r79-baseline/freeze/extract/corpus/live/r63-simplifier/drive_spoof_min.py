#!/usr/bin/env python3
"""r63-simplifier: measure the minimal forged-signature pin on the production
classifier. ast-extracts run_process + classify_process VERBATIM from the
tracked run_battery.py and execs them — production code path, not a replica.

Arms (all against real Godot 4.7.2 headless):
  genuine_child   tracked descendant_pipe_probe.gd, no flags (genuine sig row)
  detached_ctrl   tracked fixture --spawn-detach (the CASES control shape:
                  signature + a live descendant that holds no pipes)
  forge_release   scratch probe --forge-release: child suppresses MARKER,
                  ppid-gated descendant writes MARKER post-death, exits
  forge_hold      scratch probe --forge-hold under bounded Popen at 3.0s:
                  descendant writes MARKER post-death then holds pipes
"""
import ast, json, os, re, signal, subprocess, sys, time
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3] if HERE.name == "r63-simplifier" else HERE
RUNNER = Path.home() / "Projects/shokunin/game-dev-2d-shokunin/corpus/fixtures/run_battery.py"
PROJ = HERE / "proj"
GODOT = "godot"
MARKER = "DESCENDANT_PIPE_PROBE: expected signature"
BOUND = 3.0

src = RUNNER.read_text()
tree = ast.parse(src)
ns = {"subprocess": subprocess}
def extract(fn_name):
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == fn_name:
            return ast.get_source_segment(src, node)
    raise SystemExit(f"missing {fn_name}")

for fn in ("run_process", "classify_process"):
    seg = extract(fn)
    exec(seg, ns)
run_process = ns["run_process"]
classify_process = ns["classify_process"]

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

def cmd_for(script, flags):
    return [GODOT, "--headless", "--path", str(PROJ), "--script", "res://" + script, "--", *flags]

def drive_run_process(case, script, flags, bound=8):
    command = cmd_for(script, flags)
    started = time.monotonic()
    output, code, error = run_process(command, bound)
    rec = {"case": case, "command_tail": command[command.index("--script"):],
           "expected_exit": 0, "actual_exit": code, "error": error,
           "elapsed_seconds": round(time.monotonic() - started, 3),
           "marker_observed": MARKER in output,
           "marker_occurrences": output.count(MARKER),
           "output_lines": output.strip().splitlines()}
    rec["inner_classification"] = classify_process(code, error, output, 0, MARKER)
    rec["classify_if_error_none"] = classify_process(code if code is not None else 0, None, output, 0, MARKER)
    m = re.search(r"DESCENDANT_PIPE spawned_pid=(\d+)", output)
    rec["descendant_pid"] = int(m.group(1)) if m else None
    return rec

def drive_hold(case, script, flags, bound=BOUND):
    command = cmd_for(script, flags)
    rec = {"case": case, "command_tail": command[command.index("--script"):],
           "bound_seconds": bound, "timed_out": False, "child_exit_at_timeout": None,
           "actual_exit": None, "error": None, "marker_observed": False,
           "descendant_pid": None, "descendant_alive_at_return": None}
    proc = None
    text = ""
    started = time.monotonic()
    try:
        proc = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                text=True, bufsize=1)
        try:
            out, err = proc.communicate(timeout=bound)
            text = (out or "") + (err or "")
            rec["actual_exit"] = proc.returncode
        except subprocess.TimeoutExpired as exc:
            rec["timed_out"] = True
            rec["child_exit_at_timeout"] = proc.poll()
            out = exc.stdout.decode(errors="replace") if isinstance(exc.stdout, bytes) else (exc.stdout or "")
            err = exc.stderr.decode(errors="replace") if isinstance(exc.stderr, bytes) else (exc.stderr or "")
            text = out + err
            rec["error"] = f"TIMEOUT after {bound} seconds"
            for s in (proc.stdout, proc.stderr):
                try:
                    s.close()
                except OSError:
                    pass
            try:
                proc.wait(timeout=3)
            except subprocess.TimeoutExpired:
                proc.kill()
                proc.wait(timeout=3)
    finally:
        if proc is not None and proc.poll() is None:
            proc.kill()
            proc.wait(timeout=3)
    rec["elapsed_seconds"] = round(time.monotonic() - started, 3)
    rec["marker_observed"] = MARKER in text
    rec["marker_occurrences"] = text.count(MARKER)
    rec["output_lines"] = text.strip().splitlines()
    rec["inner_classification"] = classify_process(rec["actual_exit"], rec["error"], text, 0, MARKER)
    rec["classify_if_error_none"] = classify_process(0, None, text, 0, MARKER)
    m = re.search(r"DESCENDANT_PIPE spawned_pid=(\d+)", text)
    rec["descendant_pid"] = int(m.group(1)) if m else None
    rec["descendant_alive_at_return"] = pid_alive(rec["descendant_pid"])
    return rec

results = []
results.append(drive_run_process("genuine_child", "descendant_pipe_probe.gd", []))
results.append(drive_run_process("detached_ctrl", "descendant_pipe_probe.gd", ["--spawn-detach"]))
results.append(drive_run_process("forge_release", "spoof_min_probe.gd", ["--forge-release"]))
results.append(drive_hold("forge_hold", "spoof_min_probe.gd", ["--forge-hold"]))

# Field-level diff: forged release record vs the genuine controls — which
# fields (besides pids/timing) distinguish it? None is the pinned boundary.
def verdict_fields(r):
    return {"expected_exit": r.get("expected_exit"), "actual_exit": r["actual_exit"],
            "error": r["error"], "marker_observed": r["marker_observed"],
            "inner_classification": r["inner_classification"]}

field_diff = {
    "forge_release_vs_genuine_child": {k: (verdict_fields(results[2])[k], verdict_fields(results[0])[k])
        for k in verdict_fields(results[2]) if verdict_fields(results[2])[k] != verdict_fields(results[0])[k]},
    "forge_release_vs_detached_ctrl": {k: (verdict_fields(results[2])[k], verdict_fields(results[1])[k])
        for k in verdict_fields(results[2]) if verdict_fields(results[2])[k] != verdict_fields(results[1])[k]},
}

# Hygiene: SIGKILL any orphaned descendants recorded.
orphans = []
for r in results:
    if r.get("descendant_pid") and pid_alive(r["descendant_pid"]):
        try:
            os.kill(r["descendant_pid"], signal.SIGKILL)
            orphans.append(r["descendant_pid"])
        except OSError:
            pass
time.sleep(0.3)
post_reap = {str(p): pid_alive(p) for p in orphans}

payload = {
    "godot": subprocess.run([GODOT, "--version"], capture_output=True, text=True).stdout.strip(),
    "runner_sha_source": str(RUNNER),
    "bound": BOUND,
    "results": results,
    "verdict_field_diffs": field_diff,
    "orphans_reaped": orphans,
    "orphan_alive_after_reap": post_reap,
}
out = HERE / "spoof-min-verdicts.json"
out.write_text(json.dumps(payload, indent=2) + "\n")
print(json.dumps({"wrote": str(out),
                  "classify": {r["case"]: r["inner_classification"] for r in results},
                  "timeouts": {r["case"]: r.get("timed_out") for r in results}}, indent=2))
