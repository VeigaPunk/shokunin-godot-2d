#!/usr/bin/env python3
"""r92 verifier — custody re-check of the author's COMMITTED fresh-rep receipts.

Independently re-classifies corpus/live/r92-author/fresh-reps/*.{out,err,rc}
(42 receipts, 14 arms x 3) with the production `classify_process` + the
committed envelope/required_stderr/stdout-anchor path — i.e. without trusting
the author's own verify_author.py.
"""
import ast
import hashlib
import pathlib
import sys

REPO = pathlib.Path("/home/vgpnk/Projects/shokunin/game-dev-2d-shokunin")
FIX = REPO / "corpus/live/r92-verifier/tree/corpus/fixtures/run_battery.py"
REPS = REPO / "corpus/live/r92-author/fresh-reps"

src = FIX.read_text()
tree = ast.parse(src)
ns = {}
for node in ast.walk(tree):
    if isinstance(node, ast.FunctionDef) and node.name == "classify_process":
        seg = ast.get_source_segment(src, node)
        print(f"classify_process segment sha256={hashlib.sha256(seg.encode()).hexdigest()}")
        exec("import re\n" + seg, ns)
classify = ns["classify_process"]
for node in ast.walk(tree):
    if isinstance(node, ast.Assign) and getattr(node.targets[0], "id", "") == "CASES":
        cases = node.value.elts
rows = {}
for elt in cases:
    t = ast.literal_eval(elt)
    if t[0].startswith("r92_"):
        rows[t[0]] = {"exit": t[3], "sig": t[4]}
exp_errors, req_stderr = {}, {}
for node in ast.walk(tree):
    if isinstance(node, ast.Dict):
        keys = [k.value for k in node.keys if isinstance(k, ast.Constant)]
        if "r92_tilemap_atlas" in keys and "nav_lattice_bake" in keys:
            for k, v in zip(node.keys, node.values):
                if isinstance(k, ast.Constant):
                    exp_errors[k.value] = ast.literal_eval(v)
        if "r92_tilemap_nullts_crash" in keys and "nav_lattice_teardown_crash" in keys:
            for k, v in zip(node.keys, node.values):
                if isinstance(k, ast.Constant):
                    req_stderr[k.value] = ast.literal_eval(v)

fails = n = 0
n_bare_load_bearing = 0
for case in sorted(rows):
    arm = case.removeprefix("r92_tilemap_")
    arm = "nullts" if arm == "nullts_crash" else arm
    sigs = rows[case]["sig"]
    sigs = sigs if isinstance(sigs, (tuple, list)) else (sigs,)
    ee = exp_errors.get(case, ())
    rs = req_stderr.get(case, ())
    for rep in (1, 2, 3):
        out = (REPS / f"{arm}.rep{rep}.out").read_text()
        err = (REPS / f"{arm}.rep{rep}.err").read_text()
        rc = int((REPS / f"{arm}.rep{rep}.rc").read_text().strip())
        merged = out + err
        passed = any(classify(rc, None, merged, rows[case]["exit"], s, ee) for s in sigs)
        if rs:
            passed = passed and all(f in err for f in rs) and any(s in out for s in sigs)
        bare = None
        if ee:
            bare = any(classify(rc, None, merged, rows[case]["exit"], s, ()) for s in sigs)
            if not bare:
                n_bare_load_bearing += 1
        n += 1
        if not passed:
            fails += 1
            print(f"FAIL {case} rep{rep} rc={rc} bare={bare}")
print(f"committed author receipts re-checked={n} fails={fails}")
print(f"allowlist-bearing receipts where the bare classifier rejects (load-bearing)={n_bare_load_bearing}/27")
sys.exit(1 if fails else 0)
