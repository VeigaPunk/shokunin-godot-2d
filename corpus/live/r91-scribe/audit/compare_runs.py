#!/usr/bin/env python3
"""r91-scribe: compare my two independent committed-byte battery runs
(rep1 = worktree at 77d2f7e; rep2b = `git archive HEAD` extract) row by row.

Reports: identical rows, rows differing only after the row's pinned signature
(diagnostic tails), and rows differing inside the pin (would be a real
instability of a landed pin)."""
import ast, glob, json, re
from pathlib import Path
ROOT = Path("/home/vgpnk/Projects/shokunin/game-dev-2d-shokunin")
bat = ast.parse((ROOT / "corpus/fixtures/run_battery.py").read_text())
cases = next(n for n in bat.body if isinstance(n, ast.Assign)
             and any(getattr(t, "id", "") == "CASES" for t in n.targets)).value.elts
sigs = {}
for e in cases:
    name = e.elts[0].value
    ev = e.elts[4]
    sigs[name] = ([x.value for x in ev.elts] if isinstance(ev, ast.Tuple)
                  else [ev.value])

def txt(r):
    o = r.get("output")
    return "\n".join(o) if isinstance(o, list) else ("" if o is None else str(o))

def load(p):
    d = json.load(open(p))
    return {r["case"]: r for r in d["results"]}

r1 = load(sorted(glob.glob(str(ROOT / "corpus/live/r91-scribe/battery-runs/*/verdicts.json")))[-1])
r2 = load(sorted(glob.glob(str(ROOT / "corpus/live/r91-scribe/battery-committed/*/verdicts.json")))[-1])
common = [k for k in r1 if k in r2]
same = tail_only = pin_diff = 0
pin_diff_rows = []
tail_rows = []
for k in common:
    a = txt(r1[k])
    b = txt(r2[k])
    if a == b:
        same += 1
        continue
    # pinned payload = first signature (for envelope rows: any) that appears in either
    pins = [s for s in sigs[k] if s in a or s in b]
    pin_hit = [s for s in pins if s in a and s in b]
    if pin_hit:
        tail_only += 1
        tail_rows.append(k)
    else:
        pin_diff += 1
        pin_diff_rows.append(k)
print("rows compared:", len(common), "| identical:", same,
      "| tail-only diff:", tail_only, "| PIN diff:", pin_diff)
print("tail-only rows:", tail_rows[:20])
print("pin-diff rows:", pin_diff_rows[:20])
nav = [k for k in common if k.startswith("nav_lattice_")]
print("\nnav rows identical across both runs:",
      sum(1 for k in nav if txt(r1[k]) == txt(r2[k])), "/", len(nav))
for k in nav:
    a = txt(r1[k])
    b = txt(r2[k])
    la = [l for l in a.splitlines() if l.startswith("PASS ") or l.startswith("NAV_") or l.startswith("STALE ")]
    lb = [l for l in b.splitlines() if l.startswith("PASS ") or l.startswith("NAV_") or l.startswith("STALE ")]
    ta = la[0][len(sigs[k][0]):] if la and la[0].startswith(sigs[k][0]) else None
    tb = lb[0][len(sigs[k][0]):] if lb and lb[0].startswith(sigs[k][0]) else None
    print(f"  {k:28s} pin_match_both={la and lb and la[0].startswith(sigs[k][0]) and lb[0].startswith(sigs[k][0])} tail_equal={ta==tb}"
          + (f"  rep1_tail={ta!r} rep2b_tail={tb!r}" if ta != tb else ""))
