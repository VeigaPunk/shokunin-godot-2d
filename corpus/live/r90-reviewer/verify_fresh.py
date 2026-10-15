#!/usr/bin/env python3
"""r90-reviewer: independent classification of fresh receipts against the
committed r90 pins, using the production classifier AST-extracted from
ee20575:corpus/fixtures/run_battery.py (segment sha 749fa060…)."""
import ast, hashlib, subprocess, sys, glob, os
from collections import defaultdict

REPO = "/home/vgpnk/Projects/shokunin/game-dev-2d-shokunin"

def committed(path):
    return subprocess.run(["git", "show", f"ee20575:{path}"], cwd=REPO,
                          capture_output=True, text=True, check=True).stdout

src = committed("corpus/fixtures/run_battery.py")
tree = ast.parse(src)
fn = next(n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef) and n.name == "classify_process")
seg = ast.get_source_segment(src, fn)
print("classifier segment sha256:", hashlib.sha256(seg.encode()).hexdigest())
ns = {}
exec(seg, ns)
classify_process = ns["classify_process"]

# expected_errors for r90 rows, straight from the committed dict literal
expected = {}
for n in ast.walk(tree):
    if isinstance(n, ast.Dict):
        keys = [getattr(k, "value", None) for k in n.keys]
        if "r90_lattice_impedge" in keys:
            for k, v in zip(n.keys, n.values):
                if getattr(k, "value", "").startswith("r90_"):
                    expected[k.value] = tuple(ast.literal_eval(v))
print("r90 expected_errors:", expected)

cases = {}
for n in tree.body:
    if isinstance(n, ast.Assign) and getattr(n.targets[0], "id", None) == "CASES":
        for row in ast.literal_eval(n.value):
            if row[0].startswith("r90_"):
                cases[row[0]] = row
print("r90 rows:", len(cases))

runs = sys.argv[1] if len(sys.argv) > 1 else os.path.join(REPO, "corpus/live/r90-reviewer/runs")
fails = 0
uniq_out = defaultdict(set); uniq_err = defaultdict(set)
pin_match = {}
for name, row in cases.items():
    script, flags, rc, sig = row[1:]
    reps = sorted(glob.glob(os.path.join(runs, f"{name.split('r90_lattice_')[1]}.rep*.out")))
    reps = [r[:-4] for r in reps]
    verdicts = []
    for r in reps:
        out = open(r + ".out").read()
        err = open(r + ".err").read()
        code = int(open(r + ".rc").read().strip())
        merged = out + err
        ok = classify_process(code, None, merged, rc, sig, expected.get(name, ()))
        verdicts.append(ok)
        uniq_out[name].add(hashlib.sha256(out.encode()).hexdigest())
        uniq_err[name].add(hashlib.sha256(err.encode()).hexdigest())
        if not ok:
            fails += 1
            print(f"  FAIL {name} {os.path.basename(r)} rc={code}")
            # why
            if sig not in merged: print("    signature absent")
            unrelated = [l for l in merged.splitlines() if "ERROR:" in l
                         and not any(l.strip() == a for a in expected.get(name, ()))]
            if unrelated: print("    unrelated:", unrelated[:3])
    pin_match[name] = all(verdicts)
    print(f"{'PASS' if all(verdicts) else 'FAIL'} {name}: {sum(verdicts)}/{len(verdicts)} classified, out_uniq={len(uniq_out[name])} err_uniq={len(uniq_err[name])}")
print("\nTOTAL fresh rows classified PASS:", sum(1 for v in pin_match.values() if v), "/", len(cases), "| failed reps:", fails)
