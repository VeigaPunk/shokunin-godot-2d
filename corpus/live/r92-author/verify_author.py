#!/usr/bin/env python3
"""Verify r92 authored rows against fresh-rep receipts with the PRODUCTION
classify_process extracted verbatim (AST) from corpus/fixtures/run_battery.py.
Replicates execute()'s full path: rc + signature (str or envelope tuple) +
expected_errors + required_stderr + SCRIPT/Parse clauses."""
import ast, hashlib, pathlib, sys

REPO = pathlib.Path("/home/vgpnk/Projects/shokunin/game-dev-2d-shokunin")
FIX = REPO / "corpus" / "fixtures" / "run_battery.py"
REPS = REPO / "corpus" / "live" / "r92-author" / "fresh-reps"

src = FIX.read_text()
tree = ast.parse(src)
fn_src = None
for node in ast.walk(tree):
    if isinstance(node, ast.FunctionDef) and node.name == "classify_process":
        fn_src = ast.get_source_segment(src, node)
        break
seg_sha = hashlib.sha256(fn_src.encode()).hexdigest()
ns = {}
exec("import re\n" + fn_src, ns)
classify = ns["classify_process"]

rows = {}
for node in ast.walk(tree):
    if isinstance(node, ast.Assign) and getattr(node.targets[0], 'id', '') == 'CASES':
        for elt in node.value.elts:
            t = ast.literal_eval(elt)
            if t[0].startswith("r92_tilemap_"):
                rows[t[0]] = {"flags": t[2], "expected_exit": t[3], "signature": t[4]}

exp_errors, req_stderr = {}, {}
for node in ast.walk(tree):
    if isinstance(node, ast.Dict):
        keys = [k.value for k in node.keys if isinstance(k, ast.Constant)]
        if 'r92_tilemap_atlas' in keys:
            for k, v in zip(node.keys, node.values):
                if isinstance(k, ast.Constant) and k.value.startswith('r92_'):
                    exp_errors[k.value] = ast.literal_eval(v)
        if 'r92_tilemap_nullts_crash' in keys and 'nav_lattice_teardown_crash' in keys:
            for k, v in zip(node.keys, node.values):
                if isinstance(k, ast.Constant) and k.value == 'r92_tilemap_nullts_crash':
                    req_stderr[k.value] = ast.literal_eval(v)

CASE_TO_ARM = {name: name.removeprefix("r92_tilemap_") for name in rows}
CASE_TO_ARM["r92_tilemap_nullts_crash"] = "nullts"

results = []
for case, row in sorted(rows.items()):
    arm = CASE_TO_ARM[case]
    sigs = row["signature"] if isinstance(row["signature"], (tuple, list)) else (row["signature"],)
    ee = exp_errors.get(case, ())
    rs = req_stderr.get(case, ())
    for rep in (1, 2, 3):
        out = (REPS / f"{arm}.rep{rep}.out").read_text()
        err = (REPS / f"{arm}.rep{rep}.err").read_text()
        rc = int((REPS / f"{arm}.rep{rep}.rc").read_text().strip())
        merged = out + err
        passed = any(classify(rc, None, merged, row["expected_exit"], sig, ee)
                     for sig in sigs)
        if rs:
            passed = (passed
                      and all(f in err for f in rs)
                      and any(s in out for s in sigs))
        bare = None
        if ee:
            bare = any(classify(rc, None, merged, row["expected_exit"], sig, ())
                       for sig in sigs)
        results.append((case, rep, passed, bare, rc))
        flag = "OK" if passed else "FAIL"
        extra = f" bare={bare}" if bare is not None else ""
        print(f"{flag} {case} rep{rep} rc={rc}{extra}", flush=True)

n_fail = sum(1 for r in results if not r[2])
print(f"\nTOTAL rows={len(rows)} receipts={len(results)} fails={n_fail}")
print(f"classify_process segment sha256={seg_sha[:16]}")
sys.exit(1 if n_fail else 0)
