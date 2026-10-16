#!/usr/bin/env python3
"""r94 verifier — floor-gate load-bearing mutation (harness copy + dead r94 entry).

Builds corpus/live/r94-verifier/gate-probe/fixtures/ as a byte-copy of the
frozen committed fixtures, replaces its run_battery.py with a one-line mutant
that injects ONE dead `expected_errors` entry for r94_particles_cpu_never, and
prints the exact injected line. Run that mutant with
  --runs corpus/live/r94-verifier/gate-probe/runs
The `r94_expected_errors_all_matched` gate must flip to False while the r94 row
itself still PASSes. Writes only under corpus/live/r94-verifier/.
"""
import pathlib
import shutil

ROOT = pathlib.Path("/home/vgpnk/Projects/shokunin/game-dev-2d-shokunin")
FREEZE = ROOT / "corpus/live/r94-verifier/freeze/corpus/fixtures"
OUT = ROOT / "corpus/live/r94-verifier/gate-probe"
dest = OUT / "fixtures"
if dest.exists():
    shutil.rmtree(dest)
dest.mkdir(parents=True)
for item in FREEZE.iterdir():
    if item.name.startswith("."):
        continue
    if item.is_dir():
        shutil.copytree(item, dest / item.name)
    else:
        shutil.copy2(item, dest / item.name)

src = (dest / "run_battery.py").read_text()
anchor = '            expected_errors = {\n'
assert anchor in src, "expected_errors dict anchor missing"
inject = ('            expected_errors = {\n'
          '                "r94_particles_cpu_never": ("ERROR: r94-verifier injected dead entry (never emitted)",),\n')
mutant = src.replace(anchor, inject, 1)
(dest / "run_battery.py").write_text(mutant)
print("mutant harness:", dest / "run_battery.py")
print("injected line:", inject.splitlines()[1].strip())
print("line delta:", len(mutant.splitlines()) - len(src.splitlines()))
print("fixture sha256 still:", end=" ")
import hashlib
print(hashlib.sha256((dest / "particles_lattice.gd").read_bytes()).hexdigest())
