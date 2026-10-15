#!/usr/bin/env python3
"""r96-scout row verifier — classifies every author row with the PRODUCTION
`classify_process` extracted verbatim (AST) from corpus/fixtures/run_battery.py.

Each row is checked against every canonical rep receipt for its cell (stdout+stderr
merged exactly like run_battery's run_process does) and against every loadtest rep,
so a row that would flip verdict on any receipt is rejected.
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

rows_ns = {}
exec((HERE / "author-rows.py.txt").read_text(), rows_ns)
ROWS = rows_ns["ROWS"]
ROWS_PREFIX = rows_ns["ROWS_PREFIX"]
EXPECTED = rows_ns["EXPECTED_ERRORS"]


def receipts(case):
    """canonical reps + loadtest reps for one cell, stdout+stderr merged."""
    cell = case[len("r96_scene_io_"):]
    for out in sorted((HERE / "runs").glob(f"r96_{cell}.rep*.out")):
        err = out.with_suffix(".err")
        rc = out.with_suffix(".rc")
        yield out.name, out.read_text() + (err.read_text() if err.exists() else ""), int(rc.read_text().strip())
    lt = HERE / "runs" / "loadtest"
    if lt.exists():
        for out in sorted(lt.glob(f"{cell}.rep*.out")):
            err = out.with_suffix(".err")
            rc = out.with_suffix(".rc")
            yield ("loadtest/" + out.name, out.read_text() + (err.read_text() if err.exists() else ""),
                   int(rc.read_text().strip()))


def check(rows, label):
    rejected = []
    checked = 0
    for case, script, flags, expected_exit, sig in rows:
        allowed = EXPECTED.get(case, ())
        for name, output, code in receipts(case):
            ok = classify_process(code, None, output, expected_exit, sig, allowed)
            checked += 1
            if not ok:
                rejected.append((case, name))
    print(f"[{label}] rows={len(rows)} receipts_checked={checked} rejected={rejected}")
    return rejected


rejected_full = check(ROWS, "ROWS(full-line)")
rejected_prefix = check(ROWS_PREFIX, "ROWS_PREFIX(census-prefix)")
print(f"classify_process segment sha256={seg_sha[:16]}")
print(f"full_line_rejections={len(rejected_full)}  prefix_rejections={len(rejected_prefix)}")
sys.exit(1 if rejected_prefix or rejected_full else 0)
