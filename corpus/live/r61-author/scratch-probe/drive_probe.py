#!/usr/bin/env python3
"""r61 author causal scratch probe: re-derive run_process + classify_process
verbatim from the tracked run_battery.py via ast.get_source_segment (no
transcription), then run the promoted spontaneous_crash_probe.gd arms and the
planned re-classification arms. Saves raw output per arm plus a JSON result.
Scratch-only; edits nothing tracked."""
import ast
import hashlib
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
RUNNER = HERE.parent.parent.parent / "fixtures" / "run_battery.py"
PROJ = HERE / "proj"
GODOT = "godot"
MARKER = "SPONTANEOUS_CRASH_PROBE: expected signature"
CRASH_ALLOWLIST = ("ERROR: r60 spontaneous crash probe",)
WRONG_ALLOWLIST = ("ERROR: unrelated different diagnostic",)

source = RUNNER.read_text()
runner_sha = hashlib.sha256(source.encode()).hexdigest()
tree = ast.parse(source)
wanted = {"run_process", "classify_process"}
snippets = {}
for node in ast.walk(tree):
    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name in wanted:
        snippets[node.name] = ast.get_source_segment(source, node)
missing = wanted - snippets.keys()
if missing:
    raise SystemExit(f"could not extract {missing} from {RUNNER}")
ns = {"subprocess": subprocess}
for name in ("run_process", "classify_process"):
    exec(snippets[name], ns)
run_process = ns["run_process"]
classify_process = ns["classify_process"]

results = []


def run_arm(case, extra_args):
    command = [GODOT, "--headless", "--path", str(PROJ), "--script",
               "res://spontaneous_crash_probe.gd", "--"] + extra_args
    output, code, error = run_process(command, 8)
    raw_path = HERE / f"{case}.stdout"
    raw_path.write_text(output)
    record = {"case": case, "command": command, "actual_exit": code,
              "error": error, "marker_observed": MARKER in output,
              "error_lines": [l.strip() for l in output.splitlines() if "ERROR:" in l],
              "raw_capture": str(raw_path), "output": output}
    results.append(record)
    return record


crash = run_arm("crash_spontaneous_sigabrt", ["--spontaneous-crash"])
sigkill = run_arm("crash_self_sigkill", ["--spontaneous-sigkill"])
clean = run_arm("clean_nonzero_exit", [])

checks = {
    # planned tracked rows
    "crash_row_expected_-6_with_allowlist": classify_process(
        crash["actual_exit"], crash["error"], crash["output"], -6, MARKER, CRASH_ALLOWLIST),
    "sigkill_row_expected_-9_no_allowlist": classify_process(
        sigkill["actual_exit"], sigkill["error"], sigkill["output"], -9, MARKER),
    "clean_row_expected_1": classify_process(
        clean["actual_exit"], clean["error"], clean["output"], 1, MARKER),
    # planned discriminating arms on the SAME captured crash output
    "crash_expected_-9_mismatch_rejects": classify_process(
        crash["actual_exit"], crash["error"], crash["output"], -9, MARKER, CRASH_ALLOWLIST),
    "crash_missing_allowlist_rejects": classify_process(
        crash["actual_exit"], crash["error"], crash["output"], -6, MARKER, ()),
    "crash_wrong_allowlist_rejects": classify_process(
        crash["actual_exit"], crash["error"], crash["output"], -6, MARKER, WRONG_ALLOWLIST),
    "sigkill_expected_-6_mismatch_rejects": classify_process(
        sigkill["actual_exit"], sigkill["error"], sigkill["output"], -6, MARKER, CRASH_ALLOWLIST),
    # prior-behavior guards
    "crash_expected_1_rejects": classify_process(
        crash["actual_exit"], crash["error"], crash["output"], 1, MARKER, CRASH_ALLOWLIST),
    "sigkill_expected_1_rejects": classify_process(
        sigkill["actual_exit"], sigkill["error"], sigkill["output"], 1, MARKER),
}
expected = {
    "crash_row_expected_-6_with_allowlist": True,
    "sigkill_row_expected_-9_no_allowlist": True,
    "clean_row_expected_1": True,
    "crash_expected_-9_mismatch_rejects": False,
    "crash_missing_allowlist_rejects": False,
    "crash_wrong_allowlist_rejects": False,
    "sigkill_expected_-6_mismatch_rejects": False,
    "crash_expected_1_rejects": False,
    "sigkill_expected_1_rejects": False,
}
payload = {
    "mode": "r61_author_causal_scratch_spontaneous_crash",
    "stamp": datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ"),
    "runner": str(RUNNER), "runner_sha256": runner_sha,
    "extracted_sha256": {k: hashlib.sha256(v.encode()).hexdigest() for k, v in snippets.items()},
    "project": str(PROJ),
    "results": [{k: v for k, v in r.items() if k != "output"} for r in results],
    "checks": checks, "expected": expected,
    "verdict": "PASS" if checks == expected and all(r["error"] is None for r in results) else "FAIL",
}
out = HERE / "causal-scratch-verdicts.json"
out.write_text(json.dumps(payload, indent=2) + "\n")
print(json.dumps({r["case"]: r["actual_exit"] for r in results}, indent=1))
print(json.dumps(checks, indent=1))
print(f"{payload['verdict']} causal scratch probe: {out}")
sys.exit(0 if payload["verdict"] == "PASS" else 1)
