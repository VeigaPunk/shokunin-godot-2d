#!/usr/bin/env python3
"""r68 boundary driver — midlineforge mechanism edges + drain/timeout.

Phase 1: offset space beyond the author's {0,40,80,120,160,240} ladder —
pre-head/negative, jitter, duplicate writes, fine edge sweep, gap scaling.
Phase 2: does drain scheduling interact with TIMEOUT truncation (w7
xconnector-flagged cell).
Phase 3 (post-landing): landed-ladder verification + divergent_clause
collision cells + sha256 same-input edge cells. Added after diff lands.

All classifiers are ast-extracted verbatim from the CURRENT tracked
run_battery.py and sha-pinned.
"""
import ast, hashlib, json, os, re, shlex, signal, subprocess, sys, time
from pathlib import Path

ROOT = Path.home() / "Projects/shokunin/game-dev-2d-shokunin"
RUNNER = ROOT / "corpus/fixtures/run_battery.py"
OUT = ROOT / "corpus/live/r68-boundary"
PROJ = OUT / "proj"
RAW = OUT / "raw"
GODOT = "/usr/bin/godot"
SIG = "BOUNDARY_MIDLINE: expected signature"
ERRLINE = "ERROR: BOUNDARY_MIDLINE forged splice"

src = RUNNER.read_text()
tree = ast.parse(src)

def extract(funcname):
    """Pull a nested-or-top-level def's source segment by name."""
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == funcname:
            seg = ast.get_source_segment(src, node)
            return seg
    return None

ns = {"__name__": "boundary_extract"}
shas = {}
for fn in ("classify_process", "classify_streams", "classify_audio_process"):
    seg = extract(fn)
    shas[fn] = hashlib.sha256(seg.encode()).hexdigest() if seg else None
    if seg:
        exec(compile(seg, fn, "exec"), ns)
classify_process = ns["classify_process"]
classify_streams = ns["classify_streams"]

verdicts = {"runner_sha256": hashlib.sha256(RUNNER.read_bytes()).hexdigest(),
            "function_shas": shas, "phases": {}}

def merged_lines(so, se):
    return (so + se).splitlines()

def classify_pair(so, se, code, error):
    return {"merged": classify_process(code, error, so + se, 0, SIG),
            "streams": classify_streams(code, error, so, se, 0, SIG)}

def run_capture(flags, bound=8.0):
    """subprocess.run capture like run_process_streams (per-fd)."""
    cmd = [GODOT, "--headless", "--path", str(PROJ), "--script",
           "res://boundary_midline_probe.gd", "--"] + flags
    try:
        p = subprocess.run(cmd, capture_output=True, text=True, timeout=bound)
        return p.stdout or "", p.stderr or "", p.returncode, None, cmd
    except subprocess.TimeoutExpired as e:
        so = e.stdout.decode(errors="replace") if isinstance(e.stdout, bytes) else (e.stdout or "")
        se = e.stderr.decode(errors="replace") if isinstance(e.stderr, bytes) else (e.stderr or "")
        return so, se, None, f"TIMEOUT after {bound} seconds", cmd
    except OSError as e:
        return "", str(e), None, f"launch error: {e}", cmd

def midline_read(so, se):
    """Classify where the descendant write landed relative to the halves."""
    merged = so + se
    lines = merged.splitlines()
    spliced = [l for l in lines if "BOUNDARY_MIDLINE: expected " in l
               and ERRLINE in l]
    sig_intact = SIG in merged
    err_present = any(ERRLINE in l for l in lines)
    head_lines = [l for l in lines if "BOUNDARY_MIDLINE: expected " in l]
    # position of the error write relative to head bytes in the byte stream
    head_idx = merged.find("BOUNDARY_MIDLINE: expected ")
    err_idx = merged.find(ERRLINE)
    tail_idx = merged.find("\nsignature")
    pos = "absent"
    if err_idx >= 0:
        if head_idx < 0:
            pos = "no_head"
        elif err_idx < head_idx:
            pos = "before_head"
        elif tail_idx >= 0 and err_idx > tail_idx:
            pos = "after_tail"
        elif spliced:
            pos = "midline_splice"
        else:
            pos = "in_gap_other"
    return {"spliced_line": spliced[0].strip() if spliced else None,
            "signature_intact": sig_intact, "error_present": err_present,
            "err_position": pos,
            "n_error_lines": sum(1 for l in lines if "ERROR:" in l),
            "head_lines": [l.strip() for l in head_lines]}

