#!/usr/bin/env python3
"""r79 boundary-exec probe 5 runner — `love.errorhandler` windowed-surface guard.

Variants (all scratch copies under corpus/live/r79-boundary-exec/):
  love_base     committed bytes (control; must reproduce the committed receipt)
  love_win      committed conf + t.modules.window=TRUE + errorhandler override
  love_gfx_eh   window+graphics+font+image on + errorhandler override
  love_gfx_noeh window+graphics+font+image on, NO override (negative control:
                the default love.errhand is expected to open a desktop window
                and enter its error-screen loop on the fatal cell)

Classification uses the production love_battery.py predicates (imported, never
re-implemented). Receipts under runs/<stamp>/probe5/.
"""
import hashlib
import json
import os
import re
import signal
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
FIX = REPO / "corpus" / "fixtures"
COMMITTED = REPO / "corpus" / "live" / "runs" / "love-20261014T215836641142Z"
LOVE = "/usr/bin/love"
TIMEOUT_S = 30

sys.path.insert(0, str(FIX))
import love_battery  # noqa: E402  production parse_iw / iw_flat_extras / iw_classify / run_process

PINS = {cell: (name, expected, pins) for name, cell, expected, pins in love_battery.IW_CELLS}
CELLS = ["bc_setpos_unp", "baseline", "bc_setpos", "bc_destroy"]


def love_clients():
    try:
        raw = subprocess.run(["hyprctl", "clients", "-j"], capture_output=True,
                             text=True, timeout=10).stdout
        clients = json.loads(raw)
    except Exception as exc:  # noqa: BLE001
        return None, f"hyprctl error: {exc}"
    hits = [c for c in clients
            if "love" in (c.get("class", "") + c.get("initialClass", "")).lower()
            or "untitled" in c.get("title", "").lower()]
    return hits, None


def run_cell(probe_dir, cell, timeout=TIMEOUT_S):
    env = dict(os.environ)
    env["IW_CELL"] = cell
    started = time.time()
    try:
        proc = subprocess.run([LOVE, str(probe_dir)], capture_output=True, text=True,
                              timeout=timeout, env=env)
        return {"cell": cell, "probe_dir": str(probe_dir), "rc": proc.returncode,
                "stdout": proc.stdout, "stderr": proc.stderr, "timeout": None,
                "elapsed_s": round(time.time() - started, 3)}
    except subprocess.TimeoutExpired as exc:
        def text(v):
            return v.decode(errors="replace") if isinstance(v, bytes) else (v or "")
        return {"cell": cell, "probe_dir": str(probe_dir), "rc": None,
                "stdout": text(exc.stdout), "stderr": text(exc.stderr),
                "timeout": f"TIMEOUT after {timeout}s", "elapsed_s": round(time.time() - started, 3)}


def classify(cell, r):
    name, expected, pins = PINS[cell]
    flat = love_battery.parse_iw(r["stdout"])
    love_battery.iw_flat_extras(flat, r["rc"], r["stdout"], r["stderr"])
    cls, detail = love_battery.iw_classify(cell, flat, r["rc"], r["timeout"] is not None,
                                           r["stdout"])
    reasons = []
    if r["timeout"]:
        reasons.append(r["timeout"])
    if cls != expected:
        reasons.append(f"class {cls} != {expected} ({detail})")
    for k, pinned in pins.items():
        reason = love_battery.check(pinned, flat.get(k))
        if reason is not None:
            reasons.append(f"{k}: {reason}")
    return {"case": name, "cell": cell, "class": cls, "expected": expected,
            "detail": detail, "verdict": "PASS" if not reasons else "FAIL",
            "reasons": reasons, "flat": flat, "rc": r["rc"]}


