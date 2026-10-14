#!/usr/bin/env python3
"""r61 scout scratch: re-derive the spontaneous-crash classification boundary.

ast-extracts run_process + classify_process VERBATIM from the tracked runner
(run_battery.py, sha asserted below) and execs them — no transcription — then
runs the three scratch-probe arms fresh on this host and classifies the real
subprocess outputs under several expected_exit/allowlist combinations.

Scratch-only evidence for the r61 scout report; writes only under
corpus/live/r61-scout/. Mirrors the r60 verifier method (verify_probe.py).
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
    "/home/vgpnk/Projects/shokunin/game-dev-2d-shokunin/corpus/fixtures/run_battery.py"
)
PROJECT = HERE / "proj"
SCRIPT = "res://spontaneous_crash_probe.gd"
MARKER = "SPONTANEOUS_CRASH_PROBE: expected signature"
CRASH_ERROR_LINE = "ERROR: r60 spontaneous crash probe"
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


runner_sha = hashlib.sha256(RUNNER.read_bytes()).hexdigest()
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
    sig = {-v: k for k, v in signal.__dict__.items()
           if k.startswith("SIG") and "_" not in k and isinstance(v, int)}.get(code)
    return {
        "case": case,
        "command": command,
        "actual_exit": code,
        "signal_name": sig,
        "error": error,
        "marker_observed": MARKER in output,
        "elapsed_seconds": elapsed,
        # classification matrix on the REAL captured output:
        "cls_expected1": classify_process(code, error, output, 1, MARKER),
        "cls_expected_minus6": classify_process(code, error, output, -6, MARKER),
        "cls_expected_minus6_allowed": classify_process(
            code, error, output, -6, MARKER, (CRASH_ERROR_LINE,)),
        "cls_expected_minus9": classify_process(code, error, output, -9, MARKER),
        # negative controls: wrong signature must fail even with right exit;
        # wrong allowlist text must fail.
        "cls_expected_minus6_wrong_sig": classify_process(
            code, error, output, -6, "NO SUCH MARKER", (CRASH_ERROR_LINE,)),
        "cls_expected_minus6_wrong_allowed": classify_process(
            code, error, output, -6, MARKER, ("ERROR: something else",)),
        "stderr_lines_tail": [l for l in output.splitlines() if l.strip()][-4:],
    }


results = [
    run_arm("accept_clean_exit1", []),
    run_arm("os_crash", ["--spontaneous-crash"]),
    run_arm("self_sigkill", ["--spontaneous-sigkill"]),
]

payload = {
    "mode": "r61_scout_spontaneous_crash_recheck",
    "round": 61,
    "lane": "game-dev-2d",
    "host": "devin",
    "role": "scout-scratch",
    "stamp": datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ"),
    "platform": sys.platform,
    "uname": platform.uname()._asdict(),
    "runner_sha256": runner_sha,
    "extracted_source_sha256": {
        "run_process": hashlib.sha256(src_run_process.encode()).hexdigest(),
        "classify_process": hashlib.sha256(src_classify.encode()).hexdigest(),
    },
    "core_rlimit": list(resource.getrlimit(resource.RLIMIT_CORE)),
    "marker": MARKER,
    "crash_error_line": CRASH_ERROR_LINE,
    "results": results,
}
out = HERE / "r61-spontaneous-crash-recheck.json"
out.write_text(json.dumps(payload, indent=2) + "\n")
print(json.dumps({r["case"]: {k: r[k] for k in r if k != "command" and k != "stderr_lines_tail"}
                  for r in results}, indent=2))
print(f"wrote {out}")
