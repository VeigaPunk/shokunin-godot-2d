#!/usr/bin/env python3
"""r92 verifier — fresh-arm receipts in the battery's exact launch shape.

Builds arms/proj/ from the FROZEN committed extraction (tree/corpus/fixtures)
with the same three scratch transforms run_battery.py applies, then launches
each r92 arm 3x with subprocess.run(capture_output=True) and no shell wrapper,
timeout 8s (the battery's non-export bound).
"""
import pathlib
import shutil
import subprocess
import sys

REPO = pathlib.Path("/home/vgpnk/Projects/shokunin/game-dev-2d-shokunin")
V = REPO / "corpus" / "live" / "r92-verifier"
SRC = V / "tree" / "corpus" / "fixtures"
PROJ = V / "arms" / "proj"
OUT = V / "arms"
GODOT = "godot"

ARMS = ["census", "atlas", "cells", "custom", "terrain", "pattern", "encoding",
        "fixinvalid", "srcids", "physics", "timing", "quadrant", "nav", "nullts"]

if PROJ.exists():
    shutil.rmtree(PROJ)
PROJ.mkdir(parents=True)
for item in sorted(SRC.iterdir()):
    if item.name == "run_battery.py" or item.name.startswith("."):
        continue
    if item.is_dir():
        shutil.copytree(item, PROJ / item.name)
    else:
        shutil.copy2(item, PROJ / item.name)
pf = PROJ / "project.godot"
pf.write_text(pf.read_text().replace('config/name="MechanicOneShotTest"',
                                     'config/name="MechanicOneShotTest-r92verifier"', 1))
shutil.copy2(PROJ / "controls" / "pickup.tscn", PROJ / "pickup.tscn")
chain = PROJ / "causal_chain.gd"
text = chain.read_text()
anchor = "    await process_frame\n    var old := current_scene"
assert anchor in text
chain.write_text(text.replace(anchor, "    await process_frame\n    await process_frame\n    var old := current_scene", 1))
print(f"proj built at {PROJ}")

n = int(sys.argv[1]) if len(sys.argv) > 1 else 3
only = sys.argv[2:] or ARMS
for arm in only:
    for rep in range(1, n + 1):
        cmd = [GODOT, "--headless", "--path", str(PROJ), "--script",
               "res://tilemap_lattice.gd", "--", f"--arm={arm}"]
        try:
            proc = subprocess.run(cmd, capture_output=True, text=True, timeout=8)
            rc, out, err = proc.returncode, proc.stdout, proc.stderr
        except subprocess.TimeoutExpired as exc:
            rc = None
            out = (exc.stdout or b"").decode(errors="replace") if isinstance(exc.stdout, bytes) else (exc.stdout or "")
            err = (exc.stderr or b"").decode(errors="replace") if isinstance(exc.stderr, bytes) else (exc.stderr or "")
        (OUT / f"{arm}.rep{rep}.out").write_text(out)
        (OUT / f"{arm}.rep{rep}.err").write_text(err)
        (OUT / f"{arm}.rep{rep}.rc").write_text(f"{rc}\n")
        print(f"rep{rep} {arm}: rc={rc} out_lines={len(out.splitlines())} err_lines={len(err.splitlines())}", flush=True)
print("done")
