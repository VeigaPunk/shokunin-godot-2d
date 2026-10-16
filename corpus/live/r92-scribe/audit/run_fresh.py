#!/usr/bin/env python3
"""r92-scribe fresh single-arm receipts in the battery's exact launch shape.

Mirrors run_process_streams: subprocess.run(capture_output=True, text=True)
with the same 25 s bound, no shell wrapper -> returncode -6 for the abort.
usage: run_fresh.py <arm> [<arm> ...]
"""
import shutil
import subprocess
import sys
from pathlib import Path

REPO = Path("/home/vgpnk/Projects/shokunin/game-dev-2d-shokunin")
FIX = REPO / "corpus" / "fixtures"
OUT = REPO / "corpus" / "live" / "r92-scribe" / "fresh"
PROJ = REPO / "corpus" / "live" / "r92-scribe" / "fresh-proj"

if not (PROJ / "project.godot").exists():
    PROJ.mkdir(parents=True, exist_ok=True)
    for item in FIX.iterdir():
        if item.name == ".godot":
            continue
        (shutil.copytree if item.is_dir() else shutil.copy2)(item, PROJ / item.name)

OUT.mkdir(parents=True, exist_ok=True)
rc = 0
for arm in sys.argv[1:]:
    cmd = ["godot", "--headless", "--path", str(PROJ), "--script",
           "res://tilemap_lattice.gd", "--", f"--arm={arm}"]
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=25)
        code, out, err = proc.returncode, proc.stdout, proc.stderr
    except subprocess.TimeoutExpired as exc:
        code, out, err = None, exc.stdout or "", exc.stderr or ""
        rc = 1
    (OUT / f"{arm}.rep1.out").write_text(out)
    (OUT / f"{arm}.rep1.err").write_text(err)
    (OUT / f"{arm}.rep1.rc").write_text(str(code))
    print(f"{arm}: rc={code} stdout_lines={len(out.splitlines())} "
          f"stderr_bytes={len(err)}")
sys.exit(rc)
