#!/usr/bin/env python3
"""r103 V10 — byte-stability protocol tool for official battery runs.

Compares two verdicts.json receipt sets (two fresh runs of the same CASES set)
case-by-case on *stored bytes* and classifies every difference. No engine run,
no shared-file write, no battery execution: pure read of already-stored
records (the C2 "stored verdict records" surface).

Stability classes (assigned per case):
  STABLE        output list, verdict, actual_exit byte-identical.
  NORM_STABLE   differs only in fields normalized away (see NORMALIZERS) —
                path tokens, engine banner date, RIDs/instance ids, timings.
  VARIABLE      differs after normalization; first diff line pair reported.
  MISSING_A/B   case absent on one side.
  COUNT_MISMATCH both sides same case but different number of output lines.

Usage:
  r103-ver10-bytes.py A.json B.json [--json OUT.json] [--label NAME]
"""
import argparse
import json
import re
import sys

BANNER = re.compile(r"^Godot Engine v[\d.]+\.stable[^\n]*$")
RID = re.compile(r"RID\([^)]*\)")
# host/scratch absolute paths: any token starting with / that contains /
ABSPATH = re.compile(r"(?<![\w/.])/(?:[^\s'\"\]\[,;()]*)")
FLOATISH = re.compile(r"(?<![\w.])-?\d+\.\d+(?![\w.])")


def norm_line(line, root_a, root_b):
    s = line
    s = BANNER.sub("<BANNER>", s)
    s = RID.sub("<RID>", s)
    s = s.replace(root_a, "<ROOT>").replace(root_b, "<ROOT>")
    s = ABSPATH.sub("<PATH>", s)
    s = FLOATISH.sub("<FLOAT>", s)
    return s


def classify(line_a, line_b, root_a, root_b):
    if line_a == line_b:
        return "exact"
    if norm_line(line_a, root_a, root_b) == norm_line(line_b, root_a, root_b):
        return "normalized"
    return "divergent"


def compare_case(row_a, row_b, root_a, root_b):
    out = {"case": row_a["case"]}
    for key in ("verdict", "actual_exit", "signature"):
        out["a_" + key] = row_a.get(key)
        out["b_" + key] = row_b.get(key)
    la = row_a.get("output") or []
    lb = row_b.get("output") or []
    out["lines_a"], out["lines_b"] = len(la), len(lb)
    exact = norm = 0
    first_div = None
    for i in range(min(len(la), len(lb))):
        c = classify(la[i], lb[i], root_a, root_b)
        if c == "exact":
            exact += 1
        elif c == "normalized":
            norm += 1
        elif first_div is None:
            first_div = [i, la[i], lb[i]]
    out["exact_lines"], out["normalized_lines"] = exact, norm
    meta_same = (row_a.get("verdict") == row_b.get("verdict")
                 and row_a.get("actual_exit") == row_b.get("actual_exit"))
    if len(la) != len(lb):
        out["class"] = "COUNT_MISMATCH"
    elif not meta_same or first_div is not None:
        out["class"] = "VARIABLE"
    elif norm:
        out["class"] = "NORM_STABLE"
    else:
        out["class"] = "STABLE"
    if first_div is not None:
        out["first_div"] = first_div
        out["first_div_norm"] = [norm_line(first_div[1], root_a, root_b),
                                 norm_line(first_div[2], root_a, root_b)]
    return out


def load(path):
    d = json.load(open(path))
    rows = d.get("results") if isinstance(d, dict) else d
    return {r["case"]: r for r in rows}, (d.get("scratch") or "" if isinstance(d, dict) else "")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("a")
    ap.add_argument("b")
    ap.add_argument("--json")
    ap.add_argument("--label", default="")
    args = ap.parse_args()
    map_a, root_a = load(args.a)
    map_b, root_b = load(args.b)
    classes = {}
    diffs = []
    only_a = sorted(set(map_a) - set(map_b))
    only_b = sorted(set(map_b) - set(map_a))
    for case in sorted(set(map_a) & set(map_b)):
        r = compare_case(map_a[case], map_b[case], root_a, root_b)
        classes[r["class"]] = classes.get(r["class"], 0) + 1
        if r["class"] in ("VARIABLE", "COUNT_MISMATCH"):
            diffs.append(r)
    report = {
        "label": args.label,
        "a": args.a, "b": args.b,
        "root_a": root_a, "root_b": root_b,
        "cases_a": len(map_a), "cases_b": len(map_b),
        "only_in_a": only_a, "only_in_b": only_b,
        "class_counts": classes,
        "variable_cases": [d["case"] for d in diffs],
        "diffs": diffs,
    }
    if args.json:
        with open(args.json, "w") as fh:
            json.dump(report, fh, indent=1)
    print("label=%s cases_a=%d cases_b=%d" % (args.label or "-", len(map_a), len(map_b)))
    print("classes=%s" % json.dumps(classes, sort_keys=True))
    print("only_in_a=%s" % only_a)
    print("only_in_b=%s" % only_b)
    for d in diffs[:20]:
        print("-- VARIABLE %s lines=%d/%d verdict=%s/%s exit=%s/%s"
              % (d["case"], d["lines_a"], d["lines_b"], d["a_verdict"], d["b_verdict"],
                 d["a_actual_exit"], d["b_actual_exit"]))
        if "first_div_norm" in d:
            print("   A: %s" % d["first_div_norm"][0][:400])
            print("   B: %s" % d["first_div_norm"][1][:400])
    return 0


if __name__ == "__main__":
    sys.exit(main())
