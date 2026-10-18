#!/usr/bin/env python3
"""r102-D3 instrumented replica of run_battery.py --probe-timeout arms.

Shipped call sequence is reproduced byte-for-byte (Popen text/bufsize=1,
communicate(timeout), kill, second communicate, raw_stdout := post-kill only).
Instrumentation records exc.stdout (pre-kill partial) and post-kill remainder
separately so shipped-vs-union capture outcomes are both scorable.
"""
import json, os, selectors, subprocess, time

MARKER = "TIMEOUT_PROBE: expected signature"
BANNER = "Godot Engine v"
SCRATCH = "/var/tmp/r102-D3/scratch"
GODOT = "godot"
OUT = "/var/tmp/r102-D3/replica-results.json"


def classify(code, error, output, expected_exit=0):
    return (code == expected_exit and error is None and MARKER in output
            and "SCRIPT ERROR:" not in output and "Parse Error:" not in output)


def bounded_run(case, extra_args, bound, cleanup=3):
    command = [GODOT, "--headless", "--path", SCRATCH, "--script",
               "res://timeout_probe.gd", "--"] + extra_args
    rec = {"case": case, "bound": bound, "load": os.getloadavg()}
    process = None
    timed_out = False
    exc_out = more_out = ""
    raw_stdout = raw_stderr = ""
    error = None
    started = time.monotonic()
    try:
        process = subprocess.Popen(command, stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE, text=True, bufsize=1)
        try:
            out, err = process.communicate(timeout=bound)
            raw_stdout, raw_stderr = out, err
            actual_exit = process.returncode
        except subprocess.TimeoutExpired as exc:
            timed_out = True
            exc_out = exc.stdout.decode(errors="replace") if isinstance(exc.stdout, bytes) else (exc.stdout or "")
            if process.poll() is None:
                process.kill()
            more_out, more_err = process.communicate(timeout=cleanup)
            raw_stdout, raw_stderr = more_out or "", more_err or ""  # shipped clobber
            error = f"TIMEOUT after {bound} seconds"
            rec["cleanup_exit_code"] = process.returncode
    except (OSError, ValueError) as exc:
        error = f"launch/read/cleanup error: {exc}"
        if process is not None and process.poll() is None:
            process.kill()
            try:
                process.communicate(timeout=cleanup)
            except subprocess.TimeoutExpired:
                error += "; direct-child cleanup timed out"
    finally:
        if process is not None:
            rec["actual_exit"] = None if timed_out else process.poll()
            rec["direct_child_alive_after_cleanup"] = process.poll() is None
    rec["elapsed_seconds"] = round(time.monotonic() - started, 3)
    rec["error"] = error
    rec["timed_out"] = timed_out
    rec["exc_stdout"] = exc_out
    rec["more_out"] = more_out or ""
    rec["exc_len"] = len(exc_out)
    rec["more_len"] = len(more_out or "")
    rec["banner_in_exc"] = BANNER in exc_out
    rec["banner_in_more"] = BANNER in (more_out or "")
    rec["marker_in_exc"] = MARKER in exc_out
    rec["marker_in_more"] = MARKER in (more_out or "")
    rec["shipped_marker_observed"] = MARKER in raw_stdout
    rec["union_text"] = exc_out + (more_out or "")
    rec["union_marker_observed"] = MARKER in rec["union_text"]
    rec["shipped_inner_classification"] = classify(rec["actual_exit"], error, raw_stdout + raw_stderr)
    rec["union_inner_classification"] = classify(rec["actual_exit"], error, rec["union_text"] + raw_stderr)
    return rec


def timing_run(case, extra_args, bound=5.0):
    command = [GODOT, "--headless", "--path", SCRATCH, "--script",
               "res://timeout_probe.gd", "--"] + extra_args
    t0 = time.monotonic()
    p = subprocess.Popen(command, stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE, text=True, bufsize=1)
    sel = selectors.DefaultSelector()
    sel.register(p.stdout, selectors.EVENT_READ)
    events = []
    eof = False
    try:
        while (not eof) and (time.monotonic() - t0 < bound):
            for key, _ in sel.select(0.05):
                line = key.fileobj.readline()
                if not line:
                    sel.unregister(key.fileobj)
                    eof = True
                else:
                    events.append([round(time.monotonic() - t0, 3), line.rstrip("\n")[:90]])
            if eof and p.poll() is None:
                time.sleep(0.05)
    finally:
        sel.close()
        if p.poll() is None:
            p.kill()
        p.communicate(timeout=5)
    return {"case": case, "bound": bound, "events": events,
            "exit": p.returncode, "elapsed": round(time.monotonic() - t0, 3)}


def main():
    results = {"godot": subprocess.run([GODOT, "--version"], capture_output=True, text=True).stdout.strip(),
               "load0": os.getloadavg(), "runs": []}
    plan = []
    for i in range(4):
        plan.append(("timing_hold_open_%d" % i, timing_run, ["--hold-open"]))
    for i in range(2):
        plan.append(("timing_delay_clean_%d" % i, timing_run, ["--delay-clean"]))
    for i in range(8):
        plan.append(("repl_delay_clean_b075_%d" % i, None, (["--delay-clean"], 0.75)))
    for i in range(4):
        plan.append(("repl_delay_clean_b100_%d" % i, None, (["--delay-clean"], 1.0)))
    for i in range(4):
        plan.append(("repl_delay_clean_b125_%d" % i, None, (["--delay-clean"], 1.25)))
    for i in range(2):
        plan.append(("repl_delay_clean_b140_%d" % i, None, (["--delay-clean"], 1.4)))
    for i in range(2):
        plan.append(("repl_hold_open_b300_%d" % i, None, (["--hold-open"], 3.0)))
    for case, fn, a in plan:
        if fn is timing_run:
            r = timing_run(case, a)
        else:
            r = bounded_run(case, a[0], a[1])
        results["runs"].append(r)
        if "events" in r:
            print(case, "exit", r["exit"], "elapsed", r["elapsed"], "events",
                  "; ".join(f"{t}s {txt[:40]!r}" for t, txt in r["events"]), flush=True)
        else:
            print(case, "timed_out", r["timed_out"], "elapsed", r["elapsed_seconds"],
                  "shipped_marker", r["shipped_marker_observed"],
                  "union_marker", r["union_marker_observed"],
                  "exc_len", r["exc_len"], "more_len", r["more_len"],
                  "load", [round(x, 1) for x in r["load"]], flush=True)
    with open(OUT, "w") as fh:
        json.dump(results, fh, indent=1)
    print("wrote", OUT)


if __name__ == "__main__":
    main()
