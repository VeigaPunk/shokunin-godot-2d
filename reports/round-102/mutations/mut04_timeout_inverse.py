#!/usr/bin/env python3
"""mut04 -- M4 inverse-mutation harness for the C2 timeout probe (r102).

Mirrors run_battery.py's probe_timeout block VERBATIM (bounded_run + the three
clause expressions + meta_pass, lines 5322-5396 at r101-close commit 1392ca21),
parameterized on the fix constants so it can be re-pointed at D3's final fix.

The mirror runs the three arms against a chosen fixture VARIANT:
  healthy      stock corpus/fixtures/timeout_probe.gd (control)
  delay-short  inverse of the bound fix, completion side: --delay-clean delay
               shrunk to ~20% of old bound -> old arm exits clean inside bound
  slow-marker  inverse of the bound fix, startup side: marker delayed past the
               old bound -> marker never captured at kill (the r101 red class)
  hold-noop    --hold-open no longer holds -> hold arm exits clean
  marker-absent no marker printed at all -> signature lost on all arms

Exit 0 iff the probe verdict matches --expect; 1 otherwise (self-checking).
Never runs run_battery.py.
"""
import argparse, hashlib, json, os, shutil, signal, subprocess, sys, time

STOCK_FIXTURE = "corpus/fixtures/timeout_probe.gd"
MARKER_TEXT = "TIMEOUT_PROBE: expected signature"


def classify_process(code, error, output, expected_exit, signature):
    # exact port of run_battery.py:1775-1792 for the probe_timeout call site
    # (allowed_errors=(), so every "ERROR:" line is unrelated)
    lines = output.splitlines()
    unrelated_errors = [line for line in lines if "ERROR:" in line]
    return (code == expected_exit and error is None and signature in output
            and not unrelated_errors and "SCRIPT ERROR:" not in output and "Parse Error:" not in output)


def make_variant(text, variant, old_bound):
    if variant == "healthy":
        return text
    if variant == "delay-short":
        out = text.replace("create_timer(1.5)", "create_timer(%.3f)" % (0.2 * old_bound))
    elif variant == "slow-marker":
        out = text.replace("print(MARKER)",
                           "await create_timer(%.3f).timeout\n\tprint(MARKER)" % (old_bound + 1.0))
    elif variant == "hold-noop":
        out = text.replace('if "--hold-open" in user_args:\n\t\tawait create_timer(30.0).timeout',
                           'if "--hold-open" in user_args:\n\t\tpass')
    elif variant == "marker-absent":
        out = text.replace("\tprint(MARKER)\n", "")
    else:
        raise SystemExit("unknown variant " + variant)
    assert out != text, "variant %s produced no change" % variant
    return out


