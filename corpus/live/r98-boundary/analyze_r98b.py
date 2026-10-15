#!/usr/bin/env python3
"""r98b boundary analyzer.

Reads runs/<batch>/ receipts for the two probes and produces:
  runs/analyze_r98b.json  +  analysis.txt

Per batch:
  - per cell: reps, rc set, out_uniq / err_uniq / pass_uniq, ERROR-line counts
  - per key: number of distinct values across reps (key_uniq)
Cross batch:
  - per cell: PASS line per batch, per-key values per batch, invariant keys
  - frozen scout probe: byte comparison of every PASS line against the scout's
    canonical AND loadtest receipts (corpus/live/r98-scout/runs/)
Flags:
  UNSTABLE    - a cell's stdout bytes differ across reps within a batch
  NONZERO_RC  - any rc != 0
  MODE_DIFF   - a cell's PASS line differs across batches (expected for the
                attack probe's tick-phase keys; key-level detail in `key_modes`)
  SCOUT_DIFF  - frozen-probe PASS line differs from the scout's own receipt
  ERR_MISMATCH- ERROR-line count not the expected value
"""

import glob
import hashlib
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
BATCHES = ["quiet", "load", "ff1", "ff30", "ff120", "ff30load", "slow"]
SCOUT_DIR = os.path.join(HERE, "..", "r98-scout", "runs")
EXPECTED_ERR = {
    "r98_canvas_draw_refusal": 2,
    "r98_canvas_clip": 1,
    "r98b_clipmatrix": 6,
}
# keys whose value legitimately depends on the tick/frame ratio (phase position
# of tick-driven events); all other keys are expected invariant across batches
PHASE_KEYS = {
    "coalesce_draws", "frames_with_tick", "ticks_window", "max_draws_per_pf",
    "distinct_draw_pf", "hide_span_pf", "hide_same_frame", "hide_ticksep_n",
    "stagger", "stagger_off", "tree", "rev", "pf5", "ph5",
}


def read(path):
    try:
        with open(path, "rb") as f:
            return f.read()
    except OSError:
        return None


def pass_line(data):
    if data is None:
        return None
    for line in data.decode("utf-8", "replace").splitlines():
        if line.startswith("PASS "):
            return line
    return None


def parse_keys(passline):
    if passline is None:
        return {}
    parts = passline.split(" ")
    if len(parts) < 4:
        return {}
    body = " ".join(parts[3:])
    out = {}
    for chunk in body.split(" "):
        if "=" in chunk:
            k, v = chunk.split("=", 1)
            out[k] = v
    return out


def err_lines(data):
    if data is None:
        return []
    return [ln for ln in data.decode("utf-8", "replace").splitlines() if ln.startswith("ERROR")]


def sha(data):
    return hashlib.sha256(data).hexdigest()[:16] if data is not None else None


