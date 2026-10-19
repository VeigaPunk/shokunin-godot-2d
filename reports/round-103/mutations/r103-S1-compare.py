#!/usr/bin/env python3
"""r103-S1 comparator: r99b_modes.gd F2 deletion — byte-compare receipts pre/post.

Reads /var/tmp/r103-S1/receipts/{pre,post}-{arm}-r{rep}.{out,err,rc,merged}
(merged = stdout+stderr, the battery's output concatenation order: run_process_streams).

Claims checked:
  1. rc == 0 and no ERROR:/SCRIPT ERROR:/Parse Error: on every launch, both sides.
  2. The three battery row signatures (verbatim from run_battery.py CASES lines
     1528-1533) present byte-exact on every launch, both sides.
  3. Field-level byte identity: keys single-valued across all pre receipts must be
     single-valued and equal in post receipts.
  4. Null-control rule: keys that vary across pre receipts (run-to-run noise) list
     post values outside the pre value set (candidate fold-coupled keys).
  5. Full merged-output cmp per (arm, rep) pair pre vs post.
"""
import json
import pathlib
import re
import sys

BASE = pathlib.Path('/var/tmp/r103-S1/receipts')
ARMS = "modeinfo mixphase startphase peakphase mixfree finfree advfree splitcycle firstlaw".split()
SIDES = ["pre", "post"]
ROWS = {  # run_battery.py CASES, verbatim
    "startphase": 'PASS r99b startphase imm=["0.0029025", "0.0029025", "0.0029025", "0.0029025", "0.0029025"] imm_q=["true", "true", "true", "true", "true"] imm_uniq=1',
    "mixfree": "all_jumps_q=true period_is_block=true",
    "finfree": "played_gt_02=true",
}
KV = re.compile(r'([A-Za-z_][A-Za-z0-9_]*)=(\[[^\]]*\]|\{[^}]*\}|[^\s]+)')
PASS_LINE = re.compile(r'^PASS r99b (\S+) (.*)$', re.M)


def load(side, arm, rep):
    stem = BASE / f"{side}-{arm}-r{rep}"
    merged = (stem.with_suffix('.merged')).read_text()
    rc = int((stem.with_suffix('.rc')).read_text().strip())
    m = PASS_LINE.search(merged)
    fields = dict(KV.findall(m.group(2))) if m else None
    return {"rc": rc, "pass": bool(m), "fields": fields, "merged": merged,
            "errors": [ln for ln in merged.splitlines()
                       if ("ERROR:" in ln or "SCRIPT ERROR:" in ln or "Parse Error:" in ln)]}


receipts = {}
for side in SIDES:
    for arm in ARMS:
        for rep in (1, 2):
            receipts[(side, arm, rep)] = load(side, arm, rep)

report = {"launch_checks": [], "rows": {}, "arm_fields": {}}
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
        hits = [rep for rep in (1, 2) if sig in receipts[(side, arm, rep)]["merged"]]
        per_side[side] = hits
        if len(hits) != 2:
            fail = True
    report["rows"][arm] = {"signature": sig, "present": per_side}

# 3/4. field-level identity + null-control
for arm in ARMS:
    pre = [receipts[("pre", arm, rep)]["fields"] for rep in (1, 2)]
    post = [receipts[("post", arm, rep)]["fields"] for rep in (1, 2)]
    keys = sorted(set().union(*[set(f or {}) for f in pre + post]))
    stable_ok, drift_pre, drift_post = [], [], []
    for k in keys:
        pv = [f.get(k) if f else None for f in pre]   # f is None when a launch produced no PASS line (e.g. rc=143 timeout); rule 1 already red-flags it
        qv = [f.get(k) if f else None for f in post]
        if len(set(pv)) == 1:
            if set(qv) == set(pv):
                stable_ok.append(k)
            else:
                drift_post.append({"key": k, "pre": pv, "post": qv})
        else:
            pset, qset = set(pv), set(qv)
            newvals = sorted(qset - pset)
            drift_pre.append({"key": k, "pre_set": sorted(pset), "post_set": sorted(qset),
                              "post_values_outside_pre_set": newvals})
    report["arm_fields"][arm] = {
        "keys": keys,
        "byte_stable_pre_post": stable_ok,
        "varying_pre": drift_pre,
        "varying_pre_keys_with_new_post_values": [d["key"] for d in drift_pre if d["post_values_outside_pre_set"]],
        "pre_single_valued_keys_changed_post": drift_post,
    }
    if drift_post:
        fail = True

# 5. full merged cmp per arm/rep
report["merged_cmp"] = {}
for arm in ARMS:
    same = [rep for rep in (1, 2)
            if receipts[("pre", arm, rep)]["merged"] == receipts[("post", arm, rep)]["merged"]]
    report["merged_cmp"][arm] = {"byte_identical_reps": same, "of": [1, 2]}

(BASE.parent / "compare.json").write_text(json.dumps(report, indent=2))

print(f"launch checks: {sum(1 for c in report['launch_checks'] if c['ok'])}/{len(report['launch_checks'])} ok")
for arm, v in report["rows"].items():
    print(f"row {arm}: signature present pre={v['present']['pre']} post={v['present']['post']}")
for arm, v in report["arm_fields"].items():
    n_stable = len(v["byte_stable_pre_post"])
    n_var = len(v["varying_pre"])
    newv = v["varying_pre_keys_with_new_post_values"]
    drifted = [d["key"] for d in v["pre_single_valued_keys_changed_post"]]
    print(f"{arm:11s} keys={len(v['keys']):3d} stable={n_stable:3d} noisy={n_var:3d} "
          f"newvals_outside_pre={newv} stable_changed={drifted}")
print("merged per-arm byte-identical reps:", {a: v["byte_identical_reps"] for a, v in report["merged_cmp"].items()})
print("VERDICT:", "FAIL" if fail else "GREEN")
sys.exit(1 if fail else 0)
