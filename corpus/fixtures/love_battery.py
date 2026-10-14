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

r74 lattice (love.physics callback-interior writes, IW_CELLS): one
`love love_phys_probe` process per cell (IW_CELL env). Writes inside
Box2D callbacks (beginContact/preSolve/postSolve) are gated per class --
the measured partition is {refused | deferred | fatal | applied}:
  refused : structural mutation (setPosition/newBody/setActive) -> catchable
            "Box2D assertion failed: ...IsLocked() == false" Lua error
            (this build surfaces b2Assert via loveAssert as a Lua error,
            not a silent no-op and not a process abort).
  deferred: body:destroy() -> ok=true, body alive for the rest of the
            callback+step; drained after world:update with a synthesized
            EndContact at locked=false.
  fatal   : the same structural write NOT pcall-contained -> error escapes
            world:update -> LOVE error handler -> rc=1, "Error:" on stdout,
            no CELL_DONE (partial capture, measured not silent).
  applied : non-structural writes (setLinearVelocity, contact:setEnabled
            in preSolve) are legal inside the lock.
Exterior (ext_*) controls apply immediately. Interior cells are spawned
LAST and the uncontained (*_unp) cells last of all -- each cell is its
own process so a fatal cell is a measured FAIL-class for that cell only.
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
IW_PROBE_DIR = HERE / "love_phys_probe"
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


