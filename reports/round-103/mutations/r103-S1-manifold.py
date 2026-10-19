#!/usr/bin/env python3
"""r103-S1 manifold analyzer: does the F2 (`pairs` deletion) fold preserve discrimination?

Inputs (all raw receipt bytes on disk, no re-derivation):
  /var/tmp/r103-S1/receipts/{pre,post}-<arm>-r{1,2}.{merged,rc}      sweep (36 launches)
  /var/tmp/r103c-S1-R99/receipts/{pre,post}-startphase-N{1..8}.*      startphase flap probe
  /var/tmp/r103c-S1-R99/receipts/{pre,post}-{finfree,splitcycle}-M{1..6}.* counter probe

Method (deliberately conservative):
  * Per (arm, side) collect the union of field value sets over ALL receipts of that side,
    i.e. each side's observed manifolds.
  * SIGNATURE fields (the substrings run_battery.py CASES grades, lines 1528-1533) are
    required to be single-valued AND identical on both sides, on every launch.
  * NOISE fields (multi-valued somewhere) are compared by manifold overlap: report
    pre_set, post_set, and post-only values. A post-only value is evidence against the
    fold only if it sits outside the pre manifold; equal-valued flapping on both sides
    is fixture flakiness, not fold coupling.
Exit 1 only if a SIGNATURE field drifts or a noise field has a post-only value.
"""
import json
import pathlib
import re
import sys

SWEEP = pathlib.Path('/var/tmp/r103-S1/receipts')
PROBE = pathlib.Path('/var/tmp/r103c-S1-R99/receipts')
SIDES = ["pre", "post"]
KV = re.compile(r'([A-Za-z_][A-Za-z0-9_]*)=(\[[^\]]*\]|\{[^}]*\}|[^\s]+)')
PASS_LINE = re.compile(r'^PASS r99b (\S+) (.*)$', re.M)
SIG_FIELDS = {  # fields the graded substring depends on (run_battery.py:1528-1533)
    "startphase": ["imm", "imm_q", "imm_uniq"],
    "mixfree": ["all_jumps_q", "period_is_block"],
    "finfree": ["played_gt_02"],
}
SIG_TEXT = {
    "startphase": 'PASS r99b startphase imm=["0.0029025", "0.0029025", "0.0029025", "0.0029025", "0.0029025"] imm_q=["true", "true", "true", "true", "true"] imm_uniq=1',
    "mixfree": "all_jumps_q=true period_is_block=true",
    "finfree": "played_gt_02=true",
}
FILES = []  # (side, arm, pathstem, tag)
for side in SIDES:
    for arm in ("modeinfo", "mixphase", "startphase", "peakphase", "mixfree", "finfree",
                "advfree", "splitcycle", "firstlaw"):
        for rep in (1, 2):
            FILES.append((side, arm, SWEEP / f"{side}-{arm}-r{rep}", "sweep"))
    for rep in range(1, 9):
        FILES.append((side, "startphase", PROBE / f"{side}-startphase-N{rep}", "Nprobe"))
    for arm in ("finfree", "splitcycle"):
        for rep in range(1, 7):
            FILES.append((side, arm, PROBE / f"{side}-{arm}-M{rep}", "Mprobe"))
    for rep in range(1, 9):   # interleaved pre/post: breaks the "all-pre then all-post" load-order confound
        for arm in ("mixphase", "finfree", "splitcycle"):
            FILES.append((side, arm, PROBE / f"I{rep}-{side}-{arm}", "Iprobe"))

TAG_FILTER = sys.argv[1] if len(sys.argv) > 1 else None
if TAG_FILTER:
    FILES = [f for f in FILES if f[3] == TAG_FILTER]

