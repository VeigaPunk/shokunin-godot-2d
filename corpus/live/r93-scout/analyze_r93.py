#!/usr/bin/env python3
"""r93-scout analyzer — per-cell byte stability + varying-token census."""
import hashlib
import json
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
RUNS = HERE / "runs"
CELLS = ["census", "tweenval", "tweenval_grid", "animtrack", "tweenstep", "tweenchain", "tweenproc", "animseek", "animmethod", "animblend", "animproc"]


def norm(text: str) -> str:
    lines = [ln for ln in text.splitlines() if not ln.startswith("Godot Engine v")]
    return "\n".join(lines).strip()


def sha(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()[:16]


def pass_tokens(cell: str, text: str):
    for ln in text.splitlines():
        if ln.startswith(f"PASS anim_lattice {cell}"):
            body = ln[len(f"PASS anim_lattice {cell}"):].strip()
            return body.split(" ")
    return None


out = {}
for cell in CELLS:
    reps = sorted(RUNS.glob(f"r93_{cell}.rep*.out"))
    outs, errs, rcs, sigs = [], [], [], []
    for p in reps:
        o = norm(p.read_text())
        e = norm(p.with_suffix(".err").read_text())
        rc = p.with_suffix(".rc").read_text().strip()
        outs.append(o)
        errs.append(e)
        rcs.append(rc)
        sigs.append(pass_tokens(cell, o))
    varying = {}
    tokens0 = sigs[0] or []
    for i in range(len(tokens0)):
        vals = {s[i] for s in sigs if s and len(s) > i}
        if len(vals) > 1:
            varying[tokens0[i].split("=")[0]] = sorted(vals)
    out[cell] = {
        "reps": len(reps),
        "rc": sorted(set(rcs)),
        "out_uniq": len(set(outs)),
        "err_uniq": len(set(errs)),
        "err_bytes": sorted({len(e.encode()) for e in errs}),
        "out_sha_prefixes": sorted({sha(o) for o in outs}),
        "pass_token_count": len(tokens0),
        "varying_tokens": varying,
        "stable_tokens": [t for t in tokens0 if t.split("=")[0] not in varying],
    }
    print(f"{cell}: reps={out[cell]['reps']} rc={out[cell]['rc']} out_uniq={out[cell]['out_uniq']} "
          f"err_uniq={out[cell]['err_uniq']} err_bytes={out[cell]['err_bytes']} "
          f"varying={list(varying.keys())}")

Path(RUNS / "analyze_r93.json").write_text(json.dumps(out, indent=2, sort_keys=True) + "\n")
print("wrote runs/analyze_r93.json")
