#!/usr/bin/env python3
"""r68 critic — midlineforge fabrication-window ladder, rep-resolved.

Runs the parameterized replica probe across descendant write offsets with
N reps each, captures stdout/stderr via subprocess.run(capture_output=True)
(the same drain shape run_battery.py surface_run uses), and classifies each
run's stdout interleave ordering:

  E=descendant ERROR write, E2=write_ppid echo, H=printraw head, T=print tail

  pre_head_standalone : E (and E2) land before H   -> signature INTACT
  midline_splice      : H < E < T                  -> signature destroyed,
                        spliced 'expected ERROR:' line exists
  straddle_ppid       : H < E < T < E2 (E inside, E2 after tail)
  post_tail           : T < E                      -> signature INTACT

Each record also carries the verbatim classify_process verdict, whether the
midline_spliced line (run_battery.py:1725-1728 detection) is present, and
whether the signature substring survives.
"""
import json
import os
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from verbatim_classifiers import classify_process

PROJ = HERE / "proj"
GODOT = "godot"
SIG = "DESCENDANT_PIPE_PROBE: expected signature"
HEAD = "DESCENDANT_PIPE_PROBE: expected "
ERR = "ERROR: DESCENDANT_PIPE_MIDLINE forged splice"
PPID = "DESCENDANT_PIPE_MIDLINE write_ppid="
TAIL_LINE = "signature"


def run_probe(offset_ms, gap_ms=200, head_stagger_ms=0, bound=8):
    env = dict(os.environ)
    xdg = (HERE / "xdg-data").resolve()
    xdg.mkdir(exist_ok=True)
    env["XDG_DATA_HOME"] = str(xdg)
    cmd = [GODOT, "--headless", "--path", str(PROJ), "--script",
           "res://critic_midline_probe.gd", "--",
           f"--midline-offset-ms={offset_ms}",
           f"--gap-ms={gap_ms}"]
    if head_stagger_ms:
        cmd.append(f"--head-stagger-ms={head_stagger_ms}")
    t0 = time.monotonic()
    proc = subprocess.run(cmd, capture_output=True, text=True, timeout=bound,
                          env=env)
    elapsed = time.monotonic() - t0
    return cmd, proc.stdout, proc.stderr, proc.returncode, elapsed


def classify_interleave(stdout):
    """Order of marker bytes within the captured stdout."""
    h = stdout.find(HEAD)
    # tail 'signature' appears standalone after head in the splice cases;
    # search the LAST occurrence to be safe.
    t = stdout.rfind(TAIL_LINE)
    e = stdout.find(ERR)
    e2 = stdout.find(PPID, e + len(ERR)) if e >= 0 else -1
    idx = {"H": h, "T": t, "E": e, "E2": e2}
    present = {k: v for k, v in idx.items() if v >= 0}
    order = "".join(k for k, _ in sorted(present.items(), key=lambda kv: kv[1]))
    lines = stdout.splitlines()
    spliced = next((l.strip() for l in lines
                    if HEAD in l and ERR in l), None)
    sig_present = SIG in stdout
    if e < 0:
        outcome = "no_descendant_write"
    elif h >= 0 and e < h:
        outcome = "pre_head_standalone"
    elif h >= 0 and t >= 0 and h < e < t:
        # E inside the gap; check whether tail interrupts E->E2
        if e2 >= 0 and e < t < e2:
            outcome = "midline_splice_straddle_ppid"
        else:
            outcome = "midline_splice"
    elif t >= 0 and e > t:
        outcome = "post_tail"
    else:
        outcome = f"unclassified:{order}"
    return {
        "order": order, "outcome": outcome,
        "spliced_line": spliced,
        "signature_present": sig_present,
        "byte_idx": idx,
    }


def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--offsets", default="0,40,80,120,160,200,240")
    ap.add_argument("--reps", type=int, default=5)
    ap.add_argument("--gap", type=int, default=200)
    ap.add_argument("--head-stagger", type=int, default=0)
    ap.add_argument("--label", default="ladder")
    ap.add_argument("--out", default=None)
    args = ap.parse_args()
    offsets = [float(x) for x in args.offsets.split(",")]
    records = []
    for off in offsets:
        for rep in range(args.reps):
            cmd, so, se, code, elapsed = run_probe(
                off, gap_ms=args.gap, head_stagger_ms=args.head_stagger)
            inter = classify_interleave(so)
            cls = classify_process(code, None, so + se, 0, SIG)
            rec = {"offset_ms": off, "rep": rep, "exit": code,
                   "elapsed_seconds": round(elapsed, 3),
                   "cls": cls, **inter,
                   "stdout_tail_lines": so.splitlines()[-4:],
                   "stderr_lines": se.splitlines()}
            records.append(rec)
            print(f"off={off:>6} rep={rep} outcome={inter['outcome']:<28} "
                  f"order={inter['order']:<6} sig={inter['signature_present']!s:<5} "
                  f"cls={cls}", flush=True)
    out = args.out or HERE / f"{args.label}-results.json"
    Path(out).write_text(json.dumps(
        {"gap_ms": args.gap, "head_stagger_ms": args.head_stagger,
         "offsets": offsets, "reps": args.reps, "records": records},
        indent=2))
    # summary: per-offset outcome distribution
    summ = {}
    for r in records:
        summ.setdefault(r["offset_ms"], {}).setdefault(r["outcome"], 0)
        summ[r["offset_ms"]][r["outcome"]] += 1
    print("SUMMARY", json.dumps(summ, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
