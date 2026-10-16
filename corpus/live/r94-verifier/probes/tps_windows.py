#!/usr/bin/env python3
"""r94 verifier — the 60-tps-only window risk, measured directly.

The committed fixture's timing windows are internally `_okb(fin_delta, lo, hi)`
over physics ticks at the launch project's tps. The author declares them
"60-tps-only". This probe:
  1. builds scratch copies of the frozen fixtures with project.godot patched to
     `physics/common/physics_ticks_per_second = {30,120}` (default copy too);
  2. runs a tps reporter to prove the effective tps;
  3. runs the windowed arms under each project and records whether the committed
     boolean signature still holds (classify PASS/FAIL with production
     classify_process).
Writes only under corpus/live/r94-verifier/tps-probe/.
"""
import ast
import json
import pathlib
import re
import shutil
import subprocess
import sys
from datetime import datetime, timezone

ROOT = pathlib.Path("/home/vgpnk/Projects/shokunin/game-dev-2d-shokunin")
FREEZE = ROOT / "corpus/live/r94-verifier/freeze/corpus/fixtures"
OUT = ROOT / "corpus/live/r94-verifier/tps-probe"
OUT.mkdir(parents=True, exist_ok=True)
GODOT = "/usr/bin/godot"

src = (FREEZE / "run_battery.py").read_text()
tree = ast.parse(src)
fn_src = None
for node in ast.walk(tree):
    if isinstance(node, ast.FunctionDef) and node.name == "classify_process":
        fn_src = ast.get_source_segment(src, node)
        break
ns = {}
exec("import re\n" + fn_src, ns)
classify_process = ns["classify_process"]

import importlib.util
spec = importlib.util.spec_from_file_location("frozen_harness", FREEZE / "run_battery.py")
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
CASES = {c[0]: c for c in mod.CASES}

ARMS = ["census", "ppm", "convert", "cpu_lifetime", "cpu_expl", "cpu_speed_pre",
        "cpu_stop", "cpu_never", "cpu_contam", "cpu_oneshot_off", "cpu_oneshot_flag",
        "cpu_pause", "cpu_restart", "cpu_retrigger", "cpu_lt_mid", "cpu_speed_mid",
        "cpu_amount_mid", "cpu_request", "gpu_headless"]
REGIMES = [("default", None), ("tps30", 30), ("tps120", 120)]

REPORT = '''extends SceneTree
func _initialize() -> void:
	print("TPS_REPORT physics_ticks_per_second=", Engine.physics_ticks_per_second,
		" time_scale=", Engine.time_scale)
	quit(0)
'''

results = []
for label, tps in REGIMES:
    proj = OUT / f"proj-{label}"
    if proj.exists():
        shutil.rmtree(proj)
    proj.mkdir(parents=True)
    for item in FREEZE.iterdir():
        if item.name == "run_battery.py" or item.name.startswith("."):
            continue
        if item.is_dir():
            shutil.copytree(item, proj / item.name)
        else:
            shutil.copy2(item, proj / item.name)
    shutil.copy2(proj / "controls" / "pickup.tscn", proj / "pickup.tscn")
    pf = proj / "project.godot"
    text = pf.read_text()
    if tps is not None:
        text = text.rstrip() + f"\n\n[physics]\ncommon/physics_ticks_per_second={tps}\n"
        pf.write_text(text)
    (proj / "tps_report.gd").write_text(REPORT)
    p = subprocess.run([GODOT, "--headless", "--path", str(proj), "--script", "res://tps_report.gd"],
                       capture_output=True, text=True, timeout=30)
    line = next((l for l in p.stdout.splitlines() if l.startswith("TPS_REPORT")), None)
    print(f"[{label}] {line} rc={p.returncode}")
    results.append({"regime": label, "tps_requested": tps, "tps_report": line})
    for arm in ARMS:
        case = f"r94_particles_{arm}"
        c = CASES[case]
        cmd = [GODOT, "--headless", "--path", str(proj), "--script", "res://particles_lattice.gd", "--", f"--arm={arm}"]
        try:
            q = subprocess.run(cmd, capture_output=True, text=True, timeout=25)
            out, err, rc = q.stdout, q.stderr, q.returncode
        except subprocess.TimeoutExpired as exc:
            out = (exc.stdout or b"").decode(errors="replace") if isinstance(exc.stdout, bytes) else (exc.stdout or "")
            err = (exc.stderr or b"").decode(errors="replace") if isinstance(exc.stderr, bytes) else (exc.stderr or "")
            rc = None
        ok = classify_process(rc, None, out + err, 0, c[4], ())
        passline = next((l for l in out.splitlines() if l.startswith("PASS particles_lattice")), "")
        (OUT / f"{label}-{arm}.out").write_text(out)
        (OUT / f"{label}-{arm}.err").write_text(err)
        results.append({"regime": label, "arm": arm, "rc": rc, "verdict": "PASS" if ok else "FAIL",
                        "stderr_bytes": len(err.encode()), "line": passline[:400]})
        print(f"  [{label}] {case:34s} {'PASS' if ok else 'FAIL'} rc={rc} :: {passline[:160]}")

(OUT / "tps-windows.json").write_text(json.dumps(results, indent=1))
