#!/usr/bin/env python3
"""r92 verifier — stability probe for the r91 nav_lattice_path row.

rep1 of this seat's battery series failed ONLY on `nav_lattice_path` (an r91
row, untouched by the r92 insertion).  This probe runs the arm standalone N
times in the battery's launch shape and classifies each receipt with the
production classifier + that row's committed signature, so the failure can be
attributed (pre-existing load-conditioned read vs r92 regression).
"""
import ast
import pathlib
import subprocess
import sys

REPO = pathlib.Path("/home/vgpnk/Projects/shokunin/game-dev-2d-shokunin")
V = REPO / "corpus" / "live" / "r92-verifier"
PROJ = V / "arms" / "proj"
OUT = V / "arms" / "path_stability"
OUT.mkdir(exist_ok=True)

src = (V / "tree/corpus/fixtures/run_battery.py").read_text()
tree = ast.parse(src)
ns = {}
for node in ast.walk(tree):
    if isinstance(node, ast.FunctionDef) and node.name == "classify_process":
        exec("import re\n" + ast.get_source_segment(src, node), ns)
classify = ns["classify_process"]
row = None
for node in ast.walk(tree):
    if isinstance(node, ast.Assign) and getattr(node.targets[0], "id", "") == "CASES":
        cases = node.value.elts
for elt in cases:
    t = ast.literal_eval(elt)
    if t[0] == "nav_lattice_path":
        row = t
print("row:", row[0], "flags", row[2], "exit", row[3], "sig len", len(row[4]))

n = int(sys.argv[1]) if len(sys.argv) > 1 else 20
ok = 0
shapes = {}
for i in range(1, n + 1):
    proc = subprocess.run(["godot", "--headless", "--path", str(PROJ),
                           "--script", "res://nav_lattice.gd", "--", "--arm=path"],
                          capture_output=True, text=True, timeout=20)
    out, err, rc = proc.stdout, proc.stderr, proc.returncode
    (OUT / f"path.rep{i}.out").write_text(out)
    (OUT / f"path.rep{i}.err").write_text(err)
    (OUT / f"path.rep{i}.rc").write_text(f"{rc}\n")
    passed = classify(rc, None, out + err, row[3], row[4], ())
    ok += passed
    line = next((l for l in out.splitlines() if l.startswith("PASS nav_lattice path")), "")
    if not passed:
        key = line.split("diag=")[1][:60] if "diag=" in line else line[:60]
        shapes[key] = shapes.get(key, 0) + 1
    print(f"rep{i:2d} rc={rc} PASS={passed} diag={line.split('diag=')[1][:50] if 'diag=' in line else '?'}", flush=True)
print(f"\nrow={row[0]} n={n} pass={ok} fail={n-ok}")
for k, v in shapes.items():
    print(f"  failing shape n={v}: {k}")
