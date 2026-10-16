#!/usr/bin/env python3
"""Build a gate-mutant harness: one dead r95 allowlist entry injected.

The frozen committed harness with a single injected `expected_errors` entry
for `dss_lattice_census` naming a diagnostic that can never be emitted.
Expected: r95_expected_errors_all_matched == False, dead_entry_count 3,
the row itself still PASSes, every other round gate stays True.
"""
import difflib
import shutil
import sys
from pathlib import Path

FIX = Path(sys.argv[1])
DEST = Path(sys.argv[2])

if DEST.exists():
    shutil.rmtree(DEST)
shutil.copytree(FIX, DEST)
src = (DEST / "run_battery.py").read_text()
anchor = "        if passed is None:\n            expected_errors = {\n"
assert anchor in src, "anchor not found"
inject = (anchor +
          '                "dss_lattice_census": ("ERROR: r95-verifier dead entry '
          'that can never be emitted",),\n')
mutant = src.replace(anchor, inject, 1)
assert mutant != src
(DEST / "run_battery.py").write_text(mutant)
diff = difflib.unified_diff(src.splitlines(keepends=True), mutant.splitlines(keepends=True),
                            fromfile="frozen/run_battery.py", tofile="gate-mutant/run_battery.py")
print("mutant built at", DEST)
print("".join(diff))
