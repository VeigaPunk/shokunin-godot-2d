#!/usr/bin/env python3
"""r92-scribe: compact receipt summary of my two committed-byte battery runs."""
import json
import subprocess
from pathlib import Path

REPO = Path(__file__).resolve().parents[4]
LIVE = REPO / "corpus" / "live" / "r92-scribe"
src = subprocess.run(["git", "show", "HEAD:corpus/fixtures/run_battery.py"], cwd=REPO,
                     capture_output=True, check=True).stdout.decode()
import ast
tree = ast.parse(src)
cases = None
for node in tree.body:
    if isinstance(node, ast.Assign) and any(
            isinstance(t, ast.Name) and t.id == "CASES" for t in node.targets):
        cases = ast.literal_eval(node.value)
R92 = [c for c in cases if c[0].startswith("r92_")]

runs = {}
for label, d in [("rep1_worktree", LIVE / "battery-runs"), ("rep2b_committed_extract",
                                                            LIVE / "battery-committed")]:
    vj = sorted(d.glob("*/verdicts.json"))[-1]
    data = json.loads(vj.read_text())
    recs = {r["case"]: r for r in data["results"]}
    meta = recs["probe_error_clause_surface"]
    emitted = {}
    for c in R92:
        rec = recs.get(c[0])
        if rec is None:
            emitted[c[0]] = None
            continue
        sigs = c[4] if isinstance(c[4], (tuple, list)) else (c[4],)
        line = next((l for l in rec.get("output") or [] for s in sigs if l.startswith(s)), None)
        emitted[c[0]] = {"verdict": rec["verdict"], "exit": rec["actual_exit"], "line": line}
    runs[label] = {
        "stamp": vj.parent.name, "verdict": data.get("verdict"), "rows": len(data["results"]),
        "fails": sorted(k for k, r in recs.items() if r.get("verdict") == "FAIL"),
        "gate_r92": meta["discriminations"].get("r92_expected_errors_all_matched"),
        "dead_entry_count": meta["census"]["dead_entry_count"],
        "rows_with_expected_errors": meta["census"]["rows_with_expected_errors"],
        "census_bare_classifier_consistent": meta["discriminations"].get(
            "census_bare_classifier_consistent"),
        "r92": emitted,
    }
print(json.dumps(runs, indent=1)[:4000])
(LIVE / "audit" / "run_summary.json").write_text(json.dumps(runs, indent=1))
