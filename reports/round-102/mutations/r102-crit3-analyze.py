#!/usr/bin/env python3
"""r102 CRIT-3 receipt analyzer: base vs folded per-row comparison."""
import json, re, sys
from pathlib import Path

S = Path("/var/tmp/r102-crit3")
d = json.loads((S / "receipts-sweep.json").read_text())
base, fold = d["base"], d["folded"]
mask = lambda s: re.sub(r"(res://[^\s:\"']+\.gd):\d+", r"\1:N", s)

total = len(base)
vd = [n for n in base if base[n]["verdict"] != fold[n]["verdict"]]
rcd = [n for n in base if base[n]["rc"] != fold[n]["rc"]]
sigd = [n for n in base if base[n]["sig_in"] != fold[n]["sig_in"]]
rawsame = [n for n in base if base[n]["merged"] == fold[n]["merged"]]
msame = [n for n in base if mask(base[n]["merged"]) == mask(fold[n]["merged"])]
print(f"rows={total} verdict_discord={len(vd)} rc_discord={len(rcd)} sig_discord={len(sigd)}")
print(f"raw-identical={len(rawsame)}/{total}  masked-identical={len(msame)}/{total}")
for n in vd + [x for x in rcd if x not in vd]:
    print("!! DISCORD", n, base[n]["rc"], fold[n]["rc"], base[n]["verdict"], fold[n]["verdict"])
rawdiff = [n for n in base if n not in rawsame]
print(f"raw-diff rows: {len(rawdiff)}")
for n in rawdiff:
    b, f = base[n]["merged"].splitlines(), fold[n]["merged"].splitlines()
    diff = [i for i in range(min(len(b), len(f))) if b[i] != f[i]]
    cls = "BACKTRACE-ONLY" if mask(base[n]["merged"]) == mask(fold[n]["merged"]) else "OTHER"
    print(f"  {n}: {cls} nlines={len(b)}/{len(f)} firstdiff={diff[:1]}")
    if cls == "OTHER":
        for i in diff[:4]:
            print(f"     B: {b[i][:140]}")
            print(f"     F: {f[i][:140]}")
# non-verdict PASS check for verdict line
bad = [n for n in base if not base[n]["verdict"] or not fold[n]["verdict"]]
print(f"non-PASS rows (either tree): {bad}")
