#!/usr/bin/env python3
"""r93b boundary analyzer — per-batch byte-stability + cross-batch token comparison
for the r93 scout probe (scout_anim_lattice.gd) and this seat's attack probe (r93b_anim.gd).

Reads runs/<tag><cell>.rep<N>.{out,err,rc,wall} produced by run_matrix.sh and writes
runs/analyze_r93b.json + runs/analysis.txt. Read-only over the scout lane's receipts
(../r93-scout/runs/...) — never writes there.
"""
import hashlib
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
RUNS = os.path.join(ROOT, "runs")
SCOUT_RUNS = os.path.normpath(os.path.join(ROOT, "..", "r93-scout", "runs"))
SCOUT_LOADTEST = os.path.join(SCOUT_RUNS, "loadtest")

SCOUT_ARMS = ["census", "tweenval", "tweenval_grid", "animtrack", "tweenstep", "tweenchain",
              "tweenproc", "animseek", "animmethod", "animblend", "animproc"]
ATTACK_ARMS = ["clock", "manual_inv", "frame", "deferred", "purity", "blend"]
BATCHES = ["q_", "l_", "f30_", "f60_", "f120_", "f120l_", "l32_"]


def sha(b):
    return hashlib.sha256(b).hexdigest()


def read(p):
    try:
        with open(p, "rb") as f:
            return f.read()
    except OSError:
        return None


def payload(out_bytes):
    """Drop the engine banner; keep the PASS line(s)."""
    if out_bytes is None:
        return None
    txt = out_bytes.decode("utf-8", "replace")
    lines = [l for l in txt.splitlines() if l.startswith("PASS ")]
    return "\n".join(lines) + "\n" if lines else ""


def parse_pairs(line):
    """Split `PASS probe arm k=v k=v` into {k: v}; values may contain spaces inside
    brackets/parens (e.g. `vec025=(2.0, 4.0)`), so split only at depth 0."""
    parts = line.split(" ")
    if parts and parts[0] == "PASS":
        parts = parts[1:]
    if parts:
        parts = parts[1:]  # probe name
    if parts:
        parts = parts[1:]  # arm name
    depth = 0
    toks = []
    cur = ""
    for ch in " ".join(parts):
        if ch in "[(":
            depth += 1
        elif ch in "])":
            depth -= 1
        if ch == " " and depth == 0:
            if cur:
                toks.append(cur)
                cur = ""
        else:
            cur += ch
    if cur:
        toks.append(cur)
    out = {}
    for t in toks:
        if "=" in t:
            k, v = t.split("=", 1)
            out[k] = v
    return out


def cells_for(tag):
    if tag == "l32_":
        return ["tweenstep", "tweenproc", "animseek", "animproc"] + ATTACK_ARMS
    return SCOUT_ARMS + ATTACK_ARMS


def batch_stats(tag, cell):
    outs, errs, rcs, walls = [], [], [], []
    for i in range(1, 7):
        o = os.path.join(RUNS, f"{tag}{cell}.rep{i}.out")
        e = os.path.join(RUNS, f"{tag}{cell}.rep{i}.err")
        r = os.path.join(RUNS, f"{tag}{cell}.rep{i}.rc")
        w = os.path.join(RUNS, f"{tag}{cell}.rep{i}.wall")
        if not os.path.exists(o):
            continue
        ob, eb, rb, wb = read(o), read(e), read(r), read(w)
        outs.append(ob)
        errs.append(len(eb) if eb is not None else None)
        rcs.append(rb.decode().strip() if rb else None)
        try:
            walls.append(float(wb.decode().strip()))
        except (AttributeError, ValueError):
            pass
    if not outs:
        return None
    payloads = [payload(o) for o in outs]
    uniq_payloads = sorted({p for p in payloads})
    return {
        "reps": len(outs),
        "out_uniq": len({sha(o) for o in outs}),
        "payload_uniq": len(uniq_payloads),
        "payloads": uniq_payloads,
        "err_bytes": sorted({e for e in errs if e is not None}),
        "rc": sorted({r for r in rcs if r is not None}),
        "wall_min": min(walls) if walls else None,
        "wall_max": max(walls) if walls else None,
    }