def bounded_run(case, extra_args, bound, godot, scratch, script_path, marker_text,
                expected_exit, cleanup_seconds):
    # verbatim port of run_battery.py:5322-5369 (r101-close)
    command = [godot, "--headless", "--path", str(scratch), "--script",
               script_path, "--"] + extra_args
    record = {"case": case, "command": command, "expected_exit": expected_exit,
              "timeout_seconds": bound, "cleanup_seconds": cleanup_seconds,
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
            record["marker_observed"] = marker_text in out
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
    record["marker_observed"] = marker_text in record["raw_stdout"]
    record["inner_classification"] = classify_process(
        record["actual_exit"], record["error"], record["raw_stdout"] + record["raw_stderr"],
        expected_exit, marker_text)
    return record


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--godot", default="godot")
    ap.add_argument("--scratch", default="/var/tmp/r102-mut04/scratch")
    ap.add_argument("--fixture", default=STOCK_FIXTURE)
    ap.add_argument("--variant", default="healthy",
                    choices=["healthy", "delay-short", "slow-marker", "hold-noop", "marker-absent"])
    ap.add_argument("--old-bound", type=float, default=0.75)
    ap.add_argument("--delay", type=float, default=None, help="informational only; fixture carries the delay")
    ap.add_argument("--new-bound", type=float, default=3.0)
    ap.add_argument("--cleanup", type=float, default=3.0)
    ap.add_argument("--expect", choices=["PASS", "FAIL"], default=None)
    ap.add_argument("--out", default=None)
    ap.add_argument("--label", default="")
    args = ap.parse_args()

    stock = open(args.fixture, "r", encoding="utf-8").read()
    variant_text = make_variant(stock, args.variant, args.old_bound)
    os.makedirs(args.scratch, exist_ok=True)
    script_path = "res://timeout_probe.gd"
    with open(os.path.join(args.scratch, "timeout_probe.gd"), "w", encoding="utf-8") as fh:
        fh.write(variant_text)

    expected_exit = 0
    old_positive = bounded_run("slow_clean_old_bound", ["--delay-clean"], args.old_bound,
                               args.godot, args.scratch, script_path, MARKER_TEXT,
                               expected_exit, args.cleanup)
    new_positive = bounded_run("slow_clean_new_bound", ["--delay-clean"], args.new_bound,
                               args.godot, args.scratch, script_path, MARKER_TEXT,
                               expected_exit, args.cleanup)
    hold_open = bounded_run("hold_open_new_bound", ["--hold-open"], args.new_bound,
                            args.godot, args.scratch, script_path, MARKER_TEXT,
                            expected_exit, args.cleanup)
    probe_results = [old_positive, new_positive, hold_open]
    old_rejects = (old_positive["timed_out"] and old_positive["marker_observed"]
                   and old_positive["inner_classification"] is False
                   and old_positive["direct_child_alive_after_cleanup"] is False)
    new_accepts = (not new_positive["timed_out"] and new_positive["actual_exit"] == expected_exit
                   and new_positive["marker_observed"]
                   and new_positive["inner_classification"] is True)
    hold_rejects = (hold_open["timed_out"] and hold_open["marker_observed"]
                    and hold_open["inner_classification"] is False
                    and hold_open["direct_child_alive_after_cleanup"] is False)
    same_script = all(r["command"][r["command"].index("--script") + 1] == script_path for r in probe_results)
    same_expected_exit = all(r["expected_exit"] == expected_exit for r in probe_results)
    meta_pass = old_rejects and new_accepts and hold_rejects and same_script and same_expected_exit

    clauses = {"old_rejects": old_rejects, "new_accepts": new_accepts,
               "hold_rejects": hold_rejects, "same_script": same_script,
               "same_expected_exit": same_expected_exit}
    payload = {"mode": "mut04_mirror_of_run_battery_probe_timeout", "label": args.label,
               "variant": args.variant, "mirrors": "run_battery.py:5322-5396 @ r101-close 1392ca21",
               "fixture_sha256": hashlib.sha256(stock.encode()).hexdigest(),
               "variant_sha256": hashlib.sha256(variant_text.encode()).hexdigest(),
               "constants": {"old_bound": args.old_bound, "new_bound": args.new_bound,
                             "cleanup": args.cleanup, "delay": args.delay},
               "clauses": clauses, "same_script": same_script, "same_expected_exit": same_expected_exit,
               "falsifiers": [k for k, v in clauses.items() if not v],
               "results": probe_results,
               "verdict": "PASS" if meta_pass else "FAIL", "expected": args.expect}
    if args.out:
        with open(args.out, "w", encoding="utf-8") as fh:
            json.dump(payload, fh, indent=2)
            fh.write("\n")
    print(json.dumps({"label": args.label, "variant": args.variant, "verdict": payload["verdict"],
                      "expected": args.expect, "falsifiers": payload["falsifiers"],
                      "arm_shapes": [[r["case"], r["timed_out"], r["marker_observed"],
                                      r["actual_exit"], len(r["raw_stdout"]), r["elapsed_seconds"]]
                                     for r in probe_results]}, indent=2))
    if args.expect and payload["verdict"] != args.expect:
        print(f"MUT04 MISMATCH: got {payload['verdict']} expected {args.expect}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
