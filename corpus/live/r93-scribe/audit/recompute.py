#!/usr/bin/env python3
"""r93-scribe dossier recompute + landed-row mutant test.

* extracts `classify_process` verbatim from HEAD:corpus/fixtures/run_battery.py
* recomputes scout / boundary / author headline claims from the committed
  receipts on disk
* classifies every r93 row against real receipts with the production
  classifier
* mutates each landed r93 signature (value-flips + appended conjuncts) and
  checks the classifier rejects every mutant
Writes JSON under corpus/live/r93-scribe/audit/.
"""
import ast
import hashlib
import json
import re
import subprocess
from collections import defaultdict
from pathlib import Path

REPO = Path("/home/vgpnk/Projects/shokunin/game-dev-2d-shokunin")
LIVE = REPO / "corpus/live"
OUT = REPO / "corpus/live/r93-scribe/audit/recompute.json"

src = subprocess.run(["git", "-C", str(REPO), "show",
                      "HEAD:corpus/fixtures/run_battery.py"],
                     capture_output=True, text=True).stdout
tree = ast.parse(src)
fn_src = None
for node in ast.walk(tree):
    if isinstance(node, ast.FunctionDef) and node.name == "classify_process":
        fn_src = ast.get_source_segment(src, node)
        break
assert fn_src
seg_sha = hashlib.sha256(fn_src.encode()).hexdigest()
ns = {}
exec("import re\n" + fn_src, ns)
classify = ns["classify_process"]
for node in ast.walk(tree):
    if isinstance(node, ast.Assign) and any(
            isinstance(t, ast.Name) and t.id == "CASES" for t in node.targets):
        CASES = ast.literal_eval(node.value)
R93 = [c for c in CASES if c[0].startswith("r93_")]

report = {"classifier_segment_sha256": seg_sha,
          "cases_total": len(CASES), "r93_rows": len(R93)}

# ------------------------------------------------------------- scout
SCOUT = LIVE / "r93-scout"
canon = sorted((SCOUT / "runs").glob("r93_*.rep*.out"))
load = sorted((SCOUT / "runs/loadtest").glob("r93_*.rep*.out"))
cells = defaultdict(lambda: {"canon": [], "load": [], "rc": set(), "err_bytes": set()})
for p in canon:
    cell = p.name.split(".rep")[0][len("r93_"):]
    cells[cell]["canon"].append(p)
for p in load:
    cell = p.name.split(".rep")[0][len("r93_"):]
    cells[cell]["load"].append(p)
for cell, d in cells.items():
    for p in d["canon"] + d["load"]:
        d["rc"].add(int(p.with_suffix(".rc").read_text().strip()))
        d["err_bytes"].add(p.with_suffix(".err").stat().st_size)
scout = {"canon_receipts": len(canon), "load_receipts": len(load),
         "cells": {}}
for cell, d in sorted(cells.items()):
    outs_c = {p.read_bytes() for p in d["canon"]}
    outs_l = {p.read_bytes() for p in d["load"]}
    scout["cells"][cell] = {
        "canon_reps": len(d["canon"]), "load_reps": len(d["load"]),
        "canon_uniq": len(outs_c), "load_uniq": len(outs_l),
        "rc": sorted(d["rc"]), "err_bytes": sorted(d["err_bytes"]),
        "canon_eq_load_bytes": bool(outs_c & outs_l) and len(outs_c) == 1 and len(outs_l) == 1}
report["scout"] = scout

# scout frozen rows re-classified against every scout receipt
rows_src = (SCOUT / "author-rows.py.txt").read_text()
rows_ns = {}
exec(rows_src, rows_ns)
SCOUT_ROWS = rows_ns.get("ROWS", [])
scout_checks = 0
scout_rejected = []
for (name, script, flags, expected_exit, signature) in SCOUT_ROWS:
    arm = flags[0].split("=", 1)[1]
    for p in cells[arm]["canon"] + cells[arm]["load"]:
        merged = p.read_text() + p.with_suffix(".err").read_text()
        rc = int(p.with_suffix(".rc").read_text().strip())
        scout_checks += 1
        if not classify(rc, None, merged, expected_exit, signature, ()):
            scout_rejected.append(f"{name}:{p.name}")
report["scout_frozen_rows"] = {"rows": len(SCOUT_ROWS), "checks": scout_checks,
                               "rejected": scout_rejected[:20],
                               "rejected_n": len(scout_rejected)}

