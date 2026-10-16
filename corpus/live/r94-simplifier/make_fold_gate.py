#!/usr/bin/env python3
"""r94-simplifier floor-gate loudness fold.

Creates `fold-gate/` = the committed fixture tree + one injected STALE r94
allowlist entry (`r94_particles_cpu_never`), which no r94 arm can ever emit
(all 19 rows are ERROR:-clean). Expected on a full battery run: the row still
PASSes, `dead_entry_count=1` names the injected entry,
`r94_expected_errors_all_matched=False` => `probe_error_clause_surface` FAIL
=> battery FAIL. Writes `fold-gate.diff` for the report.

Usage: python3 make_fold_gate.py
"""
import difflib
import shutil
from pathlib import Path

HERE = Path(__file__).resolve().parent
HARNESS = HERE / "committed-fixtures" / "run_battery.py"
PROJ = HERE / "proj"
GATE = HERE / "fold-gate"

ANCHOR = """                'r92_tilemap_physics': (
                    'ERROR: Parameter "found" is null.',
                ),
            }.get(name, ())
"""

INJECT = """                'r92_tilemap_physics': (
                    'ERROR: Parameter "found" is null.',
                ),
                # r94-simplifier dead-entry fold: a stale r94 allowlist entry
                # that no r94 arm can ever emit (all 19 rows are ERROR:-clean).
                # The row must still PASS; the r94 floor gate must flip.
                'r94_particles_cpu_never': (
                    'ERROR: r94-simplifier dead-entry fold probe (never emitted)',
                ),
            }.get(name, ())
"""


def main():
    src = HARNESS.read_text()
    assert ANCHOR in src, "anchor not found"
    folded = src.replace(ANCHOR, INJECT, 1)

    if GATE.exists():
        shutil.rmtree(GATE)
    GATE.mkdir(parents=True)
    for item in sorted(PROJ.iterdir()):
        if item.is_dir():
            shutil.copytree(item, GATE / item.name)
        else:
            shutil.copy2(item, GATE / item.name)
    (GATE / "run_battery.py").write_text(folded)

    diff = "".join(difflib.unified_diff(
        src.splitlines(keepends=True), folded.splitlines(keepends=True),
        fromfile="committed-fixtures/run_battery.py",
        tofile="fold-gate/run_battery.py"))
    (HERE / "fold-gate.diff").write_text(diff)
    print(diff)


if __name__ == "__main__":
    main()
