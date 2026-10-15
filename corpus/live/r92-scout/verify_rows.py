#!/usr/bin/env python3
"""r92-scout row verifier — classifies every author row with the PRODUCTION
`classify_process` extracted verbatim (AST) from corpus/fixtures/run_battery.py.

Each row is checked against every canonical rep receipt for its arm AND the
loadtest receipt (stdout+stderr merged exactly like run_process does), so a row
that would flip verdict on any rep is rejected.
"""
import ast
import hashlib
import pathlib
import sys

HERE = pathlib.Path(__file__).parent
FIXTURE = HERE.parent.parent / "fixtures" / "run_battery.py"

src = FIXTURE.read_text()
tree = ast.parse(src)
fn_src = None
for node in ast.walk(tree):
    if isinstance(node, ast.FunctionDef) and node.name == "classify_process":
        fn_src = ast.get_source_segment(src, node)
        break
assert fn_src, "classify_process not found"
seg_sha = hashlib.sha256(fn_src.encode()).hexdigest()

ns = {}
exec("import re\n" + fn_src, ns)
classify_process = ns["classify_process"]

rows_src = (HERE / "author-rows.py.txt").read_text()
rows_ns = {}
exec(rows_src, rows_ns)
ROWS = rows_ns["ROWS"]
ROWS_PREFIX = rows_ns["ROWS_PREFIX"]
EXPECTED = rows_ns["EXPECTED_ERRORS"]

CASE_TO_CELL = {
    "r92_tilemap_census": "tm_census",
    "r92_tilemap_atlas": "tm_atlas",
    "r92_tilemap_cells": "tm_cells",
    "r92_tilemap_custom": "tm_custom",
    "r92_tilemap_terrain": "tm_terrain",
    "r92_tilemap_pattern": "tm_pattern",
    "r92_tilemap_encoding": "tm_encoding",
    "r92_tilemap_fixinvalid": "tm_fixinvalid",
    "r92_tilemap_srcids": "tm_srcids",
    "r92_tilemap_physics": "tm_physics",
    "r92_tilemap_timing": "tm_timing",
    "r92_tilemap_quadrant": "tm_quadrant",
    "r92_tilemap_nav": "tm_nav",
}


def receipts():
    """canonical reps + loadtest reps, merged stdout+stderr like run_process."""
    for out in sorted((HERE / "runs").glob("r92_tm_*.rep*.out")):
        err = out.with_suffix(".err")
        rc = out.with_suffix(".rc")
        yield out.name, out.read_text() + (err.read_text() if err.exists() else ""), int(rc.read_text().strip())
    for out in sorted((HERE / "runs" / "loadtest").glob("r92_tm_*.rep*.out")):
        err = out.with_suffix(".err")
        rc = out.with_suffix(".rc")
        yield "loadtest/" + out.name, out.read_text() + (err.read_text() if err.exists() else ""), int(rc.read_text().strip())


def check(rows, label):
    rejected = []
    checked = 0
    for case, script, flags, expected_exit, sig in rows:
        cell = CASE_TO_CELL[case]
        allowed = EXPECTED.get(case, ())
        for name, output, code in receipts():
            base = name.split("/")[-1]
            if not base.startswith(f"r92_{cell}."):
                continue
            ok = classify_process(code, None, output, expected_exit, sig, allowed)
            checked += 1
            if not ok:
                rejected.append((case, name))
    print(f"[{label}] rows={len(rows)} receipts_checked={checked} rejected={rejected}")
    return rejected


rejected_full = check(ROWS, "ROWS(full-line, GATING)")
rejected_prefix = check(ROWS_PREFIX, "ROWS_PREFIX(census-tail-cut)")
print(f"classify_process segment sha256={seg_sha[:16]}")
sys.exit(1 if (rejected_full or rejected_prefix) else 0)
