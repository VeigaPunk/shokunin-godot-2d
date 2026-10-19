#!/usr/bin/env python3
"""r103-ver6: extract CASES rows for one fixture from run_battery.py (AST only; never executed).

Reuses the r102-S3 extractor (CASES literal + expected_errors/required_stderr dicts).
"""
import argparse
import importlib.util
import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[3]
spec = importlib.util.spec_from_file_location(
    "s3v", ROOT / "reports/round-102/mutations/r102-S3-verify.py")
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

ap = argparse.ArgumentParser()
ap.add_argument("--src", required=True)
ap.add_argument("--fixture", required=True)
ap.add_argument("--rows", required=True)
a = ap.parse_args()

cases, ee, rs = m.extract_cases(a.src)
rows = []
for name, script, flags, expected_exit, evidence in cases:
    if script == a.fixture:
        rows.append({"name": name, "fixture": script, "flags": list(flags),
                     "expected_exit": expected_exit,
                     "evidence": list(evidence) if isinstance(evidence, (list, tuple)) else evidence,
                     "ee": list(ee.get(name, ())), "rs": list(rs.get(name, ()))})
pathlib.Path(a.rows).write_text(json.dumps(rows, indent=1))
print(f"extracted rows={len(rows)} for {a.fixture}")
for r in rows:
    print(f"  {r['name']:34s} flags={r['flags']} exit={r['expected_exit']} ee={len(r['ee'])} rs={len(r['rs'])}")
