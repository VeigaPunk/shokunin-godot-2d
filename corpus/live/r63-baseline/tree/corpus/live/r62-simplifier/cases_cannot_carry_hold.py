#!/usr/bin/env python3
"""Prove a pipe-EOF TIMEOUT record cannot classify True under any CASES tuple.

ast-extracts classify_process VERBATIM from the tracked run_battery.py and feeds
it the exact record shape the r61 boundary probe measured for a descendant-held
pipe: actual_exit=None, error="TIMEOUT after N seconds", signature present in
output. If every int expected_exit classifies False, no CASES row can pin the
hold arm — the tracked surface needs a meta row (or a runner change).
"""
import ast
import hashlib
import json
from pathlib import Path

RUNNER = Path(__file__).resolve().parents[2] / "fixtures" / "run_battery.py"
src = RUNNER.read_text()
sha = hashlib.sha256(src.encode()).hexdigest()
tree = ast.parse(src)

func_src = None
for node in ast.walk(tree):
    if isinstance(node, ast.FunctionDef) and node.name == "classify_process":
        func_src = ast.get_source_segment(src, node)
        break
assert func_src is not None, "classify_process not found"
ns = {}
exec(func_src, ns)
classify_process = ns["classify_process"]

# r61 boundary 'hold' arm shape: child exited 0, descendant held pipes to bound.
hold_output = "TREE_PROBE: expected signature\nTREE_DESC_AFTER_PARENT_WRITE\n"
matrix = []
for expected_exit in (0, 1, 2, -6, -9, None):
    for error in ("TIMEOUT after 3 seconds", "TIMEOUT after 8 seconds", None):
        verdict = classify_process(None if error else 0, error, hold_output,
                                   expected_exit, "TREE_PROBE: expected signature")
        matrix.append({"expected_exit": expected_exit, "code": None if error else 0,
                       "error": error, "signature_present": True,
                       "classify": verdict})

# Control: same output, child exit observed normally -> classifies True.
control = classify_process(0, None, hold_output, 0, "TREE_PROBE: expected signature")
matrix.append({"expected_exit": 0, "code": 0, "error": None,
               "signature_present": True, "classify": control,
               "note": "control: exit observed -> True"})

all_timeout_false = all(m["classify"] is False for m in matrix if m["error"] is not None)
result = {"runner": str(RUNNER), "runner_sha256": sha,
          "extracted_function_lines": len(func_src.splitlines()),
          "all_timeout_records_classify_false": all_timeout_false,
          "control_exit0_classifies_true": control,
          "matrix": matrix}
out = Path(__file__).parent / "cases_cannot_carry_hold.json"
out.write_text(json.dumps(result, indent=2) + "\n")
print(json.dumps({"runner_sha256": sha,
                  "all_timeout_false": all_timeout_false,
                  "control_true": control,
                  "receipt": str(out)}, indent=2))
