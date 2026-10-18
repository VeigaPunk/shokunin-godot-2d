#!/usr/bin/env python3
"""r101 receipt byte-stability: compare run-1 vs run-2 PASS lines.

- Identical pins expected for every row EXCEPT the 4 fixture-folded ytrans rows
  (y0/y1000/ym1000/ycop: PASS-line shape changed by the phase fold between
  runs) and the 3 legacy joys-token rows (folded mid-run-2 at the PIN level;
  receipts unchanged, verdicts flipped by the fold as verified separately).
- Reports: total shared rows, byte-identical count, mismatch list.
"""
import sys

def rows(path):
    d = {}
    for line in open(path, errors="replace"):
        if line.startswith(("PASS ", "FAIL ")):
            name = line.split(":", 1)[0].split(" ", 1)[1].strip()
            d[name] = line.rstrip("\n")
    return d

FOLDED = {"r101_ytrans_y0", "r101_ytrans_y1000", "r101_ytrans_ym1000", "r101_ytrans_ycop"}
LEGACY = {"input_lattice_census", "input_lattice_dev_joy", "input89_edges_axisdev"}

r1, r2 = rows(sys.argv[1]), rows(sys.argv[2])
common = set(r1) & set(r2)
mism = [n for n in sorted(common) if r1[n] != r2[n] and n not in FOLDED | LEGACY]
print("run1 rows=%d run2 rows=%d common=%d" % (len(r1), len(r2), len(common)))
print("expected-shape-changed (folded): %d  legacy-joys (pin-folded, receipts same): %d"
      % (len(FOLDED & common), len(LEGACY & common)))
if LEGACY & common:
    same = all(r1[n] == r2[n] for n in LEGACY & common)
    print("legacy trio receipts byte-identical across runs:", same)
real = [n for n in common if n not in FOLDED]
ident = sum(1 for n in real if r1[n] == r2[n])
print("comparable rows=%d byte-identical=%d mismatches=%d" % (len(real), ident, len(mism)))
for n in mism[:10]:
    print("MISMATCH", n)
    print("  r1:", r1[n][:160])
    print("  r2:", r2[n][:160])
sys.exit(1 if mism else 0)
