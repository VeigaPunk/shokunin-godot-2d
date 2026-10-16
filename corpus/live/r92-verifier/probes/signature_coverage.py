#!/usr/bin/env python3
"""r92 verifier — signature coverage over the COMMITTED receipt corpus.

For every r92 PASS arm, collect every line-anchored
`PASS tilemap_lattice <arm> …` receipt in the committed scout/boundary
corpora and classify it against the committed signature:

  EXACT   -> line == "PASS tilemap_lattice <arm> " + signature
  MATCH   -> signature is a substring of the line (extra tail bytes)
  MISS    -> neither (the shape the row does not admit)

The nav row is checked against BOTH payloads (its committed envelope).
Also reports the rc/err shape of the receipts and the pinned stderr lines.
"""
import ast
import pathlib
import re
from collections import defaultdict

REPO = pathlib.Path("/home/vgpnk/Projects/shokunin/game-dev-2d-shokunin")
FIX = REPO / "corpus" / "live" / "r92-verifier" / "tree" / "corpus" / "fixtures" / "run_battery.py"
src = FIX.read_text()
tree = ast.parse(src)
for node in ast.walk(tree):
    if isinstance(node, ast.Assign) and getattr(node.targets[0], "id", "") == "CASES":
        cases = node.value.elts
rows = {}
for elt in cases:
    t = ast.literal_eval(elt)
    if t[0].startswith("r92_tilemap_") and t[0] != "r92_tilemap_nullts_crash":
        rows[t[0].removeprefix("r92_tilemap_")] = t[4]

receipts = defaultdict(list)
for root in (REPO / "corpus/live/r92-scout", REPO / "corpus/live/r92-boundary"):
    for path in sorted(root.rglob("*")):
        if not path.is_file():
            continue
        try:
            text = path.read_text(errors="replace")
        except OSError:
            continue
        for line in text.splitlines():
            m = re.match(r"^PASS tilemap_lattice ([a-z0-9_]+) ", line)
            if m:
                receipts[m.group(1)].append((str(path.relative_to(REPO)), line))

print(f"{'arm':12s} {'n':>4s} {'EXACT':>6s} {'MATCH':>6s} {'MISS':>5s}  miss-shapes")
total_miss = 0
tot_ex = tot_n = 0
miss_shapes = defaultdict(list)
for arm in sorted(receipts):
    sigs = rows.get(arm)
    if sigs is None:
        print(f"{arm:12s} {len(receipts[arm]):4d}  (no committed r92 row — foreign arm)")
        continue
    sigs = sigs if isinstance(sigs, (tuple, list)) else (sigs,)
    n_ex = n_ma = n_mi = 0
    for path, line in receipts[arm]:
        # NOTE: the committed r92 signatures include the `PASS tilemap_lattice
        # <arm> ` prefix themselves (full-line pins), so EXACT is line == sig.
        hit = [s for s in sigs if s == line]
        sub = [s for s in sigs if s in line]
        if hit:
            n_ex += 1
        elif sub:
            n_ma += 1
        else:
            n_mi += 1
            total_miss += 1
            # what differs? report the first diverging field
            pin = sigs[0]
            pt = pin.split()
            bt = line.split()
            diff = [(a, b) for a, b in zip(pt, bt) if a != b][:3]
            miss_shapes[arm].append((path, diff or f"len {len(pt)} vs {len(bt)}"))
    print(f"{arm:12s} {len(receipts[arm]):4d} {n_ex:6d} {n_ma:6d} {n_mi:5d}")
    tot_ex += n_ex
    tot_n += len(receipts[arm])
print(f"\nTOTAL receipts={tot_n} EXACT={tot_ex} misses={total_miss}")
for arm, items in miss_shapes.items():
    print(f"\n--- {arm} miss shapes ({len(items)}) ---")
    seen = defaultdict(int)
    for path, diff in items:
        seen[str(diff)] += 1
    for k, v in sorted(seen.items(), key=lambda kv: -kv[1]):
        print(f"  n={v:3d} {k}")
