#!/usr/bin/env python3
"""r97-scout stability analyzer — per-cell rep uniqueness over the canonical runs.

For every cell: out_uniq / err_uniq / rc vector / PASS-line presence, plus the
normalized (digits -> #) view of the PASS line for unstable cells so the varying
byte ranges are visible (mode envelopes for the report).
"""
import hashlib
import json
import pathlib
import re
import sys

RUNS = pathlib.Path(__file__).parent / "runs"
CELLS = ["census", "group_order", "group_order_rev", "group_flags",
         "group_lifecycle", "group_setters", "signal_order", "signal_flags",
         "defer_ladder", "defer_slots", "defer_order", "scene_probe"]

report = {}
unstable = []
crashes = []
for cell in CELLS:
    outs = sorted(RUNS.glob(f"r97_{cell}.rep*.out"))
    reps = len(outs)
    out_hashes, err_hashes, rcs = [], [], []
    out_texts, err_texts = [], []
    for out in outs:
        err = out.with_suffix(".err")
        rc = out.with_suffix(".rc")
        out_texts.append(out.read_text())
        err_texts.append(err.read_text() if err.exists() else "")
        out_hashes.append(hashlib.sha256(out.read_bytes()).hexdigest()[:16])
        err_hashes.append(hashlib.sha256(err.read_bytes()).hexdigest()[:16] if err.exists() else "")
        rcs.append(rc.read_text().strip() if rc.exists() else "?")
    out_uniq = len(set(out_hashes))
    err_uniq = len(set(err_hashes))
    rc_vec = sorted(set(rcs))
    pass_lines = set()
    for t in out_texts:
        m = re.search(r"^PASS stree_lattice .*$", t, re.M)
        if m:
            pass_lines.add(m.group(0))
    pass_line = sorted(pass_lines)[0] if pass_lines else ""
    report[cell] = {
        "reps": reps,
        "out_uniq": out_uniq,
        "err_uniq": err_uniq,
        "rc_vec": rc_vec,
        "pass_uniq": len(pass_lines),
        "pass": bool(pass_line),
        "pass_line_len": len(pass_line),
        "err_bytes": sorted(set(len(e) for e in err_texts)),
    }
    if out_uniq > 1:
        unstable.append(cell)
        norm = set()
        for t in out_texts:
            m = re.search(r"^PASS stree_lattice .*$", t, re.M)
            if m:
                norm.add(re.sub(r"\d", "#", m.group(0)))
        report[cell]["norm_uniq"] = len(norm)
        report[cell]["norm_len"] = sorted(len(n) for n in norm)
    if any(rc not in ("0",) for rc in rcs):
        crashes.append((cell, rc_vec))

(RUNS / "analyze_r97.json").write_text(json.dumps(report, indent=2) + "\n")
print("UNSTABLE=", unstable)
print("CRASH_CELLS=", crashes)
for cell in CELLS:
    r = report[cell]
    print(f"{cell}: reps={r['reps']} out_uniq={r['out_uniq']} err_uniq={r['err_uniq']} "
          f"rc={r['rc_vec']} pass_uniq={r['pass_uniq']} line_len={r['pass_line_len']} err_bytes={r['err_bytes']}"
          + (f" norm_uniq={r['norm_uniq']}" if 'norm_uniq' in r else ""))
sys.exit(0)
