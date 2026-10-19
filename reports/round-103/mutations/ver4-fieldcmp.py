#!/usr/bin/env python3
"""r103 ver4 comparator: cross-side token comparison of r99b arm receipts.

Usage: ver4-fieldcmp.py <outroot>   (expects <outroot>/{base,ref}/<arm>.<rep>.stdout)

Rule: a PASS-line token that is byte-stable across the two base reps must be
byte-identical in both ref reps (the fold's byte-identity claim); a token that
varies within a side is reported as a timing-varying token and excluded from
the equality demand (its variation is intrinsic, proven within-side).
"""
import pathlib
import sys

root = pathlib.Path(sys.argv[1])
arms = sys.argv[2].split(",") if len(sys.argv) > 2 else ["startphase", "mixfree", "finfree", "splitcycle"]


def load(side, arm, rep):
    lines = (root / side / f"{arm}.{rep}.stdout").read_text().splitlines()
    pl = [l for l in lines if l.startswith("PASS ")]
    assert len(pl) == 1, (side, arm, rep, pl)
    return pl[0]


all_ok = True
for arm in arms:
    toks = {s: {r: load(s, arm, r).split() for r in (1, 2)} for s in ("base", "ref")}
    counts = {len(v[r]) for s in toks for r in toks[s]}
    if len(counts) != 1:
        print(f"{arm}: STRUCTURE MISMATCH token counts {sorted(counts)}")
        all_ok = False
        continue
    n = counts.pop()
    varying = [i for i in range(n) if toks["base"][1][i] != toks["base"][2][i]]
    mism = []
    for i in range(n):
        if i in varying:
            continue
        if not (toks["base"][1][i] == toks["base"][2][i] == toks["ref"][1][i] == toks["ref"][2][i]):
            mism.append((i, toks["base"][1][i], toks["ref"][1][i]))
    if mism:
        all_ok = False
    print(f"{arm}: tokens={n} within-side-varying={len(varying)} stable-token-mismatches={len(mism)} -> {'OK' if not mism else 'MISMATCH'}")
    if mism:
        for i, b, r in mism[:8]:
            print(f"   idx {i}: base={b!r} ref={r!r}")
    print(f"   within-side-varying indices: {varying}")
print("VERDICT:", "STABLE-TOKENS IDENTICAL ACROSS SIDES" if all_ok else "DIVERGENT")
