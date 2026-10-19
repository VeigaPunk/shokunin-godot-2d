#!/usr/bin/env python3
"""r103-S1 comparator v2: r99b_modes.gd F2 deletion — byte-compare receipts pre/post.

Usage: r103-S1-compare.py [receipts_dir] [json_out]
Defaults: /var/tmp/r103-S1/sweep2  /var/tmp/r103-S1/compare2.json
Receipt files per launch: {side}-{arm}-r{rep}.{out,err,rc,merged}
(merged = stdout+stderr, the battery's output concatenation order).

Checked:
  1. rc==0, PASS line present, no ERROR:/SCRIPT ERROR:/Parse Error:, both sides.
  2. The three battery row signatures (verbatim run_battery.py CASES 1528-1533)
     present byte-exact on EVERY receipt, both sides.
  3. Invariant fields: keys single-valued within each side AND equal across sides.
  4. Null-control: keys varying within pre list post values outside the pre set
     (candidate fold-coupled keys); flagged for manual class check.
  5. Post merged-output classes: every post merged output must byte-equal some
     pre merged output (no new output class introduced by the fold).
  6. Frozen receipt oracle (if /var/tmp/r103-S1/frozen exists): battery-run PASS
     lines for the three rows vs this run's post fields.
"""
import json
import pathlib
import re
import sys

BASE = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else "/var/tmp/r103-S1/sweep2")
OUT = pathlib.Path(sys.argv[2] if len(sys.argv) > 2 else "/var/tmp/r103-S1/compare2.json")
FROZEN = pathlib.Path("/var/tmp/r103-S1/frozen")
ARMS = "modeinfo mixphase startphase peakphase mixfree finfree advfree splitcycle firstlaw".split()
SIDES = ["pre", "post"]
ROWS = {  # run_battery.py CASES, verbatim
    "startphase": 'PASS r99b startphase imm=["0.0029025", "0.0029025", "0.0029025", "0.0029025", "0.0029025"] imm_q=["true", "true", "true", "true", "true"] imm_uniq=1',
    "mixfree": "all_jumps_q=true period_is_block=true",
    "finfree": "played_gt_02=true",
}
FROZEN_ROWS = {"startphase": "r99b_startphase", "mixfree": "r99b_mixfree", "finfree": "r99b_finfree_played"}
KV = re.compile(r'([A-Za-z_][A-Za-z0-9_]*)=(\[[^\]]*\]|\{[^}]*\}|[^\s]+)')
PASS_LINE = re.compile(r'^PASS r99b (\S+) (.*)$', re.M)


def reps_for(side, arm):
    reps = []
    for p in BASE.glob(f"{side}-{arm}-r*.rc"):
        m = re.fullmatch(rf"{side}-{arm}-r(\d+)\.rc", p.name)
        if m:
            reps.append(int(m.group(1)))
    return sorted(reps)


def load(side, arm, rep):
    stem = BASE / f"{side}-{arm}-r{rep}"
    merged = (stem.with_suffix(".merged")).read_text()
    rc = int((stem.with_suffix(".rc")).read_text().strip())
    m = PASS_LINE.search(merged)
    fields = dict(KV.findall(m.group(2))) if m else None
    return {"rc": rc, "pass": bool(m), "fields": fields, "merged": merged,
            "errors": [ln for ln in merged.splitlines()
                       if ("ERROR:" in ln or "SCRIPT ERROR:" in ln or "Parse Error:" in ln)]}


receipts, rep_index = {}, {}
for side in SIDES:
    for arm in ARMS:
        rs = reps_for(side, arm)
        rep_index[(side, arm)] = rs
        for rep in rs:
            receipts[(side, arm, rep)] = load(side, arm, rep)

report = {"receipts_dir": str(BASE), "reps": {f"{s}-{a}": r for (s, a), r in rep_index.items()},
          "launch_checks": [], "rows": {}, "arm_fields": {}, "merged_classes": {}, "frozen_oracle": {}}
fail = False

# 1. launch hygiene
for key, r in sorted(receipts.items()):
    ok = r["rc"] == 0 and r["pass"] and not r["errors"]
    report["launch_checks"].append({"key": "-".join(map(str, key)), "rc": r["rc"],
                                    "pass_line": r["pass"], "errors": r["errors"], "ok": ok})
    fail = fail or not ok

# 2. row signatures, both sides, every launch
for arm, sig in ROWS.items():
    per_side = {}
    for side in SIDES:
        hits = [rep for rep in rep_index[(side, arm)] if sig in receipts[(side, arm, rep)]["merged"]]
        per_side[side] = f"{len(hits)}/{len(rep_index[(side, arm)])}"
        if len(hits) != len(rep_index[(side, arm)]):
            fail = True
    report["rows"][arm] = {"signature": sig, "present": per_side}

