#!/usr/bin/env python3
"""r96-scout end-to-end smoke: run the probe exactly the way run_battery does.

Builds a scratch project (fixture dir copied, project renamed with a stamp so the
user:// dir is isolated), drops the frozen probe in as res://scene_io_lattice.gd,
launches every arm under the battery's own 8 s bound, merges stdout+stderr exactly
like run_battery's run_process, and classifies each receipt with the production
classify_process + the author rows (signature + expected_errors).
"""
import ast
import datetime
import hashlib
import pathlib
import shutil
import subprocess
import sys

HERE = pathlib.Path(__file__).parent
FIXTURES = HERE.parent.parent / "fixtures"
PROBE = HERE / "probes" / "scene_io_lattice.gd"

src = (FIXTURES / "run_battery.py").read_text()
tree = ast.parse(src)
fn_src = next(ast.get_source_segment(src, n) for n in ast.walk(tree)
              if isinstance(n, ast.FunctionDef) and n.name == "classify_process")
ns = {}
exec("import re\n" + fn_src, ns)
classify_process = ns["classify_process"]
seg_sha = hashlib.sha256(fn_src.encode()).hexdigest()

rows_ns = {}
exec((HERE / "author-rows.py.txt").read_text(), rows_ns)
ROWS = rows_ns["ROWS"]
EXPECTED = rows_ns["EXPECTED_ERRORS"]

stamp = datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
run_dir = HERE / "runs" / "smoke" / stamp
scratch = run_dir / "scratch"
scratch.mkdir(parents=True)
for item in FIXTURES.iterdir():
    if item.name == "run_battery.py" or item.name.startswith("."):
        continue
    if item.is_dir():
        shutil.copytree(item, scratch / item.name)
    else:
        shutil.copy2(item, scratch / item.name)
project_file = scratch / "project.godot"
project_file.write_text(project_file.read_text().replace(
    'config/name="MechanicOneShotTest"',
    f'config/name="MechanicOneShotTest-{stamp}"', 1))
shutil.copy2(PROBE, scratch / "scene_io_lattice.gd")

results = []
for case, script, flags, expected_exit, sig in ROWS:
    command = ["godot", "--headless", "--path", str(scratch), "--script", "res://" + script, "--", *flags]
    try:
        proc = subprocess.run(command, capture_output=True, text=True, timeout=8)
        output, code, error = proc.stdout + proc.stderr, proc.returncode, None
    except subprocess.TimeoutExpired as exc:
        output = (exc.stdout or "") + (exc.stderr or "")
        code, error = None, "TIMEOUT after 8 seconds"
    ok = classify_process(code, error, output, expected_exit, sig, EXPECTED.get(case, ()))
    results.append(ok)
    print(f"{'PASS' if ok else 'FAIL'} {case}: exit={code} error={error!r}")
    if not ok:
        (run_dir / f"{case}.fail.txt").write_text(output)

print(f"smoke: {sum(results)}/{len(results)} rows classified PASS")
print(f"classify_process segment sha256={seg_sha[:16]}  scratch={scratch}")
sys.exit(0 if all(results) else 1)
