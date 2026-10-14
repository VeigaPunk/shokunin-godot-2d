#!/usr/bin/env python3
"""r65 scout: forged-REJECTION dual — independent measurement.

ast.get_source_segment-extracts run_process + classify_process VERBATIM from
the tracked corpus/fixtures/run_battery.py (r63/r64 sibling-seat discipline).
Real Godot 4.7.2 children run on proj/ (project.godot + the author's in-flight
descendant_pipe_probe.gd copied verbatim into scratch).

Measured questions (r65 brief):
  Q1  which substrings flip a clean classify_process record -> the reject set
  Q2  does a post-death un-allowlisted ERROR: write flip a CASES-shape record
      (exit0 + signature present -> FAIL) — forged vs genuine-error control
  Q3  hold arm: is the error-axis rejection independent of the timeout axis
      (the r63 signature-spoof dual — there classify_if_error_none was True)
  Q4  does the while-live gate reject the forged-error arm (prediction: NO —
      its criterion is the signature marker only; the post-death error is
      captured but gate-invisible) + which stream carries each write
"""
import ast
import json
import os
import re
import selectors
import signal
import subprocess
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
RUNNER = HERE.parent.parent / "fixtures" / "run_battery.py"
PROJ = HERE / "proj"
SIG = "DESCENDANT_PIPE_PROBE: expected signature"
ERR = "ERROR: DESCENDANT_PIPE_ERRFORGE unrelated injected diagnostic"
PPID_LINE = "DESCENDANT_PIPE_ERRFORGE write_ppid="
BOUND = 3.0
GODOT = "godot"
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

results = {"runner": str(RUNNER), "extraction": "ast verbatim exec",
           "signature": SIG, "error_marker": ERR, "bound": BOUND,
           "substring_probes": [], "arms": []}

# --- Q1: substring reject set over synthetic outputs -------------------------
BASE = f"{SIG}\n"


def probe(name, output, allowed=()):
    verdict = classify_process(0, None, output, 0, SIG, allowed)
    results["substring_probes"].append(
        {"probe": name, "allowed": list(allowed), "classify": verdict})
    print(f"  sub[{name}] allowed={allowed!r} -> {verdict}")


probe("clean", BASE)
probe("error_line", BASE + "ERROR: injected diagnostic\n")
probe("midline_error", BASE + "prefix text ERROR: injected diagnostic\n")
probe("glued_XERROR", BASE + "XERROR: injected diagnostic\n")
probe("bare_ERROR_colon", BASE + "ERROR:\n")
probe("script_error", BASE + "SCRIPT ERROR: boom\n")
probe("parse_error", BASE + "Parse Error: boom\n")
probe("lowercase_error", BASE + "error: injected diagnostic\n")
probe("warning_line", BASE + "WARNING: injected diagnostic\n")
probe("error_as_last_colon_suffix", BASE + "ERROR: injected diagnostic\n")
probe("two_errors_one_line", BASE + "ERROR: a ERROR: b\n")
probe("exact_allowed", BASE + "ERROR: injected diagnostic\n",
      ("ERROR: injected diagnostic",))
probe("allowed_prefix_comma_hit", BASE + "ERROR: injected diagnostic, tail=1\n",
      ("ERROR: injected diagnostic,",))
probe("allowed_prefix_comma_second_error", BASE + "ERROR: injected diagnostic, ERROR: b\n",
      ("ERROR: injected diagnostic,",))
probe("allowed_prefix_nocomma", BASE + "ERROR: injected diagnostic TAIL\n",
      ("ERROR: injected diagnostic,",))
probe("allowlist_wrong_string", BASE + "ERROR: injected diagnostic\n",
      ("ERROR: different diagnostic",))
probe("strip_whitespace_match", BASE + "   ERROR: injected diagnostic   \n",
      ("ERROR: injected diagnostic",))
probe("signature_same_line_as_error", "ERROR: injected " + SIG + "\n")

# --- helpers -----------------------------------------------------------------
def kernel_ppid(pid):
    if pid is None or pid <= 0:
        return None
    try:
        with open(f"/proc/{pid}/stat") as f:
            return int(f.read().rsplit(")", 1)[1].split()[1])
    except (OSError, ValueError, IndexError):
        return None


def pid_alive(pid):
    if pid is None or pid <= 0:
        return False
    try:
        os.kill(pid, 0)
    except OSError:
        return False
    return True


def cases_record(cmd, timeout_s, tag):
    """The run_process record shape a CASES row carries (exit/error/output)."""
    output, code, error = run_process(cmd, timeout_s)
    rec = {"tag": tag, "command": cmd, "actual_exit": code, "error": error,
           "signature_observed": SIG in output,
           "error_marker_captured": ERR in output,
           "error_lines": sorted({l.strip() for l in output.splitlines()
                                  if "ERROR:" in l}),
           "inner_classification": classify_process(code, error, output, 0, SIG),
           "stripped_classification": classify_process(
               code, error,
               "\n".join(l for l in output.splitlines() if "ERROR:" not in l),
               0, SIG),
           "error_axis_only_classification": classify_process(
               0 if code is None else code, None, output, 0, SIG),
           "output_lines": output.strip().splitlines()}
    m = re.search(r"DESCENDANT_PIPE godot_pid=(\d+)", output)
    rec["godot_pid"] = int(m.group(1)) if m else None
    m = re.search(r"DESCENDANT_PIPE spawned_pid=(\d+)", output)
    rec["descendant_pid"] = int(m.group(1)) if m else None
    m = re.search(r"DESCENDANT_PIPE_ERRFORGE write_ppid=(\d+)", output)
    rec["write_ppid"] = int(m.group(1)) if m else None
    return rec


