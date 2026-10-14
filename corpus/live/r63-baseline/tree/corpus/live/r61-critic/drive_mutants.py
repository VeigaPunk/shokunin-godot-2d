#!/usr/bin/env python3
"""r61 CRITIC — adversarial driver for the planned spontaneous-crash row.

Re-extracts run_process + classify_process VERBATIM from the tracked
run_battery.py via ast (same method as r60 author/verifier), then runs a
sabotage arm battery against the declared row semantics:
  expected_exit = -6, signature = MARKER,
  allowed_errors  = ("ERROR: <crash message>",)   [exact-match allowlist]
plus alternative allowlist spellings to show what each admits.
Scratch only: writes verdicts JSON + per-arm raw captures under its own dir.
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
SCRIPT = "res://r61_critic_probe.gd"
MARKER = "R61_CRITIC_SPONTANEOUS: expected signature"
CRASH_MSG = "r61 critic abort"
EXPECTED_EXIT = -6
TIMEOUT_SECONDS = 12


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

ALLOW_EXACT = ("ERROR: " + CRASH_MSG,)
ALLOW_PREFIX = ("ERROR: " + CRASH_MSG + ",",)          # comma-prefix variant
ALLOW_NONE = ()
ALLOW_FORGED = ("ERROR: " + CRASH_MSG + ", EXTRA_UNRELATED_CONTENT",)


def run_arm(case, extra_args):
    command = ["godot", "--headless", "--path", str(PROJECT), "--script",
               SCRIPT, "--", *extra_args]
    started = time.monotonic()
    output, code, error = run_process(command, TIMEOUT_SECONDS)
    elapsed = round(time.monotonic() - started, 3)
    (HERE / f"critic_{case}.stdout").write_text(output)
    error_lines = [l.strip() for l in output.splitlines() if "ERROR:" in l]
    return {
        "case": case,
        "command": command,
        "expected_exit": EXPECTED_EXIT,
        "actual_exit": code,
        "signal_name": signal.Signals(-code).name
            if isinstance(code, int) and code < 0 else None,
        "error": error,
        "marker_observed": MARKER in output,
        "elapsed_seconds": elapsed,
        "error_lines": error_lines,
        "has_crash_handler": "handle_crash: Program crashed" in output,
        "has_script_error": "SCRIPT ERROR:" in output,
        "has_parse_error": "Parse Error:" in output,
        # verdict hypotheses against the declared row shape:
        "cls_e-6_exact": classify_process(code, error, output, -6, MARKER, ALLOW_EXACT),
        "cls_e-6_prefix": classify_process(code, error, output, -6, MARKER, ALLOW_PREFIX),
        "cls_e-6_noallow": classify_process(code, error, output, -6, MARKER, ALLOW_NONE),
        "cls_e-6_forged": classify_process(code, error, output, -6, MARKER, ALLOW_FORGED),
        "cls_e1": classify_process(code, error, output, 1, MARKER),
        "cls_e-9": classify_process(code, error, output, -9, MARKER),
        "cls_e-15": classify_process(code, error, output, -15, MARKER),
        "raw_output_lines": output.strip().splitlines(),
    }


records = [
    run_arm("os_crash_baseline", ["--os-crash"]),
    run_arm("ext_abrt_no_error", ["--ext-abrt"]),
    run_arm("ext_abrt_forged_marker", ["--ext-abrt-forged-marker"]),
    run_arm("ext_abrt_extra_error", ["--ext-abrt-extra-error"]),
    run_arm("ext_ill", ["--ext-ill"]),
    run_arm("ext_segv", ["--ext-segv"]),
    run_arm("ext_term", ["--ext-term"]),
    run_arm("self_kill_sigkill", ["--self-kill"]),
    run_arm("exit_134", ["--exit-134"]),
    run_arm("crash_before_marker", ["--crash-before-marker"]),
    run_arm("crash_diff_msg", ["--crash-diff-msg"]),
    run_arm("forge_prefix_line", ["--forge-prefix"]),
    run_arm("printerr_clean_exit0", ["--printerr-clean"]),
    run_arm("assert_fail", ["--assert-fail"]),
    run_arm("stack_overflow", ["--stack-overflow"]),
    run_arm("accept_clean_exit1", []),
]
payload = {
    "mode": "r61_critic_sabotage_battery",
    "round": 61, "lane": "game-dev-2d", "host": "devin", "role": "critic",
    "stamp": datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ"),
    "platform": sys.platform, "uname": platform.uname()._asdict(),
    "python": sys.version.split()[0],
    "core_rlimit": list(resource.getrlimit(resource.RLIMIT_CORE)),
    "runner_sha256": hashlib.sha256(RUNNER.read_bytes()).hexdigest(),
    "extracted_source_sha256": {
        "run_process": hashlib.sha256(src_run_process.encode()).hexdigest(),
        "classify_process": hashlib.sha256(src_classify.encode()).hexdigest(),
    },
    "allowlist_shapes": {
        "exact": list(ALLOW_EXACT), "comma_prefix": list(ALLOW_PREFIX),
        "none": [], "forged_line": list(ALLOW_FORGED)},
    "results": records,
}
out = HERE / "r61-critic-sabotage-verdicts.json"
out.write_text(json.dumps(payload, indent=2) + "\n")
hdr = (f"{'case':<24} {'exit':>5} {'sig':>8} {'mk':>2} {'e-6x':>4} "
       f"{'e-6p':>4} {'e-6n':>4} {'e-6f':>4} {'e1':>3} {'e-9':>3} {'e-15':>4}")
print(hdr)
for r in records:
    print(f"{r['case']:<24} {str(r['actual_exit']):>5} "
          f"{str(r['signal_name']):>8} {int(r['marker_observed']):>2} "
          f"{str(r['cls_e-6_exact']):>4} {str(r['cls_e-6_prefix']):>4} "
          f"{str(r['cls_e-6_noallow']):>4} {str(r['cls_e-6_forged']):>4} "
          f"{str(r['cls_e1']):>3} {str(r['cls_e-9']):>3} {str(r['cls_e-15']):>4}")
print(f"wrote {out}")
