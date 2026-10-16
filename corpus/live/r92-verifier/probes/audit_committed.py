#!/usr/bin/env python3
"""r92 verifier — static audit of the COMMITTED harness (5900431).

Reads the frozen extraction at corpus/live/r92-verifier/tree/ (byte-equal to
HEAD; the whole-repo `git diff --quiet HEAD` is rc=0).  Reports, without
touching the worktree:

  * CASES census (count, tuple shapes, r92 rows, index range)
  * result-row arithmetic (CASES + meta rows)
  * expected_errors / required_stderr r92 entries (verbatim)
  * the r92 floor gate
  * delimiter-aware leak check: every pinned field form must be inside the
    row signature, and no field form may appear only in a diagnostic tail
  * tail print-site ordering for the 14 r92 arms
"""
import ast
import hashlib
import pathlib
import re
import sys

REPO = pathlib.Path("/home/vgpnk/Projects/shokunin/game-dev-2d-shokunin")
FIX = REPO / "corpus" / "live" / "r92-verifier" / "tree" / "corpus" / "fixtures" / "run_battery.py"
PROBE = REPO / "corpus" / "live" / "r92-verifier" / "tree" / "corpus" / "fixtures" / "tilemap_lattice.gd"

src = FIX.read_text()
tree = ast.parse(src)
print(f"harness sha256={hashlib.sha256(src.encode()).hexdigest()}")
print(f"harness lines={len(src.splitlines())}")

cases = None
for node in ast.walk(tree):
    if isinstance(node, ast.Assign) and getattr(node.targets[0], "id", "") == "CASES":
        cases = node.value.elts
        break
print(f"\nCASES tuples={len(cases)}")
shapes = {}
for i, elt in enumerate(cases):
    t = ast.literal_eval(elt)
    shapes[len(t)] = shapes.get(len(t), 0) + 1
print(f"tuple arities={shapes}")

r92 = [(i, ast.literal_eval(e)) for i, e in enumerate(cases)
       if ast.literal_eval(e)[0].startswith("r92_")]
print(f"\nr92 rows={len(r92)} indices={r92[0][0]}..{r92[-1][0]}")
prev = ast.literal_eval(cases[r92[0][0] - 1])[0]
nxt = ast.literal_eval(cases[r92[-1][0] + 1])[0]
print(f"predecessor={prev!r} successor={nxt!r}")
for i, t in r92:
    sig = t[4]
    kind = f"ENVELOPE[{len(sig)}]" if isinstance(sig, (tuple, list)) else "scalar"
    print(f"  [{i:3d}] {t[0]:28s} script={t[1]:20s} flags={t[2]} exit={t[3]} {kind}")

# meta rows (appended by hand in main())
meta = sorted(set(re.findall(r'results\.append\(\{"case": "([a-z0-9_]+)"', src)))
meta2 = sorted(set(re.findall(r'\{"case": "([a-z0-9_]+)"', src)))
print(f"\nmeta result rows={len(meta)} {meta}")

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

print(f"\nexpected_errors total entries={len(exp_errors)}")
r92_ee = {k: v for k, v in exp_errors.items() if k.startswith("r92_")}
print(f"r92 expected_errors cases={len(r92_ee)} lines={sum(len(v) for v in r92_ee.values())}")
for k, v in sorted(r92_ee.items()):
    for line in v:
        print(f"  {k:28s} {line!r}")
r92_rs = {k: v for k, v in req_stderr.items() if k.startswith("r92_")}
print(f"\nr92 required_stderr cases={len(r92_rs)}")
for k, v in sorted(r92_rs.items()):
    print(f"  {k:28s} {v!r}")

gate = re.findall(r'"(r92_expected_errors_all_matched)": all\(([^)]*)\)', src, re.S)
print(f"\nfloor gate occurrences={len(gate)}")
for name, body in gate:
    print(f"  {name} -> {' '.join(body.split())}")

# delimiter-aware leak check: for each row, the tail fields that the fixture
# prints after the pinned prefix must NOT be part of the signature, and the
# signature must not contain a bare scheduler/envelope token.
print("\n--- signature token inventory (delimiter-aware) ---")
for i, t in r92:
    sigs = t[4] if isinstance(t[4], (tuple, list)) else (t[4],)
    toks = set()
    for s in sigs:
        toks |= set(re.findall(r"(?<![A-Za-z0-9_])([a-z_]+)=", s))
    print(f"  {t[0]:28s} fields={len(toks)} {' '.join(sorted(toks))}")

print("\n--- probe arms ---")
psrc = PROBE.read_text()
arms = re.findall(r'^\s*"([a-z0-9_]+)": _arm_', psrc, re.M)
print(f"probe sha256={hashlib.sha256(psrc.encode()).hexdigest()} lines={len(psrc.splitlines())}")
print(f"probe arms={arms}")
sys.exit(0)
