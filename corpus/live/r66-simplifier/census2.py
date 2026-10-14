#!/usr/bin/env python3
import json, sys
sys.argv = ["census.py", sys.argv[1]]
g = {}
exec(open("/home/vgpnk/Projects/shokunin/game-dev-2d-shokunin/corpus/live/r66-simplifier/census.py").read()
     .split("data = json")[0], g)
EXPECTED_ERRORS = g["EXPECTED_ERRORS"]; allowed_error = g["allowed_error"]
data = json.load(open(sys.argv[1]))
rows = {r["case"]: r for r in data["results"]}
shapes = {"exact": 0, "comma-prefix": 0, "structured": 0}
redundant = []
for case, entries in EXPECTED_ERRORS.items():
    row = rows.get(case)
    if not row:
        continue
    lines = row.get("output", [])
    err = [ln for ln in lines if "ERROR:" in ln]
    for e in entries:
        s = "comma-prefix" if e.endswith(",") else ("structured" if e == "ERROR: chain incomplete" else "exact")
        shapes[s] += 1
        others = [x for x in entries if x != e]
        sole = [ln for ln in err if allowed_error(ln, e) and not any(allowed_error(ln, o) for o in others)]
        if not sole:
            redundant.append((case, e[:70]))
print("shape histogram:", shapes)
print("entries solely-covering no line (redundant):", len(redundant))
for r in redundant:
    print("  ", r)
for case, entries in EXPECTED_ERRORS.items():
    if len(entries) > 1:
        row = rows[case]; lines = row["output"]
        print(case)
        for e in entries:
            print("   matched", sum(1 for ln in lines if allowed_error(ln, e)), "<-", e[:60])
