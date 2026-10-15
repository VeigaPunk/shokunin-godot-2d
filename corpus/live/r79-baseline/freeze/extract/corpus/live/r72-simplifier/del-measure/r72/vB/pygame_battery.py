"""r71 pygame 2.6.1 headless battery: run corpus/fixtures/pygame_probe.py
under `python3` and pin the measured first-contact lattice.

Sibling runner to run_battery.py and love_battery.py -- both stay
untouched (prior rows byte-stable); this runner owns the pygame runtime
surface.

r71 lattice (author-measured, python3.14.7 + pygame 2.6.1 / SDL 2.32.72,
SDL_VIDEODRIVER=dummy):
  - headless viability: init (5,0), driver=dummy, exit 0,
    PYGAME_PROBE_DONE. env is pinned in-fixture before `import pygame`.
  - tick(60) cadence is ~62Hz, never 60.00 -- SDL_Delay is ms-granular
    and undershoots the 16.67ms ideal (dt_mean ~16.0-16.1ms).
  - tick() uncapped is a bare-Python multi-MHz spin (dt_mean ~0ms).
  - subprocess.Popen pipe is writer-bound and byte-exact (LOVE shape):
    l2_wait ~= the flushing child's own 120ms sleep; a non-flushing
    child's l1 is withheld to child exit.
  - withholding window IS buffer-bounded, but at io.DEFAULT_BUFFER_SIZE
    = 131072 on this build, NOT ~8KB: a 9KB mid-run write stays withheld
    to exit while a 200KB mid-run write (single-shot AND cumulative-fill)
    surfaces at ~105ms carrying the withheld MARK-1 with it.

r72 lattice addition (reorder fabrication, xconnector X1): a spawned
descendant writes into the child's inherited fd1 while the child's own
earlier bytes sit in its userspace buffer.  The seam is spawn-layer
(fd1 inheritance, the same seam as Godot midlineforge / LOVE os.execute);
the fabricated byte ORDER is language-layer: a block-buffered child
releases HEAD only at exit so the descendant's bytes land FIRST
(prefix_reorder), while -u / flush=True / PYTHONUNBUFFERED=1 collapse
the window -> midline_splice (the Godot/LOVE topology), and a
descendant landing after the flush closes the window -> append.
reorder_self puts raw REORDER-HEAD/CHILD/TAIL markers on the probe's
OWN fd1: under the battery's pipe capture the wire reads CHILD first --
the pinned hazard for any streaming parser of these ARM lines (the
post-exit parser cannot observe it, the RAW_CASES check does).

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
TIMEOUT_S = 30

PROBE_ENV = {
    "SDL_VIDEODRIVER": "dummy",
    "SDL_AUDIODRIVER": "dummy",
    "PYGAME_HIDE_SUPPORT_PROMPT": "1",
}

# (name, arm, key, pinned)  pinned: exact value or (lo, hi) float bound
CASES = [
    ("viab_init_ok",           "viability", "init_fail",  "0"),
    ("viab_driver_dummy",      "viability", "driver",     "dummy"),
    ("c60_n",                  "cadence60", "n",          "240"),
    # SDL_Delay ms-granularity undershoots the 16.67ms ideal -> ~62Hz
    ("c60_mean_undershoot",    "cadence60", "dt_mean_ms", (15.5, 16.66)),
    ("c60_min",                "cadence60", "dt_min_ms",  (14.0, 16.5)),
    ("c60_max",                "cadence60", "dt_max_ms",  (15.5, 30.0)),
    ("c60_fps_over60",         "cadence60", "fps",        (60.5, 64.0)),
    ("c0_n",                   "cadence0",  "n",          "1200"),
    ("c0_mean_subms",          "cadence0",  "dt_mean_ms", (0.0, 0.1)),
    ("c0_min",                 "cadence0",  "dt_min_ms",  (0.0, 0.01)),
    # uncapped bare-Python spin: measured ~9.5MHz; floor pinned far
    # above any display cadence
    ("c0_hz_uncapped",         "cadence0",  "hz",         (20000.0, 1e9)),
    ("c0_max",                 "cadence0",  "dt_max_ms",  (0.0, 50.0)),
    ("popen_l1_exact",         "popen",     "l1",         "CHILD-MARK-1"),
    ("popen_l2_exact",         "popen",     "l2",         "CHILD-MARK-2"),
    ("popen_l1_wait_fast",     "popen",     "l1_wait_ms", (0.2, 30.0)),
    # l2_wait tracks the child's own 120ms sleep -> pipe visibility is
    # writer-bound, no engine-layer fabrication/absorption window
    ("popen_l2_wait_writer",   "popen",     "l2_wait_ms", (110.0, 140.0)),
    ("popen_close_fast",       "popen",     "close_wait_ms", (0.0, 5.0)),
    ("popen_total",            "popen",     "total_ms",   (115.0, 170.0)),
    ("popen_rest_empty",       "popen",     "rest_len",   "0"),
    # unflushed child: l1 withheld to child exit (~125ms on a 120ms child)
    ("popenbuf_l1_held",       "popen_buf", "l1_wait_ms", (110.0, 180.0)),
    # withhold_small: 9000 > the claimed ~8KB bound yet still held to
    # exit -> the bound is io.DEFAULT_BUFFER_SIZE (131072 on 3.14), not 8KB
    ("whs_bufsize",            "withhold_small", "bufsize", "131072"),
    ("whs_held_to_exit",       "withhold_small", "first_read_ms", (180.0, 3000.0)),
    ("whs_early_none",         "withhold_small", "early_bytes", "0"),
    # withhold_big: 200000 > bufsize -> mid-run flush ~105ms; withheld
    # MARK-1 rides it (fused delivery); post-flush MARK-2 re-buffered
    # and held to exit; bytes landed while the child was still asleep
    ("whb_first_early",        "withhold_big", "first_read_ms", (60.0, 190.0)),
    ("whb_mark1_rides",        "withhold_big", "mark1_ms", (60.0, 190.0)),
    ("whb_mark2_exit",         "withhold_big", "mark2_ms", (180.0, 3000.0)),
    ("whb_early_bytes",        "withhold_big", "early_bytes", (100000.0, 210000.0)),
    ("whb_alive",              "withhold_big", "alive_at_first", "True"),
    # withhold_fill: 200x1000 cumulative crossing flushes mid-run too --
    # the edge is buffer-fill, not write granularity
    ("whf_first_early",        "withhold_fill", "first_read_ms", (60.0, 190.0)),
    ("whf_mark1_rides",        "withhold_fill", "mark1_ms", (60.0, 190.0)),
    ("whf_mark2_exit",         "withhold_fill", "mark2_ms", (180.0, 3000.0)),
    ("whf_early_bytes",        "withhold_fill", "early_bytes", (60000.0, 135000.0)),
    ("whf_alive",              "withhold_fill", "alive_at_first", "True"),
    ("pump_not_needed",        "pump",      "pump_needed", "false"),
    ("pump_posted_survived",   "pump",      "posted_survived", "1"),
    # --- r72 reorder_*: fd1-inheritance x block-buffering composition ---
    # Seam = spawn-layer (inherited fd1); fabricated ORDER = language-
    # layer (buffering mode).  Same 19 bytes on every wire -- only the
    # order moves.  bufsize carried per receipt (131072 on py3.14).
    ("rord_buf_topo",      "reorder_buf",   "topology",    "prefix_reorder"),
    ("rord_buf_inj0",      "reorder_buf",   "injected_at", "0"),
    ("rord_buf_head",      "reorder_buf",   "head_at",     "8"),
    ("rord_buf_bytes",     "reorder_buf",   "wire_bytes",  "19"),
    ("rord_buf_ret",       "reorder_buf",   "ret",         "0"),
    ("rord_bufsize",       "reorder_buf",   "bufsize",     "131072"),
    ("rord_u_topo",        "reorder_unbuf", "topology",    "midline_splice"),
    ("rord_u_head0",       "reorder_unbuf", "head_at",     "0"),
    ("rord_u_bytes",       "reorder_unbuf", "wire_bytes",  "19"),
    ("rord_fl_topo",       "reorder_flush", "topology",    "midline_splice"),
    ("rord_fl_head0",      "reorder_flush", "head_at",     "0"),
    ("rord_env_topo",      "reorder_env",   "topology",    "midline_splice"),
    ("rord_env_head0",     "reorder_env",   "head_at",     "0"),
    ("rord_late_topo",     "reorder_late",  "topology",    "append"),
    ("rord_late_head0",    "reorder_late",  "head_at",     "0"),
    ("rord_late_tail",     "reorder_late",  "tail_at",     "6"),
    ("self_fd1_piped",     "reorder_self",  "fd1_isatty",  "False"),
    ("self_bufsize",       "reorder_self",  "bufsize",     "131072"),
]

# Raw-wire cases (r72): the reorder_self topology lives on the probe's
# OWN captured stream -- only the post-capture byte order can judge it.
# (name, pinned) over the marker relation in the raw stdout.
RAW_CASES = [
    ("self_wire_reorders", "prefix_reorder"),
]

ARM_LINE = re.compile(r"^PYGAME-ARM (\S+) \| (.*)$")


def run_process(command, timeout_seconds, env_extra=None):
    try:
        env = dict(os.environ)
        env.update(env_extra or {})
        # the reorder_self wire pin requires the probe itself be
        # block-buffered on our pipe -- same hygiene the probe's own
        # CHILD_ENV applies to spawned children.
        env.pop("PYTHONUNBUFFERED", None)
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
    parser.add_argument("--python", default=sys.executable)
    parser.add_argument("--runs", type=Path, default=HERE.parent / "live" / "runs")
    args = parser.parse_args()

    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    run_dir = args.runs / ("pygame-" + stamp)
    run_dir.mkdir(parents=True)

    version_out, _, version_code, version_err = run_process(
        [args.python, str(PROBE), "--version"], 20, PROBE_ENV)
    pygame_version = version_out.strip().splitlines()[0] if version_out.strip() else ""

    started = datetime.now(timezone.utc)
    stdout, stderr, code, error = run_process(
        [args.python, str(PROBE)], TIMEOUT_S, PROBE_ENV)
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

    # --- raw-wire cases: marker order on the captured stdout itself ----
    # reorder_self puts its markers on the probe's own fd1, so the
    # fabricated order is visible only in the raw capture, not ARM lines.
    h, c, t = (stdout.find(m) for m in
               ("REORDER-HEAD", "REORDER-CHILD", "REORDER-TAIL"))
    if -1 in (h, c, t):
        self_topo = "markers_missing"
    elif c < h:
        self_topo = "prefix_reorder"
    elif h < c < t:
        self_topo = "midline_splice"
    elif t < c:
        self_topo = "append"
    else:
        self_topo = "degenerate"
    for name, pinned in RAW_CASES:
        reason = None if self_topo == pinned else \
            f"{self_topo!r} != pinned {pinned!r} (idx h={h} c={c} t={t})"
        results.append({"case": name, "arm": "reorder_self",
                        "key": "wire_topology", "pinned": pinned,
                        "observed": self_topo,
                        "verdict": "PASS" if reason is None else "FAIL",
                        "reasons": ([] if reason is None else [reason])})

    passed = sum(1 for r in results if r["verdict"] == "PASS")
    failed = len(results) - passed
    for r in results:
        print(f"{r['verdict']:8} {r['case']:28} {r['arm']}|{r['key']}"
              + ("" if r['verdict'] == 'PASS' else f"  {';'.join(r['reasons'])}"))

    print(f"totals: cases={len(results)} pass={passed} fail={failed} "
          f"launch_ok={launch_ok} done_marker={done_marker} exit={code}")

    verdict = "PASS" if (failed == 0 and launch_ok and done_marker) else "FAIL"
    payload = {"python": args.python, "pygame_version": pygame_version,
               "pygame_version_exit": version_code,
               "pygame_version_error": version_err,
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
