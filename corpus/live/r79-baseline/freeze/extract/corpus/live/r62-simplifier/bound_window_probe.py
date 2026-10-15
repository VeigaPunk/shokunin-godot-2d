#!/usr/bin/env python3
"""Measure the bound window in which the hold arm misattributes.

The tracked meta uses bound 3.0s; the CASES driver bound is 8s; the fixture's
descendant holds pipes ~7s (sleep 1 + echo + sleep 6). Prediction: under a
bound > ~7s, run_process returns the child's exit 0 at ~descendant-exit time —
the same fixture arm PASSES slowly and pins nothing. That would double-confirm
the hold arm cannot be a CASES row (wrong behavior under the CASES bound) and
that the meta's bound choice is load-bearing, not arbitrary.

Uses the verbatim tracked run_process via ast extraction, against the tracked
fixture copied into a scratch project dir.
"""
import ast
import json
import shutil
import subprocess
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
proj = HERE / "proj"
proj.mkdir(exist_ok=True)
for name in ("project.godot", "descendant_pipe_probe.gd"):
    shutil.copy2(REPO / "corpus" / "fixtures" / name, proj / name)

src = (REPO / "corpus" / "fixtures" / "run_battery.py").read_text()
tree = ast.parse(src)
ns = {"subprocess": subprocess}
for node in ast.walk(tree):
    if isinstance(node, ast.FunctionDef) and node.name in ("run_process", "classify_process"):
        exec(ast.get_source_segment(src, node), ns)
run_process = ns["run_process"]
classify_process = ns["classify_process"]

cmd = ["godot", "--headless", "--path", str(proj), "--script",
       "res://descendant_pipe_probe.gd", "--", "--spawn-hold"]
results = []
for bound in (8.0,):
    t0 = time.monotonic()
    output, code, error = run_process(cmd, bound)
    elapsed = time.monotonic() - t0
    verdict = classify_process(code, error, output, 0,
                               "DESCENDANT_PIPE_PROBE: expected signature")
    results.append({"bound": bound, "actual_exit": code, "error": error,
                    "elapsed_seconds": round(elapsed, 3),
                    "marker": "DESCENDANT_PIPE_PROBE: expected signature" in output,
                    "post_exit_write": "DESCENDANT_PIPE_AFTER_EXIT_WRITE" in output,
                    "classify": verdict})
    print(json.dumps(results[-1]))

out = HERE / "bound_window.json"
out.write_text(json.dumps({"results": results}, indent=2) + "\n")
print("receipt:", out)
