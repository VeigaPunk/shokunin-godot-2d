#!/usr/bin/env python3
"""r93-critic: independent corpus check of the 23 r93 signatures.

For every r93 CASES row, count how many committed receipts of ITS OWN ARM (in the
r93-scout, r93-boundary and r93-author corpora) contain the pinned signature verbatim,
and how many contain it while the receipt is a PASS line of the arm. Also detects any
receipt of a DIFFERENT arm that contains a row's signature (cross-arm collision).

Read-only. Output: corpus/live/r93-critic/signature_census.json + stdout table.
"""
import json
import re
from pathlib import Path

SEAT = Path(__file__).resolve().parent.parent
ROOT = SEAT.parent.parent.parent  # repo root (corpus/live/r93-critic -> repo)
CORPORA = {
    "scout": ROOT / "corpus/live/r93-scout/runs",
    "boundary": ROOT / "corpus/live/r93-boundary/runs",
    "author": ROOT / "corpus/live/r93-author/fresh-reps",
}
# Arm names are unique across the two probes (anim_lattice: census/tweenval/tweenval_grid/
# tweenstep/tweenchain/tweenproc/animseek/animmethod/animtrack/animblend/animproc;
# r93b_anim: clock/manual_inv/frame/deferred/purity/blend), so the arm is recoverable from
# the receipt name whatever prefix the corpus uses (`r93_<arm>.repN.out`,
# `<cond>_<arm>.repN.out`, `<script>.<arm>.repN.out`).
ARM_TO_SCRIPT = {}
for _a in ("census tweenval tweenval_grid tweenstep tweenchain tweenproc animseek "
           "animmethod animtrack animblend animproc").split():
    ARM_TO_SCRIPT[_a] = "anim_lattice.gd"
for _a in "clock manual_inv frame deferred purity blend".split():
    ARM_TO_SCRIPT[_a] = "r93b_anim.gd"


def arm_of(name):
    if not name.endswith(".out") or ".rep" not in name:
        return None
    stem = re.sub(r"\.rep\d+\.out$", "", name)
    # longest suffix match wins: `..._tweenval_grid` must not resolve to `tweenval`
    for arm in sorted(ARM_TO_SCRIPT, key=len, reverse=True):
        if stem == arm or stem.endswith("_" + arm) or stem.endswith("." + arm):
            return arm
    return None


def receipts():
    out = []
    for corpus, base in CORPORA.items():
        if not base.exists():
            continue
        for f in base.rglob("*.out"):
            arm = arm_of(f.name)
            if not arm:
                continue
            out.append({"corpus": corpus, "path": f, "script": ARM_TO_SCRIPT[arm],
                        "arm": arm, "name": f.name})
    return out


def main():
    rows = json.loads((SEAT / "scripts" / "r93_rows.json").read_text())
    recs = receipts()
    print(f"# {len(recs)} receipts across {sorted(CORPORA)}")
    by_arm = {}
    for r in recs:
        by_arm.setdefault((r["script"], r["arm"]), []).append(r)
    print(f"# arms present: {len(by_arm)}")
    result = []
    for row in rows:
        name, script, flags, _exit, sig = row[0], row[1], row[2], row[3], row[4]
        arm = flags[0].split("=")[1]
        own = by_arm.get((script, arm), [])
        hits = [r for r in own if sig in r["path"].read_text(errors="replace")]
        other = [r for r in recs if (r["script"], r["arm"]) != (script, arm)
                 and sig in r["path"].read_text(errors="replace")]
        entry = {"row": name, "script": script, "arm": arm,
                 "own_receipts": len(own), "own_hits": len(hits),
                 "own_hit_pct": round(100.0 * len(hits) / len(own), 1) if own else None,
                 "cross_arm_hits": sorted({f"{r['corpus']}:{r['name']}" for r in other}),
                 "miss_corpora": sorted({r["corpus"] for r in own if r not in hits})}
        result.append(entry)
        flag = "" if (own and len(hits) == len(own)) else "  <-- MISS"
        print(f"{name:34s} {script}:{arm:16s} own {len(hits):3d}/{len(own):3d}"
              f" cross={len(entry['cross_arm_hits'])}{flag}")
    (SEAT / "signature_census.json").write_text(json.dumps(result, indent=1) + "\n")
    bad = [e for e in result if e["own_hits"] != e["own_receipts"]]
    print(f"# rows whose signature is absent from at least one committed receipt of their own arm: {len(bad)}")
    for e in bad:
        print(f"   {e['row']}: {e['own_hits']}/{e['own_receipts']} missing in {e['miss_corpora']}")
    cross = [e for e in result if e["cross_arm_hits"]]
    print(f"# rows with cross-arm substring hits: {len(cross)}")
    for e in cross:
        print(f"   {e['row']} also in {len(e['cross_arm_hits'])} foreign receipts e.g. {e['cross_arm_hits'][:3]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
