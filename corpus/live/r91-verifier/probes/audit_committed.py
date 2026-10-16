#!/usr/bin/env python3
"""r91 verifier — static audit of the committed 77d2f7e bytes (no writes outside stdout).

Reads the frozen extraction at corpus/live/r91-verifier/tree and reports:
  * CASES tuple census (total + nav_lattice rows) via AST literal_eval
  * per-nav-row: script, flags, expected exit, signature, expected_errors,
    required_stderr (AST-extracted from the two .get(name, ()) dict literals)
  * scheduler-token absence inside every nav signature
  * STALE-line vs signature discrimination
  * r91 floor-gate presence
  * fixture print-site ordering: for each arm, the pinned fields and the
    declared tail fields (source line numbers)
"""
import ast
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[4]  # .../game-dev-2d-shokunin
TREE = ROOT / "corpus/live/r91-verifier/tree"
HARNESS = TREE / "corpus/fixtures/run_battery.py"
FIXTURE = TREE / "corpus/fixtures/nav_lattice.gd"

TAIL_TOKENS = [
    "settle", "iter", "ladder", "first_reach", "first_reach_sync",
    "walk_steps", "reached_at", "first_reachable", "iter_b", "link_iter",
    "gate", "chg_iter_same", "chg_iter_settled", "dis_same",
    "fwd_disabled_same", "seq_a", "seq_b", "vel_a", "vel_b", "sum_max",
]
# The emitted field forms (what the fixture actually prints). These are the
# delimiter-aware patterns whose presence inside a signature would be a real
# scheduler-field leak. Bare-token substring matches (n_a inside ...,
# iter inside pre_iter, settle inside settled) are reported separately.
TAIL_FIELD_FORMS = [t + "=" for t in TAIL_TOKENS] + ["chg_iter_same=", "chg_iter_settled="]
# deliberate pinned receipt/count/state tokens (boundary-confirmed invariants,
# not scheduler fields): warm_n_a=, n_a=, n_b=, pre_iter=, settled=
PINNED_COUNTS = ["warm_n_a=", "n_a=", "n_b=", "pre_iter=", "settled="]

src = HARNESS.read_text()
tree = ast.parse(src)

# --- CASES ---------------------------------------------------------------
cases = None
for node in tree.body:
    if isinstance(node, ast.Assign):
        for t in node.targets:
            if isinstance(t, ast.Name) and t.id == "CASES":
                cases = ast.literal_eval(node.value)
assert cases is not None, "CASES not found"
print(f"CASES total tuples: {len(cases)}")
nav = [(i, c) for i, c in enumerate(cases) if c[0].startswith("nav_lattice_")]
print(f"nav_lattice CASES: {len(nav)} at indices {[i for i, _ in nav]}")
print(f"first/last nav idx: {nav[0][0]} / {nav[-1][0]}  (total idx max {len(cases)-1})")
# adjacency: what is before/after
print("case before first nav:", cases[nav[0][0] - 1][0])
print("case after last nav:", cases[nav[-1][0] + 1][0])

# --- expected_errors / required_stderr dict literals ---------------------
def dict_literal_with_key(t, key):
    for node in ast.walk(t):
        if isinstance(node, ast.Dict):
            keys = [k.value if isinstance(k, ast.Constant) else None for k in node.keys]
            if key in keys:
                return ast.literal_eval(node)
    return None

expected_errors = dict_literal_with_key(tree, "nav_lattice_sync")
required_stderr = dict_literal_with_key(tree, "nav_lattice_teardown_crash")
print("\nexpected_errors nav entries:")
for k, v in (expected_errors or {}).items():
    if k.startswith("nav_lattice_"):
        print(f"  {k}: {v}")
print("required_stderr nav entries:")
for k, v in (required_stderr or {}).items():
    if k.startswith("nav_lattice_"):
        print(f"  {k}: {v}")

# --- floor gate ----------------------------------------------------------
gate_found = "r91_expected_errors_all_matched" in src
print(f"\nr91 floor gate present: {gate_found}")
gate_line = [i + 1 for i, l in enumerate(src.splitlines())
             if "r91_expected_errors_all_matched" in l]
print(f"gate source lines: {gate_line}")
prefix_line = [i + 1 for i, l in enumerate(src.splitlines())
               if 'startswith("nav_lattice_")' in l]
print(f"gate prefix predicate lines: {prefix_line}")

# --- per-row audit -------------------------------------------------------
# Token-boundary aware: a field form counts only when not preceded by a word
# character, so `pre_iter=`/`en_a=`/`dis_settled=` do not masquerade as the
# tail fields `iter=`/`n_a=`/`settled=`.
def find_fields(sig, forms):
    return [t for t in forms if re.search(rf"(?<![A-Za-z0-9_]){re.escape(t)}", sig)]

print("\nper-row audit:")
violations = []
substring_hits = []
for idx, c in nav:
    name, script, flags, expected_exit, sig = c[0], c[1], c[2], c[3], c[4]
    inside = [t for t in TAIL_TOKENS if re.search(rf"\b{t}\b", sig)]
    if inside:
        substring_hits.append((name, inside))
    leaked = find_fields(sig, TAIL_FIELD_FORMS)
    counts = find_fields(sig, PINNED_COUNTS)
    if leaked:
        violations.append((name, leaked))
    stale_ok = sig not in f"STALE nav_lattice {name.split('_')[-1]}"
    print(f"  [{idx}] {name}: script={script} flags={flags} exit={expected_exit} "
          f"sig_len={len(sig)} field_form_leaks={leaked or 'NONE'} "
          f"pinned_counts={counts or '-'} stale_discriminates={stale_ok}")

# --- fixture print-site ordering ----------------------------------------
fx = FIXTURE.read_text().splitlines()
print("\nfixture print sites (line: first 90 chars):")
for i, l in enumerate(fx):
    if "print(" in l or "STALE" in l:
        print(f"  {i+1}: {l.strip()[:90]}")

# --- declared pinned/tail field order per arm (textual check) ------------
print("\ntail-token print sites (line: token):")
for i, l in enumerate(fx):
    for t in TAIL_TOKENS:
        if re.search(rf'"\s*{t}=?"', l):
            print(f"  {i+1}: {t} :: {l.strip()[:70]}")

print("\nviolations (field-form leak inside signature):", violations or "none")
print("substring-only hits (false positives of bare-token matching):", substring_hits or "none")
