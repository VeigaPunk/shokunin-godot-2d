#!/usr/bin/env python3
"""r102-ver9 post-analysis: classify any raw stdout/stderr diffs between
base and folded receipts using the declared mask classes
(backtrace line numbers, env/proc counters, engine id fields, wall-clock
audio tail fields). Prints per-row verdict lines.
"""
import json, re, difflib
from pathlib import Path

WORK = Path("/var/tmp/r102-ver9")
data = json.loads((WORK / "results.json").read_text())
recs, summary = data["recs"], data["summary"]

MASK_GD = re.compile(r"res://[A-Za-z0-9_./-]+\.gd:\d+")
MASK_ENV = re.compile(r"\b(env|proc|pf|ids|fresh_id)=[^ \n]*")


def mask(text):
    return MASK_ENV.sub(r"\1=#", MASK_GD.sub("res://X.gd:L", text))


print("=== rows with raw stdout diff base1 vs fold1 ===")
for name, s in summary.items():
    if not s["stdout_eq_1"]:
        b = recs[name]["base1"]["stdout"]
        f = recs[name]["fold1"]["stdout"]
        print(f"-- {name}: raw_differs; masked_equal={mask(b) == mask(f)}")
        for line in list(difflib.unified_diff(b.splitlines(), f.splitlines(),
                                              lineterm="", n=0))[:12]:
            print("   ", line[:160])
print("=== rows with raw stderr diff base1 vs fold1 ===")
for name, s in summary.items():
    if not s["stderr_eq_1"]:
        b = recs[name]["base1"]["stderr"]
        f = recs[name]["fold1"]["stderr"]
        print(f"-- {name}: raw_differs; masked_equal={mask(b) == mask(f)}")
        for line in list(difflib.unified_diff(b.splitlines(), f.splitlines(),
                                              lineterm="", n=0))[:12]:
            print("   ", line[:160])
print("=== per-row verdicts ===")
fails = 0
for name, s in summary.items():
    ok = (all(s["sig"].values())
          and set(map(str, s["rc"].values())) == {str(s["expected_exit"])}
          and not s["fold_effects"]
          and not s["fold_self_unstable"])
    fails += 0 if ok else 1
    print(f"{'PASS' if ok else 'FAIL'} {name} sig={all(s['sig'].values())} "
          f"eff={len(s['fold_effects'])} self_unstable={s['fold_self_unstable']}")
print("FAILS", fails)
