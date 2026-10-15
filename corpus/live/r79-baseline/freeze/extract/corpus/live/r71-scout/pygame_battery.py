"""r71 scout — pygame 2.6.1 headless battery (PROTOTYPE for
corpus/fixtures/pygame_battery.py; sibling to love_battery.py).

Sibling runner to run_battery.py / love_battery.py -- the Godot and LOVE
rows stay untouched (prior rows byte-stable); this runner owns the
pygame runtime surface.

One `python3 pygame_probe.py` run under
  SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy PYGAME_HIDE_SUPPORT_PROMPT=1
then pin the measured first-contact lattice:

  - headless viability: driver=dummy, set_mode ok, no silent fallback.
  - cadence is a pure Python-loop property: tick(60) ~62Hz (SDL_Delay
    ms-granular undershoot, never 60.00), tick(120) ~124Hz, tick()
    uncapped bare-loop MHz spin. Bound-pinned, not exact.
  - stdout surface is writer-flush-bound (LOVE shape): popen l2_wait
    tracks the child's own 120ms sleep; byte-exact lines; no engine seam.
  - Python stdio adds a WITHHOLDING window: an unflushed write below
    io.DEFAULT_BUFFER_SIZE (131072 on this CPython 3.14.7) is
    parent-invisible until buffer overflow, explicit flush, or exit.
    A single write >= buffer size bypasses the buffer (early); a
    segmented total == buffer size does NOT flush when exactly full;
    overflow flushes the existing buffer first (partial visibility).
  - pygame.event.pump() is not needed headless; a posted event survives
    and no spontaneous QUIT arrives.

Case model: each CASES row asserts keys on an emitted
`PYGAME-ARM <arm> | k=v` line; values pin either an exact byte or a
numeric bound tuple (lo, hi) -- jittered quantities carry measured
bounds only.
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
PROBE = HERE / "pygame_probe.py"
TIMEOUT_S = 45

ENV_EXTRA = {
    "SDL_VIDEODRIVER": "dummy",
    "SDL_AUDIODRIVER": "dummy",
    "PYGAME_HIDE_SUPPORT_PROMPT": "1",
}

# (name, arm, key, pinned)  pinned: exact value or (lo, hi) float bound
CASES = [
    ("viability_driver_dummy",   "viability", "driver",        "dummy"),
    ("viability_init_fail_zero", "viability", "init_fail",     "0"),
    ("viability_surface",        "viability", "surf",          "320x240"),

    ("stdio_buffer_size",        "stdio",     "default_buffer_size", "131072"),

    ("cadence60_n",              "cadence60", "n",             "240"),
    ("cadence60_mean_bound",     "cadence60", "dt_mean_ms",    (15.5, 17.5)),
    ("cadence60_min_undershoot", "cadence60", "dt_min_ms",     (14.0, 16.7)),
    ("cadence60_max_bound",      "cadence60", "dt_max_ms",     (15.5, 25.0)),
    ("cadence60_fps_bound",      "cadence60", "fps",           (57.0, 65.0)),
    ("cadence60_tick_ret_ms",    "cadence60", "last_tick_ret", (15.0, 18.0)),

    ("cadence120_n",             "cadence120", "n",            "240"),
    ("cadence120_mean_bound",    "cadence120", "dt_mean_ms",   (7.5, 9.0)),
    ("cadence120_min_bound",     "cadence120", "dt_min_ms",    (6.5, 8.35)),
    ("cadence120_fps_bound",     "cadence120", "fps",          (110.0, 130.0)),

    ("cadence0_uncapped_spin",   "cadence0",  "hz",            (1.0e6, 5.0e7)),
    ("cadence0_mean_subms",      "cadence0",  "dt_mean_ms",    (0.0, 0.1)),
    ("cadence0_tick_ret_floor",  "cadence0",  "last_tick_ret", "0"),

    ("cadencebusy_mean_bound",   "cadencebusy", "dt_mean_ms",  (15.5, 17.5)),
    ("cadencebusy_tail_tight",   "cadencebusy", "dt_max_ms",   (15.5, 22.0)),

    ("popen_l1_exact",           "popen",     "l1",            "CHILD-MARK-1"),
    ("popen_l2_exact",           "popen",     "l2",            "CHILD-MARK-2"),
    ("popen_l1_wait_fast",       "popen",     "l1_wait_ms",    (0.2, 60.0)),
    # l2_wait tracks the child's own 120ms sleep -> writer-bound pipe,
    # no engine-layer fabrication/absorption window (LOVE shape)
    ("popen_l2_wait_writer",     "popen",     "l2_wait_ms",    (110.0, 140.0)),
    ("popen_close_fast",         "popen",     "close_wait_ms", (0.0, 5.0)),
    ("popen_total_bound",        "popen",     "total_ms",      (115.0, 175.0)),
    ("popen_rest_empty",         "popen",     "rest_len",      "0"),
    ("popen_ret_zero",           "popen",     "ret",           "0"),

    ("popen_buf_withheld",       "popen_buf", "l1_wait_ms",    (110.0, 145.0)),
    ("popen_buf_l2_instant",     "popen_buf", "l2_wait_ms",    (0.0, 5.0)),
    ("popen_buf_l1_exact",       "popen_buf", "l1",            "CHILD-MARK-1"),
    ("popen_buf_rest_empty",     "popen_buf", "rest_len",      "0"),

    ("pump_frames_nopump",       "pump",      "frames_nopump", "400"),
    ("pump_posted_survived",     "pump",      "posted_survived", "1"),
    ("pump_posted_found",        "pump",      "posted_found_at_end", "True"),
    ("pump_total_bound",         "pump",      "nopump_total_ms", (2500.0, 6000.0)),
    ("pump2_frames",             "pump2",     "frames_withpump", "400"),
    ("pump2_queue_drained",      "pump2",     "queued_after_pump", (0.0, 5.0)),
    ("pump2_total_bound",        "pump2",     "withpump_total_ms", (2500.0, 6000.0)),

    ("flip_mean_noop",           "flip",      "flip_mean_ms",  (0.0, 0.05)),

    # withholding matrix: < buffer -> exit-batched; >= buffer single
    # write -> early; segmented exact-total -> still withheld;
    # segmented overflow -> first chunk early, remainder at exit.
    # vis_pre_exit_bytes counts only bytes readable >= 200ms before the
    # child's exit (fixed mid-run samples are load-jitter-fragile).
    ("withhold_small_withheld",   "withhold_small",   "vis_pre_exit_bytes", "0"),
    ("withhold_small_late",       "withhold_small",   "first_vis_ms", (500.0, 2500.0)),
    ("withhold_small_bytes",      "withhold_small",   "total_bytes",  "100"),
    ("withhold_small_integrity",  "withhold_small",   "integrity",    "1"),
    ("withhold_small_rc",         "withhold_small",   "rc",           "0"),
    ("withhold_edge_lo_withheld", "withhold_edge_lo", "vis_pre_exit_bytes", "0"),
    ("withhold_edge_lo_late",     "withhold_edge_lo", "first_vis_ms", (500.0, 2500.0)),
    ("withhold_edge_lo_bytes",    "withhold_edge_lo", "total_bytes",  "131071"),
    ("withhold_edge_lo_integrity", "withhold_edge_lo", "integrity",   "1"),
    ("withhold_edge_eq_early",    "withhold_edge_eq", "vis_pre_exit_bytes", "131072"),
    ("withhold_edge_eq_fast",     "withhold_edge_eq", "first_vis_ms", (0.0, 500.0)),
    ("withhold_edge_eq_bytes",    "withhold_edge_eq", "total_bytes",  "131072"),
    ("withhold_edge_eq_integrity", "withhold_edge_eq", "integrity",   "1"),
    ("withhold_edge_hi_early",    "withhold_edge_hi", "vis_pre_exit_bytes", "131073"),
    ("withhold_edge_hi_fast",     "withhold_edge_hi", "first_vis_ms", (0.0, 500.0)),
    ("withhold_edge_hi_bytes",    "withhold_edge_hi", "total_bytes",  "131073"),
    ("withhold_edge_hi_integrity", "withhold_edge_hi", "integrity",   "1"),
    ("withhold_big_early",        "withhold_big",     "vis_pre_exit_bytes", "200000"),
    ("withhold_big_fast",         "withhold_big",     "first_vis_ms", (0.0, 500.0)),
    ("withhold_big_bytes",        "withhold_big",     "total_bytes",  "200000"),
    ("withhold_big_integrity",    "withhold_big",     "integrity",    "1"),
    ("withhold_seg_eq_withheld",  "withhold_seg_eq",  "vis_pre_exit_bytes", "0"),
    ("withhold_seg_eq_late",      "withhold_seg_eq",  "first_vis_ms", (500.0, 2500.0)),
    ("withhold_seg_eq_bytes",     "withhold_seg_eq",  "total_bytes",  "131072"),
    ("withhold_seg_eq_integrity", "withhold_seg_eq",  "integrity",    "1"),
    ("withhold_seg_over_partial", "withhold_seg_over", "vis_pre_exit_bytes", "70000"),
    ("withhold_seg_over_mid",     "withhold_seg_over", "first_vis_ms", (150.0, 900.0)),
    ("withhold_seg_over_bytes",   "withhold_seg_over", "total_bytes",  "140000"),
    ("withhold_seg_over_integrity", "withhold_seg_over", "integrity",  "1"),
    ("withhold_unbuf_early",      "withhold_unbuf",   "vis_pre_exit_bytes", "100"),
    ("withhold_unbuf_fast",       "withhold_unbuf",   "first_vis_ms", (0.0, 500.0)),
    ("withhold_unbuf_bytes",      "withhold_unbuf",   "total_bytes",  "100"),
    ("withhold_unbuf_integrity",  "withhold_unbuf",   "integrity",    "1"),
]

# cross-key relations: name, left (arm, key), right (arm, key), op
RELATIONS = [
    ("edge_eq_is_buffer_size", ("withhold_edge_eq", "n"),
     ("stdio", "default_buffer_size"), "eq"),
    ("edge_lo_is_buffer_minus_1", ("withhold_edge_lo", "n"),
     ("stdio", "default_buffer_size"), "eq_minus_1"),
    ("edge_hi_is_buffer_plus_1", ("withhold_edge_hi", "n"),
     ("stdio", "default_buffer_size"), "eq_plus_1"),
    # visibility-relative-to-exit: the sharp discriminator that does not
    # depend on fixed millisecond bounds
    ("small_exit_batched", ("withhold_small", "first_vis_ms"),
     ("withhold_small", "exit_ms"), "ge_minus_150"),
    ("edge_lo_exit_batched", ("withhold_edge_lo", "first_vis_ms"),
     ("withhold_edge_lo", "exit_ms"), "ge_minus_150"),
    ("seg_eq_exit_batched", ("withhold_seg_eq", "first_vis_ms"),
     ("withhold_seg_eq", "exit_ms"), "ge_minus_150"),
    ("edge_eq_early_before_exit", ("withhold_edge_eq", "first_vis_ms"),
     ("withhold_edge_eq", "exit_ms"), "le_minus_200"),
    ("edge_hi_early_before_exit", ("withhold_edge_hi", "first_vis_ms"),
     ("withhold_edge_hi", "exit_ms"), "le_minus_200"),
    ("big_early_before_exit", ("withhold_big", "first_vis_ms"),
     ("withhold_big", "exit_ms"), "le_minus_200"),
    ("unbuf_early_before_exit", ("withhold_unbuf", "first_vis_ms"),
     ("withhold_unbuf", "exit_ms"), "le_minus_200"),
    ("seg_over_early_before_exit", ("withhold_seg_over", "first_vis_ms"),
     ("withhold_seg_over", "exit_ms"), "le_minus_200"),
]

ARM_LINE = re.compile(r"^PYGAME-ARM (\S+) \| (.*)$")


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


def relation_ok(arms, left, right, op):
    a, ka = left
    b, kb = right
    va = arms.get(a, {}).get(ka)
    vb = arms.get(b, {}).get(kb)
    if va is None or vb is None:
        return False, f"missing {a}.{ka} or {b}.{kb}"
    try:
        fa, fb = float(va), float(vb)
    except (TypeError, ValueError):
        return False, f"non-numeric {va!r} / {vb!r}"
    if op == "eq":
        ok = int(fa) == int(fb)
    elif op == "eq_minus_1":
        ok = int(fa) == int(fb) - 1
    elif op == "eq_plus_1":
        ok = int(fa) == int(fb) + 1
    elif op.startswith("ge_minus_"):
        ok = fa >= fb - float(op[len("ge_minus_"):])
    elif op.startswith("le_minus_"):
        ok = fa <= fb - float(op[len("le_minus_"):])
    else:
        ok = False
    return ok, f"{fa} vs {fb} ({op})"


def main():
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--python", default=sys.executable)
    # NOTE for landing into corpus/fixtures/: love_battery.py writes to
    # HERE.parent / "live" / "runs"; this scratch prototype stays local.
    parser.add_argument("--runs", type=Path, default=HERE / "runs")
    args = parser.parse_args()

    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    run_dir = args.runs / ("pygame-" + stamp)
    run_dir.mkdir(parents=True)

    version_out, _, version_code, version_err = run_process(
        [args.python, "-c",
         "import pygame; print(pygame.version.ver); "
         "print('.'.join(map(str, pygame.version.SDL)))"],
        20, ENV_EXTRA)
    vlines = version_out.strip().splitlines()
    pygame_version = vlines[0] if vlines else ""
    sdl_version = vlines[1] if len(vlines) > 1 else ""

    started = datetime.now(timezone.utc)
    stdout, stderr, code, error = run_process(
        [args.python, str(PROBE)], TIMEOUT_S, ENV_EXTRA)
    elapsed = (datetime.now(timezone.utc) - started).total_seconds()
    (run_dir / "probe.stdout.txt").write_text(stdout)
    (run_dir / "probe.stderr.txt").write_text(stderr)

    arms = parse_arms(stdout)
    launch_ok = error is None and code == 0
    done_marker = "PYGAME_PROBE_DONE" in [l.strip() for l in stdout.splitlines()]

    results = []
    for name, arm, key, pinned in CASES:
        got = arms.get(arm, {}).get(key)
        reason = None if arm in arms else f"missing PYGAME-ARM {arm}"
        if reason is None:
            reason = check(pinned, got)
        results.append({"case": name, "arm": arm, "key": key,
                        "pinned": list(pinned) if isinstance(pinned, tuple) else pinned,
                        "observed": got,
                        "verdict": "PASS" if reason is None else "FAIL",
                        "reasons": ([] if reason is None else [reason])})

    for name, left, right, op in RELATIONS:
        ok, detail = relation_ok(arms, left, right, op)
        results.append({"case": name, "arm": f"{left[0]}.{left[1]}",
                        "key": f"{right[0]}.{right[1]}", "pinned": op,
                        "observed": detail,
                        "verdict": "PASS" if ok else "FAIL",
                        "reasons": ([] if ok else [detail])})

    passed = sum(1 for r in results if r["verdict"] == "PASS")
    failed = len(results) - passed
    for r in results:
        print(f"{r['verdict']:8} {r['case']:28} {r['arm']}|{r['key']}"
              + ("" if r['verdict'] == 'PASS' else f"  {';'.join(r['reasons'])}"))

    print(f"totals: cases={len(results)} pass={passed} fail={failed} "
          f"launch_ok={launch_ok} done_marker={done_marker} exit={code}")

    verdict = "PASS" if (failed == 0 and launch_ok and done_marker) else "FAIL"
    payload = {"python": args.python, "pygame_version": pygame_version,
               "sdl_version": sdl_version, "version_exit": version_code,
               "version_error": version_err,
               "probe": str(PROBE), "probe_exit": code,
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
