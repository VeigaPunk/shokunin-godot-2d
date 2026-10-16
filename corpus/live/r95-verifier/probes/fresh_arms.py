#!/usr/bin/env python3
"""Fresh-process runs of the 52 r95 arms in the battery's exact launch shape
on the frozen committed fixture bytes. 3 reps each; production classifier.
"""
import importlib.util
import json
import shutil
import subprocess
import sys
import time
from pathlib import Path

FIX = Path(sys.argv[1])          # frozen corpus/fixtures
VDIR = Path(sys.argv[2])         # receipts dir
GODOT = sys.argv[3] if len(sys.argv) > 3 else "godot"

spec = importlib.util.spec_from_file_location("frozen_run_battery", FIX / "run_battery.py")
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
cases = [c for c in mod.CASES if c[0].startswith(("dss_lattice_", "r95b_order_"))]

import ast, hashlib
src = (FIX / "run_battery.py").read_text()
tree = ast.parse(src)
for node in ast.walk(tree):
    if isinstance(node, ast.FunctionDef) and node.name == "classify_process":
        cls_src = ast.get_source_segment(src, node)
ns = {}
exec(cls_src, ns)
classify_process = ns["classify_process"]

scratch = VDIR / "scratch-arms"
if scratch.exists():
    shutil.rmtree(scratch)
scratch.mkdir(parents=True)
for item in FIX.iterdir():
    if item.name == "run_battery.py" or item.name.startswith("."):
        continue
    if item.is_dir():
        shutil.copytree(item, scratch / item.name)
    else:
        shutil.copy2(item, scratch / item.name)
project_file = scratch / "project.godot"
text = project_file.read_text().replace('config/name="MechanicOneShotTest"',
                                        'config/name="MechanicOneShotTest-r95-verifier"', 1)
project_file.write_text(text)
shutil.copy2(scratch / "controls" / "pickup.tscn", scratch / "pickup.tscn")
chain = scratch / "causal_chain.gd"
text = chain.read_text()
anchor = "    await process_frame\n    var old := current_scene"
assert anchor in text
chain.write_text(text.replace(anchor, "    await process_frame\n    await process_frame\n    var old := current_scene", 1))

arms_dir = VDIR / "arms"
arms_dir.mkdir(exist_ok=True)
rows = []
for case in cases:
    name, script, flags, expected_exit, sig = case
    command = [GODOT, "--headless", "--path", str(scratch), "--script", "res://" + script, "--", *flags]
    per = {"case": name, "reps": []}
    for rep in (1, 2, 3):
        t0 = time.monotonic()
        try:
            proc = subprocess.run(command, capture_output=True, text=True, timeout=8)
            out, err, code, error = proc.stdout, proc.stderr, proc.returncode, None
        except subprocess.TimeoutExpired as exc:
            out = (exc.stdout or "").decode(errors="replace") if isinstance(exc.stdout, bytes) else (exc.stdout or "")
            err = (exc.stderr or "").decode(errors="replace") if isinstance(exc.stderr, bytes) else (exc.stderr or "")
            code, error = None, "TIMEOUT after 8 seconds"
        except OSError as exc:
            out, err, code, error = "", "", None, f"launch error: {exc}"
        wall = round(time.monotonic() - t0, 3)
        merged = out + err
        passed = classify_process(code, error, merged, expected_exit, sig, ())
        stem = arms_dir / f"{name}.rep{rep}"
        Path(str(stem) + ".out").write_text(out)
        Path(str(stem) + ".err").write_text(err)
        Path(str(stem) + ".rc").write_text(f"{code}\n")
        Path(str(stem) + ".wall_ms").write_text(f"{wall}\n")
        per["reps"].append({"rep": rep, "rc": code, "error": error, "stderr_bytes": len(err.encode()),
                            "wall_s": wall, "pass": passed, "sig_exact_line": sig in out.splitlines()})
    per["all_pass"] = all(r["pass"] for r in per["reps"])
    per["max_wall_s"] = max(r["wall_s"] for r in per["reps"])
    per["total_stderr_bytes"] = sum(r["stderr_bytes"] for r in per["reps"])
    rows.append(per)

summary = {"godot": GODOT, "scratch": str(scratch), "rows": rows,
           "all_pass": all(r["all_pass"] for r in rows),
           "failures": [r["case"] for r in rows if not r["all_pass"]],
           "slowest": sorted(((r["max_wall_s"], r["case"]) for r in rows), reverse=True)[:5],
           "nonzero_stderr_rows": [r["case"] for r in rows if r["total_stderr_bytes"]],
           "nonexact_rows": [r["case"] for r in rows
                             if not all(x["sig_exact_line"] for x in r["reps"])]}
(VDIR / "probes" / "fresh-arms.json").write_text(json.dumps(summary, indent=2) + "\n")
print(json.dumps({k: summary[k] for k in
                  ("all_pass", "failures", "slowest", "nonzero_stderr_rows", "nonexact_rows")},
                 indent=2))
