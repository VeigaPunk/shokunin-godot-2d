#!/usr/bin/env python3
"""r94 verifier — fresh-process launches of all 19 r94 arms on the frozen bytes.

Launch shape is byte-identical to the battery's `execute()` path: a scratch copy
of the frozen fixtures, project name patched, controls/pickup.tscn staged,
causal_chain readiness patch applied, `godot --headless --path <scratch>
--script res://particles_lattice.gd -- --arm=<arm>`, timeout 8 s, stdout/stderr
captured separately. Each rep is then re-classified with the production
classify_process AST-extracted from the frozen committed harness.
"""
import argparse
import ast
import hashlib
import json
import pathlib
import shutil
import subprocess
import sys
from datetime import datetime, timezone

ROOT = pathlib.Path("/home/vgpnk/Projects/shokunin/game-dev-2d-shokunin")
FREEZE = ROOT / "corpus/live/r94-verifier/freeze/corpus/fixtures"
OUTDIR = ROOT / "corpus/live/r94-verifier"
GODOT = "/usr/bin/godot"

parser = argparse.ArgumentParser()
parser.add_argument("--reps", type=int, default=3)
parser.add_argument("--godot", default=GODOT)
parser.add_argument("--out", default=str(OUTDIR / "arms"))
parser.add_argument("--timeout", type=float, default=8.0)
args = parser.parse_args()

src = (FREEZE / "run_battery.py").read_text()
tree = ast.parse(src)
fn_src = None
for node in ast.walk(tree):
    if isinstance(node, ast.FunctionDef) and node.name == "classify_process":
        fn_src = ast.get_source_segment(src, node)
        break
assert fn_src
ns = {}
exec("import re\n" + fn_src, ns)
classify_process = ns["classify_process"]

import importlib.util
spec = importlib.util.spec_from_file_location("frozen_harness", FREEZE / "run_battery.py")
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
r94 = [c for c in mod.CASES if c[0].startswith("r94_")]

outdir = pathlib.Path(args.out)
outdir.mkdir(parents=True, exist_ok=True)
stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
scratch = outdir / f"scratch-{stamp}"
scratch.mkdir(parents=True)
for item in FREEZE.iterdir():
    if item.name == "run_battery.py" or item.name.startswith("."):
        continue
    if item.is_dir():
        shutil.copytree(item, scratch / item.name)
    else:
        shutil.copy2(item, scratch / item.name)
project_file = scratch / "project.godot"
project_text = project_file.read_text()
project_text = project_text.replace('config/name="MechanicOneShotTest"',
                                    f'config/name="MechanicOneShotTest-{stamp}"', 1)
project_file.write_text(project_text)
shutil.copy2(scratch / "controls" / "pickup.tscn", scratch / "pickup.tscn")
chain = scratch / "causal_chain.gd"
text = chain.read_text()
anchor = "    await process_frame\n    var old := current_scene"
assert anchor in text
chain.write_text(text.replace(anchor, "    await process_frame\n    await process_frame\n    var old := current_scene", 1))

summary = []
fails = []
for case, script, flags, expected_exit, sig in r94:
    arm = flags[0].removeprefix("--arm=")
    for rep in range(1, args.reps + 1):
        cmd = [args.godot, "--headless", "--path", str(scratch), "--script", f"res://{script}", "--", *flags]
        started = datetime.now(timezone.utc)
        try:
            p = subprocess.run(cmd, capture_output=True, text=True, timeout=args.timeout)
            out, err, rc, terr = p.stdout, p.stderr, p.returncode, None
        except subprocess.TimeoutExpired as exc:
            out = (exc.stdout or b"").decode(errors="replace") if isinstance(exc.stdout, bytes) else (exc.stdout or "")
            err = (exc.stderr or b"").decode(errors="replace") if isinstance(exc.stderr, bytes) else (exc.stderr or "")
            rc, terr = None, f"TIMEOUT after {args.timeout} seconds"
        el = (datetime.now(timezone.utc) - started).total_seconds()
        base = outdir / f"{case}.rep{rep}"
        pathlib.Path(str(base) + ".out").write_text(out)
        pathlib.Path(str(base) + ".err").write_text(err)
        pathlib.Path(str(base) + ".rc").write_text(str(rc))
        verdict = classify_process(rc, terr, out + err, expected_exit, sig, ())
        summary.append({"case": case, "arm": arm, "rep": rep, "rc": rc, "timeout": terr,
                        "elapsed": round(el, 3), "verdict": "PASS" if verdict else "FAIL",
                        "stderr_bytes": len(err.encode()), "out": out, "err": err, "sig": sig})
        if not verdict:
            fails.append((case, rep, rc, terr, err[:200]))
        print(f"{'PASS' if verdict else 'FAIL'} {case} rep{rep} rc={rc} t={el:.2f}s stderr={len(err.encode())}B", flush=True)

(outdir / f"summary-{stamp}.json").write_text(json.dumps(summary, indent=1))
print(f"rows={len(summary)} fails={len(fails)}")
for f in fails:
    print("FAIL-DETAIL", f)
sys.exit(1 if fails else 0)
