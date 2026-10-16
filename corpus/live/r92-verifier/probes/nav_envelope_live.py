#!/usr/bin/env python3
"""r92 verifier — live check of the nav row's 2-payload scheduler envelope.

Runs the committed fixture under the battery's launch shape at four scheduler
cells and classifies each receipt with the production `classify_process` +
the row's committed envelope:
  default (idle:physics ~1)  -> expect payload[0]
  --fixed-fps 120 (ratio 2)  -> expect payload[0]
  --fixed-fps 150 (ratio 2.5)-> expect payload[1]
  --fixed-fps 600 (ratio 10) -> expect payload[1]
"""
import ast
import hashlib
import pathlib
import subprocess

REPO = pathlib.Path("/home/vgpnk/Projects/shokunin/game-dev-2d-shokunin")
V = REPO / "corpus" / "live" / "r92-verifier"
PROJ = V / "arms" / "proj"
OUT = V / "arms" / "fixedfps"
OUT.mkdir(exist_ok=True)

src = (V / "tree/corpus/fixtures/run_battery.py").read_text()
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
for elt in cases:
    t = ast.literal_eval(elt)
    if t[0] == "r92_tilemap_nav":
        p0, p1 = t[4]

cells = [("default", []), ("ff120", ["--fixed-fps", "120"]),
         ("ff150", ["--fixed-fps", "150"]), ("ff600", ["--fixed-fps", "600"])]
fails = 0
for name, extra in cells:
    for rep in (1, 2, 3):
        cmd = ["godot", "--headless", *extra, "--path", str(PROJ),
               "--script", "res://tilemap_lattice.gd", "--", "--arm=nav"]
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=20)
        out, err, rc = proc.stdout, proc.stderr, proc.returncode
        (OUT / f"nav_{name}.rep{rep}.out").write_text(out)
        (OUT / f"nav_{name}.rep{rep}.err").write_text(err)
        (OUT / f"nav_{name}.rep{rep}.rc").write_text(f"{rc}\n")
        merged = out + err
        v0 = classify(rc, None, merged, 0, p0, ())
        v1 = classify(rc, None, merged, 0, p1, ())
        admitted = v0 or v1
        want = "p0" if name in ("default", "ff120") else "p1"
        got = "p0" if v0 else "p1" if v1 else "NEITHER"
        ok = admitted and got == want
        if not ok:
            fails += 1
        line = next((l for l in out.splitlines() if l.startswith("PASS tilemap_lattice nav")), "")
        f1 = line.split("regions_f1=")[1][:1] if "regions_f1=" in line else "?"
        print(f"{'OK  ' if ok else 'FAIL'} {name} rep{rep} rc={rc} regions_f1={f1} "
              f"verdict={got} want={want} admitted={admitted}")
print(f"\ncells=4 reps=3 fails={fails}")
raise SystemExit(1 if fails else 0)
