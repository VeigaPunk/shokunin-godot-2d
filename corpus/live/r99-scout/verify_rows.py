#!/usr/bin/env python3
"""r99-scout row verifier — classifies every author row with the PRODUCTION
`classify_process` extracted verbatim (AST) from corpus/fixtures/run_battery.py.

Each row is checked against every canonical rep receipt for its cell
(stdout+stderr merged exactly like run_battery's run_process does) and — when a
loadtest directory exists — against every loadtest rep too, so a row that would
flip verdict on any receipt is rejected.
"""
import ast
import hashlib
import pathlib

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


def receipts(case):
    cell = case[len("r99_audio_"):]
    for out in sorted((HERE / "runs").glob(f"r99_{cell}.rep*.out")):
        yield (out.name, out.read_text() + out.with_suffix(".err").read_text(),
               int(out.with_suffix(".rc").read_text().strip()))
    lt = HERE / "runs" / "loadtest"
    if lt.exists():
        for out in sorted(lt.glob(f"{cell}.rep*.out")):
            yield ("loadtest/" + out.name, out.read_text() + out.with_suffix(".err").read_text(),
                   int(out.with_suffix(".rc").read_text().strip()))


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
    print(f"{label} {checked - len(rejected)}/{checked} accepted rejected={rejected}")
    return rejected


r1 = check(ROWS, "ROWS")
r2 = check(ROWS_PREFIX, "ROWS_PREFIX")
print(f"classify_process segment sha256={seg_sha}")
pass
raise SystemExit(1 if (r1 or r2) else 0)