def bounded_popen(cmd, bound, tag):
    """communicate(timeout) bound — the hold-arm record shape (r62 meta)."""
    rec = {"tag": tag, "command": cmd, "timed_out": False,
           "child_exit_at_timeout": None, "actual_exit": None,
           "error": None}
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                            text=True)
    t0 = time.monotonic()
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
    rec["elapsed_seconds"] = round(time.monotonic() - t0, 3)
    rec["signature_observed"] = SIG in text
    rec["error_marker_captured"] = ERR in text
    rec["inner_classification"] = classify_process(
        rec["actual_exit"], rec["error"], text, 0, SIG)
    # Dual datum vs r63: clear ONLY the timeout/exit axes, keep the error
    # bytes — r63's signature axis classified True here; the error axis
    # must still reject.
    rec["error_axis_only_classification"] = classify_process(
        0, None, text, 0, SIG)
    rec["output_lines"] = text.strip().splitlines()
    m = re.search(r"DESCENDANT_PIPE godot_pid=(\d+)", text)
    rec["godot_pid"] = int(m.group(1)) if m else None
    m = re.search(r"DESCENDANT_PIPE spawned_pid=(\d+)", text)
    rec["descendant_pid"] = int(m.group(1)) if m else None
    m = re.search(r"DESCENDANT_PIPE_ERRFORGE write_ppid=(\d+)", text)
    rec["write_ppid"] = int(m.group(1)) if m else None
    rec["descendant_kernel_ppid_at_return"] = kernel_ppid(rec["descendant_pid"])
    rec["descendant_alive_at_return"] = pid_alive(rec["descendant_pid"])
    if pid_alive(rec["descendant_pid"]):
        try:
            os.kill(rec["descendant_pid"], signal.SIGKILL)
        except OSError:
            pass
    return rec


def gated_dual_read(cmd, bound, tag):
    """r64 gated read + SECOND marker: liveness pinned at each completing
    observation — signature AND error tracked independently."""
    rec = {"tag": tag, "command": cmd, "bound": bound, "timed_out": False,
           "actual_exit": None, "error": None,
           "signature_observed": False, "signature_observed_at": None,
           "child_alive_at_signature_observation": None,
           "error_observed": False, "error_observed_at": None,
           "child_alive_at_error_observation": None,
           "dead_observed_at": None, "error_stream": None}
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    t0 = time.monotonic()
    captured = bytearray()
    sel = selectors.DefaultSelector()
    sel.register(proc.stdout, selectors.EVENT_READ, "stdout")
    sel.register(proc.stderr, selectors.EVENT_READ, "stderr")
    deadline = t0 + bound
    sig_b, err_b = SIG.encode(), ERR.encode()
    while sel.get_map():
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            rec["timed_out"] = True
            break
        events = sel.select(min(0.005, max(0.0, remaining)))
        now = time.monotonic()
        if rec["dead_observed_at"] is None and proc.poll() is not None:
            rec["dead_observed_at"] = round(now - t0, 6)
        for key, _ in events:
            alive_before = proc.poll() is None
            try:
                chunk = os.read(key.fileobj.fileno(), 65536)
            except OSError:
                chunk = b""
            if not chunk:
                sel.unregister(key.fileobj)
                continue
            captured += chunk
            if not rec["signature_observed"] and sig_b in captured:
                rec["signature_observed"] = True
                rec["signature_observed_at"] = round(now - t0, 6)
                rec["child_alive_at_signature_observation"] = alive_before
            if not rec["error_observed"] and err_b in captured:
                rec["error_observed"] = True
                rec["error_observed_at"] = round(now - t0, 6)
                rec["child_alive_at_error_observation"] = alive_before
                rec["error_stream"] = key.data
    if rec["dead_observed_at"] is None and proc.poll() is not None:
        rec["dead_observed_at"] = round(time.monotonic() - t0, 6)
    if rec["timed_out"]:
        rec["error"] = f"TIMEOUT after {bound} seconds"
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
    rec["actual_exit"] = proc.returncode
    text = captured.decode(errors="replace")
    rec["gated_signature_accepted"] = bool(
        rec["signature_observed"]
        and rec["child_alive_at_signature_observation"])
    rec["inner_classification"] = classify_process(
        rec["actual_exit"], rec["error"], text, 0, SIG)
    rec["output_lines"] = text.strip().splitlines()
    m = re.search(r"DESCENDANT_PIPE godot_pid=(\d+)", text)
    rec["godot_pid"] = int(m.group(1)) if m else None
    m = re.search(r"DESCENDANT_PIPE spawned_pid=(\d+)", text)
    rec["descendant_pid"] = int(m.group(1)) if m else None
    if pid_alive(rec["descendant_pid"]):
        try:
            os.kill(rec["descendant_pid"], signal.SIGKILL)
        except OSError:
            pass
    return rec


