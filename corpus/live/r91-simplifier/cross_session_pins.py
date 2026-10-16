#!/usr/bin/env python3
"""r91-simplifier: cross-session pin stability of the 11 nav_lattice rows.

Compares the pinned block (everything before the declared diagnostic tail) of
this seat's control battery run against:
  - the author's fresh-arm receipts (11 arms x 3 reps, corpus/live/r91-author)
  - the author's two green battery runs (runs1, runs2)
Tails are masked; nothing else is normalised.
"""
import json
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
AUTHOR = REPO / "corpus" / "live" / "r91-author"
CONTROL = sorted((HERE / "runs-control").glob("*/"))[-1]

TAIL_FIELDS = ["settle_a", "settle_b", "settle", "iter", "ladder", "first_reach_sync",
               "first_reach", "walk_steps", "reached_at", "first_reachable",
               "iter_b", "link_iter", "gate", "chg_iter_same",
               "chg_iter_settled", "dis_same", "fwd_disabled_same", "seq_a",
               "seq_b", "vel_a", "vel_b", "sum_max"]
MASK = [(f, re.compile(r"(?<![a-z_])%s=\S*" % re.escape(f))) for f in TAIL_FIELDS]

def mask(s):
    for _, rx in MASK:
        s = rx.sub("", s)
    return re.sub(r"\s+", " ", s).strip()

def key_line(text, arm):
    """The single emitted nav_lattice line for this arm, tails masked.
    Lines are masked individually: the harness records stdout+stderr merged,
    while the author's fresh-rep receipts keep the streams separate."""
    for l in text.splitlines():
        if ("nav_lattice " + arm) in l or l.startswith("NAV_LATTICE_TEARDOWN_CRASH"):
            return mask(l)
    return "<MISSING>"

rows = [r for r in json.loads((CONTROL / "verdicts.json").read_text())["results"]
        if r["case"].startswith("nav_lattice_")]
print("== cross-session pin stability (tails masked) ==")
print("this seat's control run: %s" % CONTROL)
print()
mismatch = 0
for r in sorted(rows, key=lambda r: r["case"]):
    arm = re.search(r"--arm=([a-z_]+)", str(r["flags"])).group(1)
    mine_key = key_line("\n".join(r["output"]), arm)
    sources = []
    # author fresh reps (stdout-only receipts)
    reps = sorted(AUTHOR.glob("fresh-reps/%s.rep*.out" % arm))
    for f in reps:
        sources.append((f.name, key_line(f.read_text(), arm)))
    # author battery runs (merged stdout+stderr)
    for run in sorted(AUTHOR.glob("runs*/*/verdicts.json")):
        rec = [x for x in json.loads(run.read_text())["results"] if x["case"] == r["case"]]
        if not rec:
            sources.append((str(run.parent.name) + "/verdicts.json", "<NO ROW>"))
            continue
        sources.append((str(run.parent.name) + "/verdicts.json",
                        key_line("\n".join(rec[0]["output"]), arm)))
    bad = [n for n, s in sources if s != mine_key]
    mismatch += len(bad)
    print("%-28s receipts_compared=%d  identical=%s" % (
        r["case"], len(sources), "ALL" if not bad else "MISMATCH " + str(bad)))
    if bad:
        print("   mine : %s" % mine_key[:200])
        for n, s in sources:
            if s != mine_key:
                print("   %-18s: %s" % (n, s[:200]))
print()
print("TOTAL_MISMATCHES=%d" % mismatch)
