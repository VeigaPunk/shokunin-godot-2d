#!/usr/bin/env python3
"""r102-D0 C2 lead reproduction harness for the r62 timeout_probe arms.

Replicates the `--probe-timeout` arm semantics (run_battery.py:5322-5369) against a
scratch copy of the fixture tree.  NEVER imports or runs run_battery.py.

Modes:
  sweep      --delay-clean over a bound ladder -> marker-observation crossover
  markertime --hold-open with a timestamped stdout reader -> marker arrival seconds
  arms       exact three-arm replication, N reps
  killcheck  --hold-open killed past the expected marker time (SIGKILL buffer-loss test)
"""
import argparse, json, os, subprocess, sys, time, threading

GODOT = "godot"
SCRIPT = "res://timeout_probe.gd"
MARKER = "TIMEOUT_PROBE: expected signature"


def run_arm(scratch, extra_args, bound, cleanup_seconds=3, timestamps=False, quiet=False):
    command = [GODOT, "--headless", "--path", str(scratch), "--script", SCRIPT, "--"] + extra_args
    record = {"case": None, "command": command, "timeout_seconds": bound,
              "actual_exit": None, "error": None, "marker_observed": False,
              "timed_out": False, "process_was_running": False,
              "direct_child_alive_after_cleanup": None, "raw_stdout": "", "raw_stderr": "",
              "marker_arrival_seconds": None, "banner_arrival_seconds": None}
    process = None
    lines = []
    started_at = time.monotonic()

    def reader(stream, sink):
        for line in iter(stream.readline, ""):
            sink.append((time.monotonic() - started_at, line))

    # A byte stream written by Godot is read line-wise here purely when timestamps are
    # requested; the plain path uses communicate() exactly like the production driver.
    t_stdout, t_stderr = [], []
    threads = []
    try:
        if timestamps:
            process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                       text=True, bufsize=1)
            threads = [threading.Thread(target=reader, args=(process.stdout, t_stdout), daemon=True),
                       threading.Thread(target=reader, args=(process.stderr, t_stderr), daemon=True)]
            for t in threads:
                t.start()
            try:
                process.wait(timeout=bound)
            except subprocess.TimeoutExpired:
                record["timed_out"] = True
            if process.poll() is None:
                record["process_was_running"] = True
                process.kill()
                process.wait(timeout=cleanup_seconds)
            for t in threads:
                t.join(timeout=1)
            record["raw_stdout"] = "".join(l for _, l in t_stdout)
            record["raw_stderr"] = "".join(l for _, l in t_stderr)
            for ts, line in t_stdout + t_stderr:
                if MARKER in line and record["marker_arrival_seconds"] is None:
                    record["marker_arrival_seconds"] = round(ts, 3)
                elif "Godot Engine v" in line and record["banner_arrival_seconds"] is None:
                    record["banner_arrival_seconds"] = round(ts, 3)
            record["actual_exit"] = None if record["timed_out"] else process.returncode
        else:
            process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                       text=True, bufsize=1)
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
                more_out, more_err = process.communicate(timeout=cleanup_seconds)
                record["raw_stdout"], record["raw_stderr"] = more_out or "", more_err or ""
                record["cleanup_exit_code"] = process.returncode
    except (OSError, ValueError, subprocess.TimeoutExpired) as exc:
        record["error"] = f"launch/read/cleanup error: {exc}"
        if process is not None and process.poll() is None:
            process.kill()
            try:
                process.communicate(timeout=cleanup_seconds)
            except subprocess.TimeoutExpired:
                record["error"] += "; direct-child cleanup timed out"
    finally:
        if process is not None:
            record["actual_exit"] = None if record["timed_out"] else process.poll()
            record["direct_child_alive_after_cleanup"] = process.poll() is None
    record["elapsed_seconds"] = round(time.monotonic() - started_at, 3)
    record["marker_observed"] = MARKER in record["raw_stdout"]
    record["banner_observed"] = "Godot Engine v" in record["raw_stdout"]
    return record


