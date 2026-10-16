#!/usr/bin/env python3
"""r95-scribe cross-run comparison: worktree run vs committed-extract run."""
import json
from pathlib import Path

REPO = Path("/home/vgpnk/Projects/shokunin/game-dev-2d-shokunin")
LANE = REPO / "corpus/live/r95-scribe"

runs = {}
for lane_dir in ("battery-runs", "battery-committed"):
    for vf in sorted((LANE / lane_dir).glob("*/verdicts.json")):
        v = json.loads(vf.read_text())
        runs[lane_dir] = {
            "stamp": vf.parent.name,
            "path": str(vf.relative_to(REPO)),
            "verdict": v["verdict"],
            "rows": len(v["results"]),
            "rows_pass": sum(1 for r in v["results"] if r["verdict"] == "PASS"),
            "fail_cases": [r["case"] for r in v["results"] if r["verdict"] != "PASS"],
            "r95_pass": sum(1 for r in v["results"]
                            if str(r["case"]).startswith(("dss_lattice_", "r95b_order_"))
                            and r["verdict"] == "PASS"),
            "r95_rows": sum(1 for r in v["results"]
                            if str(r["case"]).startswith(("dss_lattice_", "r95b_order_"))),
            "results": {r["case"]: r for r in v["results"]},
        }

if len(runs) == 2:
    a, b = (runs["battery-runs"], runs["battery-committed"])
    same, diff, flips = 0, [], []
    for case in sorted(set(a["results"]) | set(b["results"])):
        ra, rb = a["results"].get(case), b["results"].get(case)
        if ra is None or rb is None:
            diff.append({"case": case, "why": "missing in one run"})
            continue
        if ra["verdict"] != rb["verdict"]:
            flips.append({"case": case, "a": ra["verdict"], "b": rb["verdict"]})
        if (ra.get("output") or []) == (rb.get("output") or []):
            same += 1
        else:
            diff.append({"case": case, "why": "output differs",
                         "a_len": len(ra.get("output") or []),
                         "b_len": len(rb.get("output") or [])})
    r95_diff = [d for d in diff if str(d["case"]).startswith(("dss_lattice_", "r95b_order_"))]
    out = {"run_a": {k: v for k, v in a.items() if k != "results"},
           "run_b": {k: v for k, v in b.items() if k != "results"},
           "identical_rows": same,
           "differing_rows": len(diff),
           "r95_differing_rows": r95_diff,
           "verdict_flips": flips}
else:
    out = {"run_a": {k: v for k, v in runs.get("battery-runs", {}).items() if k != "results"},
           "run_b": {k: v for k, v in runs.get("battery-committed", {}).items() if k != "results"},
           "note": "only one run present"}

(LANE / "audit/compare_runs.json").write_text(json.dumps(out, indent=2, sort_keys=True))
print(json.dumps(out, indent=2)[:4000])