# 3/4. field-level identity + null-control
for arm in ARMS:
    pre = [receipts[("pre", arm, rep)]["fields"] for rep in rep_index[("pre", arm)]]
    post = [receipts[("post", arm, rep)]["fields"] for rep in rep_index[("post", arm)]]
    keys = sorted(set().union(*[set(f or {}) for f in pre + post]))
    invariant, pre_varying, pre_single_post_multi, changed_invariant = [], [], [], []
    for k in keys:
        pv, qv = [f.get(k) for f in pre], [f.get(k) for f in post]
        ps, qs = set(pv), set(qv)
        if len(ps) == 1 and len(qs) == 1 and ps == qs:
            invariant.append(k)
        elif len(ps) == 1 and ps != qs:
            if len(qs) == 1:
                changed_invariant.append({"key": k, "pre": sorted(ps), "post": sorted(qs)})
            else:
                pre_single_post_multi.append({"key": k, "pre_value": sorted(ps), "post_set": sorted(qs)})
        else:
            pre_varying.append({"key": k, "pre_set": sorted(ps), "post_set": sorted(qs),
                                "post_values_outside_pre_set": sorted(qs - ps)})
    report["arm_fields"][arm] = {
        "keys": keys, "invariant": invariant, "pre_varying": pre_varying,
        "changed_single_valued": changed_invariant, "pre_single_post_multi": pre_single_post_multi,
        "pre_varying_with_new_post_values": [d["key"] for d in pre_varying if d["post_values_outside_pre_set"]],
    }

# 5. merged output classes per arm
for arm in ARMS:
    pre_m = {receipts[("pre", arm, rep)]["merged"] for rep in rep_index[("pre", arm)]}
    post_m = {receipts[("post", arm, rep)]["merged"] for rep in rep_index[("post", arm)]}
    report["merged_classes"][arm] = {
        "pre_distinct": len(pre_m), "post_distinct": len(post_m),
        "post_outputs_not_matching_any_pre_output": len(post_m - pre_m),
        "pre_outputs_not_matching_any_post_output": len(pre_m - post_m),
    }

# 6. frozen receipt oracle
if FROZEN.is_dir():
    for arm, case in FROZEN_ROWS.items():
        f = FROZEN / f"{case}.txt"
        if not f.is_file():
            continue
        m = PASS_LINE.search(f.read_text())
        ffields = dict(KV.findall(m.group(2))) if m else {}
        post_fields = [receipts[("post", arm, rep)]["fields"] for rep in rep_index[("post", arm)]]
        agree, disagree = [], []
        for k, v in ffields.items():
            post_vals = {pf.get(k) for pf in post_fields}
            if post_vals == {v}:
                agree.append(k)
            else:
                disagree.append({"key": k, "frozen": v, "post_values": sorted(x for x in post_vals if x is not None)})
        report["frozen_oracle"][arm] = {"frozen_case": case, "keys_equal_every_post_run": agree,
                                        "keys_not_equal": disagree}

OUT.write_text(json.dumps(report, indent=2))
print(f"receipts dir: {BASE}")
print(f"launch checks: {sum(1 for c in report['launch_checks'] if c['ok'])}/{len(report['launch_checks'])} ok")
for arm, v in report["rows"].items():
    print(f"row {arm}: signature present pre={v['present']['pre']} post={v['present']['post']}")
for arm, v in report["arm_fields"].items():
    print(f"{arm:11s} keys={len(v['keys']):3d} invariant={len(v['invariant']):3d} "
          f"pre_noisy={len(v['pre_varying']):3d} changed_single={ [d['key'] for d in v['changed_single_valued']] } "
          f"pre_single_post_multi={[d['key'] for d in v['pre_single_post_multi']]} "
          f"noisy_new_post_vals={v['pre_varying_with_new_post_values']}")
for arm, v in report["merged_classes"].items():
    print(f"merged {arm:11s} pre_distinct={v['pre_distinct']} post_distinct={v['post_distinct']} "
          f"post_not_in_pre={v['post_outputs_not_matching_any_pre_output']} pre_not_in_post={v['pre_outputs_not_matching_any_post_output']}")
for arm, v in report["frozen_oracle"].items():
    print(f"frozen {arm:11s} equal_keys={len(v['keys_equal_every_post_run'])} not_equal={ [d['key'] for d in v['keys_not_equal']] }")
changed = any(v["changed_single_valued"] for v in report["arm_fields"].values())
print("VERDICT:", "FAIL" if fail else ("FLAG (changed single-valued keys)" if changed else "GREEN"))
sys.exit(1 if (fail or changed) else 0)
