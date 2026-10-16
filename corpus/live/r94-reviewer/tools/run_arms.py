#!/usr/bin/env python3
"""r94 reviewer: fresh-process arm receipts on the PINNED committed bytes.

Launch shape is byte-identical to run_battery.py's execute() path
(`godot --headless --path <scratch> --script res://<script> -- <flags>`,
streams captured separately, subprocess.run).  The classifier is extracted
verbatim from the pinned harness (classify_process segment) and its sha256 is
recorded so the extraction can be checked against the r89-r94 recorded
segment sha 749fa0607e7707e6...
"""
import argparse
import hashlib
import json
import re
import shutil
import subprocess
import sys
import textwrap
import time
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
REVIEWER = HERE.parent
PINNED = REVIEWER / "pinned-tmp"
SEG_SHA = "749fa0607e7707e614c1ab157a6f8e756dfc2f460746e6d218e6734ad8fa72c3"


def extract_classifier(pinned_harness: Path):
    """Extract the production classifier verbatim (AST source segment).

    The AST segment of `classify_process` hashes to
    749fa0607e7707e614c1ab157a6f8e756dfc2f460746e6d218e6734ad8fa72c3, the
    segment sha recorded by r89-r94 — so this seat judges receipts with the
    same production logic, not a re-implementation.
    """
    import ast
    src = pinned_harness.read_text()
    tree = ast.parse(src)
    fn = [n for n in ast.walk(tree)
          if isinstance(n, ast.FunctionDef) and n.name == "classify_process"][0]
    seg = ast.get_source_segment(src, fn)
    sha = hashlib.sha256(seg.encode()).hexdigest()
    ns = {}
    exec(textwrap.dedent(seg), ns)
    return ns["classify_process"], sha


def load_cases(pinned_harness: Path):
    import ast
    t = ast.parse(pinned_harness.read_text())
    for node in t.body:
        if isinstance(node, ast.Assign) and getattr(node.targets[0], "id", None) == "CASES":
            return [ast.literal_eval(e) for e in node.value.elts]
    raise SystemExit("CASES not found")


def make_scratch(dst: Path, stamp: str):
    if dst.exists():
        shutil.rmtree(dst)
    dst.mkdir(parents=True)
    for item in PINNED.iterdir():
        if item.name == "run_battery.py" or item.name.startswith("."):
            continue
        if item.is_dir():
            shutil.copytree(item, dst / item.name)
        else:
            shutil.copy2(item, dst / item.name)
    pf = dst / "project.godot"
    pf.write_text(pf.read_text().replace('config/name="MechanicOneShotTest"',
                                         f'config/name="MechanicOneShotTest-{stamp}"', 1))
    shutil.copy2(dst / "controls" / "pickup.tscn", dst / "pickup.tscn")
    return dst


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--godot", default="godot")
    ap.add_argument("--reps", type=int, default=5)
    ap.add_argument("--timeout", type=float, default=25.0)
    ap.add_argument("--out", type=Path, default=REVIEWER / "fresh")
    ap.add_argument("--arms", default="")  # comma list; empty = all 19 r94 arms
    args = ap.parse_args()

    classify, seg_sha = extract_classifier(PINNED / "run_battery.py")
    cases = load_cases(PINNED / "run_battery.py")
    r94 = [c for c in cases if c[0].startswith("r94_")]
    if args.arms:
        want = set(args.arms.split(","))
        r94 = [c for c in r94 if c[0].split("r94_particles_")[-1] in want]

    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    run_dir = args.out / stamp
    scratch = make_scratch(run_dir / "proj", stamp)
    out_dir = run_dir / "receipts"
    out_dir.mkdir(parents=True)

    rows = []
    for name, script, flags, expected_exit, sig in r94:
        arm = [f for f in flags if f.startswith("--arm=")][0].split("=")[1]
        rec = {"case": name, "arm": arm, "expected_exit": expected_exit,
               "reps": [], "pin_sha256": hashlib.sha256(sig.encode()).hexdigest()}
        for rep in range(1, args.reps + 1):
            cmd = [args.godot, "--headless", "--path", str(scratch),
                   "--script", "res://" + script, "--", *flags]
            t0 = time.time()
            try:
                p = subprocess.run(cmd, capture_output=True, text=True,
                                   timeout=args.timeout)
                rc, so, se, err = p.returncode, p.stdout, p.stderr, None
            except subprocess.TimeoutExpired as exc:
                rc, err = None, f"TIMEOUT after {args.timeout} seconds"
                so = (exc.stdout or b"").decode(errors="replace") if isinstance(exc.stdout, bytes) else (exc.stdout or "")
                se = (exc.stderr or b"").decode(errors="replace") if isinstance(exc.stderr, bytes) else (exc.stderr or "")
            except OSError as exc:
                rc, so, se, err = None, "", str(exc), f"launch error: {exc}"
            elapsed = time.time() - t0
            base = f"{name}.rep{rep}"
            (out_dir / f"{base}.out").write_text(so)
            (out_dir / f"{base}.err").write_text(se)
            (out_dir / f"{base}.rc").write_text(f"{rc}\n")
            merged = so + se
            lines = [l for l in so.splitlines() if l.startswith("PASS particles_lattice ")]
            verdict = classify(rc, err, merged, expected_exit, sig, ())
            rec["reps"].append({
                "rep": rep, "rc": rc, "stderr_bytes": len(se), "elapsed": round(elapsed, 3),
                "pin_in_stdout": sig in so, "pin_in_merged": sig in merged,
                "classified": verdict, "pass_line": lines[0] if lines else None,
                "timeout": err,
                "error_lines": [l for l in merged.splitlines() if "ERROR:" in l][:4],
            })
        rows.append(rec)
        v = [r["classified"] for r in rec["reps"]]
        print(f"{name:36s} arm={arm:16s} PASS {sum(v)}/{len(v)} "
              f"rc={sorted({r['rc'] for r in rec['reps']})} "
              f"stderr={sorted({r['stderr_bytes'] for r in rec['reps']})}", flush=True)

    payload = {
        "godot": args.godot, "segment_sha256": seg_sha,
        "segment_sha_expected": SEG_SHA,
        "segment_sha_matches_r89_r94": seg_sha == SEG_SHA,
        "pinned_dir": str(PINNED), "scratch": str(scratch), "stamp": stamp,
        "rows": rows,
    }
    (run_dir / "fresh.json").write_text(json.dumps(payload, indent=1))
    print("segment sha:", seg_sha, "matches recorded:", seg_sha == SEG_SHA)
    bad = [r["case"] for r in rows if not all(x["classified"] for x in r["reps"])]
    print("rows with any reject:", bad)
    return 0 if not bad else 1


if __name__ == "__main__":
    sys.exit(main())
