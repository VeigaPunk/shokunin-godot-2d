#!/usr/bin/env python3
"""r91-scout stability analyzer — per-cell rep uniqueness over the canonical runs.

For every cell: out_uniq / err_uniq / rc vector / first-PASS-line presence.
Cells whose out_uniq > 1 are printed with a normalized view (digits -> #) so the
varying byte ranges are visible (mode envelopes for the report).
"""
import hashlib
import json
import pathlib
import re
import sys

RUNS = pathlib.Path(__file__).parent / "runs"
CELLS = ["nav_census", "nav_path", "nav_query", "nav_sync", "nav_region",
         "nav_agent", "nav_avoid", "nav_bake", "nav_link"]

report = {}
unstable = []
crashes = []
for cell in CELLS:
    outs = sorted(RUNS.glob(f"r91_{cell}.rep*.out"))
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
    pass_line = ""
    for t in out_texts:
        m = re.search(r"^PASS nav_lattice .*$", t, re.M)
        if m:
            pass_line = m.group(0)
            break
    report[cell] = {
        "reps": reps,
        "out_uniq": out_uniq,
        "err_uniq": err_uniq,
        "rc_vec": rc_vec,
        "out_sha": out_hashes,
        "err_sha": err_hashes,
        "pass": bool(pass_line),
        "pass_line_len": len(pass_line),
    }
    if out_uniq > 1:
        unstable.append(cell)
    if any(rc not in ("0",) for rc in rcs):
        crashes.append((cell, rc_vec))
    if out_uniq > 1:
        norm = set()
        for t in out_texts:
            m = re.search(r"^PASS nav_lattice .*$", t, re.M)
            if m:
                norm.add(re.sub(r"\d", "#", m.group(0)))
        report[cell]["norm_uniq"] = len(norm)
        report[cell]["norm_len"] = sorted(len(n) for n in norm)

(RUNS / "analyze_r91.json").write_text(json.dumps(report, indent=2) + "\n")
print("UNSTABLE=", unstable)
print("CRASH_CELLS=", crashes)
for cell in CELLS:
    r = report[cell]
    print(f"{cell}: reps={r['reps']} out_uniq={r['out_uniq']} err_uniq={r['err_uniq']} "
          f"rc={r['rc_vec']} pass={r['pass']} line_len={r['pass_line_len']}"
          + (f" norm_uniq={r['norm_uniq']}" if 'norm_uniq' in r else ""))
sys.exit(0)
