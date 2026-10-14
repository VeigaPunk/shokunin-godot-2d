#!/usr/bin/env python3
"""r62-author causal scratch driver (scratch only; no tracked writes).

ast.get_source_segment-extracts run_process + classify_process VERBATIM from
the tracked corpus/fixtures/run_battery.py and measures the descendant
pipe-EOF misattribution the r61 boundary seat probed, now as the r62 tracked
surface candidate:

  clean        - no descendant: plain child-exit-bound classification.
  hold_run     - --spawn-hold via the verbatim run_process: what a CASES row
                 would observe (subprocess.run + communicate timeout).
  hold_popen   - --spawn-hold via Popen+communicate: polls the direct child
                 AT the TimeoutExpired catch -> proves the child already
                 exited 0 while the bound still fired on pipe drain.
  detach       - --spawn-detach via run_process: discriminating control —
                 same fixture/spawn, fds detached -> child-exit-bound PASS.

Writes descendant-probe-verdicts.json and raw/*.stdout here.
"""
import ast
import hashlib
import json
import os
import re
import signal
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
RUNNER = (HERE.parent.parent.parent / "fixtures" / "run_battery.py").resolve()
GODOT = "godot"
PROJ = HERE / "proj"
RAW = HERE / "raw"

MARKER = "DESCENDANT_PIPE_PROBE: expected signature"
POST_EXIT_WRITE = "DESCENDANT_PIPE_AFTER_EXIT_WRITE"


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


def proc_alive(pid):
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


def proc_stat(pid):
    if pid is None or pid <= 0:
        return (None, None)
    try:
        text = Path(f"/proc/{pid}/stat").read_text()
        rest = text[text.rindex(")") + 2:].split()
        return (rest[0], int(rest[1]))
    except (OSError, ValueError, IndexError):
        return (None, None)


def parse_pid(output, name):
    m = re.search(rf"{name}=(\d+)", output or "")
    return int(m.group(1)) if m else None


def command_for(extra_args):
    return [GODOT, "--headless", "--path", str(PROJ), "--script",
            "res://descendant_pipe_probe.gd", "--", *extra_args]


def finalize(record, output):
    record["marker_observed"] = MARKER in (output or "")
    record["post_exit_write_captured"] = POST_EXIT_WRITE in (output or "")
    record["godot_pid"] = parse_pid(output, "DESCENDANT_PIPE godot_pid")
    record["descendant_pid"] = parse_pid(output, "DESCENDANT_PIPE spawned_pid")
    record["godot_alive_at_return"] = proc_alive(record["godot_pid"])
    record["descendant_alive_at_return"] = proc_alive(record["descendant_pid"])
    state, ppid = proc_stat(record["descendant_pid"])
    record["descendant_state_at_return"] = state
    record["descendant_ppid_at_return"] = ppid


def run_arm(run_process, classify_process, case, extra_args, bound, outfile):
    record = {"case": case, "command": command_for(extra_args),
              "bound_seconds": bound, "driver": "run_process_verbatim",
              "actual_exit": None, "error": None}
    started = time.monotonic()
    output, code, error = run_process(record["command"], bound)
    record["elapsed_seconds"] = round(time.monotonic() - started, 3)
    (RAW / outfile).write_text(output or "")
    record["actual_exit"] = code
    record["error"] = error
    record["inner_classification"] = classify_process(code, error, output or "", 0, MARKER)
    finalize(record, output)
    print(f"{case}: exit={code} err={error!r} elapsed={record['elapsed_seconds']}s "
          f"classify={record['inner_classification']} godot_alive={record['godot_alive_at_return']} "
          f"desc_alive={record['descendant_alive_at_return']}", flush=True)
    return record


