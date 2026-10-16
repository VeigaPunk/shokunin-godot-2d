#!/usr/bin/env python3
"""Signature coverage: every canonical receipt of an r95 row's own arm is
re-classified with the production classifier (AST-extracted from the frozen
committed harness) and must contain the committed signature byte-exactly.

Also: provenance of the 17 dss_lattice signatures against the scout's
ROWS / ROWS_PREFIX tables, and per-row exact-whole-line stats for the 35
r95b rows against the boundary receipts.
"""
import ast
import importlib.util
import json
import sys
from collections import defaultdict
from pathlib import Path

REPO = Path("/home/vgpnk/Projects/shokunin/game-dev-2d-shokunin")
FIX = Path(sys.argv[1])                      # frozen corpus/fixtures
OUT = Path(sys.argv[2])
EXTRA_RECEIPT_DIRS = [Path(p) for p in sys.argv[3:]]

spec = importlib.util.spec_from_file_location("frozen_run_battery", FIX / "run_battery.py")
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

# --- production classifier, AST-extracted from the frozen harness ---------
tree = ast.parse((FIX / "run_battery.py").read_text())
cls_src = None
for node in ast.walk(tree):
    if isinstance(node, ast.FunctionDef) and node.name == "classify_process":
        cls_src = ast.get_source_segment((FIX / "run_battery.py").read_text(), node)
ns = {}
exec(cls_src, ns)
classify_process = ns["classify_process"]
import hashlib
cls_sha = hashlib.sha256(cls_src.encode()).hexdigest()

# --- scout ROWS / ROWS_PREFIX --------------------------------------------
scout_rows = {}
scout_ns = {}
exec((REPO / "corpus/live/r95-scout/author-rows.py.txt").read_text(), scout_ns)
for name, table in (("ROWS", scout_ns["ROWS"]), ("ROWS_PREFIX", scout_ns["ROWS_PREFIX"])):
    for entry in table:
        scout_rows.setdefault(name, {})[entry[0]] = entry

cases = {c[0]: c for c in mod.CASES}
r95 = {n: c for n, c in cases.items()
       if n.startswith(("dss_lattice_", "r95b_order_"))}

def cell_of(name, flags):
    if name.startswith("r95b_order_"):
        return name[len("r95b_order_"):], None
    arm = next((f.split("=", 1)[1] for f in flags if f.startswith("--arm=")), None)
    rev = "--rev" in flags
    return arm + ("_rev" if rev else ""), arm

def receipt_files(name, flags, receipt_root):
    cell, _ = cell_of(name, flags)
    if name.startswith("dss_lattice_"):
        out = sorted((receipt_root / "r95-scout/runs").glob(f"r95_dss_{cell}.rep*.out"))
        out += sorted((receipt_root / "r95-scout/runs/loadtest").glob(f"dss_{cell}.rep*.out"))
    else:
        out = sorted((receipt_root / "r95-boundary/runs").glob(f"*/{cell}.rep*.out"))
    return out

def classify_receipt(out_path):
    stem = out_path.parent / out_path.name[:-len(".out")]
    err_path = Path(str(stem) + ".err")
    rc_path = Path(str(stem) + ".rc")
    code = int(rc_path.read_text().strip()) if rc_path.exists() else None
    output = out_path.read_text() + (err_path.read_text() if err_path.exists() else "")
    return code, output

rows = []
receipt_root = REPO / "corpus/live"
totals = defaultdict(int)
for name, case in sorted(r95.items()):
    sig = case[4]
    recs = receipt_files(name, case[2], receipt_root)
    for d in EXTRA_RECEIPT_DIRS:
        recs += sorted(d.glob(f"**/{name}.rep*.out"))
    row = {"case": name, "signature_len": len(sig), "receipts": len(recs),
           "exact": 0, "sub": 0, "miss": 0, "pass": 0, "reject": 0,
           "distinct_full_lines": 0}
    full_lines = set()
    for r in recs:
        code, output = classify_receipt(r)
        if classify_process(code, None, output, case[3], sig, ()):
            row["pass"] += 1
        else:
            row["reject"] += 1
        lines = output.splitlines()
        if any(l == sig for l in lines):
            row["exact"] += 1
        elif sig in output:
            row["sub"] += 1
        else:
            row["miss"] += 1
        for l in lines:
            if l.startswith(sig[:min(len(sig), 60)]):
                full_lines.add(l)
    row["distinct_full_lines"] = len(full_lines)
    # provenance
    if name.startswith("dss_lattice_"):
        prow = scout_rows["ROWS_PREFIX"].get(name)
        row["equals_ROWS_PREFIX"] = (prow is not None and prow[4] == sig)
        frow = scout_rows["ROWS"].get(name)
        row["is_prefix_of_ROWS"] = (frow is not None and frow[4].startswith(sig))
        row["ROWS_full_line_len"] = len(frow[4]) if frow else None
    rows.append(row)
    for k in ("exact", "sub", "miss", "pass", "reject"):
        totals[k] += row[k]

summary = {"classifier_sha256": cls_sha, "rows": rows, "totals": dict(totals),
           "rows_with_miss": [r["case"] for r in rows if r["miss"]],
           "rows_with_reject": [r["case"] for r in rows if r["reject"]],
           "rows_with_sub_only": [r["case"] for r in rows if r["sub"] and not r["exact"]],
           "dss_prefix_mismatches": [r["case"] for r in rows
                                     if r["case"].startswith("dss_lattice_")
                                     and not r.get("equals_ROWS_PREFIX")],
           "dss_not_prefix_of_rows": [r["case"] for r in rows
                                      if r["case"].startswith("dss_lattice_")
                                      and not r.get("is_prefix_of_ROWS")],
           "r95b_not_exact_everywhere": [r["case"] for r in rows
                                         if r["case"].startswith("r95b_order_")
                                         and r["sub"] > 0],
           "r95b_multi_full_lines": [r["case"] for r in rows
                                     if r["case"].startswith("r95b_order_")
                                     and r["distinct_full_lines"] > 1],
           }
OUT.write_text(json.dumps(summary, indent=2) + "\n")
print(json.dumps({k: summary[k] for k in
                  ("classifier_sha256", "totals", "rows_with_miss", "rows_with_reject",
                   "rows_with_sub_only", "dss_prefix_mismatches", "dss_not_prefix_of_rows",
                   "r95b_not_exact_everywhere", "r95b_multi_full_lines")}, indent=2))
print(f"receipt instances: {sum(r['receipts'] for r in rows)}")
