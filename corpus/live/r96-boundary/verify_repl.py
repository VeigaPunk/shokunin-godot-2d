#!/usr/bin/env python3
"""r96-boundary — classifies the scout's 13 author rows against the boundary seat's
OWN replication receipts (runs/<batch>/scout_<cell>.rep*.{out,err,rc}) with the
production `classify_process` extracted verbatim (AST) from corpus/fixtures/run_battery.py.

This answers: do the 13 shipped rows still classify PASS under 16-hog load and
--fixed-fps 1/30/120, or does an attacked condition flip a row?

usage: python3 verify_repl.py
"""
import ast
import hashlib
import pathlib
import sys

HERE = pathlib.Path(__file__).parent
FIXTURE = HERE.parent.parent / "fixtures" / "run_battery.py"
SCOUT = HERE.parent / "r96-scout"
BATCHES = ["quiet", "load", "ff1", "ff30", "ff120"]

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
exec((SCOUT / "author-rows.py.txt").read_text(), rows_ns)
ROWS = rows_ns["ROWS"]
EXPECTED = rows_ns["EXPECTED_ERRORS"]

total = 0
rejected = []
for batch in BATCHES:
    d = HERE / "runs" / batch
    if not d.exists():
        continue
    n_b = 0
    for case, script, flags, expected_exit, sig in ROWS:
        cell = case[len("r96_scene_io_"):]
        allowed = EXPECTED.get(case, ())
        for out in sorted(d.glob(f"scout_{cell}.rep*.out")):
            err = out.with_suffix(".err")
            rc = out.with_suffix(".rc")
            output = out.read_text() + (err.read_text() if err.exists() else "")
            code = int(rc.read_text().strip())
            ok = classify_process(code, None, output, expected_exit, sig, allowed)
            total += 1
            n_b += 1
            if not ok:
                rejected.append((batch, case, out.name))
    print(f"[{batch}] receipts={n_b} rejected={sum(1 for r in rejected if r[0] == batch)}")
print(f"classify_process segment sha256={seg_sha[:16]}")
print(f"total_receipts={total} rejected={len(rejected)}")
for r in rejected[:40]:
    print("  REJECT", r)
sys.exit(1 if rejected else 0)
