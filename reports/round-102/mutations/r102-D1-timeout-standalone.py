#!/usr/bin/env python3
"""r102-D1 standalone timeout-probe replication (does NOT import/run run_battery.py).

Phase A: verbatim bounded_run semantics transcribed from
  corpus/fixtures/run_battery.py:5322-5369 (lines read at r102), x5 per arm.
Phase B: instrumented reader threads, per-line arrival timestamps relative to
  Popen, x5 per arm  -> measures WHEN the marker bytes reach the parent.
Phase C: startup-latency estimator: --delay-clean under a 6.0s bound (clean
  exit 0 expected), x5 -> marker arrival t == Godot boot-to-_initialize latency.

classify_process reimplemented verbatim from run_battery.py:1775-1792.
Output: JSON to /var/tmp/r102-D1/d1-results.json + summary to stdout.
"""
import json
import subprocess
import sys
import threading
import time

GODOT = "godot"
SCRATCH = "/var/tmp/r102-D1/scratch"
SCRIPT = "res://timeout_probe.gd"
MARKER = "TIMEOUT_PROBE: expected signature"
CLEANUP_SECONDS = 3
EXPECTED_EXIT = 0

ARMS = [
    ("slow_clean_old_bound", ["--delay-clean"], 0.75),
    ("slow_clean_new_bound", ["--delay-clean"], 3.0),
    ("hold_open_new_bound", ["--hold-open"], 3.0),
]


def classify_process(code, error, output, expected_exit, signature, allowed_errors=()):
    lines = output.splitlines()

    def allowed_error(line, allowed):
        stripped = line.strip()
        if stripped == allowed:
            return True
        if allowed.endswith(","):
            return stripped.startswith(allowed) and stripped.count("ERROR:") == 1
        if allowed == "ERROR: chain incomplete":
            return (stripped.startswith("ERROR: chain incomplete collections=")
                    and "scene=SceneB:<Node#" in stripped and "old_alive=false" in stripped
                    and stripped.count("ERROR:") == 1)
        return False

    unrelated_errors = [line for line in lines if "ERROR:" in line
                        and not any(allowed_error(line, allowed) for allowed in allowed_errors)]
    return (code == expected_exit and error is None and signature in output
            and not unrelated_errors and "SCRIPT ERROR:" not in output and "Parse Error:" not in output)