data = {}
for side, arm, stem, tag in FILES:
    merged_p = stem.with_suffix('.merged')
    if not merged_p.exists():
        print(f"MISSING {merged_p}")
        continue
    merged = merged_p.read_text()
    rc = int(stem.with_suffix('.rc').read_text().strip())
    m = PASS_LINE.search(merged)
    rec = {"side": side, "arm": arm, "tag": tag, "rc": rc, "pass": bool(m),
           "merged": merged,
           "sig_text_present": (arm in SIG_TEXT and SIG_TEXT[arm] in merged),
           "errors": [ln for ln in merged.splitlines()
                      if "ERROR:" in ln or "SCRIPT ERROR:" in ln or "Parse Error:" in ln]}
    rec["fields"] = dict(KV.findall(m.group(2))) if m else None
    data[(side, arm, stem.name)] = rec

arms = sorted({k[1] for k in data})
report = {"file_count": len(data), "launches_without_pass": [], "errors": [],
          "arms": {}, "verdicts": {}}
fail = False
for key, rec in data.items():
    if not rec["pass"] or rec["rc"] != 0:
        report["launches_without_pass"].append({"file": key[2], "side": key[0], "arm": key[1],
                                                "rc": rec["rc"], "bytes": len(rec["merged"])})
        fail = True
    if rec["errors"]:
        report["errors"].append({"file": key[2], "errors": rec["errors"]})
        fail = True

for arm in arms:
    side_fields = {}
    for side in SIDES:
        sets = {}
        for (s, a, name), rec in data.items():
            if a != arm or s != side or not rec["fields"]:
                continue
            for k, v in rec["fields"].items():
                sets.setdefault(k, set()).add(v)
        side_fields[side] = {k: sorted(v) for k, v in sets.items()}
    keys = sorted(set(side_fields["pre"]) | set(side_fields["post"]))
    entry = {"signature_fields": {}, "noise_fields": {}, "stable_fields": []}
    for k in keys:
        pv = side_fields["pre"].get(k, [])
        qv = side_fields["post"].get(k, [])
        is_sig = k in SIG_FIELDS.get(arm, [])
        stable = len(pv) == 1 and pv == qv
        if is_sig:
            entry["signature_fields"][k] = {"pre": pv, "post": qv, "byte_identical": stable}
            if not stable:
                fail = True
        elif len(pv) == 1 and len(qv) == 1:
            if pv == qv:
                entry["stable_fields"].append(k)
            else:
                entry["noise_fields"][k] = {"pre": pv, "post": qv, "post_only_values": []}
                fail = True   # single-valued both sides but different -> systematic drift
        else:
            post_only = sorted(set(qv) - set(pv))
            entry["noise_fields"][k] = {"pre": pv, "post": qv, "post_only_values": post_only}
            entry["noise_fields"][k]["overlap"] = sorted(set(pv) & set(qv))
    report["arms"][arm] = entry
    sig_ok = all(v["byte_identical"] for v in entry["signature_fields"].values())
    drift = [k for k, v in entry["noise_fields"].items() if v["post_only_values"]]
    report["verdicts"][arm] = {"signature_ok": sig_ok, "noise_keys_with_post_only_values": drift,
                               "noise_keys": len(entry["noise_fields"]),
                               "stable_keys": len(entry["stable_fields"])}

out = pathlib.Path(f"/var/tmp/r103c-S1-R99/manifold{'-' + TAG_FILTER if TAG_FILTER else ''}.json")
out.write_text(json.dumps(report, indent=2, sort_keys=True))
print(f"receipt files analyzed: {report['file_count']}  (tag filter: {TAG_FILTER or 'none'})")
print("launches without PASS:", report["launches_without_pass"])
print("stderr/stdout ERROR lines:", report["errors"])
for arm, v in report["verdicts"].items():
    print(f"{arm:11s} sig_ok={v['signature_ok']!s:5s} stable={v['stable_keys']:3d} "
          f"noisy={v['noise_keys']:3d} post_only={v['noise_keys_with_post_only_values']}")
print("VERDICT:", "FAIL" if fail else "GREEN")
print("json:", out)
sys.exit(1 if fail else 0)
