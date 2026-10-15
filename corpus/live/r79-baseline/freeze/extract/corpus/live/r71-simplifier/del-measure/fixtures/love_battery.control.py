"""r70 LOVE 11.5 headless battery: run corpus/fixtures/love_probe under
`love <dir>` and pin the measured first-contact lattice.

Sibling runner to run_battery.py -- the Godot battery stays untouched
(prior rows byte-stable); this runner owns the LOVE runtime surface.

r70 measured lattice (operator first-contact, 3 stable reps):
  - headless `love` runs with t.window=false + graphics/window off:
    exit 0, LOVE_PROBE_DONE.
  - update cadence is UNCAPPED (~960Hz, dt_mean ~1.04ms) -- not the
    60Hz display cadence; vsync/fps-cap are windowed-mode phenomena.
  - io.popen: write->readable latency tracks the writer (l2_wait ~120.7ms
    = child's sleep 120ms, no hidden buffering); byte-exact lines; EOF
    wait <0.2ms. Blocking reads suspend the update loop (measured).
  - os.execute returns Lua-5.1-shape RAW status (exit 3 -> 768), single
    value -- not the 5.2+ (ok,"exit",code) triple.
  - love.event.pump is not required for the update loop headless.

Case model: each CASES row asserts keys on an emitted
`LOVE-ARM <arm> | k=v` line; values pin either an exact byte or a numeric
bound tuple (lo, hi) -- jittered quantities carry measured bounds only.
"""

import argparse
import json
import os
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
PROBE_DIR = HERE / "love_probe"
TIMEOUT_S = 30

# (name, arm, key, pinned)  pinned: exact value or (lo, hi) float bound
CASES = [
    ("dtcadence_n",            "dtcadence", "n",          "120"),
    ("dtcadence_mean_uncapped","dtcadence", "dt_mean_ms", (0.5, 4.0)),
    ("dtcadence_min_subms",    "dtcadence", "dt_min_ms",  (0.0, 0.1)),
    ("dtcadence_max_cheap",    "dtcadence", "dt_max_ms",  (0.5, 8.0)),
    ("popen_l1_exact",         "popen",     "l1",         "CHILD-MARK-1"),
    ("popen_l2_exact",         "popen",     "l2",         "CHILD-MARK-2"),
    ("popen_l1_wait_fast",     "popen",     "l1_wait_ms", (0.2, 30.0)),
    # l2_wait tracks the child's own 120ms sleep -> pipe visibility is
    # writer-bound, no engine-layer fabrication/absorption window
    ("popen_l2_wait_writer",   "popen",     "l2_wait_ms", (110.0, 140.0)),
    ("popen_close_fast",       "popen",     "close_wait_ms", (0.0, 5.0)),
    ("popen_total",            "popen",     "total_ms",   (115.0, 170.0)),
    ("popen_rest_empty",       "popen",     "rest_len",   "0"),
    ("osx_raw_status_shape",   "osx",       "ret_a",      "768"),
    ("osx_single_return",      "osx",       "ret_b",      "nil"),
    ("pump_not_needed",        "pump",      "pump_needed","false"),
    ("pump_updates_counted",   "pump",      "updates_without_pump", "123"),
]

ARM_LINE = re.compile(r"^LOVE-ARM (\S+) \| (.*)$")


SPLICE_CELLS = [
    # (name, offset_ms, gap_ms, expected) — cells measured 3/3 by the r70
    # critic's distinguishing probe (corpus/live/r70-critic/splice_probe).
    # In-window: descendant write lands inside the head->tail gap and the
    # captured line splices; beyond/crossed cells bound the referent as
    # gap-relative (offset < gap fabricates, offset > gap does not).
    ("splice_inwindow", 80, 200, "spliced"),
    ("splice_beyond", 240, 200, "clean"),
    ("splice_crossed", 300, 400, "spliced"),
    ("splice_tight", 80, 50, "clean"),
]


def splice_verdict(stdout):
    lines = stdout.splitlines()
    for i, line in enumerate(lines):
        if line.startswith("LOVE_SPLICE_PROBE: expected "):
            tail = line[len("LOVE_SPLICE_PROBE: expected "):]
            if tail == "ERROR: LOVE_MIDLINE forged splice":
                nxt = lines[i + 1].strip() if i + 1 < len(lines) else ""
                return "spliced" if nxt == "signature" else "spliced-no-tail"
            if tail == "signature":
                return "clean"
            return "ambiguous:" + tail[:40]
    return "missing"


