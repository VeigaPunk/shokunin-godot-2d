#!/usr/bin/env python3
"""r95 critic: harness mutants for the r95 floor gate.

base : frozen committed fixtures with CASES trimmed to 3 r95 rows (fast run).
dead : the same, plus one synthetic never-matching expected_errors entry on an
       r95 row -> the r95 floor gate must flip to False (liveness proof).
"""
import ast
import json
import shutil
from pathlib import Path

SEAT = Path("/home/vgpnk/Projects/shokunin/game-dev-2d-shokunin/corpus/live/r95-critic")
FROZEN = SEAT / "frozen" / "corpus" / "fixtures"
MUT = SEAT / "mutants"

KEEP = {"dss_lattice_order_core", "dss_lattice_point_cap", "dss_lattice_fresh",
        # the battery hard-requires these three records (process_evidence_rows[...])
        "save_process_writer", "save_process_reader", "save_process_missing"}


def cases_span(text):
    tree = ast.parse(text)
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign) and any(
                isinstance(t, ast.Name) and t.id == "CASES" for t in node.targets):
            return node.lineno, node.end_lineno
    raise SystemExit("no CASES")


def build(name, dead):
    dest = MUT / name / "fixtures"
    if dest.exists():
        shutil.rmtree(dest)
    shutil.copytree(FROZEN, dest)
    p = dest / "run_battery.py"
    text = p.read_text()
    tree = ast.parse(text)
    allcases = None
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign) and any(
                isinstance(t, ast.Name) and t.id == "CASES" for t in node.targets):
            allcases = ast.literal_eval(node.value)
    kept = [c for c in allcases if c[0] in KEEP]
    assert len(kept) == 6, [c[0] for c in kept]
    lo, hi = cases_span(text)
    lines = text.splitlines(keepends=True)
    new_block = "CASES = [\n" + "".join(f"    {c!r},\n" for c in kept) + "]\n"
    text = "".join(lines[:lo - 1]) + new_block + "".join(lines[hi:])
    if dead:
        old = '            expected_errors = {\n'
        assert text.count(old) == 1
        text = text.replace(
            old,
            old + '                "dss_lattice_order_core": ("ERROR: synthetic dead entry never emitted by this probe",),\n',
            1)
    p.write_text(text)
    (MUT / name / "mutation.json").write_text(json.dumps(
        {"name": name, "dead_entry": dead, "cases": [c[0] for c in kept]}, indent=1))
    print(f"built {name}: {len(kept)} cases, dead_entry={dead}")


if __name__ == "__main__":
    build("harness-base", False)
    build("harness-dead", True)
