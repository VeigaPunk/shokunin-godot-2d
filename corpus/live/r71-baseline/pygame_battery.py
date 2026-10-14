"""r71 pygame headless battery: run pygame_probe.py under
`python3` with SDL_VIDEODRIVER=dummy and pin the measured
first-contact lattice.

Sibling runner to love_battery.py / run_battery.py -- the Godot and LOVE
batteries stay untouched (prior rows byte-stable); this runner owns the
pygame runtime surface. Developed at corpus/live/r71-baseline/ (baseline
seat write scope); promotion path corpus/fixtures/pygame_battery.py +
pygame_probe.py.

r71 measured lattice (this host: Python 3.14.7, pygame 2.6.1 / SDL
2.32.72, wayland compositor present):
  - headless requires SDL_VIDEODRIVER=dummy (no silent fallback);
    PYGAME_HIDE_SUPPORT_PROMPT=1 keeps stdout parseable.
  - tick(60) runs ~62Hz (SDL_Delay ms-undershoot); tick() uncapped is a
    MHz-scale bare Python loop. Cadence pinned as bounds, never 60.00.
  - subprocess.Popen child stdout is writer-flush-bound + byte-exact
    (LOVE's shape): l2_wait tracks the child's own 120ms sleep.
  - WITHHOLDING WINDOW (claim under test): unflushed piped stdout is
    parent-invisible until the buffer overflows or exit. Measured bound
    = io.DEFAULT_BUFFER_SIZE = 131072 bytes on 3.14 (not ~8KB): a write
    that fits is withheld (N<=131060 -> all at ~615ms exit); a write
    past remaining space releases pending early (N=131061 -> 12B at
    ~215ms); a write >= capacity streams through mid-run. Small tail
    writes are absorbed past capacity (line3 never flushed).
  - pygame.event.pump() not needed headless; no spontaneous QUIT.

Case model mirrors love_battery: CASES pin keys on `PYGAME-ARM <arm> |
k=v` lines (exact byte or (lo,hi) bound); WH_CELLS/IO_CELLS spawn
probe-child modes and pin the parent-visible arrival class/timing.
"""

import argparse
import json
import os
import re
import select
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
PROBE = HERE / "pygame_probe.py"
TIMEOUT_S = 60
CHILD_TIMEOUT_S = 15

# env every probe spawn runs under (frontier-measured headless pins)
ENV_EXTRA = {"SDL_VIDEODRIVER": "dummy",
             "SDL_AUDIODRIVER": "dummy",
             "PYGAME_HIDE_SUPPORT_PROMPT": "1"}

