#!/usr/bin/env python3
"""r63 non-author verifier scratch driver.

Runs three MY-scratch fixture variants plus the committed --spawn-forge-hold
shape under one bounded Popen each (communicate(timeout)), classifies with
run_process/classify_process ast-extracted VERBATIM from the committed
run_battery.py (no transcription), and kernel-side /proc corroboration of the
descendant ppid at return.

Arms:
  genuine_child     child emits the signature normally + silent descendant
                    that releases pipes ~0.5s -> must be clean PASS on the
                    child's own signature with ZERO forged-shape markers.
  markerless        no signature anywhere -> must classify False (cannot
                    forge what is absent).
  fabricated_ppid   forge-hold shape but descendant claims a bogus
                    write_ppid -> kernel /proc ppid at return must disagree,
                    i.e. the meta's kernel corroboration catches the slip.
  committed_hold    committed fixture --spawn-forge-hold replayed under my
                    own Popen (sanity anchor vs the battery's meta row).
"""
import ast
import json
import os
import re
import signal
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]  # .shokunin/game-dev-2d (corpus/live/r63-verifier/scratch -> repo root)
RUNNER = REPO / "corpus" / "fixtures" / "run_battery.py"
PROJ = HERE / "proj"
GODOT = "/usr/bin/godot"
MARKER = "DESCENDANT_PIPE_PROBE: expected signature"
BOUND = 3.0

# ast-extract run_process + classify_process verbatim from committed source
tree = ast.parse(RUNNER.read_text())
ns = {"subprocess": subprocess, "re": re}
for node in ast.walk(tree):
    if isinstance(node, ast.FunctionDef) and node.name == "main":
        for sub in node.body:
            if isinstance(sub, ast.FunctionDef) and sub.name in (
                    "run_process", "classify_process"):
                src = ast.get_source_segment(RUNNER.read_text(), sub)
                exec(src, ns)
run_process = ns["run_process"]
classify_process = ns["classify_process"]


def kernel_ppid(pid):
    if pid is None or pid <= 0:
        return None
    try:
        with open(f"/proc/{pid}/stat") as fh:
            return int(fh.read().rsplit(")", 1)[1].split()[1])
    except (OSError, ValueError, IndexError):
        return None


def pid_alive(pid):
    if pid is None or pid <= 0:
        return False
    try:
        os.kill(pid, 0)
        return True
    except OSError:
        return False


def drive(case, script, bound=BOUND):
    rec = {"case": case, "script": script, "bound_seconds": bound,
           "timed_out": False, "child_exit_at_timeout": None,
           "actual_exit": None, "error": None, "marker_observed": False,
           "godot_pid": None, "descendant_pid": None, "write_ppid": None,
           "descendant_kernel_ppid_at_return": None,
           "descendant_alive_at_return": None, "elapsed_seconds": None,
           "withheld_banner": False, "inner_classification": None}
    proc = subprocess.Popen(
        [GODOT, "--headless", "--path", str(PROJ), "--script",
         f"res://{script}", "--", "--spawn-forge-hold"],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, bufsize=1)
    started = time.monotonic()
    text = ""
    try:
        out, err = proc.communicate(timeout=bound)
        text = (out or "") + (err or "")
        rec["actual_exit"] = proc.returncode
    except subprocess.TimeoutExpired as exc:
        rec["timed_out"] = True
        rec["child_exit_at_timeout"] = proc.poll()
        out = exc.stdout.decode(errors="replace") if isinstance(exc.stdout, bytes) else (exc.stdout or "")
        err = exc.stderr.decode(errors="replace") if isinstance(exc.stderr, bytes) else (exc.stderr or "")
        text = out + err
        rec["error"] = f"TIMEOUT after {bound} seconds"
        for stream in (proc.stdout, proc.stderr):
            try:
                stream.close()
            except OSError:
                pass
        try:
            proc.wait(timeout=3)
        except subprocess.TimeoutExpired:
            proc.kill()
            try:
                proc.wait(timeout=3)
            except subprocess.TimeoutExpired:
                rec["error"] += "; post-kill wait timed out"
    finally:
        if proc.poll() is None:
            proc.kill()
            try:
                proc.wait(timeout=3)
            except subprocess.TimeoutExpired:
                rec["error"] = (rec["error"] or "") + "; forced cleanup timed out"
    rec["elapsed_seconds"] = round(time.monotonic() - started, 3)
    rec["marker_observed"] = MARKER in text
    rec["withheld_banner"] = "DESCENDANT_PIPE_FORGE child_signature=withheld" in text
    m = re.search(r"DESCENDANT_PIPE godot_pid=(\d+)", text)
    rec["godot_pid"] = int(m.group(1)) if m else None
    m = re.search(r"DESCENDANT_PIPE spawned_pid=(\d+)", text)
    rec["descendant_pid"] = int(m.group(1)) if m else None
    m = re.search(r"DESCENDANT_PIPE_FORGE write_ppid=(\d+)", text)
    rec["write_ppid"] = int(m.group(1)) if m else None
    rec["descendant_kernel_ppid_at_return"] = kernel_ppid(rec["descendant_pid"])
    rec["descendant_alive_at_return"] = pid_alive(rec["descendant_pid"])
    rec["inner_classification"] = classify_process(
        rec["actual_exit"], rec["error"], text, 0, MARKER)
    rec["output_lines"] = text.strip().splitlines()
    # hygiene: reap any still-living descendant (bounded sleeps anyway)
    if pid_alive(rec["descendant_pid"]):
        try:
            os.kill(rec["descendant_pid"], signal.SIGKILL)
        except OSError:
            pass
    rec["descendant_reaped"] = not pid_alive(rec["descendant_pid"])
    return rec


