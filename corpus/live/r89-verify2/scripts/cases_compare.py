#!/usr/bin/env python3
# r89-verifier2: CASES tuple comparison, pre-fold 8cea888 vs folded 53a0be7.
# Extracts every CASES row whose name starts with geo2d_lattice_ / input89_edges_
# (r89 family, 20 rows) or r90_lattice_ (r90 family, 12 rows) from each
# run_battery.py via AST, then compares the full literal tuples byte-for-byte.
import ast
import json
import subprocess
import sys

REPO = "/home/vgpnk/Projects/shokunin/game-dev-2d-shokunin"
FOLDED = REPO + "/corpus/live/r89-verify2/tree/corpus/fixtures/run_battery.py"


def cases_from_source(src):
    tree = ast.parse(src)
    cases = None
    for node in tree.body:
        if isinstance(node, ast.Assign):
            for t in node.targets:
                if isinstance(t, ast.Name) and t.id == "CASES":
                    cases = node.value
    assert cases is not None, "CASES not found"
    out = {}
    for elt in cases.elts:
        row = ast.literal_eval(elt)
        out[row[0]] = row
    return out


pre = subprocess.run(
    ["git", "-C", REPO, "show", "8cea888:corpus/fixtures/run_battery.py"],
    capture_output=True, text=True, check=True).stdout
# r90 rows were introduced by ee20575 (r90 author — the fold's declared base
# HEAD); 8cea888 predates them. r90 baseline is therefore ee20575.
r90base = subprocess.run(
    ["git", "-C", REPO, "show", "ee20575:corpus/fixtures/run_battery.py"],
    capture_output=True, text=True, check=True).stdout
post = open(FOLDED).read()

pre_cases = cases_from_source(pre)
r90_cases = cases_from_source(r90base)
post_cases = cases_from_source(post)

r89 = sorted(n for n in post_cases if n.startswith(("geo2d_lattice_", "input89_edges_")))
r90 = sorted(n for n in post_cases if n.startswith("r90_lattice_"))
pre_r89 = sorted(n for n in pre_cases if n.startswith(("geo2d_lattice_", "input89_edges_")))
pre_r90 = sorted(n for n in r90_cases if n.startswith("r90_lattice_"))

result = {
    "r89_rows_post": len(r89), "r89_rows_pre": len(pre_r89),
    "r90_rows_post": len(r90), "r90_rows_pre": len(pre_r90),
    "r89_missing_in_pre": [n for n in r89 if n not in pre_cases],
    "r89_dropped_in_post": [n for n in pre_r89 if n not in post_cases],
    "r90_missing_in_pre": [n for n in r90 if n not in r90_cases],
    "r90_dropped_in_post": [n for n in pre_r90 if n not in post_cases],
    "r89_mismatches": [], "r90_mismatches": [],
    "total_cases_pre": len(pre_cases), "total_cases_r90base": len(r90_cases),
    "total_cases_post": len(post_cases),
}
for n in r89:
    if n in pre_cases and pre_cases[n] != post_cases[n]:
        result["r89_mismatches"].append(n)
for n in r90:
    if n in r90_cases and r90_cases[n] != post_cases[n]:
        result["r90_mismatches"].append(n)

# whole-CASES sanity: which rows differ at all ee20575 -> 53a0be7?
result["all_diff_rows_vs_ee20575"] = sorted(
    n for n in set(r90_cases) | set(post_cases)
    if r90_cases.get(n) != post_cases.get(n))
result["ok"] = (
    not result["r89_mismatches"] and not result["r90_mismatches"]
    and not result["r89_missing_in_pre"] and not result["r89_dropped_in_post"]
    and not result["r90_missing_in_pre"] and not result["r90_dropped_in_post"])
print(json.dumps(result, indent=2))
sys.exit(0 if result["ok"] else 1)
