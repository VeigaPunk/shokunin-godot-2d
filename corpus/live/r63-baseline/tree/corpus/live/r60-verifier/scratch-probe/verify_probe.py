#!/usr/bin/env python3
"""Round-60 NON-AUTHOR verifier re-run of the spontaneous-crash probe.

Independent of drive_probe.py: re-extracts run_process + classify_process
verbatim from the tracked runner via ast.get_source_segment and execs them,
then drives the same three arm shapes against a scratch copy of the author's
probe project. Writes verifier-own JSON; does not touch author artifacts.
"""
import ast
import hashlib
import json
import platform
import resource
import signal
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
RUNNER = Path(
    "/home/vgpnk/Projects/prymeagnt/game-dev-2d/.shokunin/game-dev-2d/"
    "corpus/fixtures/run_battery.py"
)
PROJECT = HERE / "proj"
SCRIPT = "res://spontaneous_crash_probe.gd"
MARKER = "SPONTANEOUS_CRASH_PROBE: expected signature"
EXPECTED_EXIT = 1
TIMEOUT_SECONDS = 8


def extract_nested(name):
    tree = ast.parse(RUNNER.read_text())
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "main":
            for sub in node.body:
                if isinstance(sub, ast.FunctionDef) and sub.name == name:
                    return ast.get_source_segment(RUNNER.read_text(), sub)
    raise RuntimeError(f"nested def {name} not found in {RUNNER}")


src_run_process = extract_nested("run_process")
src_classify = extract_nested("classify_process")
ns = {"subprocess": subprocess}
exec(src_run_process, ns)
exec(src_classify, ns)
run_process = ns["run_process"]
classify_process = ns["classify_process"]


def run_arm(case, extra_args):
    command = ["godot", "--headless", "--path", str(PROJECT), "--script",
               SCRIPT, "--", *extra_args]
    started = time.monotonic()
    output, code, error = run_process(command, TIMEOUT_SECONDS)
    elapsed = round(time.monotonic() - started, 3)
    (HERE / f"verifier_{case}.stdout").write_text(output)
    return {
        "case": case,
        "command": command,
        "expected_exit": EXPECTED_EXIT,
        "actual_exit": code,
        "signal_name": signal.Signals(-code).name if isinstance(code, int) and code < 0 else None,
        "error": error,
        "marker_observed": MARKER in output,
        "elapsed_seconds": elapsed,
        "inner_classification_expected1": classify_process(code, error, output, EXPECTED_EXIT, MARKER),
        "inner_classification_expected_minus9": classify_process(code, error, output, -9, MARKER),
        "inner_classification_expected_minus6": classify_process(code, error, output, -6, MARKER),
        "inner_classification_expected_minus6_allowed": classify_process(
            code, error, output, -6, MARKER,
            ("ERROR: r60 spontaneous crash probe",)),
        "stderr_has_error_line": any(l.strip().startswith("ERROR:") for l in output.splitlines()),
        "stderr_has_crash_handler": "handle_crash: Program crashed" in output,
        "raw_output_lines": output.strip().splitlines(),
    }


records = [
    run_arm("accept_clean_exit1", []),
    run_arm("os_crash_a", ["--spontaneous-crash"]),
    run_arm("os_crash_b", ["--spontaneous-crash"]),
    run_arm("self_sigkill", ["--spontaneous-sigkill"]),
]
payload = {
    "mode": "real_godot_spontaneous_crash_verifier",
    "round": 60, "lane": "game-dev-2d", "host": "devin", "role": "non-author",
    "stamp": datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ"),
    "platform": sys.platform, "uname": platform.uname()._asdict(),
    "python": sys.version.split()[0],
    "core_rlimit": list(resource.getrlimit(resource.RLIMIT_CORE)),
    "runner_sha256": hashlib.sha256(RUNNER.read_bytes()).hexdigest(),
    "extracted_source_sha256": {
        "run_process": hashlib.sha256(src_run_process.encode()).hexdigest(),
        "classify_process": hashlib.sha256(src_classify.encode()).hexdigest(),
    },
    "results": records,
}
out = HERE / "verifier-spontaneous-crash-verdicts.json"
out.write_text(json.dumps(payload, indent=2) + "\n")
for r in records:
    print(r["case"], "exit=", r["actual_exit"], r["signal_name"],
          "marker=", r["marker_observed"], "err=", r["error"],
          "class_e1=", r["inner_classification_expected1"],
          "class_e-9=", r["inner_classification_expected_minus9"],
          "class_e-6=", r["inner_classification_expected_minus6"],
          "class_e-6_allowed=", r["inner_classification_expected_minus6_allowed"],
          "elapsed=", r["elapsed_seconds"])
print(f"wrote {out}")