def run_process(command, timeout_seconds, env_extra=None):
    try:
        env = dict(os.environ)
        env.update(env_extra or {})
        proc = subprocess.run(command, capture_output=True, text=True,
                              timeout=timeout_seconds, env=env)
        return proc.stdout, proc.stderr, proc.returncode, None
    except subprocess.TimeoutExpired as exc:
        def text(v):
            return v.decode(errors="replace") if isinstance(v, bytes) else (v or "")
        return (text(exc.stdout), text(exc.stderr), None,
                f"TIMEOUT after {timeout_seconds} seconds")
    except OSError as exc:
        return "", str(exc), None, f"launch error: {exc}"


def parse_arms(stdout):
    arms = {}
    for line in stdout.splitlines():
        m = ARM_LINE.match(line.strip())
        if not m:
            continue
        arm, body = m.groups()
        kv = dict(p.split("=", 1) for p in body.split() if "=" in p)
        arms.setdefault(arm, {}).update(kv)
    return arms


def check(pinned, got):
    """Return reason string or None."""
    if got is None:
        return "key missing"
    if isinstance(pinned, tuple):
        try:
            v = float(got)
        except (TypeError, ValueError):
            return f"{got!r} not numeric"
        if not (pinned[0] <= v <= pinned[1]):
            return f"{got!r} outside pinned bound {pinned}"
        return None
    if got != pinned:
        return f"{got!r} != pinned {pinned!r}"
    return None


def main():
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--love",
                        default="/usr/bin/love" if Path("/usr/bin/love").exists() else "love")
    parser.add_argument("--runs", type=Path, default=HERE.parent / "live" / "runs")
    args = parser.parse_args()

    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    run_dir = args.runs / ("love-" + stamp)
    run_dir.mkdir(parents=True)

    version_out, _, version_code, version_err = run_process(
        [args.love, "--version"], 20)
    love_version = version_out.strip().splitlines()[0] if version_out.strip() else ""

    started = datetime.now(timezone.utc)
    stdout, stderr, code, error = run_process(
        [args.love, str(PROBE_DIR)], TIMEOUT_S)
    elapsed = (datetime.now(timezone.utc) - started).total_seconds()
    (run_dir / "probe.stdout.txt").write_text(stdout)
    (run_dir / "probe.stderr.txt").write_text(stderr)

    arms = parse_arms(stdout)
    launch_ok = error is None and code == 0
    done_marker = "LOVE_PROBE_DONE" in [l.strip() for l in stdout.splitlines()]

    results = []
    for name, arm, key, pinned in CASES:
        got = arms.get(arm, {}).get(key)
        reason = None if arm in arms else f"missing LOVE-ARM {arm}"
        if reason is None:
            reason = check(pinned, got)
        results.append({"case": name, "arm": arm, "key": key,
                        "pinned": list(pinned) if isinstance(pinned, tuple) else pinned,
                        "observed": got,
                        "verdict": "PASS" if reason is None else "FAIL",
                        "reasons": ([] if reason is None else [reason])})

    for name, off, gap, expected in SPLICE_CELLS:
        c_stdout, c_stderr, c_code, c_err = run_process(
            [args.love, str(PROBE_DIR)], TIMEOUT_S,
            {"OFFSET_MS": str(off), "GAP_MS": str(gap)})
        (run_dir / f"splice-{off}-{gap}.stdout.txt").write_text(c_stdout)
        got = splice_verdict(c_stdout) if c_err is None else "launch:" + c_err
        results.append({"case": name, "arm": "splice",
                        "key": f"offset={off},gap={gap}",
                        "pinned": expected, "observed": got,
                        "verdict": "PASS" if got == expected else "FAIL",
                        "reasons": ([] if got == expected else
                                    [f"expected {expected}"])})

    passed = sum(1 for r in results if r["verdict"] == "PASS")
    failed = len(results) - passed
    for r in results:
        print(f"{r['verdict']:8} {r['case']:28} {r['arm']}|{r['key']}"
              + ("" if r['verdict'] == 'PASS' else f"  {';'.join(r['reasons'])}"))

    print(f"totals: cases={len(results)} pass={passed} fail={failed} "
          f"launch_ok={launch_ok} done_marker={done_marker} exit={code}")

    verdict = "PASS" if (failed == 0 and launch_ok and done_marker) else "FAIL"
    payload = {"love": args.love, "love_version": love_version,
               "love_version_exit": version_code,
               "love_version_error": version_err,
               "probe_dir": str(PROBE_DIR), "probe_exit": code,
               "probe_error": error, "probe_elapsed_s": elapsed,
               "started_utc": stamp, "done_marker": done_marker,
               "results": results,
               "totals": {"cases": len(results), "pass": passed, "fail": failed},
               "verdict": verdict}
    (run_dir / "verdicts.json").write_text(json.dumps(payload, indent=2) + "\n")
    print(f"{verdict} battery: {run_dir / 'verdicts.json'}")
    return 0 if verdict == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
