#!/usr/bin/env python3
"""r69-scribe — midlineforge fabrication-window REFERENT measurement.

Holds the descendant write offset fixed and sweeps the head->tail
signature gap (the r68 offset ladder's other axis): each cell is an
(offset_ms, gap_ms) pair driven through my own scratch copy of the
tracked fixture (parameterized --midline-offset-ms / --midline-gap-ms).

Question under test: is the fabrication bound's referent the GAP
(write lands inside [head_flush, tail_flush) at any gap size —
gap-relative, "offset < gap") or an ABSOLUTE write-latency constant
(~198ms from the head flush, the r68 nominal edge)?

Discriminating cells (offset, gap):
  - gap-relative MISS / absolute FABRICATE:  gap < write position < ~198
    e.g. (80,50), (120,50), (150,100)
  - gap-relative FABRICATE / absolute MISS:  ~198 < write position < gap
    e.g. (300,400), (250,800), (500,800)
  - agreement cells: inside both (80,{100,200,400,800}) or outside both
    (350,200)

Per run captures BOTH pipes with per-chunk arrival timestamps (selector
reads), so the record carries WHERE inside the head->tail window the
descendant write landed in reader-wall-time:
  t_head = first bytes of the printraw head fragment
  t_err  = first bytes of the forged ERROR line
  t_tail = first bytes completing the tail line ("signature\n")
  write_pos_in_gap = t_err - t_head ; gap_measured = t_tail - t_head

Outcome taxonomy (merged stdout order):
  midline_splice            : H < E < T        -> fabricated line + sig DESTROYED
  midline_splice_straddle   : H < E < T < E2   -> splice + ppid echo past tail
  post_tail                 : T < E            -> standalone ERROR + sig INTACT
  pre_head                  : E < H            -> standalone ERROR + sig INTACT
  no_descendant_write       : no ERROR bytes
Verdict via verbatim extracted classify_process over stdout+stderr concat
(the run_process drain shape). write_ppid parsed per run: pre-death writes
carry write_ppid == godot_pid; post-death carries the reaper pid.
"""
import argparse
import hashlib
import json
import os
import re
import selectors
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from extract_classifiers import NS, SEGMENT_SHAS

PROJ = HERE / "proj"
SIG = "DESCENDANT_PIPE_PROBE: expected signature"
HEAD = "DESCENDANT_PIPE_PROBE: expected "
ERR = "ERROR: DESCENDANT_PIPE_MIDLINE forged splice"
PPID_TOK = "DESCENDANT_PIPE_MIDLINE write_ppid="
GPID_TOK = "DESCENDANT_PIPE godot_pid="


def run_probe(offset_ms, gap_ms, bound=8, godot="godot"):
    env = dict(os.environ)
    xdg = (HERE / "xdg-data").resolve()
    xdg.mkdir(exist_ok=True)
    env["XDG_DATA_HOME"] = str(xdg)
    cmd = [godot, "--headless", "--path", str(PROJ), "--script",
           "res://descendant_pipe_probe.gd", "--", "--spawn-midlineforge",
           f"--midline-offset-ms={offset_ms}",
           f"--midline-gap-ms={gap_ms}"]
    t0 = time.monotonic()
    chunks = []
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE, env=env)
    sel = selectors.DefaultSelector()
    sel.register(proc.stdout, selectors.EVENT_READ, "stdout")
    sel.register(proc.stderr, selectors.EVENT_READ, "stderr")
    timed_out = False
    try:
        while sel.get_map():
            if time.monotonic() - t0 > bound:
                timed_out = True
                proc.kill()
            for key, _ in sel.select(0.05):
                data = os.read(key.fileobj.fileno(), 65536)
                if data:
                    chunks.append((round((time.monotonic() - t0) * 1000, 3),
                                   key.data, data))
                else:
                    sel.unregister(key.fileobj)
        proc.wait(timeout=3)
    except subprocess.TimeoutExpired:
        proc.kill()
        proc.wait()
    elapsed = time.monotonic() - t0
    stdout_b = b"".join(c[2] for c in chunks if c[1] == "stdout")
    stderr_b = b"".join(c[2] for c in chunks if c[1] == "stderr")
    return (cmd, chunks, stdout_b.decode(errors="replace"),
            stderr_b.decode(errors="replace"), proc.returncode,
            timed_out, round(elapsed, 3))


def first_byte_ts(chunks, needle, stream="stdout"):
    nb = needle.encode()
    seen = b""
    for t, s, data in chunks:
        if s != stream:
            continue
        seen += data
        if nb in seen:
            return t
    return None


def parse_kv(text, token):
    for line in text.splitlines():
        if token in line:
            m = re.search(re.escape(token) + r"(\d+)", line)
            if m:
                return int(m.group(1))
    return None


