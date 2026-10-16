#!/usr/bin/env python3
"""r92-scribe: cross-run comparison of my two committed-byte battery runs.

Row-by-row: the pinned signature (payload-aware) vs the emitted line.
identical  = same line bytes
tail-only  = the pin region matches; bytes after the pin differ
pin-diff   = the pin region itself differs (a real mismatch)
"""
import ast
import json
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[4]
LIVE = REPO / "corpus" / "live"
src = subprocess.run(["git", "show", "HEAD:corpus/fixtures/run_battery.py"], cwd=REPO,
                     capture_output=True, check=True).stdout.decode()
tree = ast.parse(src)
cases = None
for node in tree.body:
    if isinstance(node, ast.Assign) and any(
            isinstance(t, ast.Name) and t.id == "CASES" for t in node.targets):
        cases = ast.literal_eval(node.value)
ROWS = {c[0]: c for c in cases}


def load(run_dir):
    vj = sorted(Path(run_dir).glob("*/verdicts.json"))
    assert vj, f"no verdicts.json under {run_dir}"
    data = json.loads(vj[-1].read_text())
    return {r["case"]: r for r in data["results"] if isinstance(r, dict) and "case" in r}, data


def line_of(rec, case):
    case_def = ROWS.get(case)
    if not case_def:
        return None, None
    sigs = case_def[4] if isinstance(case_def[4], (tuple, list)) else (case_def[4],)
    for line in rec.get("output") or []:
        for s in sigs:
            if line.startswith(s):
                return line, s
    return None, None


def classify(a, b, case):
    la, sa = line_of(a, case)
    lb, sb = line_of(b, case)
    if la is None or lb is None:
        return "no-pinned-line", {"a": la, "b": lb}
    if la == lb:
        return "identical", None
    if la.startswith(sa) and lb.startswith(sb) and la[:len(sa)] == sa and lb[:len(sb)] == sb:
        return "tail-only", {"pin": sa, "a_tail": la[len(sa):][:200],
                             "b_tail": lb[len(sb):][:200]}
    return "pin-diff", {"a": la[:200], "b": lb[:200]}


a, da = load(LIVE / "r92-scribe" / "battery-runs")
b, db = load(LIVE / "r92-scribe" / "battery-committed")
common = sorted(set(a) & set(b))
buckets = {"identical": [], "tail-only": [], "pin-diff": [], "no-pinned-line": []}
detail = {}
for case in common:
    kind, info = classify(a[case], b[case], case)
    buckets[kind].append(case)
    if kind != "identical":
        detail[case] = {"kind": kind, "info": info,
                        "verdict_a": a[case].get("verdict"),
                        "verdict_b": b[case].get("verdict"),
                        "exit_a": a[case].get("actual_exit"),
                        "exit_b": b[case].get("actual_exit")}

r92 = {c: {"a": a[c].get("verdict"), "b": b[c].get("verdict"),
           "kind": classify(a[c], b[c], c)[0],
           "exit_a": a[c].get("actual_exit"), "exit_b": b[c].get("actual_exit")}
       for c in common if c.startswith("r92_")}
out = {
    "run_a": {"verdict": da.get("verdict"), "rows": len(a),
              "fails": sorted(c for c, r in a.items() if r.get("verdict") == "FAIL")},
    "run_b": {"verdict": db.get("verdict"), "rows": len(b),
              "fails": sorted(c for c, r in b.items() if r.get("verdict") == "FAIL")},
    "common_rows": len(common),
    "only_a": sorted(set(a) - set(b)), "only_b": sorted(set(b) - set(a)),
    "buckets": {k: {"count": len(v), "cases": v} for k, v in buckets.items()},
    "detail": detail,
    "r92": r92,
    "gates": {"a": {k: v.get("discriminations", {}).get("r92_expected_errors_all_matched")
                    for k, v in a.items() if k == "probe_error_clause_surface"},
              "b": {k: v.get("discriminations", {}).get("r92_expected_errors_all_matched")
                    for k, v in b.items() if k == "probe_error_clause_surface"}},
    "census": {"a": {k: v.get("census", {}) for k, v in a.items()
                     if k == "probe_error_clause_surface"},
               "b": {k: v.get("census", {}) for k, v in b.items()
                     if k == "probe_error_clause_surface"}},
}
print(json.dumps({k: v for k, v in out.items() if k != "detail"}, indent=1))
(Path(__file__).parent / "compare_runs.json").write_text(json.dumps(out, indent=1))
