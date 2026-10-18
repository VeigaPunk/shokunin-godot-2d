#!/usr/bin/env python3
"""r102-w6: cases_integrity existence probe for the export_launch_ prefix.

Evaluates the EXACT cases_integrity expression (ast.get_source_segment) from the
live corpus/fixtures/run_battery.py under counterfactual CASES/results inputs.
Read-only: never executes the battery. Works pre- and post-splice:
  PRE-SPLICE  -> expr_prop = expr + "export_launch_" appended to the prefix tuple
  POST-SPLICE -> expr already carries the prefix; expr_prop == expr
Run from the repo:  python3 reports/round-102/mutations/w6_cases_integrity_probe.py
"""
import ast
import json
import importlib.util
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
COPY = REPO / "corpus/fixtures/run_battery.py"
REAL_RUN = REPO / "corpus/live/runs/20261018T202131127599Z/verdicts.json"

src = COPY.read_text()
tree = ast.parse(src)
expr_src = None
prefix_tuple = None
for node in ast.walk(tree):
    if isinstance(node, ast.Dict):
        for k, v in zip(node.keys, node.values):
            if isinstance(k, ast.Constant) and k.value == "cases_integrity":
                expr_src = ast.get_source_segment(src, v)
                for sub in ast.walk(v):
                    if isinstance(sub, ast.Tuple) and all(
                            isinstance(e, ast.Constant) and isinstance(e.value, str)
                            for e in sub.elts):
                        if len(sub.elts) >= 5:
                            prefix_tuple = tuple(e.value for e in sub.elts)
assert expr_src and prefix_tuple
print("SOURCE=%s" % COPY)
print("EXPR_BYTES=%d PREFIX_N=%d" % (len(expr_src), len(prefix_tuple)))
print("PREFIXES:", prefix_tuple)
print("expr has export_launch_:", "export_launch_" in expr_src)

if "export_launch_" in expr_src:
    expr_prop = expr_src
    print("MODE=POST-SPLICE (prefix already landed)")
else:
    old_tail = '"r101_seqfull_", "r101_ytrans_", "export_prod_"))'
    new_tail = ('"r101_seqfull_", "r101_ytrans_", "export_prod_",\n'
                '                          "export_launch_"))')
    assert expr_src.count(old_tail) == 1, "tail anchor not unique"
    expr_prop = expr_src.replace(old_tail, new_tail)
    print("MODE=PRE-SPLICE (prefix absent; prop = curated patch)")

spec = importlib.util.spec_from_file_location("rb_w6", COPY)
rb = importlib.util.module_from_spec(spec)
spec.loader.exec_module(rb)  # module import only; main() guarded by __main__
cases = [c[0] for c in rb.CASES]
print("REAL_CASES_N=%d UNIQUE=%d" % (len(cases), len(set(cases))))
print("existing_export_launch_named:", [c for c in cases if c.startswith("export_launch")])
print("export_prod_n:", sum(1 for c in cases if c.startswith("export_prod_")))


def gate(expr, cases_list, results_list):
    ns = {"CASES": [(c,) for c in cases_list],
          "results": [{"case": c} for c in results_list],
          "__builtins__": {"len": len, "any": any, "all": all}}
    return eval("(" + expr + ")", ns)


base_results = [p + "row" for p in prefix_tuple] + ["probe_error_clause_surface"]
launch6 = ["export_launch_s0%d_arm" % i for i in range(1, 7)]


def cell(label, expr, cl, rl):
    v = gate(expr, cl, rl)
    print("CELL %-58s -> %s" % (label, v))
    return v


r = {}
r["A"] = cell("A cur tuple, no launch rows (baseline)", expr_src, cases, base_results)
r["B1"] = cell("B1 cur tuple, full launch splice simulated", expr_src, cases + launch6,
               base_results + launch6)
r["B2"] = cell("B2 cur tuple, launch drop-mutant (dropped from both)", expr_src, cases,
               base_results)
r["C"] = cell("C prop tuple, full launch splice", expr_prop, cases + launch6,
              base_results + launch6)
r["D"] = cell("D prop tuple, rows absent (tuple-only splice)", expr_prop, cases,
              base_results)
r["E"] = cell("E prop tuple, rows renamed export_lanch_*", expr_prop,
              cases + [n.replace("export_launch_", "export_lanch_") for n in launch6],
              base_results + [n.replace("export_launch_", "export_lanch_") for n in launch6])
r["F"] = cell("F prop tuple, rows named r102_export_launch_s0N", expr_prop,
              cases + ["r102_" + n for n in launch6],
              base_results + ["r102_" + n for n in launch6])
r["G"] = cell("G prop tuple, PARTIAL drop (3 of 6 rows left)", expr_prop,
              cases + launch6[:3], base_results + launch6[:3])
r["H"] = cell("H prop tuple, row named exactly export_launch", expr_prop,
              cases + ["export_launch"], base_results + ["export_launch"])
print("I  probe_export_launch.startswith('export_launch_') =",
      "probe_export_launch".startswith("export_launch_"))
print("I2 nested arm labels matching prefix (not top-level results):",
      [c for c in ["export_launch_positive", "export_launch_missing_startup_event"]
       if c.startswith("export_launch_")])

if REAL_RUN.exists():
    payload = json.loads(REAL_RUN.read_text())
    real = [row["case"] for row in payload["results"]]
    print("REAL_R101_ROWS=%d" % len(real))
    r["J1"] = cell("J1 cur tuple over REAL r101 results", expr_src, real, real)
    r["J2"] = cell("J2 prop tuple over REAL r101 results (no launch rows yet)", expr_prop,
                   real, real)
    r["J3"] = cell("J3 prop tuple over REAL r101 results + simulated launch rows",
                   expr_prop, real + launch6, real + launch6)
else:
    print("REAL_RUN missing:", REAL_RUN)
print("MATRIX:", {k: v for k, v in r.items()})
