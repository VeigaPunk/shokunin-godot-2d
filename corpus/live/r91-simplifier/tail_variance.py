#!/usr/bin/env python3
"""r91-simplifier: tail-variance census — evidence that the boundary fold was
load-bearing (the fields moved OUT of the pin really do vary run to run).

Sources: the author's fresh-arm receipts (3 reps/arm) and this seat's control
battery run (1 rep/arm). For every declared diagnostic tail field, count the
distinct values observed and show the range. A field with >1 distinct value
would have flaked the row had it stayed pinned.
"""
import json
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
AUTHOR = REPO / "corpus" / "live" / "r91-author"
CONTROL = sorted((HERE / "runs-control").glob("*/"))[-1]

TAIL = ["settle_a", "settle_b", "settle", "iter", "ladder", "first_reach_sync",
        "first_reach", "walk_steps", "reached_at", "first_reachable", "iter_b",
        "link_iter", "gate", "chg_iter_same", "chg_iter_settled", "dis_same",
        "fwd_disabled_same", "seq_a", "seq_b", "vel_a", "vel_b", "sum_max"]
FIELD_RE = [(f, re.compile(r"(?<![a-z_])%s=(\S*)" % re.escape(f))) for f in TAIL]

ARMS = ["census", "sync", "path", "query", "region", "agent", "avoid", "bake",
        "link", "teardown_crash", "teardown_clean"]

def nav_line(text, arm):
    for l in text.splitlines():
        if ("nav_lattice " + arm) in l or l.startswith("NAV_LATTICE_TEARDOWN_CRASH"):
            return l
    return ""

print("== tail-variance census (fields deliberately moved out of the pin) ==")
print("sources: %s (3 reps/arm) + control battery run (1 rep/arm)" % AUTHOR.name)
print()
for arm in ARMS:
    lines = []
    for f in sorted(AUTHOR.glob("fresh-reps/%s.rep*.out" % arm)):
        lines.append(("author/" + f.name, nav_line(f.read_text(), arm)))
    rec = [r for r in json.loads((CONTROL / "verdicts.json").read_text())["results"]
           if r["case"] == "nav_lattice_" + arm]
    if rec:
        lines.append(("control-run", nav_line("\n".join(rec[0]["output"]), arm)))
    print("-- %s (%d receipts) --" % (arm, len(lines)))
    found = False
    for f, rx in FIELD_RE:
        vals = []
        for _, l in lines:
            m = rx.search(l)
            if m:
                vals.append(m.group(1))
        if not vals:
            continue
        found = True
        uniq = sorted(set(vals))
        flag = "VARIES" if len(uniq) > 1 else "constant"
        show = uniq if len(uniq) <= 4 else uniq[:2] + ["..."] + uniq[-2:]
        print("   %-18s %-9s n=%d distinct=%d %s" % (f, flag, len(vals), len(uniq), show))
    if not found:
        print("   (no declared tail field emitted by this arm)")
