#!/usr/bin/env python3
"""Seat R2 (r102) C2 counterfactual replay — timeout-probe arms, standalone.

Process handling replicates run_battery.py:5322-5369 (r101 commit ac4eb8d4,
`bounded_run`) verbatim: Popen(text=True, bufsize=1) -> communicate(bound);
on TimeoutExpired kill + second communicate (whose accumulated output
REPLACES raw_stdout); then marker recomputed from final raw_stdout;
inner_classification = classify_process(code, error, out+err, 0, marker).

Modes:
  arms --old-bound S --repeat N   three canonical arms; prints per-arm record
         fields + clause evaluation (current clauses + marker-dropped variant)
  timeline --args "..." --bound S  line-timestamped run: t_banner/t_marker

NEVER runs corpus/fixtures/run_battery.py.
"""
import argparse
import json
import subprocess
import sys
import time

GODOT = "/usr/bin/godot"
PROJ = "/var/tmp/r102-R2/proj"
SCRIPT = "res://timeout_probe.gd"
MARKER = "TIMEOUT_PROBE: expected signature"
EXPECTED_EXIT = 0
NEW_BOUND = 3.0
CLEANUP = 3


def classify_process(code, error, output):
    lines = output.splitlines()
    unrelated_errors = [line for line in lines if "ERROR:" in line]
    return (code == EXPECTED_EXIT and error is None and MARKER in output
            and not unrelated_errors and "SCRIPT ERROR:" not in output
            and "Parse Error:" not in output)


def bounded_run(case, extra_args, bound):
    command = [GODOT, "--headless", "--path", PROJ, "--script", SCRIPT, "--"] + extra_args
    record = {"case": case, "command": command, "expected_exit": EXPECTED_EXIT,
              "timeout_seconds": bound, "cleanup_seconds": CLEANUP,
              "actual_exit": None, "error": None, "marker_observed": False,
              "timed_out": False, "process_was_running": False,
              "direct_child_alive_after_cleanup": None, "raw_stdout": "", "raw_stderr": ""}
    process = None
    started_at = time.monotonic()
    try:
        process = subprocess.Popen(command, stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE, text=True, bufsize=1)
        try:
            out, err = process.communicate(timeout=bound)
            record["raw_stdout"], record["raw_stderr"] = out, err
            record["actual_exit"] = process.returncode
        except subprocess.TimeoutExpired as exc:
            record["timed_out"] = True
            out = exc.stdout.decode(errors="replace") if isinstance(exc.stdout, bytes) else (exc.stdout or "")
            err = exc.stderr.decode(errors="replace") if isinstance(exc.stderr, bytes) else (exc.stderr or "")
            record["raw_stdout"], record["raw_stderr"] = out, err
            record["marker_observed"] = MARKER in out
            record["process_was_running"] = process.poll() is None
            record["error"] = f"TIMEOUT after {bound} seconds"
            if process.poll() is None:
                process.kill()
            more_out, more_err = process.communicate(timeout=CLEANUP)
            record["raw_stdout"], record["raw_stderr"] = more_out or "", more_err or ""
            record["cleanup_exit_code"] = process.returncode
    except (OSError, ValueError, subprocess.TimeoutExpired) as exc:
        record["error"] = f"launch/read/cleanup error: {exc}"
        if process is not None and process.poll() is None:
            process.kill()
            try:
                process.communicate(timeout=CLEANUP)
            except subprocess.TimeoutExpired:
                record["error"] += "; direct-child cleanup timed out"
    finally:
        if process is not None:
            record["actual_exit"] = None if record["timed_out"] else process.poll()
            record["direct_child_alive_after_cleanup"] = process.poll() is None
    record["elapsed_seconds"] = round(time.monotonic() - started_at, 3)
    record["marker_observed"] = MARKER in record["raw_stdout"]
    record["inner_classification"] = classify_process(
        record["actual_exit"], record["error"],
        record["raw_stdout"] + record["raw_stderr"])
    return record


def eval_clauses(old, new, hold, old_bound):
    old_rejects = (old["timed_out"] and old["marker_observed"]
                   and old["inner_classification"] is False
                   and old["direct_child_alive_after_cleanup"] is False)
    # candidate repair variant: marker-on-old-arm demoted to diagnostic
    old_rejects_nomarker = (old["timed_out"]
                            and old["inner_classification"] is False
                            and old["direct_child_alive_after_cleanup"] is False)
    new_accepts = (not new["timed_out"] and new["actual_exit"] == EXPECTED_EXIT
                   and new["marker_observed"] and new["inner_classification"] is True)
    hold_rejects = (hold["timed_out"] and hold["marker_observed"]
                    and hold["inner_classification"] is False
                    and hold["direct_child_alive_after_cleanup"] is False)
    return {"old_bound": old_bound,
            "old_rejects_current": bool(old_rejects),
            "old_rejects_without_marker_clause": bool(old_rejects_nomarker),
            "new_accepts": bool(new_accepts), "hold_rejects": bool(hold_rejects),
            "meta_pass_current": bool(old_rejects and new_accepts and hold_rejects),
            "meta_pass_envelope_variant": bool(old_rejects_nomarker and new_accepts and hold_rejects)}


def mode_arms(args):
    for i in range(args.repeat):
        old = bounded_run("slow_clean_old_bound", ["--delay-clean"], args.old_bound)
        new = bounded_run("slow_clean_new_bound", ["--delay-clean"], NEW_BOUND)
        hold = bounded_run("hold_open_new_bound", ["--hold-open"], NEW_BOUND)
        for r in (old, new, hold):
            r.pop("command", None)
        print(json.dumps({"repeat": i + 1, "arms": [old, new, hold],
                          "clauses": eval_clauses(old, new, hold, args.old_bound)}))


def mode_timeline(args):
    import threading
    command = [GODOT, "--headless", "--path", PROJ, "--script", SCRIPT,
               "--"] + args.args.split()
    started = time.monotonic()
    p = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                         text=True, bufsize=1)
    marks = {}

    def reader():
        for line in p.stdout:
            t = round(time.monotonic() - started, 3)
            if "Godot Engine v" in line and "t_banner" not in marks:
                marks["t_banner"] = t
            if MARKER in line and "t_marker" not in marks:
                marks["t_marker"] = t

    th = threading.Thread(target=reader, daemon=True)
    th.start()
    while time.monotonic() < started + args.bound and p.poll() is None:
        time.sleep(0.02)
    killed_at_bound = p.poll() is None
    if killed_at_bound:
        p.kill()
    p.communicate(timeout=CLEANUP)
    th.join(timeout=1.0)
    marks["bound"] = args.bound
    marks["args"] = args.args
    marks["killed_at_bound"] = killed_at_bound
    marks["elapsed_seconds"] = round(time.monotonic() - started, 3)
    print(json.dumps(marks))


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="mode", required=True)
    a1 = sub.add_parser("arms")
    a1.add_argument("--old-bound", type=float, required=True)
    a1.add_argument("--repeat", type=int, default=1)
    a2 = sub.add_parser("timeline")
    a2.add_argument("--args", required=True)
    a2.add_argument("--bound", type=float, default=10.0)
    args = ap.parse_args()
    if args.mode == "arms":
        mode_arms(args)
    else:
        mode_timeline(args)


if __name__ == "__main__":
    sys.exit(main())
