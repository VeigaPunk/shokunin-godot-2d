#!/usr/bin/env python3
"""Per-sub 3-rep determinism table for the edge sweep + full payload dump."""
import sys
from pathlib import Path
SEAT = Path(__file__).resolve().parent
RUNS = SEAT / "runs"
subs = []
for line in (SEAT / "run_all.py").read_text().split("EDGE_SUBS = [")[1].split("]")[0].splitlines():
    for tok in line.split(","):
        tok = tok.strip().strip('"').strip("'")
        if tok and tok != "sanity":
            subs.append(tok)
out = []
for sub in subs:
    rcs, last, errs = [], set(), set()
    for rep in (1, 2, 3):
        rcf = RUNS / f"edge_{sub}.rep{rep}.rc"
        outf = RUNS / f"edge_{sub}.rep{rep}.out"
        if not rcf.exists():
            rcs.append("MISSING"); continue
        rcs.append(rcf.read_text().strip())
        lines = [l for l in outf.read_text().splitlines() if l.startswith("PASS b89_edge")]
        last.add(lines[-1] if lines else "<no PASS>")
        ef = RUNS / f"edge_{sub}.rep{rep}.err"
        errs.add(ef.read_text().strip().splitlines()[0] if ef.read_text().strip() else "")
    uniq = len(last)
    out.append((sub, ",".join(rcs), uniq, len(errs), sorted(last)[0]))
print(f"subs={len(out)}")
n_unstable = 0
for sub, rcs, uniq, nerr, first in out:
    flag = "UNSTABLE" if uniq > 1 or len(set(rcs.split(","))) > 1 else ""
    if flag:
        n_unstable += 1
    print(f"{sub:26s} rc=[{rcs:8s}] out_uniq={uniq} err_uniq={nerr} {flag}")
    if uniq > 1:
        for u in sorted(last):
            print(f"    ALT: {u[:300]}")
print(f"UNSTABLE={n_unstable}")
