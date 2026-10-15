#!/usr/bin/env python3
"""r68-scribe — midlineforge fabrication-window ladder, independently
measured. Runs the tracked fixture's --spawn-midlineforge arm (scratch copy
parameterized by --midline-offset-ms / --midline-gap-ms /
--midline-head-stagger-ms) across descendant write offsets.

Per run captures BOTH pipes with per-chunk arrival timestamps (selector
reads on stdout/stderr), so the record carries not just the merged-byte
outcome but WHERE inside the head->tail gap the descendant write landed in
reader-wall-time: t_head (first byte of the printraw head), t_err (first
byte of the forged ERROR line), t_tail (first byte completing the tail
line). Window position = (t_err - t_head); gap = (t_tail - t_head).

Classification per run:
  pre_head_standalone : E before H          -> signature INTACT
  midline_splice      : H < E < T           -> signature destroyed +
                        fabricated 'expected ERROR:' line
  straddle_ppid       : H < E < T < E2      -> E inside, ppid echo after tail
  post_tail           : T < E               -> signature INTACT
Verdict via verbatim extracted classify_process over stdout+stderr concat
(the run_process drain shape).
"""
import argparse
import hashlib
import json
import os
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
PPID = "DESCENDANT_PIPE_MIDLINE write_ppid="


def run_probe(offset_ms, gap_ms=200, head_stagger_ms=0, bound=8,
              godot="godot"):
    """Popen with selector-timestamped chunk reads on both pipes."""
    env = dict(os.environ)
    xdg = (HERE / "xdg-data").resolve()
    xdg.mkdir(exist_ok=True)
    env["XDG_DATA_HOME"] = str(xdg)
    cmd = [godot, "--headless", "--path", str(PROJ), "--script",
           "res://descendant_pipe_probe.gd", "--", "--spawn-midlineforge",
           f"--midline-offset-ms={offset_ms}",
           f"--midline-gap-ms={gap_ms}"]
    if head_stagger_ms:
        cmd.append(f"--midline-head-stagger-ms={head_stagger_ms}")
    t0 = time.monotonic()
    chunks = []  # (t_rel_ms, stream, bytes)
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
    """First arrival timestamp (ms) of a chunk containing needle bytes."""
    nb = needle.encode()
    seen = b""
    for t, s, data in chunks:
        if s != stream:
            continue
        seen += data
        if nb in seen:
            # refine: the needle may complete inside this chunk; the chunk
            # arrival ts is the bound we can prove.
            return t
    return None


def classify_interleave(stdout):
    h = stdout.find(HEAD)
    # 'signature' tail: last occurrence avoids matching 'expected signature'
    # inside a fully-intact marker if one were somehow printed whole.
    t = stdout.rfind("signature")
    e = stdout.find(ERR)
    e2 = stdout.find(PPID, e + len(ERR)) if e >= 0 else stdout.find(PPID)
    idx = {"H": h, "T": t, "E": e, "E2": e2}
    order = "".join(k for k, v in sorted(idx.items(), key=lambda kv: kv[1])
                    if v >= 0)
    lines = stdout.splitlines()
    spliced = next((l.strip() for l in lines if HEAD in l and ERR in l), None)
    sig_present = SIG in stdout
    if e < 0:
        outcome = "no_descendant_write"
    elif h >= 0 and e < h:
        outcome = "pre_head_standalone"
    elif h >= 0 and t >= 0 and h < e < t:
        outcome = ("midline_splice_straddle_ppid"
                   if e2 >= 0 and e < t < e2 else "midline_splice")
    elif t >= 0 and e > t:
        outcome = "post_tail"
    else:
        outcome = f"unclassified:{order}"
    return {"order": order, "outcome": outcome, "spliced_line": spliced,
            "signature_present": sig_present, "byte_idx": idx}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--offsets", default="0,40,80,120,160,240")
    ap.add_argument("--reps", type=int, default=5)
    ap.add_argument("--gap", type=int, default=200)
    ap.add_argument("--head-stagger", type=int, default=0)
    ap.add_argument("--godot", default="godot")
    ap.add_argument("--label", default="ladder")
    ap.add_argument("--out", default=None)
    args = ap.parse_args()
    offsets = [float(x) for x in args.offsets.split(",")]
    records = []
    for off in offsets:
        for rep in range(args.reps):
            cmd, chunks, so, se, code, timed_out, elapsed = run_probe(
                off, gap_ms=args.gap, head_stagger_ms=args.head_stagger,
                godot=args.godot)
            inter = classify_interleave(so)
            cls = NS["classify_process"](code, None, so + se, 0, SIG)
            t_head = first_byte_ts(chunks, HEAD)
            t_err = first_byte_ts(chunks, ERR)
            # tail completes when the standalone 'signature\n' lands
            t_tail = first_byte_ts(chunks, "signature\n")
            rec = {"offset_ms": off, "rep": rep, "exit": code,
                   "timed_out": timed_out,
                   "elapsed_seconds": elapsed,
                   "cls": cls,
                   "t_head_ms": t_head, "t_err_ms": t_err,
                   "t_tail_ms": t_tail,
                   "write_pos_in_gap_ms": (
                       round(t_err - t_head, 3)
                       if t_head is not None and t_err is not None else None),
                   "gap_ms_measured": (
                       round(t_tail - t_head, 3)
                       if t_head is not None and t_tail is not None else None),
                   "raw_stdout_sha256": hashlib.sha256(so.encode()).hexdigest(),
                   "raw_stderr_sha256": hashlib.sha256(se.encode()).hexdigest(),
                   "raw_stdout": so, "raw_stderr": se,
                   **inter,
                   "stdout_tail_lines": so.splitlines()[-4:],
                   "stderr_lines": se.splitlines(),
                   "n_chunks_stdout": sum(1 for c in chunks if c[1] == "stdout")}
            records.append(rec)
            print(f"off={off:>6} rep={rep} outcome={inter['outcome']:<28} "
                  f"order={inter['order']:<6} sig={inter['signature_present']!s:<5} "
                  f"cls={cls} pos={rec['write_pos_in_gap_ms']} "
                  f"gap={rec['gap_ms_measured']}", flush=True)
    out = args.out or HERE / f"{args.label}-results.json"
    Path(out).write_text(json.dumps(
        {"probe": "r68-scribe midlineforge offset ladder",
         "proj_probe_sha256": hashlib.sha256(
             (PROJ / "descendant_pipe_probe.gd").read_bytes()).hexdigest(),
         "classifier_segment_shas": SEGMENT_SHAS,
         "gap_ms": args.gap, "head_stagger_ms": args.head_stagger,
         "offsets": offsets, "reps": args.reps,
         "records": records}, indent=2) + "\n")
    summ = {}
    for r in records:
        summ.setdefault(str(r["offset_ms"]), {}).setdefault(r["outcome"], 0)
        summ[str(r["offset_ms"])][r["outcome"]] += 1
    print("SUMMARY", json.dumps(summ, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