# (name, arm, key, pinned)  pinned: exact value or (lo, hi) float bound
CASES = [
    ("viability_driver",       "viability", "driver",    "dummy"),
    ("viability_init_fail",    "viability", "init_fail", "0"),
    ("viability_pygame",       "viability", "pygame_ver", "2.6.1"),
    ("viability_sdl",          "viability", "sdl",       "2.32.72"),
    ("viability_surf",         "viability", "surf",      "320x240"),
    ("viability_flags",        "viability", "flags",     "0x1000000"),
    # (a) cadence bounds — 62Hz-class, never 60.00 (SDL_Delay undershoot)
    ("cad60_n",                "cadence60", "n",         "240"),
    ("cad60_mean",             "cadence60", "dt_mean_ms", (15.8, 16.4)),
    ("cad60_min",              "cadence60", "dt_min_ms",  (14.5, 16.2)),
    ("cad60_max",              "cadence60", "dt_max_ms",  (15.9, 18.0)),
    ("cad60_hz",               "cadence60", "eff_hz",     (61.0, 64.0)),
    ("cad60_fps",              "cadence60", "fps",        (61.0, 64.0)),
    ("cad60_tickret",          "cadence60", "last_tick_ret", (14, 18)),
    # (a) uncapped — MHz-scale bare loop; pinned as a floor, not a value
    ("cad0_n",                 "cadence0", "n",          "1200"),
    ("cad0_mean_subms",        "cadence0", "dt_mean_ms",  (0.0, 0.05)),
    ("cad0_max_cheap",         "cadence0", "dt_max_ms",   (0.001, 1.0)),
    ("cad0_hz_mhz",            "cadence0", "hz",          (1e5, 2e7)),
    ("cad0_fps_inf",           "cadence0", "fps",         "inf"),
    ("cad0_tickret_zero",      "cadence0", "last_tick_ret", "0"),
    ("cadbusy_mean",           "cadencebusy", "dt_mean_ms", (15.8, 16.2)),
    ("cadbusy_max_tight",      "cadencebusy", "dt_max_ms",  (15.9, 17.2)),
    # (c) subprocess.Popen — writer-flush-bound + byte-exact (LOVE shape)
    ("popen_l1_exact",         "popen",     "l1",         "CHILD-MARK-1"),
    ("popen_l2_exact",         "popen",     "l2",         "CHILD-MARK-2"),
    ("popen_l1_wait_fast",     "popen",     "l1_wait_ms", (0.5, 30.0)),
    ("popen_l2_wait_writer",   "popen",     "l2_wait_ms", (110.0, 140.0)),
    ("popen_close_fast",       "popen",     "close_wait_ms", (0.0, 5.0)),
    ("popen_total",            "popen",     "total_ms",   (115.0, 200.0)),
    ("popen_rest_empty",       "popen",     "rest_len",   "0"),
    ("popen_ret",              "popen",     "ret",        "0"),
    # (c) non-flushing child — direction-1 withholding: both lines land
    #     in one burst at child exit (~120ms), second wait ~0
    ("popenbuf_l1_exact",      "popen_buf", "l1",         "CHILD-MARK-1"),
    ("popenbuf_l2_exact",      "popen_buf", "l2",         "CHILD-MARK-2"),
    ("popenbuf_l1_exit",       "popen_buf", "l1_wait_ms", (100.0, 200.0)),
    ("popenbuf_l2_burst",      "popen_buf", "l2_wait_ms", (0.0, 5.0)),
    ("popenbuf_rest_empty",    "popen_buf", "rest_len",   "0"),
    # (d) pump-free headless
    ("pump_posted_survives",   "pump",      "posted_found_at_end", "true"),
    ("pump_nopump_total",      "pump",      "nopump_total_ms", (3000.0, 3700.0)),
    ("pump2_total",            "pump2",     "withpump_total_ms", (3000.0, 3700.0)),
    ("quitpoll_none",          "quitpoll",  "quits_seen", "0"),
    ("flip_cheap",             "flip",      "flip_mean_ms", (0.0, 0.05)),
]

ARM_LINE = re.compile(r"^PYGAME-ARM (\S+) \| (.*)$")

# (name, probe argv tail, expected class, first_byte_ms bound,
#  first_bytes bound) — class from the arrival trace:
#   early    : bytes surface >=200ms before EOF (a write released them)
#   withheld : first byte within 100ms of EOF (all batched at exit)
# last tuple = early_bytes bound (bytes surfaced >=100ms before EOF)
WH_CELLS = [
    # >8KB mid-run write does NOT surface early — the ~8KB edge is
    # falsified on this interpreter (buffer is 128KiB, not 8KiB)
    ("wh_8k_withheld",   ["--wh-child", "8192"],   "withheld",
     (300.0, 3000.0), (0, 0)),
    ("wh_64k_withheld",  ["--wh-child", "65536"],  "withheld",
     (300.0, 3000.0), (0, 0)),
    # fit-under-capacity cells — entire payload withheld to exit
    ("wh_below_cap",     ["--wh-child", "131048"], "withheld",
     (300.0, 3000.0), (0, 0)),
    ("wh_at_cap",        ["--wh-child", "131060"], "withheld",
     (300.0, 3000.0), (0, 0)),
    # past remaining space -> pending 12B released ~200ms mid-run
    ("wh_over_cap_line1", ["--wh-child", "131061"], "early",
     (100.0, 350.0), (1, 40)),
    # >= capacity -> write streams through mid-run (bulk at ~215ms)
    ("wh_through_cap",   ["--wh-child", "131072"], "early",
     (100.0, 350.0), (120000, 132000)),
    ("wh_1m_through",    ["--wh-child", "1048576"], "early",
     (100.0, 350.0), (1000000, 1049000)),
    # same edge with pygame fully initialised — the window is
    # language-layer (Python stdio), not SDL
    ("wh_init_below_cap", ["--wh-child", "131060", "--wh-init"],
     "withheld", (300.0, 4000.0), (0, 0)),
    ("wh_init_through",   ["--wh-child", "131072", "--wh-init"],
     "early", (100.0, 1200.0), (120000, 132000)),
    # drip-feed: accumulated small writes tip at the same bound —
    # flushed pending lands on the write grid (12 + k*chunk)
    ("wh_drip_tip",      ["--wh-drip", "16384,10,30"], "early",
     (250.0, 600.0), (114000, 116000)),
    ("wh_drip8k_tip",    ["--wh-drip", "8192,17,15"], "early",
     (250.0, 700.0), (120000, 125000)),
]

