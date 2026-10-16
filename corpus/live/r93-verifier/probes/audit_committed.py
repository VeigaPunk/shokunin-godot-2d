#!/usr/bin/env python3
"""r93 verifier — static audit of the COMMITTED harness (4b75151).

Reads the frozen extraction at corpus/live/r93-verifier/freeze/x/ (byte-equal
to HEAD; whole-repo `git diff --quiet HEAD` rc=0 at freeze time). Reports,
without touching the worktree:

  * CASES census (count, tuple arities, r93 rows, index range, slot)
  * result-row arithmetic (CASES + meta rows)
  * expected_errors / required_stderr r93 entries (must be zero)
  * the r93 floor gate (prefix coverage)
  * delimiter-aware signature token inventory for the 23 r93 rows
  * fixture arm lists + fixture sha256s
  * classify_process source-segment sha256 (r89–r92 pinned 749fa0607e7707e6)
"""
import ast
import hashlib
import pathlib
import re
import sys

REPO = pathlib.Path("/home/vgpnk/Projects/shokunin/game-dev-2d-shokunin")
ROOT = REPO / "corpus" / "live" / "r93-verifier" / "freeze" / "x" / "corpus" / "fixtures"
FIX = ROOT / "run_battery.py"
PROBES = {"anim_lattice.gd": ROOT / "anim_lattice.gd", "r93b_anim.gd": ROOT / "r93b_anim.gd"}

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
for elt in cases:
    t = ast.literal_eval(elt)
    shapes[len(t)] = shapes.get(len(t), 0) + 1
print(f"tuple arities={shapes}")

r93 = [(i, ast.literal_eval(e)) for i, e in enumerate(cases)
       if ast.literal_eval(e)[0].startswith("r93_")]
print(f"\nr93 rows={len(r93)} indices={r93[0][0]}..{r93[-1][0]}")
prev = ast.literal_eval(cases[r93[0][0] - 1])[0]
nxt = ast.literal_eval(cases[r93[-1][0] + 1])[0]
print(f"predecessor={prev!r} successor={nxt!r}")
for i, t in r93:
    sig = t[4]
    kind = f"ENVELOPE[{len(sig)}]" if isinstance(sig, (tuple, list)) else "scalar"
    print(f"  [{i:3d}] {t[0]:36s} script={t[1]:18s} flags={t[2]} exit={t[3]} {kind}")

# meta rows (appended by hand in main())
meta = sorted(set(re.findall(r'results\.append\(\{"case": "([a-z0-9_]+)"', src)))
print(f"\nmeta result rows={len(meta)} {meta}")
print(f"row arithmetic: CASES {len(cases)} + meta {len(meta)} = {len(cases) + len(meta)}")

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

print(f"\nexpected_errors total cases={len(exp_errors)} entries={sum(len(v) for v in exp_errors.values())}")
r93_ee = {k: v for k, v in exp_errors.items() if k.startswith("r93_")}
print(f"r93 expected_errors cases={len(r93_ee)} lines={sum(len(v) for v in r93_ee.values())}")
for k, v in sorted(r93_ee.items()):
    for line in v:
        print(f"  {k:36s} {line!r}")
r93_rs = {k: v for k, v in req_stderr.items() if k.startswith("r93_")}
print(f"r93 required_stderr cases={len(r93_rs)}")

gate = re.findall(r'"(r93_expected_errors_all_matched)": all\(([^)]*)\)', src, re.S)
print(f"\nfloor gate occurrences={len(gate)}")
for name, body in gate:
    print(f"  {name} -> {' '.join(body.split())}")

print("\n--- signature token inventory (delimiter-aware) ---")
for i, t in r93:
    sigs = t[4] if isinstance(t[4], (tuple, list)) else (t[4],)
    toks = set()
    for s in sigs:
        toks |= set(re.findall(r"(?<![A-Za-z0-9_])([a-z_0-9]+)=", s))
    print(f"  {t[0]:36s} fields={len(toks)} {' '.join(sorted(toks))}")

print("\n--- probes ---")
for name, path in PROBES.items():
    psrc = path.read_text()
    arms = re.findall(r'^\s*"([a-z0-9_]+)": _arm_', psrc, re.M)
    print(f"{name}: sha256={hashlib.sha256(psrc.encode()).hexdigest()} lines={len(psrc.splitlines())} arms={arms}")

seg = None
for node in ast.walk(tree):
    if isinstance(node, ast.FunctionDef) and node.name == "classify_process":
        seg = ast.get_source_segment(src, node)
        break
if seg is None:
    print("\nclassify_process: NOT FOUND")
    sys.exit(1)
print(f"\nclassify_process segment sha256={hashlib.sha256(seg.encode()).hexdigest()[:16]} "
      f"(bytes={len(seg.encode())}, lines={len(seg.splitlines())})")
sys.exit(0)