# ------------------------------------------------------------- boundary
BOUND = LIVE / "r93-boundary"
batch_of = defaultdict(list)
for p in sorted((BOUND / "runs").glob("*.rep*.out")):
    stem = p.name.split(".rep")[0]
    if "_" not in stem:
        continue
    b, cell = stem.split("_", 1)
    batch_of[(b, cell)].append(p)
bnd = {"runs": sum(len(v) for v in batch_of.values()),
       "batches": defaultdict(int), "rc": set(), "err_bytes": set(),
       "cells": defaultdict(lambda: defaultdict(lambda: {"uniq": None}))}
for (b, cell), ps in batch_of.items():
    bnd["batches"][b] += len(ps)
    outs = {p.read_bytes() for p in ps}
    bnd["cells"][cell][b] = {"reps": len(ps), "uniq": len(outs)}
    for p in ps:
        bnd["rc"].add(int(p.with_suffix(".rc").read_text().strip()))
        bnd["err_bytes"].add(p.with_suffix(".err").stat().st_size)
bnd["batches"] = dict(bnd["batches"])
bnd["rc"] = sorted(bnd["rc"])
bnd["err_bytes"] = sorted(bnd["err_bytes"])
# compare boundary bytes to scout canonical for the scout cells
cross = {}
for cell in ("census", "tweenval", "tweenval_grid", "animtrack", "animmethod",
             "tweenchain", "animblend", "tweenstep", "animseek", "tweenproc", "animproc"):
    scout_bytes = {p.read_bytes() for p in cells.get(cell, {}).get("canon", [])}
    bnd_bytes = {p.read_bytes() for (b, c), ps in batch_of.items() if c == cell
                 for p in ps}
    cross[cell] = {"boundary_reps": sum(1 for (b, c) in batch_of if c == cell),
                   "boundary_uniq": len(bnd_bytes),
                   "scout_bytes_contained": bool(bnd_bytes & scout_bytes)}
bnd["cross_vs_scout"] = cross
report["boundary"] = json.loads(json.dumps(bnd, default=str))
report["boundary"]["cells"] = {c: dict(b) for c, b in bnd["cells"].items()}

# ------------------------------------------------------------- author
AUTH = LIVE / "r93-author"
fresh = sorted((AUTH / "fresh-reps").glob("*.rep*.out"))
fresh_arms = defaultdict(list)
for p in fresh:
    stem = p.name.split(".rep")[0]
    fixture, arm = stem.split(".", 1)
    fresh_arms[f"{fixture}:{arm}"].append(p)
auth = {"fresh_out_files": len(fresh), "arms": len(fresh_arms),
        "arm_reps": {k: len(v) for k, v in sorted(fresh_arms.items())},
        "rc": set(), "err_bytes": set()}
for p in fresh:
    auth["rc"].add(int(p.with_suffix(".rc").read_text().strip()))
    auth["err_bytes"].add(p.with_suffix(".err").stat().st_size)
auth["rc"] = sorted(auth["rc"])
auth["err_bytes"] = sorted(auth["err_bytes"])
# classify every r93 row against its 3 fresh reps
fresh_pass = 0
fresh_fail = []
for (name, script, flags, expected_exit, signature) in R93:
    arm = flags[0].split("=", 1)[1]
    key = f"{script.removesuffix('.gd')}:{arm}"
    for p in fresh_arms.get(key, []):
        merged = p.read_text() + p.with_suffix(".err").read_text()
        rc = int(p.with_suffix(".rc").read_text().strip())
        if classify(rc, None, merged, expected_exit, signature, ()):
            fresh_pass += 1
        else:
            fresh_fail.append(f"{name}:{p.name}")
auth["r93_classify_pass"] = fresh_pass
auth["r93_classify_total"] = sum(
    len(fresh_arms.get(f"{c[1].removesuffix('.gd')}:{c[2][0].split('=', 1)[1]}", []))
    for c in R93)