def window_negative_control(probe_dir, cell, bound_s=8.0):
    """Run the fatal cell WITHOUT the override; poll hyprctl for a love window;
    kill the process group at the bound. Returns the observation."""
    env = dict(os.environ)
    env["IW_CELL"] = cell
    out_f = probe_dir.parent / "negctl.stdout.txt"
    err_f = probe_dir.parent / "negctl.stderr.txt"
    before, err0 = love_clients()
    with open(out_f, "w") as so, open(err_f, "w") as se:
        proc = subprocess.Popen([LOVE, str(probe_dir)], stdout=so, stderr=se,
                                env=env, start_new_session=True)
    window_seen = None
    deadline = time.time() + bound_s
    while time.time() < deadline:
        if proc.poll() is not None:
            break
        hits, err = love_clients()
        if hits:
            window_seen = {"t_s": round(bound_s - (deadline - time.time()), 3),
                           "clients": [{k: c.get(k) for k in
                                        ("class", "initialClass", "title", "pid")} for c in hits]}
            break
        time.sleep(0.25)
    exited_early = proc.poll() is not None
    killed = False
    if not exited_early:
        try:
            os.killpg(os.getpgid(proc.pid), signal.SIGKILL)
            killed = True
        except ProcessLookupError:
            pass
        proc.wait(timeout=10)
    after, err1 = love_clients()
    return {"cell": cell, "window_seen": window_seen, "exited_early": exited_early,
            "killed": killed, "rc_after_kill": proc.returncode,
            "clients_before": len(before or []), "clients_after": len(after or []),
            "hyprctl_error": err0 or err1,
            "stdout": out_f.read_text(), "stderr": err_f.read_text()}


def main():
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    out_dir = HERE / "runs" / stamp / "probe5"
    out_dir.mkdir(parents=True)
    out = {"stamp": stamp, "love": LOVE,
           "love_version": subprocess.run([LOVE, "--version"], capture_output=True,
                                          text=True).stdout.strip(),
           "committed_receipts": str(COMMITTED.relative_to(REPO)),
           "variants": {}, "classify": {}, "diffs": {}}

    def shas(d):
        return {p.name: hashlib.sha256(p.read_bytes()).hexdigest()
                for p in sorted(d.glob("*")) if p.is_file()}

    out["variants"] = {v: shas(HERE / v) for v in
                       ("love_base", "love_win", "love_win2", "love_gfx_eh",
                        "love_gfx_eh2", "love_gfx_noeh")}

    def record(variant, cell):
        r = run_cell(HERE / variant, cell)
        (out_dir / f"{variant}-{cell}.stdout.txt").write_text(r["stdout"])
        (out_dir / f"{variant}-{cell}.stderr.txt").write_text(r["stderr"])
        c = classify(cell, r)
        key = f"{variant}/{cell}"
        out["classify"][key] = {k: v for k, v in c.items() if k != "flat"}
        out["classify"][key]["flat"] = c["flat"]
        out["classify"][key]["elapsed_s"] = r["elapsed_s"]
        out["classify"][key]["stdout_sha256"] = hashlib.sha256(r["stdout"].encode()).hexdigest()
        committed = COMMITTED / f"iw-{cell}.stdout.txt"
        if committed.exists():
            same = r["stdout"] == committed.read_text()
            out["diffs"][key] = {"byte_identical": same,
                                 "committed_sha256": hashlib.sha256(committed.read_bytes()).hexdigest(),
                                 "emitted_sha256": hashlib.sha256(r["stdout"].encode()).hexdigest()}
        print(f"{'OK ' if c['verdict'] == 'PASS' else 'BAD'} {key} rc={r['rc']} "
              f"class={c['class']}/{c['expected']} identical_to_committed="
              f"{out['diffs'].get(key, {}).get('byte_identical')} reasons={c['reasons']}")
        return r

    print("--- base control (committed bytes)")
    record("love_base", "bc_setpos_unp")
    print("--- variant A: love_win (modules.window=TRUE + override)")
    for cell in CELLS:
        record("love_win", cell)
    print("--- variant B: love_gfx_eh (window+graphics on + override)")
    record("love_gfx_eh", "bc_setpos_unp")
    print("--- variant A2/B2: level-2 traceback override")
    record("love_win2", "bc_setpos_unp")
    record("love_gfx_eh2", "bc_setpos_unp")
    for cell in ("baseline", "bc_setpos", "bc_destroy"):
        record("love_win2", cell)
    print("--- negative control: love_gfx_noeh (no override)")
    neg = window_negative_control(HERE / "love_gfx_noeh", "bc_setpos_unp", bound_s=8.0)
    out["negative_control"] = neg
    print(f"window_seen={neg['window_seen']} exited_early={neg['exited_early']} "
          f"killed={neg['killed']} clients_after={neg['clients_after']}")

    final_hits, final_err = love_clients()
    out["clients_after_all"] = {"n": len(final_hits or []), "error": final_err}
    print(f"love clients after all runs: {out['clients_after_all']}")

    (out_dir / "probe5.json").write_text(json.dumps(out, indent=2) + "\n")
    print(f"wrote {out_dir.relative_to(REPO)}/probe5.json")
    return 0


if __name__ == "__main__":
    sys.exit(main())
