#!/usr/bin/env python3
"""r95 critic arm runner.

Faithful replay of the battery's launch shape for the r95 arms (and their
mutants), with the battery's own classify_process semantics:

    scratch = byte-copy of <fixtures>  (run_battery.py excluded)
    scratch/project.godot: config/name -> unique suffix
    controls/pickup.tscn staged at scratch/pickup.tscn
    causal_chain.gd readiness fix (two awaits)
    godot --headless [--fixed-fps N] --path scratch --script res://<script> -- <flags>
    8 s per-case bound (the battery's non-export bound)

Records per receipt: rc, wall, stdout, stderr, signature-matched,
unallowlisted ERROR: lines, verdict (classify_process with expected_errors=()).
"""
import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path("/home/vgpnk/Projects/shokunin/game-dev-2d-shokunin")
SEAT = ROOT / "corpus" / "live" / "r95-critic"
FROZEN = SEAT / "frozen" / "corpus" / "fixtures"


def load_rows():
    return json.loads((SEAT / "scripts" / "rows.json").read_text())["r95_rows"]


def build_scratch(dest: Path, fixtures: Path, tps=None, threaded=False):
    dest.mkdir(parents=True, exist_ok=True)
    for item in fixtures.iterdir():
        if item.name == "run_battery.py" or item.name.startswith("."):
            continue
        if item.is_dir():
            shutil.copytree(item, dest / item.name)
        else:
            shutil.copy2(item, dest / item.name)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    pf = dest / "project.godot"
    text = pf.read_text().replace('config/name="MechanicOneShotTest"',
                                  f'config/name="MechanicOneShotTest-{stamp}"', 1)
    extra = []
    if tps:
        extra.append(f"common/physics_ticks_per_second={tps}")
    if threaded:
        extra.append("2d/run_on_separate_thread=true")
    if extra:
        text += "\n[physics]\n" + "\n".join(extra) + "\n"
    pf.write_text(text)
    shutil.copy2(dest / "controls" / "pickup.tscn", dest / "pickup.tscn")
    chain = dest / "causal_chain.gd"
    ctext = chain.read_text()
    anchor = "    await process_frame\n    var old := current_scene"
    assert anchor in ctext, "causal fixture changed"
    chain.write_text(ctext.replace(anchor, "    await process_frame\n    await process_frame\n    var old := current_scene", 1))


def classify(code, error, output, expected_exit, signature):
    lines = output.splitlines()
    unrelated = [l for l in lines if "ERROR:" in l]
    return (code == expected_exit and error is None and signature in output
            and not unrelated and "SCRIPT ERROR:" not in output and "Parse Error:" not in output)


def run_batch(name, fixtures, rows, reps, timeout, out_root, fixed_fps=None,
              tps=None, threaded=False, hog=0, scratch_reuse=False, extra_env=None):
    batch = out_root / name
    if batch.exists():
        shutil.rmtree(batch)
    batch.mkdir(parents=True)
    scratch = batch / "scratch"
    if not scratch_reuse:
        build_scratch(scratch, fixtures, tps=tps, threaded=threaded)
    hogs = []
    if hog:
        for _ in range(hog):
            hogs.append(subprocess.Popen(["yes"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL))
    loadavg_start = Path("/proc/loadavg").read_text().split()[0]
    receipts = []
    try:
        for rep in range(reps):
            for row in rows:
                cmd = ["godot", "--headless"]
                if fixed_fps:
                    cmd += ["--fixed-fps", str(fixed_fps)]
                cmd += ["--path", str(scratch), "--script", "res://" + row["script"], "--", *row["args"]]
                env = os.environ.copy()
                if extra_env:
                    env.update(extra_env)
                t0 = time.time()
                err = None
                try:
                    proc = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout, env=env)
                    so, se, rc = proc.stdout, proc.stderr, proc.returncode
                except subprocess.TimeoutExpired as exc:
                    so = (exc.stdout or b"").decode(errors="replace") if isinstance(exc.stdout, bytes) else (exc.stdout or "")
                    se = (exc.stderr or b"").decode(errors="replace") if isinstance(exc.stderr, bytes) else (exc.stderr or "")
                    rc, err = None, f"TIMEOUT after {timeout} seconds"
                out = so + se
                wall = time.time() - t0
                passed = classify(rc, err, out, row["rc"], row["sig"])
                rec = {"batch": name, "rep": rep, "case": row["case"], "script": row["script"],
                       "args": row["args"], "rc": rc, "error": err, "wall": round(wall, 3),
                       "verdict": "PASS" if passed else "FAIL",
                       "sig_in_output": row["sig"] in out,
                       "sig_in_stdout": row["sig"] in so,
                       "unrelated_errors": [l.strip() for l in out.splitlines() if "ERROR:" in l],
                       "stderr_bytes": len(se.encode()),
                       "stdout_sha256": hashlib.sha256(so.encode()).hexdigest(),
                       "stderr_sha256": hashlib.sha256(se.encode()).hexdigest(),
                       "output": out}
                receipts.append(rec)
                if not passed:
                    print(f"  FAIL {row['case']} rc={rc} err={err} sig_in={rec['sig_in_output']} "
                          f"unrelated={rec['unrelated_errors'][:2]} wall={wall:.2f}", flush=True)
    finally:
        for p in hogs:
            p.kill()
    (batch / "receipts.json").write_text(json.dumps(receipts))
    summary = {
        "batch": name, "reps": reps, "rows": len(rows), "receipts": len(receipts),
        "pass": sum(1 for r in receipts if r["verdict"] == "PASS"),
        "fail": sum(1 for r in receipts if r["verdict"] != "PASS"),
        "timeouts": sum(1 for r in receipts if r["error"]),
        "max_wall": max(r["wall"] for r in receipts) if receipts else None,
        "max_wall_case": max(receipts, key=lambda r: r["wall"])["case"] if receipts else None,
        "loadavg_start": loadavg_start,
        "loadavg_end": Path("/proc/loadavg").read_text().split()[0],
        "fixed_fps": fixed_fps, "tps": tps, "threaded": threaded, "hog": hog,
        "nonzero_stderr": sum(1 for r in receipts if r["stderr_bytes"]),
    }
    (batch / "summary.json").write_text(json.dumps(summary, indent=1))
    print(json.dumps(summary, indent=1), flush=True)
    return summary


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--batch", required=True)
    ap.add_argument("--fixtures", default=str(FROZEN))
    ap.add_argument("--rows-json", default=None, help="override row list (mutants)")
    ap.add_argument("--reps", type=int, default=1)
    ap.add_argument("--timeout", type=float, default=8)
    ap.add_argument("--fixed-fps", type=int, default=None)
    ap.add_argument("--tps", type=int, default=None)
    ap.add_argument("--threaded", action="store_true")
    ap.add_argument("--hog", type=int, default=0)
    ap.add_argument("--filter", default=None, help="substring filter on case name")
    ap.add_argument("--out", default=str(SEAT / "runs"))
    args = ap.parse_args()

    if args.rows_json:
        rows = json.loads(Path(args.rows_json).read_text())
    else:
        rows = load_rows()
    if args.filter:
        rows = [r for r in rows if args.filter in r["case"]]
    out_root = Path(args.out)
    out_root.mkdir(parents=True, exist_ok=True)
    run_batch(args.batch, Path(args.fixtures), rows, args.reps, args.timeout, out_root,
              fixed_fps=args.fixed_fps, tps=args.tps, threaded=args.threaded, hog=args.hog)


if __name__ == "__main__":
    sys.exit(main())
