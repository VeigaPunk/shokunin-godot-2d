#!/usr/bin/env python3
"""r101-ver12 mutation matrix — drives ver12_census_check.py through every
state the r101 row landing can take. All mutants are applied IN MEMORY by the
checker (no battery copies, no writes outside stdout): this host's /tmp is a
quota-bound tmpfs shared with sibling swarms (Errno 122 observed twice), so the
matrix must not depend on scratch space.

modes (expected verdict for family `export_prod`):
  healthy      row + dict entry + gate + integrity prefix        PASS
  no_gate      as healthy minus the r101 gate                    FAIL gate_missing
  no_integrity as healthy minus the integrity prefix              FAIL integrity_unpinned
  drop_row     row dropped, dict entry kept                      FAIL rows_missing,dict_entry_orphan
  rename_row   row renamed out of the family, entry kept         FAIL rows_missing,dict_entry_orphan
  orphan_file  extra unreferenced export_prod fixture            FAIL fixture_file_unreferenced
  missing_file planted row's fixture file absent                 FAIL fixture_file_missing
  shadow_api   row + entry renamed to r100b_*, r101 gate useless  FAIL row_under_foreign_prefix

Usage: python3 ver12_plant.py [--battery PATH] [--fixtures DIR] [--modes all]
"""
import argparse
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
CHECKER = HERE / "ver12_census_check.py"
REPO = HERE.parents[2]
BATTERY = REPO / "corpus" / "fixtures" / "run_battery.py"

BASE = ["--plant", "export_prod", "--plant-gate", "--plant-integrity"]
MODES = {
    "healthy": (BASE, False),
    "no_gate": (["--plant", "export_prod", "--plant-integrity"], True),
    "no_integrity": (["--plant", "export_prod", "--plant-gate"], True),
    "drop_row": (BASE + ["--drop-case", "export_prod_s01"], True),
    "rename_row": (BASE + ["--rename-case", "export_prod_s01=seq_full_s01"], True),
    "orphan_file": (BASE + ["--orphan-fixture", "export_prod_s99.gd"], True),
    "missing_file": (BASE + ["--no-fixture", "export_prod_s01.gd"], True),
    "shadow_api": (BASE + ["--rename-case", "export_prod_s01=r100b_shadow01",
                           "--rename-entry", "export_prod_s01=r100b_shadow01"], True),
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--battery", type=Path, default=BATTERY)
    ap.add_argument("--fixtures", type=Path, default=None)
    ap.add_argument("--modes", default="all")
    args = ap.parse_args()
    # Isolate the matrix from sibling fixtures landing concurrently: the
    # planted family must be judged on its own, not on files another seat has
    # dropped into corpus/fixtures ahead of its CASES rows. mkdir only — no
    # file writes, so the Arc/quota-bound tmpfs is not touched.
    fixtures = args.fixtures
    if fixtures is None:
        fixtures = Path("/tmp/r101-VER12/empty-fixtures")
        fixtures.mkdir(parents=True, exist_ok=True)
    modes = list(MODES) if args.modes == "all" else args.modes.split(",")
    unexpected = 0
    for mode in modes:
        flags, expect_fail = MODES[mode]
        cmd = [sys.executable, str(CHECKER), "--battery", str(args.battery),
               "--fixtures", str(fixtures)]
        cmd += flags
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        fam = next((ln for ln in proc.stdout.splitlines()
                    if ln.startswith("family=export_prod")), "NO_FAMILY_LINE")
        ok = (proc.returncode != 0) == expect_fail
        unexpected += 0 if ok else 1
        print(f"mode={mode} exit={proc.returncode} expected_fail={expect_fail} "
              f"{'OK' if ok else 'UNEXPECTED'} {fam}")
        if not ok and proc.stderr:
            print("  stderr=" + proc.stderr.strip().splitlines()[-1][:200])
    print(f"plant_modes={len(modes)} unexpected={unexpected}")
    sys.exit(0 if unexpected == 0 else 1)


if __name__ == "__main__":
    main()
