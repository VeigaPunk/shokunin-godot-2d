#!/usr/bin/env python3
"""r95-scribe floor-gate loudness + classifier properties.

Gate: extract `r95_expected_errors_all_matched` verbatim from
HEAD:corpus/fixtures/run_battery.py and evaluate it over synthetic census rows
(live entry, dead entry, mixed, dead non-r95 entry) and over a real run's
census rows.

Classifier properties (pre-existing, recorded so a future reader does not
over-read "signature pinned"): trailing token after the pin; PASS delivered on
stderr; destroyed signature control.
Read-only.
"""
import ast
import hashlib
import json
import re
import subprocess
from pathlib import Path

REPO = Path("/home/vgpnk/Projects/shokunin/game-dev-2d-shokunin")
LANE = REPO / "corpus/live/r95-scribe"

src = subprocess.run(["git", "show", "HEAD:corpus/fixtures/run_battery.py"],
                     cwd=REPO, capture_output=True, text=True).stdout
tree = ast.parse(src)


def find_gate():
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            for t in node.targets:
                if isinstance(t, ast.Name) and t.id == "sf_discriminations":
                    for k, v in zip(node.value.keys, node.value.values):
                        if ast.literal_eval(k) == "r95_expected_errors_all_matched":
                            return ast.get_source_segment(src, v), ast.unparse(v)
    raise SystemExit("gate not found")


seg, expr = find_gate()
ns = {}
exec("def gate_fn(census_rows):\n    return (" + expr + ")", ns)
gate = ns["gate_fn"]


def census(rows):
    return rows


def row(case, entries):
    return {"case": case,
            "entries": [{"entry": e, "dead_in_run": d} for e, d in entries]}


synthetic = {
    "live_r95_entry": census([row("dss_lattice_ray_flags", [("ERROR: x", False)])]),
    "dead_r95_entry": census([row("r95b_order_canon", [("ERROR: x", True)])]),
    "mixed_r95_entries": census([row("dss_lattice_shape", [("ERROR: x", False), ("ERROR: y", True)])]),
    "dead_non_r95_entry": census([row("phys2d_events_edge_node", [("ERROR: x", True)])]),
    "no_entries": census([row("dss_lattice_fresh", [])]),
    "empty_census": census([]),
}
synthetic_result = {k: gate(v) for k, v in synthetic.items()}

# real census from a battery run (latest green author run)
real = {}
vf = REPO / "corpus/live/runs/20261016T065922894811Z/verdicts.json"
if vf.exists():
    v = json.loads(vf.read_text())
    meta = next((r for r in v["results"] if r.get("case") == "probe_error_clause_surface"), {})
    rows = meta.get("census", {}).get("rows", [])
    real = {"rows": len(rows), "gate": gate(rows),
            "dead_entry_count": meta.get("census", {}).get("dead_entry_count"),
            "r95_rows_in_census": sum(1 for r in rows if str(r["case"]).startswith(
                ("dss_lattice_", "r95b_order_")))}

# ---- classifier properties -------------------------------------------------
def extract(name):
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == name:
            return ast.unparse(node)
    raise SystemExit(name)


ns2 = {}
exec(extract("classify_process"), ns2)
classify = ns2["classify_process"]

receipts = {}
for p in sorted((LANE / "fresh").glob("*.out")):
    receipts.setdefault(p.name.split(".")[0], p.read_text(errors="replace"))
for vf2 in sorted((LANE / "battery-runs").glob("*/verdicts.json")) + \
        sorted((LANE / "battery-committed").glob("*/verdicts.json")):
    v2 = json.loads(vf2.read_text())
    for r in v2["results"]:
        if str(r.get("case", "")).startswith(("dss_lattice_", "r95b_order_")):
            receipts.setdefault(r["case"], "\n".join(r.get("output") or []))
if vf.exists():
    for r in v["results"]:
        if str(r.get("case", "")).startswith(("dss_lattice_", "r95b_order_")):
            receipts.setdefault(r["case"], "\n".join(r.get("output") or []))

cases = []
for node in tree.body:
    if isinstance(node, ast.Assign):
        for t in node.targets:
            if isinstance(t, ast.Name) and t.id == "CASES":
                cases = [tuple(ast.literal_eval(e) for e in c.elts) for c in node.value.elts]
cases = [c for c in cases if str(c[0]).startswith(("dss_lattice_", "r95b_order_"))]

trailing_ok, stderr_ok, control_ok = 0, 0, 0
trailing_total, stderr_total, control_total = 0, 0, 0
for case, script, flags, exit_code, sig in cases:
    text = receipts.get(case)
    if text is None:
        continue
    i = text.find(sig)
    if i < 0:
        continue
    # 1. trailing token appended AFTER the pin on the same line
    j = text.find("\n", i)
    j = len(text) if j < 0 else j
    mutated = text[:j] + " trailing_token=1" + text[j:]
    trailing_total += 1
    trailing_ok += bool(classify(exit_code, None, mutated, exit_code, sig, ()))
    # 2. PASS line delivered on stderr only (merged-blob classification)
    body = text[:i] + text[i + len(sig):]
    stderr_only = body + "\n" + sig
    stderr_total += 1
    stderr_ok += bool(classify(exit_code, None, stderr_only, exit_code, sig, ()))
    # 3. control: signature destroyed
    control_total += 1
    control_ok += bool(classify(exit_code, None, text.replace(sig, "PASS destroyed", 1),
                                exit_code, sig, ()))

out = {
    "gate_segment_sha256": hashlib.sha256(seg.encode()).hexdigest(),
    "gate_expression": expr,
    "synthetic": synthetic_result,
    "real_census": real,
    "classifier_properties": {
        "rows": trailing_total,
        "trailing_token_after_pin_accepted": trailing_ok,
        "stderr_only_pass_accepted": stderr_ok,
        "control_destroyed_signature_accepted": control_ok,
    },
}
(LANE / "audit/floor_gate.json").write_text(json.dumps(out, indent=2, sort_keys=True))
print(json.dumps(out, indent=2)[:3000])
