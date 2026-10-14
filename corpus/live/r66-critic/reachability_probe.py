#!/usr/bin/env python3
"""r66 critic reachability probe: census evidence by RUNNING cases, not grep.

For each grep-absent allowlist entry and each blob-scan clause, execute the
fixture (or a minimal crashing .gd) and record whether the clause/entry is
tripped by a reachable emission. Verbatim classify extraction identical to
clause_probe.py.
"""
import json
import re
import shutil
import subprocess
import sys
import textwrap
from pathlib import Path

ROOT = Path(__file__).resolve().parent
FIXTURES = ROOT.parent.parent / "fixtures"
GODOT = "/usr/bin/godot"
REACH = ROOT / "reach_proj"

# fresh fixture copy (mirrors run_battery.py's scratch copy)
if REACH.exists():
    shutil.rmtree(REACH)
shutil.copytree(FIXTURES, REACH, ignore=shutil.ignore_patterns(".godot", "out"))
(REACH / ".godot").mkdir(exist_ok=True)
(REACH / ".godot" / ".gdignore").write_text("")


def run(cmd, timeout=30, env=None):
    try:
        p = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout, env=env)
        return (p.stdout or "") + (p.stderr or ""), p.returncode
    except subprocess.TimeoutExpired as e:
        o = e.stdout.decode(errors="replace") if isinstance(e.stdout, bytes) else (e.stdout or "")
        r = e.stderr.decode(errors="replace") if isinstance(e.stderr, bytes) else (e.stderr or "")
        return o + r + "\n<TIMEOUT>", None


res = {}

# --- allowlist-entry reachability (run the actual case rows) ---
cases = [
    ("negative_transition", "controls/scene_transition_negative.gd", [], 1,
     ["ERROR: Can't change to a null scene. Use unload_current_scene() if you wish to unload it.",
      "ERROR: negative control: deliberately invalid scene destination rejected"]),
    ("camera_far_bound", "camera_limit.gd", ["--far-bound"], 2,
     ["ERROR: camera limit assertion failed: expected active center within right boundary and distinct from target"]),
    ("camera_far_bottom_bound", "camera_limit.gd", ["--far-bottom-bound"], 2,
     ["ERROR: camera limit assertion failed: expected active center within bottom boundary and distinct from target"]),
]
for name, script, flags, exp, allow_entries in cases:
    out, code = run([GODOT, "--headless", "--path", str(REACH),
                     "--script", "res://" + script, "--"] + flags, timeout=15)
    res[f"case_{name}"] = {
        "exit": code, "expected_exit": exp,
        "entries": [{"entry": e, "emitted_verbatim": e in out,
                     "emitting_line": next((l for l in out.splitlines()
                                            if e in l or (e.endswith(",") and e[:-1] in l)), None)}
                    for e in allow_entries],
        "all_error_lines": sorted({l.strip() for l in out.splitlines() if "ERROR:" in l}),
    }

# export_preset_missing: engine-emitted export error
miss = ROOT / "reach_missing"
if miss.exists():
    shutil.rmtree(miss)
shutil.copytree(REACH, miss, ignore=shutil.ignore_patterns(".godot", "out"))
(miss / "out").mkdir()
out, code = run([GODOT, "--headless", "--path", str(miss),
                 "--export-debug", "Missing preset", str(miss / "out" / "fixture.x86_64")], timeout=60)
res["case_export_preset_missing"] = {
    "exit": code,
    "entry": "ERROR: Invalid export preset name: Missing preset.",
    "emitted_verbatim": "ERROR: Invalid export preset name: Missing preset." in out,
    "all_error_lines": sorted({l.strip() for l in out.splitlines() if "ERROR:" in l}),
}

# --- blob-clause reachability: does Godot itself emit SCRIPT ERROR:/Parse Error:? ---
crash = REACH / "critic_crash.gd"
crash.write_text("extends SceneTree\n\nfunc _initialize() -> void:\n\tvar x = null\n\tx.nonexistent_method()\n\tquit(1)\n")
out, code = run([GODOT, "--headless", "--path", str(REACH),
                 "--script", "res://critic_crash.gd"], timeout=15)
res["blob_script_error_reachable"] = {
    "exit": code,
    "SCRIPT_ERROR_present": "SCRIPT ERROR:" in out,
    "lines": [l for l in out.splitlines() if "ERROR" in l or "Error" in l][:6],
}
parse = REACH / "critic_parse.gd"
parse.write_text("extends SceneTree\n\nfunc _initialize() -> void\n\tthis is not gdscript {{{\n")
out, code = run([GODOT, "--headless", "--path", str(REACH),
                 "--script", "res://critic_parse.gd"], timeout=15)
res["blob_parse_error_reachable"] = {
    "exit": code,
    "Parse_Error_present": "Parse Error:" in out,
    "SCRIPT_ERROR_present": "SCRIPT ERROR:" in out,
    "lines": [l for l in out.splitlines() if "ERROR" in l or "Error" in l][:6],
}
crash.unlink(); parse.unlink()

# --- prefix-entry dynamic tail: save_process_missing real emission shape ---
import os
env = os.environ.copy(); env["XDG_DATA_HOME"] = str(ROOT / "xdg")
(ROOT / "xdg").mkdir(exist_ok=True)
out, code = run([GODOT, "--headless", "--path", str(REACH),
                 "--script", "res://save_process.gd", "--", "--missing"], timeout=15, env=env)
res["save_process_missing_shape"] = {
    "exit": code,
    "error_lines": sorted({l.strip() for l in out.splitlines() if "ERROR:" in l}),
    "prefix_entry": "ERROR: SAVE PROCESS EXPECTED NEGATIVE: missing file rejected signature=FILE_NOT_FOUND,",
}

(ROOT / "reachability-results.json").write_text(json.dumps(res, indent=2) + "\n")
print(json.dumps(res, indent=1)[:7000])
