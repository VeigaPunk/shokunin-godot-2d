#!/usr/bin/env python3
"""Summarize battery verdicts.json runs: totals, failures, r95 row instances,
floor-gate values, dead-entry counts, per-row distinct boolean blocks."""
import json
import sys
from collections import defaultdict
from pathlib import Path

runs = [Path(p) for p in sys.argv[1:]]
summary = []
row_payloads = defaultdict(set)
for run in runs:
    v = json.loads((run / "verdicts.json").read_text())
    res = v["results"]
    fails = [r["case"] for r in res if r["verdict"] != "PASS"]
    r95 = [r for r in res if r["case"].startswith(("dss_lattice_", "r95b_order_"))]
    gates = None
    for r in res:
        if r["case"] == "probe_error_clause_surface":
            gates = r.get("discriminations", {})
    r95_gate = gates.get("r95_expected_errors_all_matched") if gates else None
    gate_keys = {k: val for k, val in (gates or {}).items() if k.endswith("_all_matched")}
    dead = None
    for r in res:
        if r["case"] == "probe_error_clause_surface":
            dead = r.get("census", {}).get("dead_entry_count")
    summary.append({
        "run": run.name, "verdict": v["verdict"], "rows": len(res),
        "fails": fails, "r95_instances": len(r95),
        "r95_fails": [r["case"] for r in r95 if r["verdict"] != "PASS"],
        "r95_gate": r95_gate, "dead_entry_count": dead,
        "all_round_gates": gate_keys,
    })
    for r in res:
        row_payloads[r["case"]].add(r["verdict"])
out = {"runs": summary,
       "r95_instances_total": sum(s["r95_instances"] for s in summary),
       "r95_fails_total": sum(len(s["r95_fails"]) for s in summary),
       "rows_with_mixed_verdicts": [c for c, vs in row_payloads.items() if len(vs) > 1]}
print(json.dumps(out, indent=2))
