#!/usr/bin/env python3
"""r103-W4 verify pass: multi-PASS census invariants on r102 verdicts.json runs.
Read-only. Prints strict invariants; exits 0 always (report tool)."""
import json, re, hashlib

PASS_START = re.compile(r"^PASS(\b|$|[:=])")
RUNS = {"run1": "corpus/live/runs/20261018T212500022987Z/verdicts.json",
        "run2": "corpus/live/runs/20261018T213443471189Z/verdicts.json"}

data = {}
for k, p in RUNS.items():
    b = open(p, "rb").read()
    print(f"{k}: {p} bytes={len(b)} sha256={hashlib.sha256(b).hexdigest()}")
    data[k] = json.loads(b)

def passlines(row):
    ls = row.get("output")
    return None if ls is None else [x for x in ls if PASS_START.match(x)]

# 1. case alignment
mis = [(i, a.get("case"), b.get("case")) for i, (a, b) in
       enumerate(zip(data["run1"]["results"], data["run2"]["results"]))
       if a.get("case") != b.get("case")]
print("1. case-order mismatches:", mis if mis else "NONE (554/554 aligned)")

# 2. multi-PASS sets per run (recompute) + cross-run byte identity restricted to them
multi1 = {r["case"]: passlines(r) for r in data["run1"]["results"] if len(passlines(r) or []) > 1}
multi2 = {r["case"]: passlines(r) for r in data["run2"]["results"] if len(passlines(r) or []) > 1}
print(f"2. multi-PASS case sets: run1 n={len(multi1)} run2 n={len(multi2)} identical={set(multi1)==set(multi2)}")
diff = [c for c in multi1 if multi1[c] != multi2.get(c)]
print("   multi-PASS lines byte-identity across runs:",
      "ALL IDENTICAL" if not diff else f"DIFFS in {diff}")

# 3. per-multi-case line counts + distinct two-token tags
for c in sorted(multi1, key=lambda c: [r["case"] for r in data["run1"]["results"]].index(c)):
    tags = {}
    for ln in multi1[c]:
        t = " ".join(ln.split()[:2])
        tags[t] = tags.get(t, 0) + 1
    print(f"   {c}: nPASS={len(multi1[c])} tags={tags}")

# 4. single-PASS rows whose line differs across runs (context: timing drift class)
sp_diff, sp_same = [], 0
for a, b in zip(data["run1"]["results"], data["run2"]["results"]):
    la, lb = passlines(a), passlines(b)
    if la is not None and len(la) == 1 and lb is not None and len(lb) == 1:
        if la[0] == lb[0]:
            sp_same += 1
        else:
            sp_diff.append((a.get("case"), la[0], lb[0]))
print(f"4. single-PASS rows: byte-identical across runs={sp_same} drifted={len(sp_diff)}")
first_tags = {c: (x.split()[:1], y.split()[:1]) for c, x, y in sp_diff}
tag_ok = all(x == y for x, y in first_tags.values())
print("   drifted rows keep same first token:", tag_ok)
for c, x, y in sp_diff[:3]:
    print(f"   e.g. {c}\n     run1: {x[:100]}\n     run2: {y[:100]}")

# 5. signature presence and relation for multi cases
print("5. signature presence over all rows:")
for k in RUNS:
    n_none = sum(1 for r in data[k]["results"] if not r.get("signature"))
    print(f"   {k}: rows with empty/None signature = {n_none}")

# 6. zero-PASS rows census (context for gate fail-closed)
for k in RUNS:
    zp = [r.get("case") for r in data[k]["results"]
          if (r.get("output") is not None and not passlines(r))]
    no_out = [r.get("case") for r in data[k]["results"] if r.get("output") is None]
    print(f"6. {k}: zero-PASS rows={len(zp)} no-output rows={len(no_out)}")
    print(f"   zero-PASS sample: {zp[:6]} … {zp[-4:]}")
