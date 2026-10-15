#!/usr/bin/env python3
"""r100-scout row verifier — classifies every author row with the PRODUCTION
`classify_process` extracted verbatim (AST) from corpus/fixtures/run_battery.py.

Each row is checked against every canonical rep receipt for its cell
(stdout+stderr merged exactly like run_battery's run_process does: stdout+stderr)
and — when the loadtest directory exists — against every loadtest rep too, so a
row that would flip verdict on any receipt is rejected.
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
EXPECTED = rows_ns.get("EXPECTED_ERRORS", {})


def receipts(cell):
    """canonical reps + loadtest reps for one cell, stdout+stderr merged."""
    for out in sorted((HERE / "runs").glob(f"r100_gui_{cell}.rep*.out")):
        err = out.with_suffix(".err")
        rc = out.with_suffix(".rc")
        yield out.name, out.read_text() + (err.read_text() if err.exists() else ""), int(rc.read_text().strip())
    lt = HERE / "runs" / "loadtest"
    if lt.exists():
        for out in sorted(lt.glob(f"r100_gui_{cell}.rep*.out")):
            err = out.with_suffix(".err")
            rc = out.with_suffix(".rc")
            yield ("loadtest/" + out.name,
                   out.read_text() + (err.read_text() if err.exists() else ""),
                   int(rc.read_text().strip()))


def check(rows, label):
    rejected = []
    checked = 0
    per_case = {}
    for case, script, flags, expected_exit, sig in rows:
        cell = case[len("r100_gui_"):]
        allowed = EXPECTED.get(case, ())
        n = 0
        for name, output, code in receipts(cell):
            ok = classify_process(code, None, output, expected_exit, sig, allowed)
            checked += 1
            n += 1
            if not ok:
                rejected.append((case, name))
        per_case[case] = n
    print(f"[{label}] rows={len(rows)} receipts_checked={checked} rejected={rejected}")
    return rejected


rejected_full = check(ROWS, "ROWS(full-line)")
rejected_prefix = check(ROWS_PREFIX, "ROWS_PREFIX(stable-prefix, GATING)")
print(f"classify_process segment sha256={seg_sha[:16]}")
print(f"full_line_rejections={len(rejected_full)}  prefix_rejections={len(rejected_prefix)}")
sys.exit(1 if rejected_prefix else 0)