# (name, child mode, want line, wait bound) — direction-2 writer-bound
IO_CELLS = [
    ("iochild_flush_l1", "flush", "PYGAME-IOCHILD-1", (5.0, 150.0)),
    ("iochild_flush_l2", "flush", "PYGAME-IOCHILD-2", (150.0, 400.0)),
    # unflushed: both lines withheld to child exit (~200ms+)
    ("iochild_buf_l1",   "buf",   "PYGAME-IOCHILD-1", (150.0, 450.0)),
    ("iochild_buf_l2",   "buf",   "PYGAME-IOCHILD-2", (150.0, 450.0)),
]


def classify(first_byte_ms, eof_ms):
    if first_byte_ms is None:
        return "silent"
    gap = eof_ms - first_byte_ms
    if gap >= 200.0:
        return "early"
    if gap <= 100.0:
        return "withheld"
    return "mid"


def run_process(command, timeout_seconds, env_extra=None):
    try:
        env = dict(os.environ)
        env.update(ENV_EXTRA)
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


def trace_pipe(probe, argv_tail, timeout_s=CHILD_TIMEOUT_S):
    """Spawn `python3 pygame_probe.py <argv_tail>` (NO -u: buffering is
    the surface under test), timestamp every parent-side read event."""
    env = dict(os.environ)
    env.update(ENV_EXTRA)
    t0 = time.perf_counter()
    proc = subprocess.Popen([sys.executable, str(probe)] + argv_tail,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.DEVNULL, env=env)
    events = []
    while True:
        left = timeout_s - (time.perf_counter() - t0)
        if left <= 0:
            events.append({"t_ms": round((time.perf_counter() - t0) * 1e3, 2),
                           "bytes": -1, "note": "TIMEOUT"})
            proc.kill()
            break
        ready, _, _ = select.select([proc.stdout], [], [], left)
        if not ready:
            events.append({"t_ms": round((time.perf_counter() - t0) * 1e3, 2),
                           "bytes": -1, "note": "TIMEOUT"})
            proc.kill()
            break
        data = os.read(proc.stdout.fileno(), 1 << 22)
        events.append({"t_ms": round((time.perf_counter() - t0) * 1e3, 2),
                       "bytes": len(data)})
        if not data:
            break
    proc.wait()
    eof_ms = round((time.perf_counter() - t0) * 1e3, 2)
    good = [e for e in events if e["bytes"] > 0]
    first = good[0] if good else None
    # bytes surfaced >=100ms before EOF — measures what the flush edge
    # released mid-run (first_bytes alone is pipe-capacity-capped @64KiB)
    early_bytes = sum(e["bytes"] for e in good
                      if e["t_ms"] <= eof_ms - 100.0)
    return {"argv": argv_tail, "events": events, "eof_ms": eof_ms,
            "ret": proc.returncode,
            "first_byte_ms": first["t_ms"] if first else None,
            "first_bytes": first["bytes"] if first else 0,
            "early_bytes": early_bytes,
            "total_bytes": sum(e["bytes"] for e in good),
            "class": classify(first["t_ms"] if first else None, eof_ms)}


def trace_lines(probe, mode, timeout_s=CHILD_TIMEOUT_S):
    """--io-child capture: per-line parent-visible wait from spawn."""
    env = dict(os.environ)
    env.update(ENV_EXTRA)
    t0 = time.perf_counter()
    proc = subprocess.Popen([sys.executable, str(probe),
                             "--io-child", mode],
                            stdout=subprocess.PIPE,
                            stderr=subprocess.DEVNULL, env=env, text=True)
    waits = {}
    for want in ("PYGAME-IOCHILD-1", "PYGAME-IOCHILD-2"):
        ready, _, _ = select.select([proc.stdout], [], [], timeout_s)
        if not ready:
            waits[want] = None
            continue
        line = proc.stdout.readline()
        waits[want] = {"wait_ms": round((time.perf_counter() - t0) * 1e3, 2),
                       "line": line.strip()}
    proc.wait()
    return {"mode": mode, "waits": waits,
            "eof_ms": round((time.perf_counter() - t0) * 1e3, 2),
            "ret": proc.returncode}


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


def bound_check(bound, got):
    if got is None:
        return "missing"
    if not (bound[0] <= got <= bound[1]):
        return f"{got!r} outside bound {bound}"
    return None


