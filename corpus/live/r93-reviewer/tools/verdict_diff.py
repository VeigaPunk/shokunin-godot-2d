#!/usr/bin/env python3
"""r93-reviewer verdicts.json comparison.

usage: verdict_diff.py <mine> <reference> [--fields ...]

Compares two verdicts.json files row-by-row (keyed by case name): reports
missing/extra cases, verdict differences, and raw differences in the declared
fields; also prints the gate values of interest.
"""
import argparse
import json
import pathlib


def load(p):
    d = json.loads(pathlib.Path(p).read_text())
    return d, {r["case"]: r for r in d["results"]}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("mine")
    ap.add_argument("ref")
    ap.add_argument("--json", default=None)
    args = ap.parse_args()
    m, mr = load(args.mine)
    r, rr = load(args.ref)
    fields = ["verdict", "signature", "expected_exit", "actual_exit", "script",
              "flags", "error", "required_stderr", "expected_errors"]
    out = {"mine": {"verdict": m["verdict"], "n": len(m["results"])},
           "ref": {"verdict": r["verdict"], "n": len(r["results"])},
           "mine_only": sorted(set(mr) - set(rr)),
           "ref_only": sorted(set(rr) - set(mr)),
           "verdict_diffs": [], "field_diffs": []}
    for case in sorted(set(mr) & set(rr)):
        a, b = mr[case], rr[case]
        if a.get("verdict") != b.get("verdict"):
            out["verdict_diffs"].append({"case": case, "mine": a.get("verdict"),
                                         "ref": b.get("verdict")})
        for f in fields:
            if a.get(f) != b.get(f):
                out["field_diffs"].append({"case": case, "field": f,
                                           "mine": a.get(f), "ref": b.get(f)})
    print(json.dumps(out, indent=1))
    if args.json:
        pathlib.Path(args.json).write_text(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
