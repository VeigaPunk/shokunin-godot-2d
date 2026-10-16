#!/usr/bin/env python3
"""r92 verifier — nav envelope exhaustiveness over the COMMITTED receipt corpus.

Every line-anchored `PASS tilemap_lattice nav …` receipt in the committed
scout/boundary corpora must match EXACTLY ONE of the committed row's two
payloads (or, for the scout's canonical-run bookkeeping, be counted and
reported).  Also classifies each receipt by its scheduler cell (from the
directory / filename) so the envelope's regime claim is auditable.
"""
import ast
import pathlib
import re

REPO = pathlib.Path("/home/vgpnk/Projects/shokunin/game-dev-2d-shokunin")
FIX = REPO / "corpus" / "live" / "r92-verifier" / "tree" / "corpus" / "fixtures" / "run_battery.py"
src = FIX.read_text()
tree = ast.parse(src)
cases = None
for node in ast.walk(tree):
    if isinstance(node, ast.Assign) and getattr(node.targets[0], "id", "") == "CASES":
        cases = node.value.elts
for elt in cases:
    t = ast.literal_eval(elt)
    if t[0] == "r92_tilemap_nav":
        payloads = list(t[4])
        break
print("payload[0] regions_f1=1:", "regions_f1=1" in payloads[0])
print("payload[1] regions_f1=0:", "regions_f1=0" in payloads[1])
print("payloads differ only in regions_f1:",
      payloads[0].replace("regions_f1=1", "X") == payloads[1].replace("regions_f1=0", "X"))
print("both pin regions_f2=1:", all("regions_f2=1" in p for p in payloads))
print()

roots = [REPO / "corpus" / "live" / "r92-scout", REPO / "corpus" / "live" / "r92-boundary"]
pat = re.compile(r"^PASS tilemap_lattice nav ")
counts = {"p0": 0, "p1": 0, "neither": 0}
files = {"p0": [], "p1": [], "neither": []}
shapes = {}
for root in roots:
    for path in sorted(root.rglob("*")):
        if not path.is_file():
            continue
        try:
            text = path.read_text(errors="replace")
        except OSError:
            continue
        for line in text.splitlines():
            if not pat.match(line):
                continue
            body = line[len("PASS tilemap_lattice nav "):]
            hits = [i for i, p in enumerate(payloads) if p in line]
            key = "p0" if hits == [0] else "p1" if hits == [1] else "neither"
            counts[key] += 1
            files[key].append(str(path.relative_to(REPO)))
            if key == "neither":
                shapes.setdefault(body, []).append(str(path.relative_to(REPO)))
            else:
                # residual: what is in the receipt that is NOT the payload?
                resid = line.replace(payloads[hits[0]], "")
                shapes.setdefault(("resid", resid), []).append(str(path.relative_to(REPO)))

print(f"receipts: payload[0]={counts['p0']} payload[1]={counts['p1']} NEITHER={counts['neither']}")
print(f"total={sum(counts.values())}")
print("\n--- distinct receipt shapes ---")
for k, v in sorted(shapes.items(), key=lambda kv: -len(kv[1])):
    if isinstance(k, tuple):
        print(f"  n={len(v):3d} residual-after-payload={k[1]!r}")
    else:
        print(f"  n={len(v):3d} NEITHER shape: {k!r}")
        for f in v[:5]:
            print(f"        {f}")

print("\n--- per-directory regime ---")
reg = {}
for key in ("p0", "p1"):
    for f in files[key]:
        d = str(pathlib.Path(f).parent)
        reg.setdefault(d, {}).setdefault(key, 0)
        reg[d][key] += 1
for d, c in sorted(reg.items()):
    print(f"  {d:55s} p0={c.get('p0',0):3d} p1={c.get('p1',0):3d}")