def scout_ref(cell):
    """The scout's own canonical + loadtest payload sets (read-only)."""
    out = {}
    for label, d in (("canon", SCOUT_RUNS), ("load", SCOUT_LOADTEST)):
        ps = []
        for i in range(1, 7):
            p = os.path.join(d, f"r93_{cell}.rep{i}.out")
            b = read(p)
            if b is not None:
                ps.append(payload(b))
        if ps:
            out[label] = {"reps": len(ps), "payload_uniq": len(set(ps)), "payloads": sorted(set(ps))}
    return out


def tokens(payload_str):
    if not payload_str:
        return {}
    for line in payload_str.splitlines():
        if line.startswith("PASS "):
            return parse_pairs(line)
    return {}


def main():
    report = {"batches": {}, "scout_ref": {}, "notes": []}
    for tag in BATCHES:
        report["batches"][tag] = {}
        for cell in cells_for(tag):
            st = batch_stats(tag, cell)
            if st is None:
                continue
            report["batches"][tag][cell] = st
    for cell in SCOUT_ARMS:
        report["scout_ref"][cell] = scout_ref(cell)

    # cross-batch payload comparison per cell
    compare = {}
    all_cells = sorted({c for tag in BATCHES for c in report["batches"].get(tag, {})})
    for cell in all_cells:
        per_batch = {tag: report["batches"][tag][cell]["payloads"]
                     for tag in BATCHES if cell in report["batches"].get(tag, {})}
        flat = sorted({p for ps in per_batch.values() for p in ps})
        ref = report["scout_ref"].get(cell)
        ref_payloads = sorted({p for lbl in (ref or {}).values() for p in lbl["payloads"]})
        entry = {
            "per_batch_uniq": {tag: len(ps) for tag, ps in per_batch.items()},
            "all_uniq": len(flat),
            "payloads": flat,
            "matches_scout_ref": {p: (p in ref_payloads) for p in flat},
            "scout_ref_uniq": len(ref_payloads),
        }
        # token-level census: which keys vary, and their observed values
        keyvals = {}
        for p in flat:
            for k, v in tokens(p).items():
                keyvals.setdefault(k, set()).add(v)
        entry["varying_keys"] = {k: sorted(vs) for k, vs in keyvals.items() if len(vs) > 1}
        entry["constant_keys"] = sorted(k for k, vs in keyvals.items() if len(vs) == 1)
        compare[cell] = entry
    report["compare"] = compare

    with open(os.path.join(RUNS, "analyze_r93b.json"), "w") as f:
        json.dump(report, f, indent=1, sort_keys=True)

    # human-readable
    lines = []
    for tag in BATCHES:
        lines.append(f"== batch {tag} ==")
        for cell in cells_for(tag):
            st = report["batches"].get(tag, {}).get(cell)
            if st is None:
                continue
            lines.append(f"  {cell:14s} reps={st['reps']} out_uniq={st['out_uniq']} "
                         f"payload_uniq={st['payload_uniq']} rc={st['rc']} err={st['err_bytes']} "
                         f"wall=[{st['wall_min']},{st['wall_max']}]")
    lines.append("")
    lines.append("== cross-batch payload comparison (all_uniq>1 = launch/condition-sensitive) ==")
    for cell in all_cells:
        e = compare[cell]
        ref = report["scout_ref"].get(cell)
        refline = ""
        if ref:
            refline = f" scout_ref_uniq={e['scout_ref_uniq']}"
        lines.append(f"  {cell:14s} all_uniq={e['all_uniq']}{refline} per_batch={e['per_batch_uniq']}")
        for p in e["payloads"]:
            mark = "S" if e["matches_scout_ref"][p] else " "
            lines.append(f"      [{mark}] {p}")
    lines.append("")
    lines.append("== varying keys per cell (across all batches+reps) ==")
    for cell in all_cells:
        vk = compare[cell]["varying_keys"]
        if not vk:
            lines.append(f"  {cell:14s} (none — every key constant)")
            continue
        lines.append(f"  {cell:14s}")
        for k, vs in vk.items():
            shown = vs if len(vs) <= 8 else vs[:8] + [f"...(+{len(vs)-8})"]
            lines.append(f"      {k}: {shown}")
    with open(os.path.join(RUNS, "analysis.txt"), "w") as f:
        f.write("\n".join(lines) + "\n")
    print("\n".join(lines[:80]))
    print(f"... full: {os.path.join(RUNS, 'analysis.txt')}")


if __name__ == "__main__":
    sys.exit(main())
