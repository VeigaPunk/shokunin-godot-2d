#!/usr/bin/env python3
"""r69 boundary — fabrication-window REFERENT edge cells + merged-sha edges.

Probes the r69 declared axis-move's edges on a scratch copy of the tracked
descendant_pipe_probe.gd carrying the same opt-in parameterization the author
was tasked to land: --midline-gap-ms=N (default 200). Record shape mirrors
run_battery.py:surface_run (3.0s bound, communicate(), TimeoutExpired
errors=replace recovery); classify_process is extracted VERBATIM from the
landed runner and sha-pinned.

Cells (lane brief):
 (1) gap below the spawn-overhead floor (~<2ms): can the write ever win?
 (2) gap == offset (80,80): degenerate cell + referent knife-edge 78..86
 (3) offset > gap (240/100, 120/100, 100/100, 95/100, 160/50): post-tail by
     construction + provenance crossover check
 (4) gap=800 drain interaction + TIMEOUT-truncation onset bracket
Plus: sha256(so+se) vs sha256(se+so) order-sensitivity census on every
captured record (the merged-digest upgrade's coverage edge: blind when one
stream is empty).
"""
import ast, hashlib, json, re, subprocess, sys, time
from pathlib import Path

ROOT = Path.home() / "Projects/shokunin/game-dev-2d-shokunin"
RUNNER = ROOT / "corpus/fixtures/run_battery.py"
FIXTURE = ROOT / "corpus/fixtures/descendant_pipe_probe.gd"
OUT = ROOT / "corpus/live/r69-boundary"
PROJ = OUT / "proj"
RAW = OUT / "raw"
GODOT = "/usr/bin/godot"
BOUND = 3.0            # surface_run bound
SIG = "DESCENDANT_PIPE_PROBE: expected signature"
HEAD = "DESCENDANT_PIPE_PROBE: expected "
MIDERR = "ERROR: DESCENDANT_PIPE_MIDLINE forged splice"

# --- verbatim extractor: sha-pin the classifier we apply -------------------
src = RUNNER.read_text()
tree = ast.parse(src)
seg = None
for node in ast.walk(tree):
    if isinstance(node, ast.FunctionDef) and node.name == "classify_process":
        seg = ast.get_source_segment(src, node)
ns = {"__name__": "b", "hashlib": hashlib}
exec(compile(seg, "classify_process", "exec"), ns)
classify_process = ns["classify_process"]

def sha(s):
    return hashlib.sha256(s.encode()).hexdigest()

def run_cell(off_ms, gap_ms, rep, bound=BOUND):
    cmd = [GODOT, "--headless", "--path", str(PROJ), "--script",
           "res://descendant_pipe_probe.gd", "--", "--spawn-midlineforge",
           f"--midline-offset-ms={off_ms}", f"--midline-gap-ms={gap_ms}"]
    rec = {"off_ms": off_ms, "gap_ms": gap_ms, "rep": rep,
           "bound_seconds": bound, "timed_out": False,
           "child_exit_at_timeout": None, "actual_exit": None,
           "error": None, "elapsed_seconds": None,
           "command_tail": cmd[-4:]}
    started = time.monotonic()
    try:
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE, text=True, bufsize=1)
        try:
            so, se = proc.communicate(timeout=bound)
            rec["actual_exit"] = proc.returncode
        except subprocess.TimeoutExpired as exc:
            rec["timed_out"] = True
            rec["child_exit_at_timeout"] = proc.poll()
            so = (exc.stdout.decode(errors="replace")
                  if isinstance(exc.stdout, bytes) else (exc.stdout or ""))
            se = (exc.stderr.decode(errors="replace")
                  if isinstance(exc.stderr, bytes) else (exc.stderr or ""))
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
    except (OSError, ValueError) as exc:
        so, se = "", ""
        rec["error"] = f"launch/read error: {exc}"
    rec["elapsed_seconds"] = round(time.monotonic() - started, 3)
    merged = so + se
    lines = merged.splitlines()
    spliced = next((l.strip() for l in lines
                    if HEAD in l and MIDERR in l), None)
    rec["spliced_line"] = spliced
    rec["fabrication_landed"] = spliced is not None
    rec["signature_observed"] = SIG in merged
    rec["error_lines"] = sorted({l.strip() for l in lines if "ERROR:" in l})
    m = re.search(r"DESCENDANT_PIPE godot_pid=(\d+)", merged)
    rec["godot_pid"] = int(m.group(1)) if m else None
    m = re.search(r"DESCENDANT_PIPE spawned_pid=(\d+)", merged)
    rec["descendant_pid"] = int(m.group(1)) if m else None
    m = re.search(r"DESCENDANT_PIPE_MIDLINE write_ppid=(\d+)", merged)
    rec["write_ppid"] = int(m.group(1)) if m else None
    rec["write_pre_death"] = (rec["write_ppid"] is not None
                              and rec["write_ppid"] == rec["godot_pid"])
    rec["merged_classification"] = classify_process(
        rec["actual_exit"], rec["error"], merged, 0, SIG)
    # receipt-upgrade edge fields: the declared sha256(merged) plus the
    # REVERSED-concat digest — order-sensitivity is exactly what the upgrade
    # claims to gate; equal digests = concat order indistinguishable.
    rec["stdout_sha256"] = sha(so)
    rec["stderr_sha256"] = sha(se)
    rec["merged_sha256"] = sha(merged)
    rec["merged_reversed_sha256"] = sha(se + so)
    rec["merged_order_sensitive"] = (rec["merged_sha256"]
                                     != rec["merged_reversed_sha256"])
    rec["stdout_bytes"] = len(so.encode())
    rec["stderr_bytes"] = len(se.encode())
    rec["stderr_empty"] = (se == "")
    tag = f"o{off_ms}_g{gap_ms}_r{rep}"
    (RAW / f"{tag}.stdout").write_text(so)
    (RAW / f"{tag}.stderr").write_text(se)
    return rec

