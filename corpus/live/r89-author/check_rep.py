#!/usr/bin/env python3
"""r89-author rep checker — summarize a battery run dir: verdict, failed rows,
new-row status, pre_frame emitted mode."""
import json
import pathlib
import re
import sys

rd = pathlib.Path(sys.argv[1])
vf = sorted(rd.glob("*/verdicts.json"))
if not vf:
    print("no verdicts yet")
    sys.exit(2)
d = json.loads(vf[-1].read_text())
fails = [r["case"] for r in d["results"] if r["verdict"] != "PASS"]
new = [r for r in d["results"] if r["case"].startswith(("geo2d_lattice_", "input89_edges_"))]
print(f"{vf[-1].parent.name} verdict={d['verdict']} rows={len(d['results'])} "
      f"new_rows={len(new)} new_all_PASS={all(r['verdict'] == 'PASS' for r in new)}")
if fails:
    print("FAILS:", fails)
    for c in fails:
        r = next(x for x in d["results"] if x["case"] == c)
        pl = [l for l in (r.get("output") or []) if l.startswith("PASS") or "ERROR" in l or "ASSERTION" in l]
        print(f"  {c}: exit={r.get('actual_exit')}", ("|" + pl[-1][:110]) if pl else "")
ex = next(r for r in d["results"] if r["case"] == "input89_edges_exact")
pl = [l for l in ex["output"] if l.startswith("PASS")]
mode = "Q" if pl and "w_jp[ex=false inex=true]" in pl[0] else (
    "L" if pl and "w_jp[ex=false inex=false]" in pl[0] else "?")
pf = next(r for r in d["results"] if r["case"] == "input_lattice_pre_frame")
pfl = [l for l in (pf.get("output") or []) if l.startswith("PASS")]
mph = re.search(r"post_ph=\[[^]]*\]", pfl[0]) if pfl else None
print(f"exact_mode={mode} pre_frame={pf['verdict']} ({mph.group(0) if mph else '?'})")
