#!/usr/bin/env python3
"""End-to-end: run the real Godot binary, capture stdout/stderr with the same
subprocess.run(capture_output=True) shape the battery uses, then feed BOTH
verbatim classifiers the same captured bytes."""
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from verbatim_classifiers import classify_process, classify_streams

ROOT = HERE.parents[2]
FIXTURES = ROOT / "corpus" / "fixtures"
SCRATCH = HERE / "e2e-scratch"
SIG = "CRITIC_E2E: expected marker"
GODOT = "godot"

def setup():
    if SCRATCH.exists():
        shutil.rmtree(SCRATCH)
    SCRATCH.mkdir(parents=True)
    shutil.copy2(FIXTURES / "project.godot", SCRATCH / "project.godot")
    shutil.copy2(HERE / "critic_e2e_probe.gd", SCRATCH / "critic_e2e_probe.gd")

def run_streams(flags):
    env = dict(os.environ)
    xdg = (HERE / "xdg-data").resolve()
    xdg.mkdir(exist_ok=True)
    env["XDG_DATA_HOME"] = str(xdg)
    cmd = [GODOT, "--headless", "--path", str(SCRATCH), "--script",
           "res://critic_e2e_probe.gd", "--", *flags]
    proc = subprocess.run(cmd, capture_output=True, text=True, timeout=15, env=env)
    return cmd, proc.stdout, proc.stderr, proc.returncode

def main():
    setup()
    rows = []
    for label, flags in [
        ("clean_sig_stdout", []),
        ("stdout_error", ["--stdout-error"]),
        ("stderr_error", ["--stderr-error"]),
        ("stderr_push_error", ["--stderr-push"]),
        ("stderr_warning", ["--stderr-warning"]),
        ("sig_on_stderr", ["--sig-stderr"]),
        ("stdout_no_newline", ["--stdout-no-newline"]),
    ]:
        cmd, out, err, code = run_streams(flags)
        merged = classify_process(code, None, out + err, 0, SIG)
        streams = classify_streams(code, None, out, err, 0, SIG, allowed_stderr=())
        rows.append({
            "case": label, "flags": flags, "exit": code,
            "merged": merged, "streams": streams,
            "divergent": merged != streams,
            "stdout_lines": out.splitlines(), "stderr_lines": err.splitlines(),
            "command": cmd,
        })
        print(f"{'DIV' if merged != streams else '  ='} {label:22s} exit={code} "
              f"merged={merged!s:5s} streams={streams!s:5s}")
        for l in err.splitlines():
            print(f"      stderr| {l}")
    (HERE / "e2e_results.json").write_text(json.dumps(rows, indent=2) + "\n")
    print(f"\nwrote {HERE / 'e2e_results.json'}")

main()