auth["r93_classify_fail"] = fresh_fail[:20]
# author battery runs
runs = {}
for i in (1, 2, 3):
    for vj in sorted((AUTH / f"runs{i}").glob("*/verdicts.json")):
        data = json.loads(vj.read_text())
        rows = data.get("results")
        r93v = [r for r in rows if r["case"].startswith("r93_")]
        meta = [r for r in rows if r["case"] == "probe_error_clause_surface"]
        disc = meta[0]["discriminations"] if meta else {}
        census = meta[0]["census"] if meta else {}
        runs[f"runs{i}:{vj.parent.name}"] = {
            "rows": len(rows),
            "verdict": data.get("verdict"),
            "n_pass": sum(1 for r in rows if r["verdict"] == "PASS"),
            "r93": {v: sum(1 for r in r93v if r["verdict"] == v)
                    for v in {r["verdict"] for r in r93v}},
            "fails": [r["case"] for r in rows if r["verdict"] != "PASS"],
            "gate_r93": disc.get("r93_expected_errors_all_matched"),
            "gate_r92": disc.get("r92_expected_errors_all_matched"),
            "dead_entry_count": census.get("dead_entry_count"),
            "rows_with_expected_errors": census.get("rows_with_expected_errors"),
            "census_bare_classifier_consistent":
                disc.get("census_bare_classifier_consistent"),
            "census_allowlisted_reproduces_verdicts":
                disc.get("census_allowlisted_reproduces_verdicts"),
        }
auth["battery_runs"] = runs
report["author"] = auth

# ------------------------------------------------------------- mutant test
mut = {"value_flips": 0, "boolean_flips": 0, "appended_conjuncts": 0,
       "rejected": 0, "accepted": [], "per_row": {}}
num_re = re.compile(r"=(-?\d+(?:\.\d+)?)")
bool_re = re.compile(r"=(true|false)\b")
for (name, script, flags, expected_exit, signature) in R93:
    arm = flags[0].split("=", 1)[1]
    key = f"{script.removesuffix('.gd')}:{arm}"
    recs = fresh_arms.get(key, [])
    if not recs:
        continue
    p = recs[0]
    merged = p.read_text() + p.with_suffix(".err").read_text()
    rc = int(p.with_suffix(".rc").read_text().strip())
    n_flip = 0
    # value flips: mutate one numeric token at a time (up to 8 per row)
    seen = set()
    for m in num_re.finditer(signature):
        tok = m.group(1)
        if tok in seen:
            continue
        seen.add(tok)
        if len(seen) > 8:
            break
        try:
            float(tok)
        except ValueError:
            continue
        new = ("9" if "." in tok else "9") + tok if not tok.startswith("-") else tok[1:] + "9"
        mutated = signature[:m.start(1)] + new + signature[m.end(1):]
        mut["value_flips"] += 1
        if classify(rc, None, merged, expected_exit, mutated, ()):
            mut["accepted"].append({"row": name, "kind": "value_flip",
                                    "token": tok, "mutant": mutated[:80]})
        else:
            mut["rejected"] += 1
        n_flip += 1
    # boolean flips: every true/false token, one at a time
    seen_b = set()
    for m in bool_re.finditer(signature):
        tok = m.group(1)
        if tok in seen_b:
            continue
        seen_b.add(tok)
        new = "false" if tok == "true" else "true"
        mutated = signature[:m.start(1)] + new + signature[m.end(1):]
        mut["boolean_flips"] += 1
        if classify(rc, None, merged, expected_exit, mutated, ()):
            mut["accepted"].append({"row": name, "kind": "boolean_flip",
                                    "token": tok})
        else:
            mut["rejected"] += 1
    # appended conjunct: extend the pin with a never-emitted clause
    for suffix in (" r93_forge=1", " forged=1"):
        mutated = signature + suffix
        mut["appended_conjuncts"] += 1
        if classify(rc, None, merged, expected_exit, mutated, ()):
            mut["accepted"].append({"row": name, "kind": "append",
                                    "suffix": suffix})
        else:
            mut["rejected"] += 1
    mut["per_row"][name] = {"value_flips": n_flip,
                            "boolean_flips": len(seen_b)}
report["mutants"] = {k: v for k, v in mut.items() if k != "per_row"}
report["mutants"]["total"] = (mut["value_flips"] + mut["boolean_flips"]
                              + mut["appended_conjuncts"])

OUT.write_text(json.dumps(report, indent=1, sort_keys=True, default=str))
print(json.dumps({k: v for k, v in report.items() if k not in ("mutants",)},
                 indent=1, sort_keys=True, default=str)[:7000])
print("MUTANTS:", json.dumps(report["mutants"], indent=1)[:3000])
