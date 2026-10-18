#!/usr/bin/env python3
"""r102-S2: AST-extract CASES rows + expected_errors + required_stderr for the
two fixtures this seat owns (stree_lattice.gd, scene_io_lattice.gd) from
corpus/fixtures/run_battery.py. NEVER executes the battery (hard rule 1)."""
import ast
import json
import sys

SRC = sys.argv[1] if len(sys.argv) > 1 else "corpus/fixtures/run_battery.py"
OUT = sys.argv[2] if len(sys.argv) > 2 else "/var/tmp/r102-S2/rows.json"
SCRIPTS = {"stree_lattice.gd", "scene_io_lattice.gd"}

tree = ast.parse(open(SRC).read())

cases = None
exp_errors = {}
req_stderr = {}
for node in ast.walk(tree):
    if isinstance(node, ast.Assign):
        for t in node.targets:
            if isinstance(t, ast.Name) and t.id == "CASES":
                cases = ast.literal_eval(node.value)
            if isinstance(t, ast.Name) and t.id == "expected_errors":
                v = node.value
                # shape: { ... }.get(name, ())
                while isinstance(v, ast.Call):
                    v = v.func.value
                exp_errors = ast.literal_eval(v)
            if isinstance(t, ast.Name) and t.id == "required_stderr":
                v = node.value
                while isinstance(v, ast.Call):
                    v = v.func.value
                req_stderr = ast.literal_eval(v)

assert cases is not None, "CASES not found"
rows = []
for i, (name, script, flags, expected_exit, evidence) in enumerate(cases):
    if script in SCRIPTS:
        rows.append({
            "index": i,
            "name": name,
            "script": script,
            "flags": list(flags),
            "expected_exit": expected_exit,
            "evidence": evidence,
            "expected_errors": list(exp_errors.get(name, ())),
            "required_stderr": list(req_stderr.get(name, ())),
        })
json.dump(rows, open(OUT, "w"), indent=1)
print(f"CASES total={len(cases)}")
for r in rows:
    print(f"{r['index']:>4} {r['name']:<32} {r['script']:<22} {' '.join(r['flags']):<18} "
          f"exp={r['expected_exit']} errs={len(r['expected_errors'])} reqstderr={len(r['required_stderr'])}")
print(f"wrote {OUT} rows={len(rows)}")
