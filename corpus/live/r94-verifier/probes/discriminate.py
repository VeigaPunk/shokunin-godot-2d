#!/usr/bin/env python3
"""r94 verifier — discrimination: would a broken law actually fail the row?

For each r94 row, take a fresh/committed receipt that classifies PASS, mutate
one pinned token at a time in the observed output, and re-classify with the
PRODUCTION classify_process. Every mutation inside a pin must reject; mutations
of the deliberately unpinned ` | ` tail must be admitted (documented controls).

Also: global rejection axes (rc flip, injected ERROR line, injected SCRIPT
ERROR line) for every row.
"""
import ast
import hashlib
import json
import pathlib
import re
import sys

ROOT = pathlib.Path("/home/vgpnk/Projects/shokunin/game-dev-2d-shokunin")
FREEZE = ROOT / "corpus/live/r94-verifier/freeze/corpus/fixtures"
OUTDIR = ROOT / "corpus/live/r94-verifier"

src = (FREEZE / "run_battery.py").read_text()
tree = ast.parse(src)
fn_src = None
for node in ast.walk(tree):
    if isinstance(node, ast.FunctionDef) and node.name == "classify_process":
        fn_src = ast.get_source_segment(src, node)
        break
ns = {}
exec("import re\n" + fn_src, ns)
classify_process = ns["classify_process"]

import importlib.util
spec = importlib.util.spec_from_file_location("frozen_harness", FREEZE / "run_battery.py")
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
r94 = [c for c in mod.CASES if c[0].startswith("r94_")]

# gather one PASS receipt per row: prefer fresh arms, else author battery runs
receipts = {}
for out in sorted((OUTDIR / "arms").glob("r94_particles_*.rep1.out")):
    case = out.name.split(".rep1.out")[0]
    receipts[case] = out.read_text()
for vj in sorted((ROOT / "corpus/live/runs").glob("20261016T*/verdicts.json")):
    j = json.loads(vj.read_text())
    for r in j.get("results", []):
        if r["case"].startswith("r94_") and r["case"] not in receipts:
            receipts[r["case"]] = "\n".join(r.get("output", [])) + "\n"

TOKEN = re.compile(r"(?P<name>[A-Za-z_][A-Za-z0-9_]*)=(?P<val>true|false|[-+]?\d+(?:\.\d+)?)")

total_mut = 0
rejected = 0
admitted = []
admissions_detail = []
global_axes = {"rc_flip": 0, "injected_error": 0, "injected_script_error": 0}
global_total = 0
tail_admitted = 0
tail_total = 0

for case, script, flags, expected_exit, sig in r94:
    output = receipts.get(case)
    if output is None:
        print(f"MISSING RECEIPT {case}")
        continue
    assert classify_process(0, None, output, expected_exit, sig, ()), f"baseline not PASS: {case}"
    # pinned region = the signature itself; tail = observed line minus signature
    line = next(l for l in output.splitlines() if sig in l)
    tail = line.split(sig, 1)[1] if sig in line else ""
    toks = list(TOKEN.finditer(sig))
    # sample tokens: all booleans up to 16, numerics up to 8, evenly spaced if more
    bools = [m for m in toks if m.group("val") in ("true", "false")]
    nums = [m for m in toks if m.group("val") not in ("true", "false")]
    def sample(lst, k):
        if len(lst) <= k:
            return lst
        step = len(lst) / k
        return [lst[int(i * step)] for i in range(k)]
    chosen = sample(bools, 16) + sample(nums, 8)
    for m in chosen:
        name, val = m.group("name"), m.group("val")
        if val in ("true", "false"):
            new = "false" if val == "true" else "true"
        elif "." in val:
            new = val[:-1] + ("9" if val[-1] != "9" else "1")
        else:
            new = str(int(val) + 1)
        mutated = output.replace(f"{name}={val}", f"{name}={new}", 1)
        if mutated == output:
            continue
        total_mut += 1
        ok = classify_process(0, None, mutated, expected_exit, sig, ())
        if ok:
            admitted.append((case, f"{name}={val}->{new}"))
        else:
            rejected += 1
    # tail controls: mutate an unpinned tail token (expect admission)
    if tail:
        for m in list(TOKEN.finditer(tail))[:2]:
            name, val = m.group("name"), m.group("val")
            if val in ("true", "false"):
                new = "false" if val == "true" else "true"
            elif "." in val:
                new = val[:-1] + ("9" if val[-1] != "9" else "1")
            else:
                new = str(int(val) + 7)
            mutated = output.replace(f"{name}={val}", f"{name}={new}", 1)
            if mutated == output:
                continue
            tail_total += 1
            ok = classify_process(0, None, mutated, expected_exit, sig, ())
            if ok:
                tail_admitted += 1
            else:
                admissions_detail.append((case, f"TAIL-REJECTED {name}={val}->{new}"))
    # global axes
    global_total += 3
    bad_rc = expected_exit + 1 if expected_exit is not None else 1
    if not classify_process(bad_rc, None, output, expected_exit, sig, ()):
        global_axes["rc_flip"] += 1
    if not classify_process(0, None, output + "\nERROR: unrelated injected diagnostic\n", expected_exit, sig, ()):
        global_axes["injected_error"] += 1
    if not classify_process(0, None, output + "\nSCRIPT ERROR: injected\n", expected_exit, sig, ()):
        global_axes["injected_script_error"] += 1

print(f"pinned-token mutations: {total_mut}, rejected: {rejected}, admitted: {len(admitted)}")
for a in admitted:
    print("  ADMITTED (inside pin):", a)
print(f"tail controls: {tail_total}, admitted: {tail_admitted}, rejected: {tail_total - tail_admitted}")
for a in admissions_detail:
    print("  ", a)
print(f"global axes: {global_axes} of {global_total}")
print(f"classify_process sha256 = {hashlib.sha256(fn_src.encode()).hexdigest()[:16]}")
sys.exit(1 if (admitted or admissions_detail or rejected != total_mut or
               any(v != global_total // 3 for v in global_axes.values())) else 0)
