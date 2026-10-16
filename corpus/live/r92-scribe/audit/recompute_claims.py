#!/usr/bin/env python3
"""r92-scribe: recompute the dossier headline claims from on-disk receipts.

A. author battery runs1-5 (verdicts.json): row counts, verdict, r92 14/14,
   floor gate, dead-entry census, discriminations.
B. author fresh-reps (14 arms x 3): production classify_process with the
   landed row pins; byte-identity across reps; allowlist load-bearing.
C. boundary matrix receipts: production classifier over every
   <condition>_<arm>.rep<N>.out receipt in the 13-condition matrix.
D. scout canonical runs: out_uniq / err_uniq per cell.
Everything is recomputed from HEAD's harness (AST) and the receipt files.
"""
import ast
import hashlib
import json
import re
import subprocess
from collections import Counter, defaultdict
from pathlib import Path

REPO = Path(__file__).resolve().parents[4]
LIVE = REPO / "corpus" / "live"
src = subprocess.run(["git", "show", "HEAD:corpus/fixtures/run_battery.py"], cwd=REPO,
                     capture_output=True, check=True).stdout.decode()
tree = ast.parse(src)

# --- production classifier (verbatim segment) ---
fn_src = None
for node in ast.walk(tree):
    if isinstance(node, ast.FunctionDef) and node.name == "classify_process":
        seg = ast.get_source_segment(src, node)
        fn_src = "    " + seg.replace("\n", "\n    ")
        break
ns = {}
exec("def _wrap():\n" + fn_src + "\n    return classify_process\n", ns)
classify_process = ns["_wrap"]()
seg_sha = hashlib.sha256(fn_src.encode()).hexdigest()

cases = None
for node in tree.body:
    if isinstance(node, ast.Assign) and any(
            isinstance(t, ast.Name) and t.id == "CASES" for t in node.targets):
        cases = ast.literal_eval(node.value)
rows = {c[0]: c for c in cases}

ee = rs = None
for node in ast.walk(tree):
    if isinstance(node, ast.Assign):
        for t in node.targets:
            if isinstance(t, ast.Name) and t.id == "expected_errors":
                for sub in ast.walk(node.value):
                    if isinstance(sub, ast.Dict) and any(
                            isinstance(k, ast.Constant) and isinstance(k.value, str)
                            and k.value.startswith("r92_") for k in sub.keys):
                        ee = ast.literal_eval(sub)
            if isinstance(t, ast.Name) and t.id == "required_stderr":
                for sub in ast.walk(node.value):
                    if isinstance(sub, ast.Dict) and any(
                            isinstance(k, ast.Constant) and isinstance(k.value, str)
                            and k.value.startswith("r92_") for k in sub.keys):
                        rs = ast.literal_eval(sub)
assert ee is not None and rs is not None

R92 = {k: v for k, v in rows.items() if k.startswith("r92_")}
out = {"classify_process_segment_sha256": seg_sha}


def row_ok(name, code, stdout, stderr, bare=False):
    """Full harness pass condition for one landed row against a receipt."""
    case = rows[name]
    expected, sig = case[3], case[4]
    allowed = () if bare else tuple(ee.get(name, ()))
    merged = stdout + stderr
    sigs = sig if isinstance(sig, (tuple, list)) else (sig,)
    passed = any(classify_process(code, None, merged, expected, s, allowed) for s in sigs)
    if name in rs:
        frags = rs[name]
        passed = passed and all(f in stderr for f in frags) and any(s in stdout for s in sigs)
    return passed


# ------------------------------------------------------------------ A
author_runs = {}
for vj in sorted((LIVE / "r92-author").glob("runs*/**/verdicts.json")):
    data = json.loads(vj.read_text())
    res = data.get("results", data)
    recs = {r["case"]: r for r in res if isinstance(r, dict) and "case" in r}
    r92v = {k: recs[k]["verdict"] for k in R92 if k in recs}
    meta = {k: recs[k].get("verdict") for k in recs if k.startswith("probe_")}
    author_runs[vj.parent.name + "/" + vj.parent.parent.name] = {
        "rows": len(recs),
        "verdict": data.get("verdict"),
        "fails": [k for k, r in recs.items() if r.get("verdict") == "FAIL"],
        "r92_pass": sum(1 for v in r92v.values() if v == "PASS"),
        "r92_total": len(r92v),
        "gate": recs.get("r92_expected_errors_all_matched", {}).get("verdict"),
        "error_clause_meta": {k: v for k, v in meta.items() if "error_clause" in k or
                              "bare" in k or "expected_errors" in k},
        "error_clause_meta_detail": {
            k: {kk: vv for kk, vv in recs[k].items()
                if kk in ("dead_entry_count", "rows_with_expected_errors",
                          "census_bare_classifier_consistent")}
            for k in meta if k == "probe_error_clause_surface"},
    }
out["author_battery_runs"] = author_runs

# ------------------------------------------------------------------ B
fresh = defaultdict(dict)
for p in sorted((LIVE / "r92-author" / "fresh-reps").glob("*.out")):
    arm, rep = p.name[:-4].split(".")
    fresh[arm][rep] = {"stdout": p.read_text(errors="replace"),
                       "stderr": p.with_suffix(".err").read_text(errors="replace"),
                       "rc": int(p.with_suffix(".rc").read_text().strip())}