def one_run(flags, bound=8.0, tag=""):
    so, se, code, error, cmd = run_capture(flags, bound)
    rec = {"flags": flags, "tag": tag, "exit": code, "error": error,
           "ppid_write": None, "godot_pid": None}
    m = re.search(r"godot_pid=(\d+)", so + se)
    rec["godot_pid"] = int(m.group(1)) if m else None
    m = re.search(r"write_ppid=(\d+)", so + se)
    rec["ppid_write"] = int(m.group(1)) if m else None
    rec.update(midline_read(so, se))
    rec["verdicts"] = classify_pair(so, se, code, error)
    return rec, so, se

# ---------- Phase 1: offset space beyond the ladder ----------
p1 = {"note": "signature=BOUNDARY_MIDLINE: expected signature; "
              "gap=200ms; mechanism identical to landed midlineforge"}

# 1a. Negative / pre-gap writes: --off=-1 -> immediate write racing head;
# --pre-head -> provably before gap.
for tag, flags in (("off_-1", ["--off=-1"]), ("off_-999", ["--off=-999"]),
                   ("pre_head_150", ["--pre-head", "--off=0"])):
    reps = []
    for i in range(3):
        rec, so, se = one_run(flags, tag=f"{tag}#{i}")
        reps.append({"err_position": rec["err_position"],
                     "sig_intact": rec["signature_intact"],
                     "spliced": rec["spliced_line"] is not None,
                     "merged": rec["verdicts"]["merged"],
                     "streams": rec["verdicts"]["streams"],
                     "n_err": rec["n_error_lines"]})
        (RAW / f"p1_{tag}_{i}.stdout").write_text(so)
        (RAW / f"p1_{tag}_{i}.stderr").write_text(se)
    p1[tag] = reps

# 1b. Edge sweep finer than the author ladder: {160..320} step 10/20/40/80.
p1["edge_sweep"] = {}
for off in (150, 160, 170, 180, 190, 195, 200, 205, 210, 220, 240, 260, 300, 400):
    reps = []
    for i in range(3):
        rec, so, se = one_run(["--off=" + str(off)], tag=f"off{off}#{i}")
        reps.append({"pos": rec["err_position"], "sig": rec["signature_intact"],
                     "merged": rec["verdicts"]["merged"],
                     "streams": rec["verdicts"]["streams"]})
        if i == 0:
            (RAW / f"p1_off{off}.stdout").write_text(so)
            (RAW / f"p1_off{off}.stderr").write_text(se)
    p1["edge_sweep"][str(off)] = reps

# 1c. Jitter arm: 80 + RANDOM%40 ms, 6 reps.
p1["jitter_80_40"] = []
for i in range(6):
    rec, so, se = one_run(["--jitter=80,40"], tag=f"j{i}")
    p1["jitter_80_40"].append({"pos": rec["err_position"],
                               "sig": rec["signature_intact"],
                               "merged": rec["verdicts"]["merged"],
                               "streams": rec["verdicts"]["streams"]})

# 1d. Duplicate mid-gap writes: (40,140) both inside; (80,260) straddling hi;
# (0,0) double at gap open.
p1["dup"] = {}
for tag, flags in (("dup_40_140", ["--dup=40,140"]),
                   ("dup_80_260", ["--dup=80,260"]),
                   ("dup_10_10", ["--dup=10,10"])):
    reps = []
    for i in range(3):
        rec, so, se = one_run(flags, tag=f"{tag}#{i}")
        reps.append({"pos": rec["err_position"], "sig": rec["signature_intact"],
                     "n_err": rec["n_error_lines"],
                     "spliced": rec["spliced_line"],
                     "merged": rec["verdicts"]["merged"],
                     "streams": rec["verdicts"]["streams"]})
        (RAW / f"p1_{tag}_{i}.stdout").write_text(so)
        (RAW / f"p1_{tag}_{i}.stderr").write_text(se)
    p1["dup"][tag] = reps

# 1e. Gap scaling: same 80ms offset with gap=60 (write lands after gap) and
# gap=400 (deep inside) — is the window the gap or the delay quantum?
p1["gap_scaling"] = {}
for g in (60, 120, 400):
    reps = []
    for i in range(3):
        rec, so, se = one_run(["--off=80", "--gap=" + str(g)], tag=f"g{g}#{i}")
        reps.append({"pos": rec["err_position"], "sig": rec["signature_intact"],
                     "merged": rec["verdicts"]["merged"]})
    p1["gap_scaling"][str(g)] = reps

