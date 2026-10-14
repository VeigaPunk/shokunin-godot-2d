#!/usr/bin/env python3
"""r69-scribe — prior-row byte-stability on the landed tree.

Compares a fresh flagged replay receipt against the r68-scribe landed
receipts (same HEAD code family — r68 work commit f754546 + hygiene
e8d4fb7 + corpus-ignore 5d66b4d, all probes/meta-only diffs):

  verdicts.json                    -> shared rows identical in case,
                                      verdict, and key set
  stream-attribution-verdicts.json -> dual_classify records + divergence
                                      table byte-identical modulo the
                                      volatile path/timestamp fields
  midlineforge-ladder-verdicts.json-> cell outcomes + discriminations

Volatile fields scrubbed before compare: run_dir paths inside `command`,
`artifact`, `output`/`raw_*` streams embed no paths (verified: grep for
the run dir returns nothing outside command), elapsed/elapsed_seconds
timing fields, and per-run descendant_pid/godot_pid/write_ppid values
(pids differ by construction; the PREDICATES on them are compared).
"""
import json
import re
import sys
from pathlib import Path

VOLATILE_KEYS = {"command", "artifact", "elapsed_seconds", "elapsed",
                 "descendant_pid", "godot_pid", "write_ppid",
                 "descendant_kernel_ppid_at_return",
                 "child_exit_at_timeout", "run_dir", "timestamp",
                 "raw_merged_sha256", "merged_sha256"}  # r69 additive field


def scrub(o, run_paths):
    if isinstance(o, dict):
        return {k: scrub(v, run_paths) for k, v in o.items()
                if k not in VOLATILE_KEYS}
    if isinstance(o, list):
        return [scrub(v, run_paths) for v in o]
    if isinstance(o, str):
        for p in run_paths:
            o = o.replace(str(p), "<RUNDIR>")
        return o
    return o


def canon(o):
    return json.dumps(o, sort_keys=True, ensure_ascii=False)


def find_dual(payload):
    recs = []
    def walk(o, path):
        if isinstance(o, dict):
            if ("merged_classification" in o
                    and "stream_classification" in o
                    and "divergent" in o):
                recs.append((path, o))
            for k, v in o.items():
                walk(v, f"{path}.{k}")
        elif isinstance(o, list):
            for i, v in enumerate(o):
                walk(v, f"{path}[{i}]")
    walk(payload, "$")
    return recs


def main():
    mine_dir = Path(sys.argv[1])
    ref_dir = Path(sys.argv[2])
    report = {"mine": str(mine_dir), "ref": str(ref_dir), "checks": {}}

    # 1. verdicts.json rows
    vmine = json.loads((mine_dir / "verdicts.json").read_text())
    vref = json.loads((ref_dir / "verdicts.json").read_text())
    cmine = {r["case"]: r for r in vmine["results"]}
    cref = {r["case"]: r for r in vref["results"]}
    shared = set(cmine) & set(cref)
    report["checks"]["verdicts"] = {
        "verdict_mine": vmine["verdict"], "verdict_ref": vref["verdict"],
        "rows_mine": len(cmine), "rows_ref": len(cref),
        "only_mine": sorted(set(cmine) - set(cref)),
        "only_ref": sorted(set(cref) - set(cmine)),
        "verdict_mismatch": sorted(
            c for c in shared if cmine[c]["verdict"] != cref[c]["verdict"]),
        "keyset_mismatch": sorted(
            c for c in shared
            if set(cmine[c]) - VOLATILE_KEYS != set(cref[c]) - VOLATILE_KEYS),
    }

    # 2. stream-attribution payload: scrub paths/timing, compare deep
    smine = json.loads((mine_dir / "stream-attribution-verdicts.json").read_text())
    sref = json.loads((ref_dir / "stream-attribution-verdicts.json").read_text())
    sm = scrub(smine, [mine_dir, ref_dir])
    sr = scrub(sref, [mine_dir, ref_dir])
    report["checks"]["stream_attribution"] = {
        "equal_after_scrub": canon(sm) == canon(sr),
        "dual_records_mine": len(find_dual(smine)),
        "dual_records_ref": len(find_dual(sref)),
        "verdict_mine": smine["verdict"], "verdict_ref": sref["verdict"],
        "disc_mine": smine["divergence"]["discriminations"],
        "disc_ref": sref["divergence"]["discriminations"],
    }
    if canon(sm) != canon(sr):
        # locate first differing top-level key for the report
        diffs = [k for k in set(sm) | set(sr)
                 if canon(sm.get(k)) != canon(sr.get(k))]
        report["checks"]["stream_attribution"]["diff_keys"] = diffs
        for k in diffs[:6]:
            a, b = sm.get(k), sr.get(k)
            report["checks"]["stream_attribution"].setdefault("samples", {})[k] = {
                "mine_head": canon(a)[:400], "ref_head": canon(b)[:400]}

    # 3. midlineforge ladder payload
    lmine_p = mine_dir / "midlineforge-ladder-verdicts.json"
    lref_p = ref_dir / "midlineforge-ladder-verdicts.json"
    if lmine_p.exists() and lref_p.exists():
        lmine = json.loads(lmine_p.read_text())
        lref = json.loads(lref_p.read_text())
        lm = scrub(lmine, [mine_dir, ref_dir])
        lr = scrub(lref, [mine_dir, ref_dir])
        report["checks"]["midlineforge_ladder"] = {
            "verdict_mine": lmine["verdict"], "verdict_ref": lref["verdict"],
            "cells_mine": {c["offset_ms"]: c["outcome"] for c in lmine["ladder"]},
            "cells_ref": {c["offset_ms"]: c["outcome"] for c in lref["ladder"]},
            "disc_mine": lmine["discriminations"],
            "disc_ref": lref["discriminations"],
            "equal_after_scrub": canon(lm) == canon(lr),
        }
        if canon(lm) != canon(lr):
            diffs = [k for k in set(lm) | set(lr)
                     if canon(lm.get(k)) != canon(lr.get(k))]
            report["checks"]["midlineforge_ladder"]["diff_keys"] = diffs

    print(json.dumps(report, indent=2, default=str))


if __name__ == "__main__":
    main()