fresh_summary = {}
for arm, reps in sorted(fresh.items()):
    name = f"r92_tilemap_{'nullts_crash' if arm == 'nullts' else arm}"
    if name not in rows:
        fresh_summary[arm] = {"error": "no such row"}
        continue
    verdicts = {rep: row_ok(name, v["rc"], v["stdout"], v["stderr"])
                for rep, v in reps.items()}
    bare = {rep: row_ok(name, v["rc"], v["stdout"], v["stderr"], bare=True)
            for rep, v in reps.items()}
    fresh_summary[arm] = {
        "row": name,
        "rc": [v["rc"] for v in reps.values()],
        "pass": verdicts,
        "bare_pass": bare,
        "stdout_identical": len({v["stdout"] for v in reps.values()}) == 1,
        "stderr_identical": len({v["stderr"] for v in reps.values()}) == 1,
    }
out["author_fresh_reps"] = fresh_summary

# ------------------------------------------------------------------ C
MATRIX = ["q60", "l60", "f30", "f60", "f120", "f120l", "t120", "q60b", "f10",
          "f20", "f600", "f30l", "l32"]
ARM2ROW = {arm: f"r92_tilemap_{'nullts_crash' if arm == 'nullts' else arm}"
           for arm in ["census", "atlas", "cells", "custom", "terrain", "pattern",
                       "encoding", "fixinvalid", "srcids", "physics", "timing",
                       "quadrant", "nav"]}
pat = re.compile(r"^(" + "|".join(MATRIX) + r")_([a-z]+)\.rep(\d+)\.out$")
per_cond = defaultdict(lambda: {"checked": 0, "rejected": []})
per_cond_single = defaultdict(lambda: {"checked": 0, "rejected": []})
nav_row = rows["r92_tilemap_nav"]
nav_single = nav_row[4][0]


def row_ok_single(name, code, stdout, stderr):
    """Same as row_ok but with the pre-envelope single payload (scout ROWS)."""
    case = rows[name]
    expected, sig = case[3], nav_single if name == "r92_tilemap_nav" else case[4]
    allowed = tuple(ee.get(name, ()))
    merged = stdout + stderr
    passed = classify_process(code, None, merged, expected, sig, allowed)
    if name in rs:
        frags = rs[name]
        passed = passed and all(f in stderr for f in frags) and sig in stdout
    return passed


for p in sorted((LIVE / "r92-boundary" / "runs").iterdir()):
    m = pat.match(p.name)
    if not m:
        continue
    cond, arm = m.group(1), m.group(2)
    if arm not in ARM2ROW:
        continue
    rcf = p.with_suffix(".rc")
    code = int(rcf.read_text().strip()) if rcf.exists() else None
    stdout = p.read_text(errors="replace")
    stderr = p.with_suffix(".err").read_text(errors="replace")
    ok = row_ok(ARM2ROW[arm], code, stdout, stderr)
    per_cond[cond]["checked"] += 1
    if not ok:
        per_cond[cond]["rejected"].append(p.name)
    ok1 = row_ok_single(ARM2ROW[arm], code, stdout, stderr)
    per_cond_single[cond]["checked"] += 1
    if not ok1:
        per_cond_single[cond]["rejected"].append(p.name)
out["boundary_matrix"] = {k: v for k, v in per_cond.items()}
out["boundary_matrix_total"] = {
    "checked": sum(v["checked"] for v in per_cond.values()),
    "rejected": sum(len(v["rejected"]) for v in per_cond.values()),
    "rejected_files": [f for v in per_cond.values() for f in v["rejected"]],
}
out["boundary_matrix_pre_envelope_nav_payload0_only"] = {
    "checked": sum(v["checked"] for v in per_cond_single.values()),
    "rejected": sum(len(v["rejected"]) for v in per_cond_single.values()),
    "rejected_files": [f for v in per_cond_single.values() for f in v["rejected"]],
}

# ------------------------------------------------------------------ D
scout = defaultdict(lambda: {"out": set(), "err": set(), "rc": set(), "n": 0})
for p in sorted((LIVE / "r92-scout" / "runs").glob("r92_tm_*.rep*.out")):
    m = re.match(r"^r92_tm_([a-z]+)\.rep(\d+)\.out$", p.name)
    if not m:
        continue
    arm = m.group(1)
    scout[arm]["out"].add(p.read_text(errors="replace"))
    scout[arm]["err"].add(p.with_suffix(".err").read_text(errors="replace"))
    rcf = p.with_suffix(".rc")
    scout[arm]["rc"].add(rcf.read_text().strip() if rcf.exists() else None)
    scout[arm]["n"] += 1
out["scout_canonical"] = {arm: {"n": v["n"], "out_uniq": len(v["out"]),
                                "err_uniq": len(v["err"]), "rc": sorted(v["rc"])}
                          for arm, v in sorted(scout.items())}

print(json.dumps(out, indent=1)[:6000])
(Path(__file__).parent / "recompute_claims.json").write_text(json.dumps(out, indent=1))
