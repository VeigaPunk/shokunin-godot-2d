#!/usr/bin/env python3
"""r92 verifier — re-check fresh-arm receipts under the PRODUCTION classifier.

classify_process / classify_streams are AST-extracted verbatim from the
committed harness; the envelope + required_stderr + stdout-anchor logic mirrors
execute() (harness lines 1249-1266).
"""
import ast
import hashlib
import pathlib
import sys

REPO = pathlib.Path("/home/vgpnk/Projects/shokunin/game-dev-2d-shokunin")
V = REPO / "corpus" / "live" / "r92-verifier"
FIX = V / "tree" / "corpus" / "fixtures" / "run_battery.py"
ARMS = V / "arms"

src = FIX.read_text()
tree = ast.parse(src)
ns = {}
for node in ast.walk(tree):
    if isinstance(node, ast.FunctionDef) and node.name in ("classify_process", "classify_streams"):
        seg = ast.get_source_segment(src, node)
        print(f"{node.name} segment sha256={hashlib.sha256(seg.encode()).hexdigest()}")
        exec("import re\n" + seg, ns)
classify = ns["classify_process"]

cases = None
for node in ast.walk(tree):
    if isinstance(node, ast.Assign) and getattr(node.targets[0], "id", "") == "CASES":
        cases = node.value.elts
rows = {}
for elt in cases:
    t = ast.literal_eval(elt)
    if t[0].startswith("r92_"):
        rows[t[0]] = {"flags": t[2], "exit": t[3], "sig": t[4]}

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

fails = 0
n_rep = 0
for case in sorted(rows):
    arm = case.removeprefix("r92_tilemap_")
    arm = "nullts" if arm == "nullts_crash" else arm
    row = rows[case]
    sigs = row["sig"] if isinstance(row["sig"], (tuple, list)) else (row["sig"],)
    ee = exp_errors.get(case, ())
    rs = req_stderr.get(case, ())
    for rep in (1, 2, 3):
        out = (ARMS / f"{arm}.rep{rep}.out").read_text()
        err = (ARMS / f"{arm}.rep{rep}.err").read_text()
        raw_rc = (ARMS / f"{arm}.rep{rep}.rc").read_text().strip()
        rc = None if raw_rc == "None" else int(raw_rc)
        err_msg = "TIMEOUT after 8 seconds" if rc is None else None
        merged = out + err
        passed = any(classify(rc, err_msg, merged, row["exit"], sig, ee) for sig in sigs)
        bare = None
        if ee:
            bare = any(classify(rc, err_msg, merged, row["exit"], sig, ()) for sig in sigs)
        if rs:
            passed = passed and all(f in err for f in rs) and any(s in out for s in sigs)
        n_rep += 1
        if not passed:
            fails += 1
        extra = f" bare={bare}" if bare is not None else ""
        # which payload matched
        pay = [i for i, s in enumerate(sigs) if s in out]
        print(f"{'OK  ' if passed else 'FAIL'} {case} rep{rep} rc={rc} payloads_on_stdout={pay}{extra}")
print(f"\nTOTAL row-reps={n_rep} fails={fails}")
sys.exit(1 if fails else 0)