# ---- r74 interior-write lattice ------------------------------------------
#
# (case, cell, expected_class, {flat_key: pinned})
# expected_class in {captured, applied, refused, deferred, fatal} -- the
# falsifiable partition the arm pins. flat keys are `<tag>.<key>` from the
# probe's `IW | cell=<cell> | <tag> k=v ...` lines, plus synthesized keys:
#   rc / done / err_on / assert_txt / evpin_<cb>_lck / evpin_<cb>_step
# Measured on this host (18 cells x>=2 stable reps; the r74-scout scratch
# receipts are byte-identical twins of this probe's output).
IW_CELLS = [
    # availability lattice: reads inside callbacks are legal; locked=true
    ("iw_avail_lattice", "baseline", "captured", {
        "built.bodies": "4", "built.locked": "false",
        "viability.love": "11.5.0",
        "evpin_bc_lck": "true", "evpin_pre_lck": "true",
        "evpin_post_lck": "true", "evpin_ec_lck": "true",
        "evpin_ec_step": "74",
        "final.steps": "200", "final.count": "4",
        "final.bc": "5", "final.ec": "4",
        "final.pre": "36", "final.post": "36",
        "final.fired": "false", "done": "true", "rc": "0"}),
    # exterior controls -- the same mutations outside any callback apply
    ("iw_ext_setpos", "ext_setpos", "applied", {
        "ext_setpos.ok": "true", "ext_setpos.err": "nil",
        "ext_before.pos": "400,60",
        "ext_setpos.pos_after": "1234.5,678.9000244140625",
        "done": "true", "rc": "0"}),
    ("iw_ext_newbody", "ext_newbody", "applied", {
        "ext_newbody.ok": "true",
        "ext_newbody.count_before": "4", "ext_newbody.count_after": "5",
        "ext_newbody.nb_pos": "700,100",
        "done": "true", "rc": "0"}),
    ("iw_ext_destroy", "ext_destroy", "applied", {
        # immediate: body is dead the instant the call returns (contrast
        # with the deferred interior class below)
        "ext_destroy.ok": "true",
        "ext_destroy.count_before": "4", "ext_destroy.count_after": "3",
        "ext_destroy.b1pos_after": "ERR:Attempt to use destroyed body.",
        "done": "true", "rc": "0"}),
    # interior structural writes -> refused (catchable Lua assert)
    ("iw_bc_setpos", "bc_setpos", "refused", {
        "fire.step": "73", "fire.locked": "true",
        "cb_setpos.ok": "false",
        "cb_setpos.err": "Box2D assertion failed: m_world->IsLocked() == false",
        "cb_setpos.pos_after": "400,520.1500244140625",
        "after_update.b1pos": "400,511.13113403320312",
        "evpin_ec_lck": "true", "done": "true", "rc": "0"}),
    ("iw_pre_setpos", "pre_setpos", "refused", {
        "fire.step": "73", "fire.cb": "pre",
        "cb_setpos.ok": "false",
        "cb_setpos.err": "Box2D assertion failed: m_world->IsLocked() == false",
        "cb_setpos.pos_after": "400,520.1500244140625",
        "done": "true", "rc": "0"}),
    ("iw_post_setpos", "post_setpos", "refused", {
        # postSolve channel sees the POST-step pose (frontier channel split)
        "fire.step": "73", "fire.cb": "post",
        "fire.pos": "400,511.13113403320312",
        "cb_setpos.ok": "false",
        "cb_setpos.err": "Box2D assertion failed: m_world->IsLocked() == false",
        "cb_setpos.pos_after": "400,511.13113403320312",
        "done": "true", "rc": "0"}),
    ("iw_bc_newbody", "bc_newbody", "refused", {
        # world-level fn: assert text drops the m_world-> prefix
        "fire.step": "73", "fire.locked": "true",
        "cb_newbody.ok": "false",
        "cb_newbody.err": "Box2D assertion failed: IsLocked() == false",
        "cb_newbody.count_before": "4", "cb_newbody.count_after": "4",
        "done": "true", "rc": "0"}),
    ("iw_pre_newbody", "pre_newbody", "refused", {
        "fire.cb": "pre",
        "cb_newbody.ok": "false",
        "cb_newbody.err": "Box2D assertion failed: IsLocked() == false",
        "cb_newbody.count_after": "4", "done": "true", "rc": "0"}),
    ("iw_post_newbody", "post_newbody", "refused", {
        "fire.cb": "post",
        "cb_newbody.ok": "false",
        "cb_newbody.err": "Box2D assertion failed: IsLocked() == false",
        "cb_newbody.count_after": "4", "done": "true", "rc": "0"}),
    # interior destroy -> deferred (drained after world:update, ec at
    # locked=false inside the update epilogue)
    ("iw_bc_destroy", "bc_destroy", "deferred", {
        "fire.step": "73", "fire.locked": "true",
        "cb_destroy.ok": "true", "cb_destroy.err": "nil",
        "cb_destroy.alive_in_cb": "400,520.1500244140625",
        "cb_destroy.count_after": "4",
        "after_update.count": "3",
        "after_update.b1pos": "ERR:Attempt to use destroyed body.",
        "evpin_ec_lck": "false", "evpin_ec_step": "73",
        "done": "true", "rc": "0"}),
    ("iw_pre_destroy", "pre_destroy", "deferred", {
        "fire.cb": "pre",
        "cb_destroy.ok": "true",
        "cb_destroy.alive_in_cb": "400,520.1500244140625",
        "cb_destroy.count_after": "4",
        "after_update.count": "3",
        "evpin_ec_lck": "false", "evpin_ec_step": "73",
        "done": "true", "rc": "0"}),
    ("iw_post_destroy", "post_destroy", "deferred", {
        "fire.cb": "post",
        "cb_destroy.ok": "true",
        "cb_destroy.alive_in_cb": "400,511.13113403320312",
        "cb_destroy.count_after": "4",
        "after_update.count": "3",
        "evpin_ec_lck": "false", "evpin_ec_step": "73",
        "done": "true", "rc": "0"}),
    # edges: active-body write refused; contact mask + velocity accepted
    ("iw_bc_setactive", "bc_setactive", "refused", {
        "fire.step": "73",
        "cb_setactive.ok": "false",
        "cb_setactive.err": "Box2D assertion failed: m_world->IsLocked() == false",
        "cb_setactive.isActive_after": "true",
        "cb_setactive.count_after": "4", "done": "true", "rc": "0"}),
    ("iw_pre_contactmask", "pre_contactmask", "applied", {
        # legal single-step mask: no impulse lands that update
        "fire.cb": "pre", "fire.step": "73",
        "cb_contactmask.ok": "true",
        "cb_contactmask.isEnabled_after": "false",
        "cb_contactmask.isTouching": "true",
        "after_update.b1pos": "400,531.054443359375",
        "after_update.b1vel": "0,763.8724365234375",
        "done": "true", "rc": "0"}),
    ("iw_bc_setvel", "bc_setvel", "applied", {
        # non-structural write has no locked assert
        "fire.step": "73", "fire.locked": "true",
        "cb_setvel.ok": "true", "cb_setvel.err": "nil",
        "cb_setvel.vel_after": "55,-7",
        "done": "true", "rc": "0"}),
    # uncontained escapes -> fatal, spawned LAST
    ("iw_bc_setpos_unp", "bc_setpos_unp", "fatal", {
        "fire.step": "73", "fire.locked": "true",
        "rc": "1", "done": "false",
        "err_on": "stdout", "assert_txt": "m_world_islocked"}),
    ("iw_bc_newbody_unp", "bc_newbody_unp", "fatal", {
        "fire.step": "73",
        "rc": "1", "done": "false",
        "err_on": "stdout", "assert_txt": "islocked"}),
]

IW_LINE = re.compile(r"^IW \| cell=(\S+) \| (.*)$")
IW_KV = re.compile(r"(\w+)=")