def main():
    report = {"batches": {}, "cells": {}, "flags": {}}
    all_cells = {}
    for batch in BATCHES:
        bdir = os.path.join(HERE, "runs", batch)
        if not os.path.isdir(bdir):
            continue
        cells = {}
        for out in sorted(glob.glob(os.path.join(bdir, "*.rep*.out"))):
            m = re.match(r"(.+)\.rep(\d+)\.out$", os.path.basename(out))
            if not m:
                continue
            cell, rep = m.group(1), int(m.group(2))
            base = out[:-4]
            cells.setdefault(cell, []).append(
                {
                    "rep": rep,
                    "out": read(out),
                    "err": read(base + ".err"),
                    "rc": read(base + ".rc"),
                    "wall": read(base + ".wall_ms"),
                }
            )
        batch_info = {}
        for cell, reps in sorted(cells.items()):
            outs = {sha(r["out"]) for r in reps}
            errs = {sha(r["err"]) for r in reps}
            passes = {pass_line(r["out"]) for r in reps}
            rcs = {r["rc"].decode().strip() if r["rc"] else "?" for r in reps}
            err_counts = sorted({len(err_lines(r["err"])) for r in reps})
            key_uniq = {}
            for r in reps:
                for k, v in parse_keys(pass_line(r["out"])).items():
                    key_uniq.setdefault(k, set()).add(v)
            batch_info[cell] = {
                "reps": len(reps),
                "out_uniq": len(outs),
                "err_uniq": len(errs),
                "pass_uniq": len(passes),
                "rc": sorted(rcs),
                "err_line_counts": err_counts,
                "key_uniq": {k: len(v) for k, v in sorted(key_uniq.items())},
                "pass": sorted(p for p in passes if p)[0] if passes else None,
                "wall_ms": [int(r["wall"].decode().strip()) for r in reps if r["wall"]],
            }
            all_cells.setdefault(cell, {})[batch] = batch_info[cell]
        report["batches"][batch] = batch_info

    flags = {"UNSTABLE": [], "NONZERO_RC": [], "MODE_DIFF": [], "SCOUT_DIFF": [], "ERR_MISMATCH": []}
    cells_out = {}
    for cell, per_batch in sorted(all_cells.items()):
        pass_by_batch = {b: v["pass"] for b, v in per_batch.items()}
        uniq_pass = {p for p in pass_by_batch.values() if p}
        # key-level values across batches
        key_vals = {}
        for b, p in pass_by_batch.items():
            if p:
                for k, v in parse_keys(p).items():
                    key_vals.setdefault(k, {})[b] = v
        invariant_keys = sorted(k for k, v in key_vals.items() if len(set(v.values())) == 1)
        mode_keys = sorted(k for k, v in key_vals.items() if len(set(v.values())) > 1)
        entry = {
            "pass_by_batch": pass_by_batch,
            "pass_uniq_across_batches": len(uniq_pass),
            "invariant_keys": invariant_keys,
            "mode_keys": mode_keys,
            "mode_key_values": {k: key_vals[k] for k in mode_keys},
        }
        for b, v in per_batch.items():
            if v["out_uniq"] > 1 or v["pass_uniq"] > 1:
                flags["UNSTABLE"].append(f"{b}/{cell}")
            if v["rc"] != ["0"]:
                flags["NONZERO_RC"].append(f"{b}/{cell} rc={v['rc']}")
            exp = EXPECTED_ERR.get(cell, 0)
            if v["err_line_counts"] != [exp]:
                flags["ERR_MISMATCH"].append(f"{b}/{cell} err={v['err_line_counts']} expected={exp}")
        if len(uniq_pass) > 1:
            # mode diff is expected only on tick-phase keys; flag the cell if an
            # invariant key also differs (none can, by construction) -- so flag
            # only when a NON-phase key is among the differing keys
            unexpected = [k for k in mode_keys if k not in PHASE_KEYS]
            if unexpected:
                flags["MODE_DIFF"].append(f"{cell} unexpected_keys={unexpected}")
        if cell.startswith("r98_canvas_"):
            scout_passes = []
            for pat in ("%s.rep*.out", os.path.join("loadtest", "%s.rep*.out")):
                scout_passes += [pass_line(read(p)) for p in glob.glob(os.path.join(SCOUT_DIR, pat % cell))]
            scout_passes = [p for p in scout_passes if p]
            entry["scout_receipts"] = len(scout_passes)
            entry["scout_match"] = bool(scout_passes) and all(
                p == scout_passes[0] for p in pass_by_batch.values() if p
            ) and all(p == scout_passes[0] for p in scout_passes)
            if not entry["scout_match"]:
                flags["SCOUT_DIFF"].append(cell)
        cells_out[cell] = entry
    report["cells"] = cells_out
    report["flags"] = flags

    with open(os.path.join(HERE, "runs", "analyze_r98b.json"), "w") as f:
        json.dump(report, f, indent=1, sort_keys=True)

    lines = ["r98b analysis", f"batches: {[b for b in BATCHES if b in report['batches']]}"]
    for b in BATCHES:
        if b not in report["batches"]:
            continue
        info = report["batches"][b]
        bad = [c for c, v in info.items() if v["out_uniq"] > 1 or v["rc"] != ["0"]]
        lines.append(f"  {b}: cells={len(info)} rep-unstable={len(bad)} {bad if bad else ''}")
    lines.append(f"UNSTABLE={flags['UNSTABLE']}")
    lines.append(f"NONZERO_RC={flags['NONZERO_RC']}")
    lines.append(f"MODE_DIFF={flags['MODE_DIFF']}")
    lines.append(f"SCOUT_DIFF={flags['SCOUT_DIFF']}")
    lines.append(f"ERR_MISMATCH={flags['ERR_MISMATCH']}")
    lines.append("")
    for cell, entry in sorted(cells_out.items()):
        lines.append(f"[{cell}] pass_uniq={entry['pass_uniq_across_batches']} invariant_keys={len(entry['invariant_keys'])}")
        if entry.get("scout_match") is not None:
            lines.append(f"  scout_match={entry['scout_match']} receipts={entry.get('scout_receipts')}")
        for b, p in entry["pass_by_batch"].items():
            if p:
                lines.append(f"  {b}: {p}")
        if entry["mode_keys"]:
            lines.append(f"  mode_keys={entry['mode_keys']}")
            for k in entry["mode_keys"]:
                lines.append(f"    {k}: {entry['mode_key_values'][k]}")
    with open(os.path.join(HERE, "analysis.txt"), "w") as f:
        f.write("\n".join(lines) + "\n")
    print("\n".join(lines[:30]))
    print("flags:", json.dumps(flags, indent=1))


if __name__ == "__main__":
    sys.exit(main())