GODOT_CMD = [GODOT, "--headless", "--path", str(PROJ), "--script",
             "res://descendant_pipe_probe.gd"]

print("== substring probes ==")
# (already printed inline above)

print("== mechanism arm: sh forged-error release (no Godot) ==")
sh_forge_err = ["/usr/bin/sh", "-c",
    'echo "' + SIG + '"; echo SH godot_pid=$$; '
    'sh -c \'while read -r _ _ _ pp _ < /proc/self/stat && '
    '[ "$pp" = "$0" ]; do sleep 0.05; done; echo "' + ERR + '"; '
    'echo "DESCENDANT_PIPE_ERRFORGE write_ppid=$pp"\' $$ & '
    'echo SH spawned_pid=$!; exit 0']
rec = cases_record(sh_forge_err, 8, "sh_forge_error_release")
results["arms"].append(rec)
print(json.dumps({k: rec[k] for k in
      ("tag", "actual_exit", "error", "signature_observed",
       "error_marker_captured", "inner_classification",
       "stripped_classification", "write_ppid")}))

print("== real Godot arms under verbatim run_process (CASES record shape) ==")
for tag, flags in (("godot_default", []),
                   ("godot_errforge_release", ["--spawn-errforge-release"]),
                   ("godot_emit_errforge", ["--emit-errforge"])):
    rec = cases_record(GODOT_CMD + ["--"] + flags, 8, tag)
    results["arms"].append(rec)
    print(json.dumps({k: rec[k] for k in
          ("tag", "actual_exit", "error", "signature_observed",
           "error_marker_captured", "inner_classification",
           "stripped_classification", "error_axis_only_classification",
           "write_ppid")}))

print("== allowlist-absorption counterfactual on forged release bytes ==")
rel = next(a for a in results["arms"] if a["tag"] == "godot_errforge_release")
merged = "\n".join(rel["output_lines"])
absorbed = classify_process(0, None, merged, 0, SIG, (ERR,))
results["allowlist_absorption"] = {
    "classify_with_forged_line_allowlisted": absorbed,
    "classify_with_empty_allowlist": rel["inner_classification"]}
print(json.dumps(results["allowlist_absorption"]))

print("== bounded-Popen hold arm (3.0s) ==")
rec = bounded_popen(GODOT_CMD + ["--", "--spawn-errforge-hold"], BOUND,
                    "godot_errforge_hold")
results["arms"].append(rec)
print(json.dumps({k: rec[k] for k in
      ("tag", "timed_out", "child_exit_at_timeout", "actual_exit", "error",
       "signature_observed", "error_marker_captured", "inner_classification",
       "error_axis_only_classification", "write_ppid",
       "descendant_kernel_ppid_at_return", "descendant_alive_at_return")}))

print("== dual-marker gated read (r64 gate criterion + error marker) ==")
for tag, flags, reps in (
        ("gate_errforge_release", ["--spawn-errforge-release"], 3),
        ("gate_emit_errforge", ["--emit-errforge"], 2),
        ("gate_default_control", [], 2)):
    for i in range(reps):
        rec = gated_dual_read(GODOT_CMD + ["--"] + flags, BOUND,
                              f"{tag}_r{i}")
        results["arms"].append(rec)
        print(json.dumps({k: rec[k] for k in
              ("tag", "actual_exit", "signature_observed",
               "child_alive_at_signature_observation", "error_observed",
               "child_alive_at_error_observation", "error_stream",
               "dead_observed_at", "signature_observed_at",
               "error_observed_at", "gated_signature_accepted",
               "inner_classification")}))

print("== stream split (separate pipes) ==")
for tag, flags in (("split_errforge_release", ["--spawn-errforge-release"]),
                   ("split_emit_errforge", ["--emit-errforge"])):
    proc = subprocess.run(GODOT_CMD + ["--"] + flags, capture_output=True,
                          text=True, timeout=8)
    rec = {"tag": tag, "actual_exit": proc.returncode,
           "error_on_stdout": ERR in proc.stdout,
           "error_on_stderr": ERR in proc.stderr,
           "signature_on_stdout": SIG in proc.stdout,
           "merged_classification": classify_process(
               proc.returncode, None, proc.stdout + proc.stderr, 0, SIG),
           "stdout_lines": proc.stdout.strip().splitlines(),
           "stderr_lines": proc.stderr.strip().splitlines()}
    results["arms"].append(rec)
    print(json.dumps({k: rec[k] for k in
          ("tag", "actual_exit", "error_on_stdout", "error_on_stderr",
           "signature_on_stdout", "merged_classification")}))

out = HERE / "errforge-verdicts.json"
out.write_text(json.dumps(results, indent=2) + "\n")
print("wrote", out)