def interleave(stdout):
    h = stdout.find(HEAD)
    t = stdout.rfind("signature")
    e = stdout.find(ERR)
    e2 = stdout.find(PPID_TOK, e + len(ERR)) if e >= 0 else stdout.find(PPID_TOK)
    idx = {"H": h, "T": t, "E": e, "E2": e2}
    order = "".join(k for k, v in sorted(idx.items(), key=lambda kv: kv[1])
                    if v >= 0)
    spliced = next((l.strip() for l in stdout.splitlines()
                    if HEAD in l and ERR in l), None)
    sig_present = SIG in stdout
    if e < 0:
        outcome = "no_descendant_write"
    elif h >= 0 and e < h:
        outcome = "pre_head"
    elif h >= 0 and t >= 0 and h < e < t:
        outcome = ("midline_splice_straddle"
                   if e2 >= 0 and e < t < e2 else "midline_splice")
    elif t >= 0 and e > t:
        outcome = "post_tail"
    else:
        outcome = f"unclassified:{order}"
    return {"order": order, "outcome": outcome,
            "spliced_line": spliced, "signature_present": sig_present,
            "byte_idx": idx}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cells", required=True,
                    help="comma list of offset_ms:gap_ms pairs")
    ap.add_argument("--reps", type=int, default=6)
    ap.add_argument("--godot", default="godot")
    ap.add_argument("--label", default="gapladder")
    ap.add_argument("--out", default=None)
    args = ap.parse_args()
    cells = []
    for tok in args.cells.split(","):
        off, gap = tok.split(":")
        cells.append((float(off), int(gap)))
    records = []
    for off, gap in cells:
        for rep in range(args.reps):
            cmd, chunks, so, se, code, timed_out, elapsed = run_probe(
                off, gap, godot=args.godot)
            inter = interleave(so)
            merged = so + se
            cls = NS["classify_process"](code, None, merged, 0, SIG)
            t_head = first_byte_ts(chunks, HEAD)
            t_err = first_byte_ts(chunks, ERR)
            t_tail = first_byte_ts(chunks, "signature\n")
            write_ppid = parse_kv(so, PPID_TOK)
            godot_pid = parse_kv(so, GPID_TOK)
            rec = {"offset_ms": off, "gap_ms": gap, "rep": rep,
                   "exit": code, "timed_out": timed_out,
                   "elapsed_seconds": elapsed, "cls": cls,
                   "t_head_ms": t_head, "t_err_ms": t_err,
                   "t_tail_ms": t_tail,
                   "write_pos_in_gap_ms": (
                       round(t_err - t_head, 3)
                       if t_head is not None and t_err is not None else None),
                   "gap_measured_ms": (
                       round(t_tail - t_head, 3)
                       if t_head is not None and t_tail is not None else None),
                   "write_ppid": write_ppid, "godot_pid": godot_pid,
                   "write_pre_death": (write_ppid is not None
                                       and write_ppid == godot_pid),
                   "raw_stdout_sha256": hashlib.sha256(
                       so.encode()).hexdigest(),
                   "raw_stderr_sha256": hashlib.sha256(
                       se.encode()).hexdigest(),
                   "merged_sha256": hashlib.sha256(
                       merged.encode()).hexdigest(),
                   "raw_stdout": so, "raw_stderr": se,
                   **inter,
                   "n_chunks_stdout": sum(1 for c in chunks
                                          if c[1] == "stdout")}
            records.append(rec)
            print(f"off={off:>6} gap={gap:>5} rep={rep} "
                  f"outcome={inter['outcome']:<24} order={inter['order']:<7} "
                  f"sig={inter['signature_present']!s:<5} cls={cls!s:<5} "
                  f"pos={rec['write_pos_in_gap_ms']} "
                  f"gapM={rec['gap_measured_ms']} "
                  f"pre={rec['write_pre_death']!s:<5}", flush=True)
    out = args.out or HERE / f"{args.label}-results.json"
    Path(out).write_text(json.dumps(
        {"probe": "r69-scribe midlineforge gap-referent crossed ladder",
         "proj_probe_sha256": hashlib.sha256(
             (PROJ / "descendant_pipe_probe.gd").read_bytes()).hexdigest(),
         "classifier_segment_shas": SEGMENT_SHAS,
         "cells": cells, "reps": args.reps,
         "records": records}, indent=2) + "\n")
    summ = {}
    for r in records:
        k = f"off{r['offset_ms']}:gap{r['gap_ms']}"
        summ.setdefault(k, {}).setdefault(r["outcome"], 0)
        summ[k][r["outcome"]] += 1
    print("SUMMARY", json.dumps(summ, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
