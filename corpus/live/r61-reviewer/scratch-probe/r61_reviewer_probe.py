#!/usr/bin/env python3
"""Round-61 NON-AUTHOR reviewer re-run of the r60 spontaneous-crash probe.

Third independent derivation (after author's drive_probe.py, which is no
longer on disk, and r60-verifier's verify_probe.py). Same recipe as the r60
reports describe: ast-extract the nested run_process + classify_process defs
verbatim from the tracked run_battery.py, exec them unmodified, and drive
the four arms against a scratch probe project carrying the same emitted
marker. Writes r61-reviewer-own JSON + raw stdout captures only inside this
scratch dir.
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
TIMEOUT_SECONDS = 8


def extract_nested(name):
    text = RUNNER.read_text()
    tree = ast.parse(text)
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "main":
            for sub in node.body:
                if isinstance(sub, ast.FunctionDef) and sub.name == name:
                    return ast.get_source_segment(text, sub)
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
    (HERE / f"r61_{case}.stdout").write_text(output)
    return {
        "case": case,
        "command": command,
        "expected_exit": 1,
        "actual_exit": code,
        "signal_name": signal.Signals(-code).name
            if isinstance(code, int) and code < 0 else None,
        "error": error,
        "marker_observed": MARKER in output,
        "elapsed_seconds": elapsed,
        "classify_expected1": classify_process(code, error, output, 1, MARKER),
        "classify_expected_minus9": classify_process(code, error, output, -9, MARKER),
        "classify_expected_minus6": classify_process(code, error, output, -6, MARKER),
        "classify_expected_minus6_crash_error_allowed": classify_process(
            code, error, output, -6, MARKER,
            ("ERROR: r60 spontaneous crash probe",)),
        "stderr_has_error_line": any(
            l.strip().startswith("ERROR:") for l in output.splitlines()),
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
    "mode": "real_godot_spontaneous_crash_r61_reviewer",
    "round": 61, "lane": "game-dev-2d", "host": "devin", "role": "reviewer",
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
out = HERE / "r61-reviewer-spontaneous-crash-verdicts.json"
out.write_text(json.dumps(payload, indent=2) + "\n")
for r in records:
    print(r["case"], "exit=", r["actual_exit"], r["signal_name"],
          "marker=", r["marker_observed"], "err=", r["error"],
          "e1=", r["classify_expected1"],
          "e-9=", r["classify_expected_minus9"],
          "e-6=", r["classify_expected_minus6"],
          "e-6_allowed=", r["classify_expected_minus6_crash_error_allowed"],
          "elapsed=", r["elapsed_seconds"])
print(f"wrote {out}")
