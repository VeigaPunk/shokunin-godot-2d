#!/usr/bin/env python3
"""r103-S2: AST-extract the 4 rows that consume r100b_seq.gd / r101_seqfull.gd
from corpus/fixtures/run_battery.py (which is NEVER executed), plus their
expected_errors entries. Emits rows.json for r103-S2-harness.py.

Rows: r100b_seq_clean, r100b_seq_noclean, r101_seqfull_clean, r101_seqfull_noclean.
"""
import ast
import json
import sys


def main(battery_path, out_path):
    src = open(battery_path).read()
    tree = ast.parse(src)
    cases = None
    errors_dict = None
    stderr_dict = None

    def dict_literal(value):
        if isinstance(value, ast.Dict):
            return ast.literal_eval(value)
        if isinstance(value, ast.Call) and isinstance(value.func, ast.Attribute) \
                and value.func.attr == "get" and isinstance(value.func.value, ast.Dict):
            return ast.literal_eval(value.func.value)
        return None

    for node in ast.walk(tree):
        if not isinstance(node, ast.Assign):
            continue
        for t in node.targets:
            if not isinstance(t, ast.Name):
                continue
            if t.id == "CASES":
                cases = ast.literal_eval(node.value)
            if t.id == "expected_errors":
                errors_dict = dict_literal(node.value) or errors_dict
            if t.id == "required_stderr":
                stderr_dict = dict_literal(node.value) or stderr_dict

    assert cases is not None, "CASES not found"
    want_scripts = {"r100b_seq.gd", "r101_seqfull.gd"}
    rows = []
    for c in cases:
        name, script, flags, exit_code, sig = c[0], c[1], c[2], c[3], c[4]
        if script not in want_scripts:
            continue
        rows.append({
            "name": name,
            "script": script,
            "flags": list(flags),
            "expected_exit": exit_code,
            "evidence": sig,
            "expected_errors": list((errors_dict or {}).get(name, ())),
            "required_stderr": list((stderr_dict or {}).get(name, ())),
        })
    json.dump(rows, open(out_path, "w"), indent=1)
    for r in rows:
        print(f"{r['name']:<24} {r['script']:<18} flags={r['flags']} exit={r['expected_exit']} "
              f"sig={len(r['evidence'])}B allow={len(r['expected_errors'])}")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