def main():
    results = []
    results.append(drive("genuine_child", "verifier_genuine_child.gd"))
    results.append(drive("markerless", "verifier_markerless.gd"))
    results.append(drive("fabricated_ppid", "verifier_fabricated_ppid.gd"))
    results.append(drive("committed_hold", "descendant_pipe_probe.gd"))
    checks = {
        # genuine child signature: PASS-shaped, zero forged-shape markers
        "genuine_passes_clean": (results[0]["inner_classification"] is True
                                 and results[0]["actual_exit"] == 0
                                 and results[0]["error"] is None
                                 and results[0]["marker_observed"]),
        "genuine_no_forged_shape": (not results[0]["withheld_banner"]
                                    and results[0]["write_ppid"] is None),
        # markerless: cannot forge what is absent
        "markerless_rejects": (results[1]["inner_classification"] is False
                               and not results[1]["marker_observed"]),
        # fabricated ppid: self-report lies; kernel truth disagrees
        "fabricated_ppid_caught": (results[2]["write_ppid"] is not None
                                   and results[2]["descendant_kernel_ppid_at_return"] is not None
                                   and results[2]["write_ppid"]
                                   != results[2]["descendant_kernel_ppid_at_return"]),
        "fabricated_hold_times_out": (results[2]["timed_out"]
                                      and results[2]["child_exit_at_timeout"] == 0
                                      and results[2]["marker_observed"]),
        # committed fixture anchor: hold shape under my own Popen
        "committed_hold_shape": (results[3]["timed_out"]
                                 and results[3]["child_exit_at_timeout"] == 0
                                 and results[3]["marker_observed"]
                                 and results[3]["withheld_banner"]
                                 and results[3]["write_ppid"] is not None
                                 and results[3]["descendant_kernel_ppid_at_return"]
                                 == results[3]["write_ppid"]
                                 and results[3]["write_ppid"] != results[3]["godot_pid"]
                                 and results[3]["inner_classification"] is False),
    }
    payload = {"runner": str(RUNNER), "runner_sha256_note": "ast-extracted verbatim",
               "godot": GODOT, "bound_seconds": BOUND, "results": results,
               "checks": checks,
               "verdict": "PASS" if all(checks.values()) else "FAIL"}
    out = HERE / "verifier-drive-verdicts.json"
    out.write_text(json.dumps(payload, indent=2) + "\n")
    for r in results:
        print(f"{r['case']}: exit={r['actual_exit']} timeout={r['timed_out']} "
              f"marker={r['marker_observed']} banner={r['withheld_banner']} "
              f"write_ppid={r['write_ppid']} kernel_ppid={r['descendant_kernel_ppid_at_return']} "
              f"inner={r['inner_classification']}")
    print(f"{payload['verdict']} verifier drive: {out}")
    return 0 if payload["verdict"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