def summary(record, case):
    return (f"{case:26s} bound={record['timeout_seconds']:<5} timed_out={int(record['timed_out'])} "
            f"marker={int(record['marker_observed'])} banner={int(record['banner_observed'])} "
            f"exit={record['actual_exit']} elapsed={record['elapsed_seconds']} "
            f"marker_at={record['marker_arrival_seconds']} alive_after={record['direct_child_alive_after_cleanup']}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--scratch", required=True)
    ap.add_argument("--mode", required=True,
                    choices=["sweep", "markertime", "arms", "killcheck", "policy"])
    ap.add_argument("--reps", type=int, default=1)
    ap.add_argument("--out", default=None)
    args = ap.parse_args()
    scratch = args.scratch
    results, payload = [], {}

    if args.mode == "sweep":
        for bound in [0.5, 0.6, 0.7, 0.75, 0.8, 0.85, 0.9, 1.0, 1.25, 1.5, 2.0, 2.5]:
            r = run_arm(scratch, ["--delay-clean"], bound)
            r["case"] = f"sweep_delay_clean_{bound}"
            results.append(r)
            print(summary(r, r["case"]), flush=True)
        payload = {"mode": "bound_sweep", "delay_seconds": 1.5}
    elif args.mode == "markertime":
        for i in range(args.reps):
            r = run_arm(scratch, ["--hold-open"], 6.0, timestamps=True)
            r["case"] = f"markertime_rep{i}"
            results.append(r)
            print(summary(r, r["case"]), flush=True)
        payload = {"mode": "marker_arrival", "note": "hold-open, 6.0s bound; killed past 30s timer"}
    elif args.mode == "arms":
        for i in range(args.reps):
            for case, extra, bound in [("slow_clean_old_bound", ["--delay-clean"], 0.75),
                                       ("slow_clean_new_bound", ["--delay-clean"], 3.0),
                                       ("hold_open_new_bound", ["--hold-open"], 3.0)]:
                r = run_arm(scratch, extra, bound)
                r["case"] = f"{case}_rep{i}"
                results.append(r)
                print(summary(r, r["case"]), flush=True)
        payload = {"mode": "three_arm_replication", "constants":
                   {"old": 0.75, "new": 3.0, "delay": 1.5, "cleanup": 3}}
    elif args.mode == "killcheck":
        for bound in [1.0, 1.25, 1.5, 2.0]:
            r = run_arm(scratch, ["--hold-open"], bound)
            r["case"] = f"killcheck_hold_open_{bound}"
            results.append(r)
            print(summary(r, r["case"]), flush=True)
        payload = {"mode": "sigkill_buffer_loss_test",
                   "claim_under_test": "a SIGKILLed Godot child loses unflushed captured bytes"}
    elif args.mode == "policy":
        # Candidate repair R-B, evaluated verbatim: both bounds are derived from a same-run
        # no-flag control arm instead of carried as host-independent constants.
        old_margin = float(os.environ.get("D0_OLD_MARGIN", "0.35"))
        new_margin = float(os.environ.get("D0_NEW_MARGIN", "0.75"))
        delay_seconds = float(os.environ.get("D0_DELAY_SECONDS", "1.5"))

        def inner_ok(record):
            # classify_process(run_battery.py:1775) restricted to this surface's inputs.
            output = record["raw_stdout"] + record["raw_stderr"]
            unrelated = [l for l in output.splitlines() if "ERROR:" in l]
            return (record["actual_exit"] == 0 and record["error"] is None
                    and MARKER in output and not unrelated
                    and "SCRIPT ERROR:" not in output and "Parse Error:" not in output)

        control = run_arm(scratch, [], 8.0)
        control["case"] = "clean_startup_control"
        results.append(control)
        print(summary(control, control["case"]), flush=True)
        startup = control["elapsed_seconds"]
        old_bound = round(startup + old_margin, 3)
        new_bound = round(startup + delay_seconds + new_margin, 3)
        old_positive = run_arm(scratch, ["--delay-clean"], old_bound)
        old_positive["case"] = "slow_clean_old_bound"
        new_positive = run_arm(scratch, ["--delay-clean"], new_bound)
        new_positive["case"] = "slow_clean_new_bound"
        hold_open = run_arm(scratch, ["--hold-open"], new_bound)
        hold_open["case"] = "hold_open_new_bound"
        trio = [old_positive, new_positive, hold_open]
        results += trio
        for r in trio:
            print(summary(r, r["case"]), flush=True)
        old_rejects = (old_positive["timed_out"] and old_positive["marker_observed"]
                       and not inner_ok(old_positive)
                       and old_positive["direct_child_alive_after_cleanup"] is False)
        new_accepts = (not new_positive["timed_out"] and inner_ok(new_positive)
                       and new_positive["marker_observed"])
        hold_rejects = (hold_open["timed_out"] and hold_open["marker_observed"]
                        and not inner_ok(hold_open)
                        and hold_open["direct_child_alive_after_cleanup"] is False)
        clauses = {"old_rejects": bool(old_rejects), "new_accepts": bool(new_accepts),
                   "hold_rejects": bool(hold_rejects)}
        payload = {"mode": "measured_bound_policy", "control_elapsed": startup,
                   "old_bound": old_bound, "new_bound": new_bound, "old_margin": old_margin,
                   "new_margin": new_margin, "delay_seconds": delay_seconds,
                   "inner_classifications": [inner_ok(r) for r in trio],
                   "clauses": clauses,
                   "policy_verdict": "PASS" if all(clauses.values()) else "FAIL"}

    payload["results"] = results
    text = json.dumps(payload, indent=2) + "\n"
    if args.out:
        with open(args.out, "w") as fh:
            fh.write(text)
    else:
        sys.stdout.write(text)


if __name__ == "__main__":
    main()