# 1f. Burst: writes at 20..340ms — count how many land mid-line / where.
p1["burst"] = []
for i in range(2):
    rec, so, se = one_run(["--burst"], tag=f"b{i}")
    lines = (so + se).splitlines()
    p1["burst"].append({"n_err": rec["n_error_lines"],
                        "sig": rec["signature_intact"],
                        "merged": rec["verdicts"]["merged"],
                        "spliced": rec["spliced_line"],
                        "err_lines": [l.strip() for l in lines if "ERROR:" in l]})
    (RAW / f"p1_burst_{i}.stdout").write_text(so)
    (RAW / f"p1_burst_{i}.stderr").write_text(se)

verdicts["phases"]["p1_offsets_beyond_ladder"] = p1

# ---------- Phase 2: drain scheduling x TIMEOUT truncation ----------
p2 = {"note": ("communicate(timeout) partial buffers are drain-scheduled; "
               "success-path drain order is invisible (fixed concat). "
               "Probes the w7-xconnector flagged interaction cell.")}

# 2a. hold-flood: stderr numbered flood while descendant holds pipes past
# bound -> which flood index is the captured tail per rep?
p2["hold_flood"] = {"bound": 1.5, "reps": []}
for i in range(10):
    so, se, code, error, cmd = run_capture(["--hold-flood=5"], bound=1.5)
    idxs = [int(m.group(1)) for m in re.finditer(r"T-FLOOD-(\d+)", se)]
    rec = {"rep": i, "error": error, "exit": code,
           "stderr_lines": len(idxs), "last_idx": idxs[-1] if idxs else None,
           "stdout_lines": len(so.splitlines()),
           "sig_in_stdout": SIG in so}
    p2["hold_flood"]["reps"].append(rec)
    if i == 0:
        (RAW / "p2_flood_0.stdout").write_text(so)
        (RAW / "p2_flood_0.stderr").write_text(se)
last = [r["last_idx"] for r in p2["hold_flood"]["reps"] if r["last_idx"] is not None]
p2["hold_flood"]["tail_spread"] = (max(last) - min(last)) if last else None
p2["hold_flood"]["distinct_tails"] = sorted(set(last))

# 2b. hold-seam at various schedules around the bound: does the stderr head
# land in the truncated capture, and is the fabricated phantom present?
p2["hold_seam"] = {"bound": 2.0, "cells": {}}
for sched in (500, 1500, 1900, 2100, 2500):
    reps = []
    for i in range(3):
        so, se, code, error, cmd = run_capture(["--hold-seam", "--sched=" + str(sched)],
                                               bound=2.0)
        merged = so + se
        phantom = "BOUNDARY trunc tail ends in ERROR: TRUNC phantom fabricated line"
        reps.append({"sched_ms": sched, "rep": i, "error": error,
                     "timed_out": error is not None and "TIMEOUT" in error,
                     "stdout_tail_unterminated": so.rstrip("\n").splitlines()[-1].strip()
                        if so.splitlines() else None,
                     "stderr_head": se.splitlines()[0].strip() if se.splitlines() else None,
                     "phantom_in_merged": phantom in merged,
                     "phantom_line": [l.strip() for l in merged.splitlines()
                                      if "TRUNC phantom" in l],
                     "held_ppid_captured": "BOUNDARY_HELD write_ppid=" in se})
        (RAW / f"p2_seam_{sched}_{i}.stdout").write_text(so)
        (RAW / f"p2_seam_{sched}_{i}.stderr").write_text(se)
    p2["hold_seam"]["cells"][str(sched)] = reps

# 2c. deadline-race granularity: writes landing ±20ms around the bound — the
# drain thread's last read window. stderr write at bound-20ms, bound-5ms etc.
p2["deadline_race"] = {"bound": 2.0, "cells": {}}
for sched in (1980, 1995, 2005, 2020):
    hits = []
    for i in range(4):
        so, se, code, error, cmd = run_capture(["--hold-seam", "--sched=" + str(sched)],
                                               bound=2.0)
        hits.append("TRUNC phantom" in se)
    p2["deadline_race"]["cells"][str(sched)] = {"captured_in_stderr": hits}

verdicts["phases"]["p2_drain_timeout"] = p2

(OUT / "boundary-verdicts.json").write_text(json.dumps(verdicts, indent=2) + "\n")
print(json.dumps({k: "done" for k in verdicts["phases"]}, indent=0))
