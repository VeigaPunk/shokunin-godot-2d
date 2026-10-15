#!/usr/bin/env python3
"""Per-row 6-rep load-stability table + verbatim alt payloads."""
import re
from pathlib import Path
SEAT = Path(__file__).resolve().parent
RUNS = SEAT / "runs"
text = (SEAT.parent / "r89-scout" / "author-rows.py.txt").read_text()
pat = re.compile(r"\('([^']+)',\s*'([^']+)',\s*\[([^\]]*)\],\s*(-?\d+),\s*'([^']*)'\)", re.S)
rows = [(m.group(1), m.group(5)) for m in pat.finditer(text)]
print(f"rows={len(rows)}")
for name, sig in rows:
    hits, rcs, lines, errs = 0, [], [], set()
    for rep in range(1, 7):
        rc = (RUNS / f"row_{name}.rep{rep}.rc").read_text().strip()
        out = (RUNS / f"row_{name}.rep{rep}.out").read_text()
        err = (RUNS / f"row_{name}.rep{rep}.err").read_text()
        rcs.append(rc)
        hits += 1 if sig in out else 0
        ln = [l for l in out.splitlines() if l.startswith("PASS ") or l.startswith("R89 lineempty")]
        lines.append(ln[-1] if ln else "<none>")
        errs.add(err.strip().splitlines()[0] if err.strip() else "")
    uniq = sorted(set(lines))
    print(f"{name:28s} sig_hits={hits}/6 rc={sorted(set(rcs))} pass_uniq={len(uniq)} err_uniq={len(errs)}")
    if len(uniq) > 1:
        for u in uniq:
            print(f"    ALT: {u}")
