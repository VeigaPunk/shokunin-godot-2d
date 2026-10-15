#!/usr/bin/env python3
"""Extract the committed 2-payload envelope and diff vs live emissions."""
import ast, pathlib
REPO = pathlib.Path("/home/vgpnk/Projects/shokunin/game-dev-2d-shokunin")
src = (REPO / "corpus/fixtures/run_battery.py").read_text()
for node in ast.walk(ast.parse(src)):
    if isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and t.id=="CASES" for t in node.targets):
        cases = ast.literal_eval(node.value)
row = next(c for c in cases if c[0]=="input89_edges_exact")
payloads = row[4]
print(f"payloads={len(payloads)}")
# token-level diff of the two payloads
t0, t1 = payloads[0].split(), payloads[1].split()
diffs = [(a,b) for a,b in zip(t0,t1) if a!=b]
print(f"token count p0={len(t0)} p1={len(t1)} len_eq={len(t0)==len(t1)}")
print("differing tokens:", diffs)
# live mode-L line vs payload[1]
live = pathlib.Path("runs/input89_edges.gd.exact.load.rep1.out").read_text()
live_line = next(l for l in live.splitlines() if l.startswith("PASS input89_edges exact"))
print("live mode-L == payload[1]:", live_line == payloads[1])
print("live mode-L == payload[0]:", live_line == payloads[0])
# scout quiet receipt vs payload[0]
scout = REPO/"corpus/live/r89-scout/runs"
import glob
found = []
for p in sorted(scout.glob("in_exact.rep*.out")):
    for l in p.read_text().splitlines():
        if l.startswith("PASS input89_edges exact"):
            found.append((p.name, l))
if found:
    print("scout rep1 == payload[0]:", found[0][1] == payloads[0], f"({found[0][0]})")
