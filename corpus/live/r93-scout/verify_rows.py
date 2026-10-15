#!/usr/bin/env python3
"""r93-scout row verifier — classifies every emitted author row with the
PRODUCTION `classify_process` extracted verbatim (AST) from
corpus/fixtures/run_battery.py.

Each row is checked against every canonical rep receipt for its arm plus every
loadtest rep receipt (stdout+stderr merged exactly like run_process does), so a
row that would flip verdict on any rep is rejected.
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
ROWS_FULL = rows_ns["ROWS_FULL"]
EXPECTED = rows_ns["EXPECTED_ERRORS"]

ARM_TO_CELL = {
    "census": "census", "tweenval": "tweenval", "tweenval_grid": "tweenval_grid",
    "tweenstep": "tweenstep", "tweenchain": "tweenchain", "tweenproc": "tweenproc",
    "animseek": "animseek", "animmethod": "animmethod", "animtrack": "animtrack",
    "animblend": "animblend", "animproc": "animproc",
}


def receipts():
    """canonical reps + loadtest reps, merged stdout+stderr like run_process."""
    for out in sorted((HERE / "runs").glob("r93_*.rep*.out")):
        err = out.with_suffix(".err")
        rc = out.with_suffix(".rc")
        yield out.name, out.read_text() + (err.read_text() if err.exists() else ""), int(rc.read_text().strip())
    for out in sorted((HERE / "runs" / "loadtest").glob("r93_*.rep*.out")):
        err = out.with_suffix(".err")
        rc = out.with_suffix(".rc")
        yield "loadtest/" + out.name, out.read_text() + (err.read_text() if err.exists() else ""), int(rc.read_text().strip())


def check(rows, label):
    rejected = []
    checked = 0
    for case, script, flags, expected_exit, sig in rows:
        arm = next(f.split("=", 1)[1] for f in flags if f.startswith("--arm="))
        cell = ARM_TO_CELL[arm]
        allowed = EXPECTED.get(case, ())
        for name, output, code in receipts():
            base = name.split("/")[-1]
            if not base.startswith(f"r93_{cell}."):
                continue
            ok = classify_process(code, None, output, expected_exit, sig, allowed)
            checked += 1
            if not ok:
                rejected.append((case, name))
    print(f"[{label}] rows={len(rows)} receipts_checked={checked} rejected={rejected}")
    return rejected


rejected_full = check(ROWS_FULL, "ROWS_FULL(full-line, informational)")
rejected = check(ROWS, "ROWS(recommended, GATING)")
print(f"classify_process segment sha256={seg_sha[:16]}")
print(f"full_line_rejections={len(rejected_full)} (expected: load-fragile mode counters)")
sys.exit(1 if rejected else 0)