out = {"runner_sha256": hashlib.sha256(RUNNER.read_bytes()).hexdigest(),
       "tracked_fixture_sha256": hashlib.sha256(FIXTURE.read_bytes()).hexdigest(),
       "scratch_fixture_sha256": sha((PROJ / "descendant_pipe_probe.gd").read_text()),
       "classify_process_sha256": sha(seg),
       "bound_seconds": BOUND, "phases": {}}

def cell(name, off, gap, reps):
    recs = [run_cell(off, gap, i) for i in range(reps)]
    landed = sum(1 for r in recs if r["fabrication_landed"])
    return {"off_ms": off, "gap_ms": gap, "reps": recs,
            "reps_landed": landed,
            "outcome": ("fabricated" if landed == reps
                        else "missed" if landed == 0 else "mixed")}

ph = out["phases"]

# P1 — declared crossed ladder bridge (author sweep, offset fixed 80)
ph["p1_declared_gap_ladder"] = [
    cell(f"g{g}", 80, g, 3) for g in (50, 100, 200, 400, 800)]

# P2 — below the spawn-overhead floor: can the write ever win?
ph["p2a_floor_off80"] = [cell(f"o80_g{g}", 80, g, 3) for g in (0, 1, 2, 3, 5, 10)]
ph["p2b_floor_off0"] = [cell(f"o0_g{g}", 0, g, 3) for g in (0, 1, 2, 3, 5)]
ph["p2c_floor_offneg50"] = [cell(f"oneg50_g{g}", -50, g, 3) for g in (0, 2, 5)]

# P3 — degenerate cell (gap==offset) + referent knife-edge bracket
ph["p3_degenerate_g80"] = cell("o80_g80", 80, 80, 6)
ph["p3_referent_edge"] = [cell(f"o80_g{g}", 80, g, 3)
                          for g in (78, 79, 81, 82, 83, 84, 85, 86)]

# P4 — offset > gap: write lands post-tail by construction
ph["p4_offset_over_gap"] = [
    cell(f"o{o}_g{g}", o, g, 3)
    for o, g in ((240, 100), (120, 100), (100, 100), (95, 100), (160, 50))]

# P5 — long gap (800ms) stability + TIMEOUT-truncation onset
ph["p5a_gap800_stability"] = cell("o80_g800", 80, 800, 8)
# startup estimate from the gap=0 cells: elapsed ~= startup
el0 = [r["elapsed_seconds"] for c in ph["p2a_floor_off80"] + ph["p2b_floor_off0"]
       for r in c["reps"] if r["elapsed_seconds"] is not None]
startup_est = min(el0) if el0 else 0.5
# truncation onset: child exits ~startup+gap; TIMEOUT when that > bound
onset_ms = int(round((BOUND - startup_est) * 1000 / 50.0) * 50)
ph["p5b_timeout_onset"] = {
    "startup_est_seconds": round(startup_est, 3),
    "onset_gap_ms_estimate": onset_ms,
    "cells": [cell(f"o80_g{g}", 80, g, 2)
              for g in (max(0, onset_ms - 300), max(0, onset_ms - 100),
                        onset_ms + 100, onset_ms + 400)]}

# P6 — merged-sha order-sensitivity census across all captured records
all_recs = []
def collect(x):
    if isinstance(x, dict) and "reps" in x:
        all_recs.extend(x["reps"])
    elif isinstance(x, list):
        for i in x:
            collect(i)
    elif isinstance(x, dict):
        for v in x.values():
            collect(v)
collect(ph)
order_sensitive = sum(1 for r in all_recs if r["merged_order_sensitive"])
empty_stderr = sum(1 for r in all_recs if r["stderr_empty"])
ph["p6_merged_sha_census"] = {
    "records": len(all_recs),
    "order_sensitive": order_sensitive,
    "empty_stderr_records": empty_stderr,
    "order_blind_when_stderr_empty": all(
        (not r["merged_order_sensitive"]) for r in all_recs
        if r["stderr_empty"]),
    "note": ("sha256(so+se) != sha256(se+so) iff both streams nonempty "
             "(for these marker shapes): the merged digest gates concat "
             "order ONLY on two-stream records; an empty stderr makes "
             "merged sha identical to sha(so) under either order.")}

(OUT / "boundary-verdicts.json").write_text(json.dumps(out, indent=2) + "\n")
print("done; records:", len(all_recs),
      "order_sensitive:", order_sensitive,
      "empty_stderr:", empty_stderr)