def run_arm_popen(classify_process, case, extra_args, bound, outfile):
    """Popen variant: polls the direct child at the TimeoutExpired catch."""
    record = {"case": case, "command": command_for(extra_args),
              "bound_seconds": bound, "driver": "popen_communicate",
              "actual_exit": None, "error": None, "timed_out": False,
              "child_exit_at_timeout": None}
    started = time.monotonic()
    output = ""
    process = subprocess.Popen(record["command"], stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE, text=True, bufsize=1)
    try:
        out, err = process.communicate(timeout=bound)
        output = (out or "") + (err or "")
        record["actual_exit"] = process.returncode
    except subprocess.TimeoutExpired as exc:
        record["timed_out"] = True
        record["child_exit_at_timeout"] = process.poll()
        out = exc.stdout.decode(errors="replace") if isinstance(exc.stdout, bytes) else (exc.stdout or "")
        err = exc.stderr.decode(errors="replace") if isinstance(exc.stderr, bytes) else (exc.stderr or "")
        output = out + err
        record["error"] = f"TIMEOUT after {bound} seconds"
        if process.poll() is None:
            process.kill()
        try:
            process.wait(timeout=3)
        except subprocess.TimeoutExpired:
            record["error"] += "; post-timeout wait timed out"
    record["elapsed_seconds"] = round(time.monotonic() - started, 3)
    (RAW / outfile).write_text(output)
    record["inner_classification"] = classify_process(
        None if record["timed_out"] else record["actual_exit"],
        record["error"], output, 0, MARKER)
    finalize(record, output)
    # Hygiene: the orphaned descendant self-exits ~7s after spawn; reap early.
    if proc_alive(record["descendant_pid"]):
        try:
            os.kill(record["descendant_pid"], signal.SIGKILL)
            record["descendant_reaped_by_driver"] = True
        except OSError as exc:
            record["descendant_reaped_by_driver"] = f"kill failed: {exc}"
    print(f"{case}: exit={record['actual_exit']} err={record['error']!r} "
          f"elapsed={record['elapsed_seconds']}s child_exit_at_timeout={record['child_exit_at_timeout']} "
          f"classify={record['inner_classification']} "
          f"desc_alive={record['descendant_alive_at_return']}", flush=True)
    return record


def main():
    RAW.mkdir(parents=True, exist_ok=True)
    runner_sha = hashlib.sha256(RUNNER.read_bytes()).hexdigest()
    run_process, classify_process, segs = extract_runner_functions(RUNNER)
    env = {
        "godot_version": subprocess.run([GODOT, "--version"], capture_output=True, text=True).stdout.strip(),
        "python": sys.version.split()[0],
        "platform": subprocess.run(["uname", "-srvm"], capture_output=True, text=True).stdout.strip(),
        "runner": str(RUNNER),
        "runner_sha256": runner_sha,
        "started_utc": datetime.now(timezone.utc).isoformat(),
    }
    print(json.dumps(env, indent=2), flush=True)

    bound = 3.0
    results = [
        run_arm(run_process, classify_process, "clean", [], bound, "clean.stdout"),
        run_arm(run_process, classify_process, "hold_run", ["--spawn-hold"], bound, "hold-run.stdout"),
        run_arm_popen(classify_process, "hold_popen", ["--spawn-hold"], bound, "hold-popen.stdout"),
        run_arm(run_process, classify_process, "detach", ["--spawn-detach"], bound, "detach.stdout"),
    ]
    payload = {
        "mode": "descendant_pipe_eof_four_arm",
        "mechanism": (
            "run_process uses subprocess.run(capture_output, timeout); on POSIX "
            "communicate(timeout) returns only when the child exits AND both "
            "captured pipes reach EOF; a descendant holding inherited pipes "
            "delays EOF past the bound -> TIMEOUT with the child already dead; "
            "timeout kill targets the direct child only, descendants orphan"),
        "environment": env,
        "results": results,
    }
    out_path = HERE / "descendant-probe-verdicts.json"
    out_path.write_text(json.dumps(payload, indent=2) + "\n")
    print(f"receipt: {out_path}", flush=True)


if __name__ == "__main__":
    main()