def parse_iw(stdout):
    """Parse `IW | cell=<c> | <tag> k=v ...` lines.

    Values may contain spaces (assert text, ERR: strings): a value runs
    until the next `word=` boundary or end of line. Returns
    (flat, evpins): flat is `<tag>.<key>` -> last-wins merge across lines;
    evpins is the ordered list of evpin kv dicts (one per cb).
    """
    flat, evpins = {}, []
    for line in stdout.splitlines():
        m = IW_LINE.match(line.strip())
        if not m:
            continue
        body = m.group(2).strip()
        if body == "CELL_DONE":
            flat["done"] = "true"
            continue
        parts = [(mm.start(), mm.group(1)) for mm in IW_KV.finditer(body)]
        if not parts:
            continue
        tag = body[:parts[0][0]].strip()
        kv = {}
        for i, (at, k) in enumerate(parts):
            end = parts[i + 1][0] if i + 1 < len(parts) else len(body)
            kv[k] = body[at + len(k) + 1:end].strip()
        if tag == "evpin":
            evpins.append(kv)
        for k, v in kv.items():
            flat[f"{tag}.{k}"] = v
    for e in evpins:
        cb = e.get("cb", "?")
        flat[f"evpin_{cb}_lck"] = e.get("locked", "?")
        flat[f"evpin_{cb}_step"] = e.get("step", "?")
    flat.setdefault("done", "false")
    return flat, evpins


def iw_classify(cell, flat, evpins, rc, timed_out, stdout):
    """Map one cell's capture onto {captured|applied|refused|deferred|
    fatal|timeout|died|nolaunch|anomaly}. Partial-capture detection is
    built in: fire-present without CELL_DONE is never a pass shape."""
    if timed_out:
        return "timeout", f"exceeded {TIMEOUT_S}s"
    done = flat.get("done") == "true"
    has_fire = "fire.step" in flat
    if done and rc == 0:
        if cell == "baseline":
            return "captured", "availability lattice"
        mut = next((t for t in ("cb_setpos", "cb_newbody", "cb_destroy",
                              "cb_setactive", "cb_contactmask", "cb_setvel",
                              "ext_setpos", "ext_newbody", "ext_destroy")
                    if f"{t}.ok" in flat), None)
        if mut is None:
            return "anomaly", "CELL_DONE but no mutation line"
        if flat[f"{mut}.ok"] == "false":
            if "assertion" in flat.get(f"{mut}.err", ""):
                return "refused", flat[f"{mut}.err"]
            return "anomaly", "ok=false without Box2D assertion"
        if flat[f"{mut}.ok"] == "true":
            if mut == "cb_destroy":
                try:
                    drop = int(flat.get("after_update.count", "-1")) == \
                        int(flat.get("built.bodies", "0")) - 1
                except ValueError:
                    drop = False
                ec_lck = flat.get("evpin_ec_lck")
                dead = flat.get("after_update.b1pos", "").startswith("ERR:")
                if drop and dead and ec_lck == "false":
                    return "deferred", "drain ec at locked=false"
                return "anomaly", "destroy ok without deferred witness"
            return "applied", mut
        return "anomaly", f"unhandled ok={flat[f'{mut}.ok']!r}"
    if has_fire and not done and rc not in (0, None):
        if "Box2D assertion" in stdout:
            return "fatal", f"rc={rc}, assert text on stdout"
        return "died", f"rc={rc} without assert text"
    if not has_fire and not done:
        return "nolaunch", f"rc={rc} and no fire line"
    return "anomaly", f"rc={rc} done={done} fire={has_fire}"


def iw_flat_extras(flat, rc, stdout, stderr):
    flat["rc"] = str(rc)
    if "m_world->IsLocked() == false" in stdout:
        flat["assert_txt"] = "m_world_islocked"
    elif "IsLocked() == false" in stdout:
        flat["assert_txt"] = "islocked"
    elif "Box2D assertion" in stdout:
        flat["assert_txt"] = "other"
    else:
        flat["assert_txt"] = "none"
    if "Box2D assertion" in stdout:
        flat["err_on"] = "stdout"
    elif "Box2D assertion" in stderr:
        flat["err_on"] = "stderr"
    else:
        flat["err_on"] = "none"
    return flat


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

    # r74 interior-write lattice: one love process per cell, spawned last
    # (uncontained *_unp cells are last in the table -- a fatal cell kills
    # only its own launch and its truncated receipt is the measurement).
    for name, cell, expected, pins in IW_CELLS:
        c_stdout, c_stderr, c_code, c_err = run_process(
            [args.love, str(IW_PROBE_DIR)], TIMEOUT_S,
            {"IW_CELL": cell})
        (run_dir / f"iw-{cell}.stdout.txt").write_text(c_stdout)
        (run_dir / f"iw-{cell}.stderr.txt").write_text(c_stderr)
        flat, evpins = parse_iw(c_stdout)
        iw_flat_extras(flat, c_code, c_stdout, c_stderr)
        cls, detail = iw_classify(
            cell, flat, evpins, c_code,
            c_err is not None and c_err.startswith("TIMEOUT"), c_stdout)
        reasons = []
        if c_err is not None:
            reasons.append(c_err)
        if cls != expected:
            reasons.append(f"class {cls} != {expected} ({detail})")
        for k, pinned in pins.items():
            reason = check(pinned, flat.get(k))
            if reason is not None:
                reasons.append(f"{k}: {reason}")
        results.append({"case": name, "arm": "iw",
                        "key": f"cell={cell}",
                        "pinned": expected, "observed": cls,
                        "verdict": "PASS" if not reasons else "FAIL",
                        "reasons": reasons})

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
