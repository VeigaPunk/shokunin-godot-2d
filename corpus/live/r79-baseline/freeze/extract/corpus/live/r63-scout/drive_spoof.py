#!/usr/bin/env python3
"""r63 scout: signature-spoof boundary measurement.

ast.get_source_segment-extracts run_process + classify_process VERBATIM from
the tracked corpus/fixtures/run_battery.py and execs them (production code
path, no transcription — the r61/r62 sibling-seat discipline).

Arms are pure /usr/bin/sh children: the mechanism under test is POSIX
pipe-inheritance + the merged-capture signature check, not Godot itself
(Godot is one possible child shape; the classifier only sees bytes + exit).
Each spoof arm's descendant waits for its /proc/self/stat ppid to flip off
the child pid — the same post-death gate the tracked fixture uses
(descendant_pipe_probe.gd:33) — so the signature write is provably after
the direct child's exit.

Arms:
  genuine          child prints the signature itself, exits 0        (control)
  spoof_release    child exits 0 fast; descendant writes signature
                   post-death, then EXITS (releases pipes < bound)
  spoof_hold       same gated write, then descendant SLEEPS 5s
                   (holds pipes past the 3.0s bound)
  spoof_hold_popen same shape under a Popen+communicate replica of the
                   r62 meta (run_battery.py:574-605) to capture
                   child_exit_at_timeout via poll() in TimeoutExpired
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
RUNNER = HERE.parent.parent / "fixtures" / "run_battery.py"
SIG = "SPOOF_SIG: expected signature"
BOUND = 3.0
RAW = HERE / "raw"
RAW.mkdir(exist_ok=True)

source = RUNNER.read_text()
tree = ast.parse(source)
funcs = {}
for node in ast.walk(tree):
    if isinstance(node, ast.FunctionDef) and node.name in (
            "run_process", "classify_process"):
        funcs[node.name] = ast.get_source_segment(source, node)
ns = {"subprocess": subprocess}
for name, seg in funcs.items():
    exec(seg, ns)
run_process = ns["run_process"]
classify_process = ns["classify_process"]

GATE = ('while read -r _ _ _ pp _ < /proc/self/stat && '
        '[ "$pp" = "{pid}" ]; do sleep 0.05; done; ')


def desc_script(child_pid_lit, tail):
    # Runs as `sh -c <script>`; its ppid starts as the child pid and flips to
    # the subreaper when the child exits — the tracked fixture's own gate.
    return GATE.format(pid=child_pid_lit) + tail


def child_cmd(inner_desc_tail):
    # Child: print own pid, spawn pipe-inheriting descendant in background,
    # print descendant pid, exit 0 immediately.
    # $$ inside the child expands to the child pid and is spliced into the
    # descendant's ppid gate literally.
    return ["/usr/bin/sh", "-c",
            'echo SPOOF_CHILD_PID=$$; '
            'sh -c \'while read -r _ _ _ pp _ < /proc/self/stat && '
            '[ "$pp" = "\'$$\'" ]; do sleep 0.05; done; ' + inner_desc_tail + '\' & '
            'echo SPOOF_DESC_PID=$!; exit 0']


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


def parse_pids(text):
    child = re.search(r"SPOOF_CHILD_PID=(\d+)", text)
    desc = re.search(r"SPOOF_DESC_PID=(\d+)", text)
    return (int(child.group(1)) if child else None,
            int(desc.group(1)) if desc else None)


records = []

# --- arm: genuine control -------------------------------------------------
out, code, err = run_process(
    ["/usr/bin/sh", "-c", f'echo "{SIG}"; exit 0'], BOUND)
records.append({"arm": "genuine", "elapsed": None, "actual_exit": code,
                "error": err, "signature_in_merged_output": SIG in out,
                "classify_process": classify_process(code, err, out, 0, SIG),
                "output": out.strip().splitlines()})

# --- arm: spoof_release (descendant writes sig post-death, releases) ------
started = time.monotonic()
out, code, err = run_process(
    child_cmd(f'echo "{SIG}"'), BOUND)
elapsed = round(time.monotonic() - started, 3)
child_pid, desc_pid = parse_pids(out)
records.append({"arm": "spoof_release", "elapsed": elapsed,
                "actual_exit": code, "error": err,
                "signature_in_merged_output": SIG in out,
                "child_pid": child_pid, "descendant_pid": desc_pid,
                "child_alive_at_return": pid_alive(child_pid),
                "descendant_alive_at_return": pid_alive(desc_pid),
                "classify_process": classify_process(code, err, out, 0, SIG),
                "output": out.strip().splitlines()})
(RAW / "spoof_release.stdout").write_text(out)

# --- arm: spoof_hold via verbatim run_process (subprocess.run path) -------
started = time.monotonic()
out, code, err = run_process(
    child_cmd(f'echo "{SIG}"; sleep 5'), BOUND)
elapsed = round(time.monotonic() - started, 3)
child_pid, desc_pid = parse_pids(out)
hold = {"arm": "spoof_hold", "elapsed": elapsed, "actual_exit": code,
        "error": err, "signature_in_merged_output": SIG in out,
        "child_pid": child_pid, "descendant_pid": desc_pid,
        "child_alive_at_return": pid_alive(child_pid),
        "descendant_alive_at_return": pid_alive(desc_pid),
        "classify_process": classify_process(code, err, out, 0, SIG),
        # the synthetic reclassification: same captured bytes, forged
        # signature axis evaluated on its own (exit 0, no error)
        "classify_if_error_none": classify_process(0, None, out, 0, SIG),
        "output": out.strip().splitlines()}
records.append(hold)
(RAW / "spoof_hold.stdout").write_text(out)
if pid_alive(desc_pid):
    try:
        os.kill(desc_pid, signal.SIGKILL)
    except OSError:
        pass

# --- arm: spoof_hold under Popen replica (child_exit_at_timeout) ----------
pop = {"arm": "spoof_hold_popen", "bound_seconds": BOUND, "timed_out": False,
       "child_exit_at_timeout": None, "actual_exit": None, "error": None,
       "signature_in_merged_output": False, "elapsed_seconds": None,
       "inner_classification": None}
proc = None
started = time.monotonic()
text = ""
try:
    proc = subprocess.Popen(child_cmd(f'echo "{SIG}"; sleep 5'),
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                            text=True, bufsize=1)
    try:
        o, e = proc.communicate(timeout=BOUND)
        text = (o or "") + (e or "")
        pop["actual_exit"] = proc.returncode
    except subprocess.TimeoutExpired as exc:
        pop["timed_out"] = True
        pop["child_exit_at_timeout"] = proc.poll()
        o = (exc.stdout.decode(errors="replace")
             if isinstance(exc.stdout, bytes) else (exc.stdout or ""))
        e = (exc.stderr.decode(errors="replace")
             if isinstance(exc.stderr, bytes) else (exc.stderr or ""))
        text = o + e
        pop["error"] = f"TIMEOUT after {BOUND} seconds"
        for s in (proc.stdout, proc.stderr):
            try:
                s.close()
            except OSError:
                pass
        try:
            proc.wait(timeout=3)
        except subprocess.TimeoutExpired:
            proc.kill()
            proc.wait(timeout=3)
except (OSError, ValueError) as exc:
    pop["error"] = f"launch/read error: {exc}"
finally:
    if proc is not None and proc.poll() is None:
        proc.kill()
        try:
            proc.wait(timeout=3)
        except subprocess.TimeoutExpired:
            pass
pop["elapsed_seconds"] = round(time.monotonic() - started, 3)
pop["signature_in_merged_output"] = SIG in text
pop["inner_classification"] = classify_process(
    pop["actual_exit"], pop["error"], text, 0, SIG)
pop["classify_if_error_none"] = classify_process(0, None, text, 0, SIG)
c2, d2 = parse_pids(text)
pop["child_pid"], pop["descendant_pid"] = c2, d2
pop["child_alive_at_return"] = pid_alive(c2)
pop["descendant_alive_at_return"] = pid_alive(d2)
pop["output"] = text.strip().splitlines()
records.append(pop)
(RAW / "spoof_hold_popen.stdout").write_text(text)
if pid_alive(d2):
    try:
        os.kill(d2, signal.SIGKILL)
    except OSError:
        pass

payload = {"runner": str(RUNNER),
           "extraction": "ast.get_source_segment verbatim exec",
           "signature": SIG, "bound_seconds": BOUND, "arms": records}
(HERE / "spoof-verdicts.json").write_text(json.dumps(payload, indent=2) + "\n")
for r in records:
    print(r["arm"], "| exit:", r.get("actual_exit"), "| err:", r.get("error"),
          "| sig_seen:", r.get("signature_in_merged_output"),
          "| classify:", r.get("classify_process", r.get("inner_classification")),
          "| child_exit_at_timeout:", r.get("child_exit_at_timeout"))