def bounded_run(case, extra_args, bound):
    """Verbatim transcription of run_battery.py bounded_run (r102 read)."""
    command = [GODOT, "--headless", "--path", SCRATCH, "--script",
               SCRIPT, "--"] + extra_args
    record = {"case": case, "command": command, "expected_exit": EXPECTED_EXIT,
              "timeout_seconds": bound, "cleanup_seconds": CLEANUP_SECONDS,
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
            more_out, more_err = process.communicate(timeout=CLEANUP_SECONDS)
            record["raw_stdout"], record["raw_stderr"] = more_out or "", more_err or ""
            record["cleanup_exit_code"] = process.returncode
    except (OSError, ValueError, subprocess.TimeoutExpired) as exc:
        record["error"] = f"launch/read/cleanup error: {exc}"
        if process is not None and process.poll() is None:
            process.kill()
            try:
                process.communicate(timeout=CLEANUP_SECONDS)
            except subprocess.TimeoutExpired:
                record["error"] += "; direct-child cleanup timed out"
    finally:
        if process is not None:
            record["actual_exit"] = None if record["timed_out"] else process.poll()
            record["direct_child_alive_after_cleanup"] = process.poll() is None
    record["elapsed_seconds"] = round(time.monotonic() - started_at, 3)
    record["marker_observed"] = MARKER in record["raw_stdout"]
    record["inner_classification"] = classify_process(
        record["actual_exit"], record["error"], record["raw_stdout"] + record["raw_stderr"],
        EXPECTED_EXIT, MARKER)
    return record


def _reader(stream, name, start, events, store):
    for line in stream:
        events.append([round(time.monotonic() - start, 3), name, line.rstrip("\n")])
        store[name] += line


def instrumented_run(case, extra_args, bound):
    """Line-arrival timing; wait(timeout) deadline (no pipe-holding descendants
    in these arms, so wait-deadline == communicate-deadline for liveness)."""
    command = [GODOT, "--headless", "--path", SCRATCH, "--script",
               SCRIPT, "--"] + extra_args
    record = {"case": case, "command": command, "bound": bound,
              "actual_exit": None, "error": None, "timed_out": False,
              "alive_at_deadline": None, "line_events": [], "raw_stdout": ""}
    process = subprocess.Popen(command, stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE, text=True, bufsize=1)
    start = time.monotonic()
    events, store = [], {"stdout": "", "stderr": ""}
    threads = [threading.Thread(target=_reader, args=(process.stdout, "stdout", start, events, store)),
               threading.Thread(target=_reader, args=(process.stderr, "stderr", start, events, store))]
    for t in threads:
        t.start()
    try:
        rc = process.wait(timeout=bound)
        record["actual_exit"] = rc
    except subprocess.TimeoutExpired:
        record["timed_out"] = True
        record["alive_at_deadline"] = process.poll() is None
        record["error"] = f"TIMEOUT after {bound} seconds"
        if process.poll() is None:
            process.kill()
        record["actual_exit"] = process.wait()
    for t in threads:
        t.join(timeout=2)
    record["elapsed_seconds"] = round(time.monotonic() - start, 3)
    record["line_events"] = events
    record["raw_stdout"] = store["stdout"]
    record["raw_stderr"] = store["stderr"]
    banner_t = next((e[0] for e in events if e[1] == "stdout" and e[2].startswith("Godot Engine v")), None)
    marker_t = next((e[0] for e in events if e[1] == "stdout" and e[2] == MARKER), None)
    record["banner_arrival_t"] = banner_t
    record["marker_arrival_t"] = marker_t
    record["marker_observed"] = marker_t is not None
    return record


def main():
    repetitions = int(sys.argv[1]) if len(sys.argv) > 1 else 5
    out = {"host": {}, "phase_a_bounded_run": [], "phase_b_instrumented": [], "phase_c_startup": []}
    with open("/proc/loadavg") as fh:
        out["host"]["loadavg_at_start"] = fh.read().strip()
    out["host"]["uptime"] = subprocess.run(["uptime"], capture_output=True, text=True).stdout.strip()
    out["godot_version"] = subprocess.run([GODOT, "--version"], capture_output=True, text=True).stdout.strip()
    fixture_sha = subprocess.run(["sha256sum", f"{SCRATCH}/timeout_probe.gd"],
                                 capture_output=True, text=True).stdout.split()[0]
    out["scratch_fixture_sha256"] = fixture_sha

    for rep in range(repetitions):
        for case, extra, bound in ARMS:
            rec = bounded_run(case, extra, bound)
            rec["rep"] = rep + 1
            out["phase_a_bounded_run"].append(rec)
            print(f"A rep{rep+1} {case}: timed_out={rec['timed_out']} "
                  f"marker={rec['marker_observed']} exit={rec['actual_exit']} "
                  f"elapsed={rec['elapsed_seconds']} err={rec['error']}", flush=True)

    for rep in range(repetitions):
        for case, extra, bound in ARMS:
            rec = instrumented_run(case, extra, bound)
            rec["rep"] = rep + 1
            out["phase_b_instrumented"].append(rec)
            print(f"B rep{rep+1} {case}: banner_t={rec['banner_arrival_t']} "
                  f"marker_t={rec['marker_arrival_t']} timed_out={rec['timed_out']} "
                  f"elapsed={rec['elapsed_seconds']}", flush=True)

    for rep in range(repetitions):
        rec = instrumented_run("startup_estimator", ["--delay-clean"], 6.0)
        rec["rep"] = rep + 1
        out["phase_c_startup"].append(rec)
        print(f"C rep{rep+1} startup_estimator: banner_t={rec['banner_arrival_t']} "
              f"marker_t={rec['marker_arrival_t']} exit={rec['actual_exit']} "
              f"elapsed={rec['elapsed_seconds']}", flush=True)

    with open("/proc/loadavg") as fh:
        out["host"]["loadavg_at_end"] = fh.read().strip()
    with open("/var/tmp/r102-D1/d1-results.json", "w") as fh:
        json.dump(out, fh, indent=2)
    print("WROTE /var/tmp/r102-D1/d1-results.json")


if __name__ == "__main__":
    main()
