#!/usr/bin/env python3
"""r102-w7: targeted replay of run_battery.py's probe_timeout three-arm bounded_run.

Mirrors the driver at corpus/fixtures/run_battery.py:5322-5369 (read-only copy) so the
r101 red conjunct (slow_clean_old_bound.marker_observed) can be reproduced/attributed on
a scratch project. This is NOT run_battery.py and never touches the battery.

usage: python3 r102-w7-timeout-bound-repro.py /var/tmp/r102-w7/proj
"""
import json
import subprocess
import sys
import time

MARKER = "TIMEOUT_PROBE: expected signature"


def bounded_run(proj, case, extra_args, bound, cleanup_seconds=3.0):
    command = ["godot", "--headless", "--path", proj, "--script",
               "res://timeout_probe.gd", "--"] + extra_args
    record = {"case": case, "command": command, "timeout_seconds": bound,
              "timed_out": False, "marker_observed": False, "actual_exit": None,
              "error": None, "process_was_running": None,
              "direct_child_alive_after_cleanup": None, "raw_stdout": ""}
    started_at = time.monotonic()
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                               text=True, bufsize=1)
    try:
        out, err = process.communicate(timeout=bound)
        record["raw_stdout"], record["raw_stderr"] = out, err
        record["actual_exit"] = process.returncode
    except subprocess.TimeoutExpired as exc:
        record["timed_out"] = True
        out = exc.stdout.decode(errors="replace") if isinstance(exc.stdout, bytes) else (exc.stdout or "")
        record["raw_stdout"] = out
        record["process_was_running"] = process.poll() is None
        record["error"] = f"TIMEOUT after {bound} seconds"
        if process.poll() is None:
            process.kill()
        more_out, more_err = process.communicate(timeout=cleanup_seconds)
        record["raw_stdout"], record["raw_stderr"] = more_out or "", more_err or ""
        record["cleanup_exit_code"] = process.returncode
    finally:
        if process.poll() is None:
            process.kill()
            process.communicate(timeout=cleanup_seconds)
        record["actual_exit"] = None if record["timed_out"] else process.poll()
        record["direct_child_alive_after_cleanup"] = process.poll() is None
    record["elapsed_seconds"] = round(time.monotonic() - started_at, 3)
    record["marker_observed"] = MARKER in record["raw_stdout"]
    record["inner_classification"] = (
        record["actual_exit"] == 0 and record["error"] is None
        and MARKER in record["raw_stdout"])
    return record


def marker_arrival(proj, extra_args):
    """Unbounded run; timestamp each stdout line to date marker arrival from exec."""
    command = ["godot", "--headless", "--path", proj, "--script",
               "res://timeout_probe.gd", "--"] + extra_args
    started_at = time.monotonic()
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                               text=True, bufsize=1)
    lines = []
    for line in process.stdout:
        lines.append((round(time.monotonic() - started_at, 3), line.rstrip("\n")))
    process.wait(timeout=30)
    return {"elapsed": round(time.monotonic() - started_at, 3), "line_times": lines,
            "exit": process.returncode}


def main():
    proj = sys.argv[1]
    runs = []
    for i in range(2):
        runs.append(bounded_run(proj, f"slow_clean_old_bound#iter{i+1}", ["--delay-clean"], 0.75))
        runs.append(bounded_run(proj, f"slow_clean_new_bound#iter{i+1}", ["--delay-clean"], 3.0))
    runs.append(bounded_run(proj, "hold_open_new_bound#iter1", ["--hold-open"], 3.0))
    arrival = marker_arrival(proj, ["--delay-clean"])
    print(json.dumps({"runs": runs, "marker_arrival_unbounded_delayclean": arrival},
                     indent=2))


if __name__ == "__main__":
    main()
