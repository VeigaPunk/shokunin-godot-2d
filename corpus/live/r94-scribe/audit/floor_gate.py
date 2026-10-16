#!/usr/bin/env python3
"""r94 scribe — floor-gate loudness proof (static, from HEAD bytes).

The r94 floor gate is vacuously true on the current bytes (no r94 allowlist
entries). This script proves it is *load-bearing as code*: it extracts
`surface_allowed_error` / `entry_shape` and the gate expression from HEAD, then
evaluates the gate over synthetic census rows:

  live  entry (allowlisted line present in the row output)  -> gate True
  dead  entry (allowlisted line absent)                     -> gate False
  two rows, one dead                                        -> gate False

plus the real census row set of a completed scribe battery run (from
verdicts.json meta record), re-evaluating the gate expression on it.

Writes corpus/live/r94-scribe/audit/floor_gate.json.
"""
import ast
import json
import re
import subprocess
from pathlib import Path

REPO = Path("/home/vgpnk/Projects/shokunin/game-dev-2d-shokunin")
OUT = REPO / "corpus/live/r94-scribe/audit"

src = subprocess.run(["git", "show", "HEAD:corpus/fixtures/run_battery.py"],
                     cwd=REPO, capture_output=True).stdout.decode()
tree = ast.parse(src)

# extract helpers + the gate comprehension source
ns = {}
for node in ast.walk(tree):
    if isinstance(node, ast.FunctionDef) and node.name in ("surface_allowed_error", "entry_shape"):
        exec(ast.get_source_segment(src, node), ns)
surface_allowed_error = ns["surface_allowed_error"]
entry_shape = ns["entry_shape"]

gate_m = re.search(r'"r94_expected_errors_all_matched": (all\(.*?\)),\n', src, re.S)
gate_src = gate_m.group(1)
gate_code = compile(gate_src, "<gate>", "eval")


def gate(census_rows):
    """Evaluate the EXTRACTED gate expression with `census_rows` bound."""
    return eval(gate_code, {"all": all, "census_rows": census_rows})


def census_row(case, signature, output_lines, entries):
    entry_records = []
    for entry in entries:
        matched = [l.strip() for l in output_lines if surface_allowed_error(l, entry)]
        entry_records.append({"entry": entry, "shape": entry_shape(entry),
                              "matched_lines": len(matched),
                              "first_match": matched[0] if matched else None,
                              "dead_in_run": not matched})
    return {"case": case, "entries": entry_records}


def gate_over(rows):
    return gate(rows)


res = {"gate_source": gate_src}
live = census_row("r94_particles_synthetic", "sig",
                  ["PASS x", "ERROR: r94 synthetic live line"], ["ERROR: r94 synthetic live line"])
dead = census_row("r94_particles_synthetic", "sig",
                  ["PASS x"], ["ERROR: r94 synthetic dead line"])
mixed = census_row("r94_particles_synthetic", "sig",
                   ["PASS x", "ERROR: r94 synthetic live line"],
                   ["ERROR: r94 synthetic live line", "ERROR: r94 synthetic dead line"])
nonr94_dead = census_row("r93_synthetic", "sig", ["PASS x"], ["ERROR: not present"])
res["synthetic"] = {
    "live_only_gate": gate_over([live]),
    "dead_only_gate": gate_over([dead]),
    "mixed_gate": gate_over([mixed]),
    "non_r94_dead_row_gate": gate_over([nonr94_dead]),
}
assert res["synthetic"]["live_only_gate"] is True
assert res["synthetic"]["dead_only_gate"] is False
assert res["synthetic"]["mixed_gate"] is False
assert res["synthetic"]["non_r94_dead_row_gate"] is True  # out of prefix scope

# real census from a completed scribe battery run
runs = sorted((REPO / "corpus/live/r94-scribe/battery-runs").glob("*/verdicts.json"))
if runs:
    d = json.loads(runs[-1].read_text())
    meta = next(r for r in d["results"] if r["case"] == "probe_error_clause_surface")
    real = meta["census"]
    res["real_run"] = {
        "run": runs[-1].parent.name,
        "rows_with_expected_errors": real["rows_with_expected_errors"],
        "dead_entry_count": real["dead_entry_count"],
        "r94_census_rows": [r["case"] for r in real["rows"] if r["case"].startswith("r94_")],
        "gate_recomputed_from_census_rows": gate_over(real["rows"]),
        "gate_reported_in_run": meta["discriminations"]["r94_expected_errors_all_matched"],
    }
(OUT / "floor_gate.json").write_text(json.dumps(res, indent=2) + "\n")
print(json.dumps(res, indent=1))
