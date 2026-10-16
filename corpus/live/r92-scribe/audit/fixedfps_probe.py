#!/usr/bin/env python3
"""r92-scribe: is the envelope's payload[1] branch reachable from the LANDED fixture?

Runs the landed `tilemap_lattice.gd --arm=nav` in the battery's exact launch
shape under (a) the default scheduler and (b) --fixed-fps {120,150,180,600},
then classifies each receipt with (i) the landed 2-payload envelope and
(ii) a payload[0]-only check (the pre-envelope scout row).
Receipts: corpus/live/r92-scribe/fixedfps/.
"""
import ast
import json
import shutil
import subprocess
from pathlib import Path

REPO = Path("/home/vgpnk/Projects/shokunin/game-dev-2d-shokunin")
LIVE = REPO / "corpus" / "live"
OUT = LIVE / "r92-scribe" / "fixedfps"
PROJ = LIVE / "r92-scribe" / "fixedfps-proj"

src = subprocess.run(["git", "show", "HEAD:corpus/fixtures/run_battery.py"], cwd=REPO,
                     capture_output=True, check=True).stdout.decode()
tree = ast.parse(src)
fn_src = None
for node in ast.walk(tree):
    if isinstance(node, ast.FunctionDef) and node.name == "classify_process":
        fn_src = "    " + ast.get_source_segment(src, node).replace("\n", "\n    ")
        break
ns = {}
exec("def _wrap():\n" + fn_src + "\n    return classify_process\n", ns)
classify_process = ns["_wrap"]()
cases = None
for node in tree.body:
    if isinstance(node, ast.Assign) and any(
            isinstance(t, ast.Name) and t.id == "CASES" for t in node.targets):
        cases = ast.literal_eval(node.value)
row = next(c for c in cases if c[0] == "r92_tilemap_nav")
payloads = list(row[4])

if not (PROJ / "project.godot").exists():
    PROJ.mkdir(parents=True, exist_ok=True)
    for item in (REPO / "corpus" / "fixtures").iterdir():
        if item.name == ".godot":
            continue
        (shutil.copytree if item.is_dir() else shutil.copy2)(item, PROJ / item.name)
OUT.mkdir(parents=True, exist_ok=True)

res = {}
for label, extra in [("default", []), ("ff120", ["--fixed-fps", "120"]),
                     ("ff150", ["--fixed-fps", "150"]), ("ff180", ["--fixed-fps", "180"]),
                     ("ff600", ["--fixed-fps", "600"])]:
    cmd = (["godot", "--headless", *extra, "--path", str(PROJ), "--script",
            "res://tilemap_lattice.gd", "--", "--arm=nav"])
    proc = subprocess.run(cmd, capture_output=True, text=True, timeout=40)
    (OUT / f"nav_{label}.out").write_text(proc.stdout)
    (OUT / f"nav_{label}.err").write_text(proc.stderr)
    (OUT / f"nav_{label}.rc").write_text(str(proc.returncode))
    line = next((l for l in proc.stdout.splitlines()
                 if l.startswith("PASS tilemap_lattice nav")), None)
    merged = proc.stdout + proc.stderr
    res[label] = {
        "rc": proc.returncode,
        "line": line,
        "match": ("payload0" if line == payloads[0] else
                  "payload1" if line == payloads[1] else "neither"),
        "envelope_accepts": bool(line) and any(
            classify_process(proc.returncode, None, merged, row[3], s) for s in payloads),
        "payload0_only_accepts": bool(line) and classify_process(
            proc.returncode, None, merged, row[3], payloads[0]),
        "regions_f2": (line.split("regions_f2=")[1].split()[0] if line
                       and "regions_f2=" in line else None),
        "command": " ".join(cmd),
    }

print(json.dumps(res, indent=1))
(Path(__file__).parent / "fixedfps_probe.json").write_text(json.dumps(res, indent=1))
