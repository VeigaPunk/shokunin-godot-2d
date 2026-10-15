#!/usr/bin/env python3
"""r66 critic real-pipe arm: post-death descendant splices on actual pipes.

Runs godot --headless --script critic_surface_probe.gd under a bounded Popen
with separate stdout/stderr pipes, merges verbatim (stdout + stderr), and
reclassifies with the verbatim-extracted classify_process. Records kernel
ppid provenance exactly like run_battery.py's errforge_run.
"""
import json
import os
import re
import subprocess
import sys
import textwrap
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent
FIXTURES = ROOT.parent.parent / "fixtures"
SRC = (FIXTURES / "run_battery.py").read_text()
GODOT = "/usr/bin/godot"
BOUND = 6.0
SIG = "DESCENDANT_PIPE_PROBE: expected signature"
SAVE_ALLOW = ("ERROR: SAVE EXPECTED NEGATIVE: malformed JSON rejected signature=JSON_PARSE_ERROR",)

m = re.search(r"(    def classify_process\(.*?\n)(?=    def classify_streams)", SRC, re.S)
ns = {"re": re}
exec(textwrap.dedent(m.group(1)), ns)
classify_process = ns["classify_process"]


def pid_alive(pid):
    if pid is None or pid <= 0:
        return None
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    except PermissionError:
        return True
    except OSError:
        return False
    return True


def kernel_ppid(pid):
    if pid is None or pid <= 0:
        return None
    try:
        stat = Path(f"/proc/{pid}/stat").read_text()
    except OSError:
        return None
    return int(stat.rsplit(")", 1)[1].split()[1])


def run_arm(case, flag, bound=BOUND):
    rec = {"case": case, "flags": [flag]}
    cmd = [GODOT, "--headless", "--path", str(ROOT / "proj"),
           "--script", "res://critic_surface_probe.gd", "--", flag]
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                            text=True, bufsize=1)
    t0 = time.monotonic()
    try:
        out, err = proc.communicate(timeout=bound)
        rec["actual_exit"] = proc.returncode
        rec["timed_out"] = False
    except subprocess.TimeoutExpired:
        proc.kill(); proc.wait()
        out, err = proc.communicate()
        rec["timed_out"] = True
    rec["elapsed"] = round(time.monotonic() - t0, 3)
    rec["stdout_blob"] = out or ""
    rec["stderr_blob"] = err or ""
    text = (out or "") + (err or "")           # verbatim merge
    rec["signature_observed"] = SIG in text
    rec["merged_error_lines"] = sorted(
        {l.strip() for l in text.splitlines() if "ERROR:" in l})
    rec["stdout_error_lines"] = sorted(
        {l.strip() for l in (out or "").splitlines() if "ERROR:" in l})
    rec["stderr_error_lines"] = sorted(
        {l.strip() for l in (err or "").splitlines() if "ERROR:" in l})
    pm = re.search(r"CRITIC_SURFACE write_ppid=(\d+)", text)
    rec["write_ppid"] = int(pm.group(1)) if pm else None
    pm = re.search(r"DESCENDANT_PIPE godot_pid=(\d+)", text)
    rec["godot_pid"] = int(pm.group(1)) if pm else None
    pm = re.search(r"DESCENDANT_PIPE spawned_pid=(\d+)", text)
    rec["descendant_pid"] = int(pm.group(1)) if pm else None
    rec["descendant_alive_at_return"] = pid_alive(rec["descendant_pid"])
    rec["descendant_kernel_ppid_at_return"] = kernel_ppid(rec["descendant_pid"])
    rec["inner_cls_no_allowlist"] = classify_process(
        rec["actual_exit"], None, text, 0, SIG)
    rec["inner_cls_save_allowlist"] = classify_process(
        rec["actual_exit"], None, text, 0, SIG, SAVE_ALLOW)
    return rec


res = {"runs": []}
for flag in ("--splice-phantom", "--splice-allowlisted", "--double"):
    for rep in range(3):
        rec = run_arm(f"{flag.strip('-')}_r{rep}", flag)
        res["runs"].append(rec)
        print(f"[{flag} r{rep}] exit={rec['actual_exit']} "
              f"merged_err={rec['merged_error_lines']} "
              f"cls={rec['inner_cls_no_allowlist']}/{rec['inner_cls_save_allowlist']} "
              f"wppid={rec['write_ppid']} gpid={rec['godot_pid']}", flush=True)

out = ROOT / "realpipe-results.json"
out.write_text(json.dumps(res, indent=2) + "\n")
print("wrote", out)