def main():
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--python", default=sys.executable,
                        help="interpreter for the probe (must have pygame)")
    parser.add_argument("--probe", type=Path, default=PROBE)
    parser.add_argument("--runs", type=Path,
                        default=HERE.parent / "live" / "runs")
    parser.add_argument("--skip-io", action="store_true",
                        help="skip WH/IO child cells (main probe arms only)")
    args = parser.parse_args()

    probe = args.probe

    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    run_dir = args.runs / ("pygame-" + stamp)
    run_dir.mkdir(parents=True)

    ver_out, _, ver_code, ver_err = run_process(
        [args.python, "-c",
         "import os;os.environ['PYGAME_HIDE_SUPPORT_PROMPT']='1';"
         "import pygame;print(pygame.version.ver,"
         " '.'.join(map(str, pygame.get_sdl_version())))"], 20)
    pygame_version = ver_out.strip()

    started = datetime.now(timezone.utc)
    stdout, stderr, code, error = run_process(
        [args.python, str(probe)], TIMEOUT_S)
    elapsed = (datetime.now(timezone.utc) - started).total_seconds()
    (run_dir / "probe.stdout.txt").write_text(stdout)
    (run_dir / "probe.stderr.txt").write_text(stderr)

    arms = parse_arms(stdout)
    launch_ok = error is None and code == 0
    done_marker = "PYGAME_PROBE_DONE" in [l.strip()
                                          for l in stdout.splitlines()]

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

    if not args.skip_io:
        for name, tail, want_class, fb_bound, fbytes_bound in WH_CELLS:
            trace = trace_pipe(probe, tail)
            (run_dir / f"{name}.json").write_text(
                json.dumps(trace, indent=2) + "\n")
            reasons = []
            if trace["ret"] != 0:
                reasons.append(f"child ret={trace['ret']}")
            if trace["class"] != want_class:
                reasons.append(
                    f"class {trace['class']!r} != {want_class!r} "
                    f"(first_byte_ms={trace['first_byte_ms']} "
                    f"eof_ms={trace['eof_ms']})")
            for key, bound, got in (("first_byte_ms", fb_bound,
                                     trace["first_byte_ms"]),
                                    ("early_bytes", fbytes_bound,
                                     trace["early_bytes"])):
                r = bound_check(bound, got)
                if r:
                    reasons.append(f"{key} {r}")
            results.append({"case": name, "arm": "wh",
                            "key": " ".join(tail),
                            "pinned": want_class,
                            "observed": trace["class"],
                            "first_byte_ms": trace["first_byte_ms"],
                            "early_bytes": trace["early_bytes"],
                            "eof_ms": trace["eof_ms"],
                            "verdict": "PASS" if not reasons else "FAIL",
                            "reasons": reasons})

        for name, mode, want, bound in IO_CELLS:
            tr = trace_lines(probe, mode)
            (run_dir / f"{name}.json").write_text(
                json.dumps(tr, indent=2) + "\n")
            got = tr["waits"].get(want, {})
            wait = got.get("wait_ms") if isinstance(got, dict) else None
            reasons = []
            if tr["ret"] != 0:
                reasons.append(f"child ret={tr['ret']}")
            if not isinstance(got, dict) or got.get("line") != want:
                reasons.append(f"line {got!r} != {want!r}")
            r = bound_check(bound, wait)
            if r:
                reasons.append(f"wait_ms {r}")
            results.append({"case": name, "arm": "iochild",
                            "key": f"{mode}|{want}",
                            "pinned": list(bound), "observed": wait,
                            "verdict": "PASS" if not reasons else "FAIL",
                            "reasons": reasons})

    passed = sum(1 for r in results if r["verdict"] == "PASS")
    failed = len(results) - passed
    for r in results:
        print(f"{r['verdict']:8} {r['case']:28} {r['arm']}|{r['key']}"
              + ("" if r['verdict'] == 'PASS' else f"  {';'.join(r['reasons'])}"))
        sys.stdout.flush()

    print(f"totals: cases={len(results)} pass={passed} fail={failed} "
          f"launch_ok={launch_ok} done_marker={done_marker} exit={code}")

    verdict = "PASS" if (failed == 0 and launch_ok and done_marker) else "FAIL"
    payload = {"python": args.python, "pygame_version": pygame_version,
               "pygame_version_exit": ver_code,
               "pygame_version_error": ver_err,
               "probe": str(probe), "probe_exit": code,
               "probe_error": error, "probe_elapsed_s": elapsed,
               "started_utc": stamp, "done_marker": done_marker,
               "results": results,
               "totals": {"cases": len(results), "pass": passed,
                          "fail": failed},
               "verdict": verdict}
    (run_dir / "verdicts.json").write_text(json.dumps(payload, indent=2) + "\n")
    print(f"{verdict} battery: {run_dir / 'verdicts.json'}")
    return 0 if verdict == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
