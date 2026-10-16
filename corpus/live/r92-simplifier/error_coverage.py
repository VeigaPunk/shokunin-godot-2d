#!/usr/bin/env python3
"""r92-simplifier: ERROR:-line coverage census over fresh receipts.

For every r92 arm receipt in fold-runs/default/, enumerate the lines carrying
"ERROR:" and check each is absorbed by the row's expected_errors under the
production allowed_error semantics. Also checks the four entry-less rows emit
no ERROR: line at all.

Usage: python3 error_coverage.py
"""
import ast
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
FIX = HERE / "committed-fixtures" / "run_battery.py"
RUNS = HERE / "fold-runs" / "default"


def load_harness():
    src = FIX.read_text()
    tree = ast.parse(src)
    cases, exp = {}, {}
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign) and getattr(node.targets[0], "id", "") == "CASES":
            for elt in node.value.elts:
                t = ast.literal_eval(elt)
                if t[0].startswith("r92_"):
                    cases[t[0]] = t[2][0].split("=", 1)[1]
        if isinstance(node, ast.Dict):
            keys = [k.value for k in node.keys if isinstance(k, ast.Constant)]
            if "r92_tilemap_atlas" in keys and "nav_lattice_bake" in keys:
                for k, v in zip(node.keys, node.values):
                    if isinstance(k, ast.Constant) and k.value.startswith("r92_"):
                        exp[k.value] = ast.literal_eval(v)
    return cases, exp


def allowed_error(line, allowed):
    stripped = line.strip()
    if stripped == allowed:
        return True
    if allowed.endswith(","):
        return stripped.startswith(allowed) and stripped.count("ERROR:") == 1
    return False


def main():
    cases, exp = load_harness()
    uncovered_total = 0
    print("== ERROR: line coverage per r92 arm (fresh default receipts) ==")
    for case in sorted(cases):
        arm = cases[case]
        out = (RUNS / (arm + ".out")).read_text()
        err = (RUNS / (arm + ".err")).read_text()
        blob = out + err
        err_lines = [l for l in blob.splitlines() if "ERROR:" in l]
        entries = exp.get(case, ())
        uncovered = [l for l in err_lines
                     if not any(allowed_error(l, e) for e in entries)]
        uncovered_total += len(uncovered)
        print("  %-28s arm=%-11s ERROR_lines=%-2d entries=%d uncovered=%d"
              % (case, arm, len(err_lines), len(entries), len(uncovered)))
        for l in uncovered:
            print("      UNCOVERED: %s" % l.strip()[:140])
        if not entries:
            script_err = [l for l in err.splitlines() if "ERROR:" in l]
            print("      entry-less row stderr ERROR: lines: %d" % len(script_err))
            for l in err.splitlines():
                if "WARNING" in l:
                    print("      stderr WARNING: %s" % l.strip()[:140])
    print()
    print("TOTAL_UNCOVERED_ERROR_LINES=%d" % uncovered_total)
    return 0 if uncovered_total == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
