#!/usr/bin/env python3
"""V5 independent replica of run_battery.py's probe_timeout bounded_run flow (3 arms x N reps).
Exact same capture order/fields as the driver, plus extra diagnostics (exc vs retry stdout split).
Writes /var/tmp/r102-ver5/logs/replica-matrix.json and prints one line per run.
"""
import json, subprocess, time, sys

GODOT = "godot"
SCRATCH = "/var/tmp/r102-ver5/scratch"
MARKER = "TIMEOUT_PROBE: expected signature"
RETRIES = int(sys.argv[1]) if len(sys.argv) > 1 else 5
ARMS = [("slow_clean_old_bound", ["--delay-clean"], 0.75),
        ("slow_clean_new_bound", ["--delay-clean"], 3.0),
        ("hold_open_new_bound", ["--hold-open"], 3.0)]

def classify_process(code, error, output, expected_exit, signature, allowed_errors=()):
    lines = output.splitlines()
    unrelated_errors = [l for l in lines if "ERROR:" in l and not any(l.strip() == a for a in allowed_errors)]
    return (code == expected_exit and error is None and signature in output
            and not unrelated_errors and "SCRIPT ERROR:" not in output and "Parse Error:" not in output)

def bounded_run(case, extra_args, bound):
    command = [GODOT, "--headless", "--path", SCRATCH, "--script", "res://timeout_probe.gd", "--"] + extra_args
    record = {"case": case, "command": command, "expected_exit": 0,
              "timeout_seconds": bound, "cleanup_seconds": 3,
              "actual_exit": None, "error": None, "marker_observed": False,
              "timed_out": False, "process_was_running": False,
              "direct_child_alive_after_cleanup": None, "raw_stdout": "", "raw_stderr": ""}
    process = None
    started_at = time.monotonic()
    try:
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, bufsize=1)
        try:
            out, err = process.communicate(timeout=bound)
            record["raw_stdout"], record["raw_stderr"] = out, err
            record["actual_exit"] = process.returncode
        except subprocess.TimeoutExpired as exc:
            record["timed_out"] = True
            out = exc.stdout.decode(errors="replace") if isinstance(exc.stdout, bytes) else (exc.stdout or "")
            err = exc.stderr.decode(errors="replace") if isinstance(exc.stderr, bytes) else (exc.stderr or "")
            record["exc_stdout"] = out
            record["exc_stdout_len"] = len(out)
            record["exc_stdout_has_marker"] = MARKER in out
            record["raw_stdout"], record["raw_stderr"] = out, err
            record["marker_observed"] = MARKER in out
            record["process_was_running"] = process.poll() is None
            record["error"] = "TIMEOUT after %s seconds" % bound
            if process.poll() is None:
                process.kill()
            more_out, more_err = process.communicate(timeout=3)
            record["retry_stdout"] = more_out or ""
            record["raw_stdout"], record["raw_stderr"] = more_out or "", more_err or ""
            record["cleanup_exit_code"] = process.returncode
    except (OSError, ValueError, subprocess.TimeoutExpired) as exc:
        record["error"] = "launch/read/cleanup error: %s" % exc
        if process is not None and process.poll() is None:
            process.kill()
            try:
                process.communicate(timeout=3)
            except subprocess.TimeoutExpired:
                record["error"] += "; direct-child cleanup timed out"
    finally:
        if process is not None:
            record["actual_exit"] = None if record["timed_out"] else process.poll()
            record["direct_child_alive_after_cleanup"] = process.poll() is None
    record["elapsed_seconds"] = round(time.monotonic() - started_at, 3)
    record["marker_observed"] = MARKER in record["raw_stdout"]
    record["inner_classification"] = classify_process(record["actual_exit"], record["error"],
                                                      record["raw_stdout"] + record["raw_stderr"], 0, MARKER)
    return record

def loadavg():
    return open("/proc/loadavg").read().split()[0:3]

def main():
    matrix = {"retries": RETRIES, "scratch": SCRATCH, "godot": GODOT,
              "loadavg_start": loadavg(), "runs": []}
    for rep in range(1, RETRIES + 1):
        for case, extra, bound in ARMS:
            r = bounded_run(case, extra, bound)
            r["rep"] = rep
            r["loadavg_after"] = loadavg()
            matrix["runs"].append(r)
            print("rep%d %s to=%s marker=%s inner=%s rc=%s child_alive=%s elapsed=%s exc_len=%s retry_len=%s"
                  % (rep, case, r["timed_out"], r["marker_observed"], r["inner_classification"],
                     r["actual_exit"], r["direct_child_alive_after_cleanup"], r["elapsed_seconds"],
                     r.get("exc_stdout_len"), len(r.get("retry_stdout", ""))))
    # per-rep predicate simulation, mirroring driver constants exactly
    def preds(rep):
        by = {r["case"]: r for r in matrix["runs"] if r["rep"] == rep}
        o, n, h = by["slow_clean_old_bound"], by["slow_clean_new_bound"], by["hold_open_new_bound"]
        old_rejects = (o["timed_out"] and o["marker_observed"] and o["inner_classification"] is False
                       and o["direct_child_alive_after_cleanup"] is False)
        new_accepts = (not n["timed_out"] and n["actual_exit"] == 0 and n["marker_observed"]
                       and n["inner_classification"] is True)
        hold_rejects = (h["timed_out"] and h["marker_observed"] and h["inner_classification"] is False
                        and h["direct_child_alive_after_cleanup"] is False)
        return old_rejects, new_accepts, hold_rejects, old_rejects and new_accepts and hold_rejects
    matrix["per_rep_predicates"] = {str(rep): preds(rep) for rep in range(1, RETRIES + 1)}
    matrix["loadavg_end"] = loadavg()
    with open("/var/tmp/r102-ver5/logs/replica-matrix.json", "w") as f:
        json.dump(matrix, f, indent=2)
    print("PREDS (old_rejects,new_accepts,hold_rejects,meta_pass):", matrix["per_rep_predicates"])
    return 0

if __name__ == "__main__":
    sys.exit(main())
