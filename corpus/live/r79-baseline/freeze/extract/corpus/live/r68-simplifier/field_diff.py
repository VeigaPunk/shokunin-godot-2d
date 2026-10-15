#!/usr/bin/env python3
"""r67 simplifier field-diff: compare two verdicts.json runs on shared rows.
Normalizes volatile fields (pids, timestamps, ASLR hex, elapsed floats, run
dirs) then reports: shared-row verdict diffs, new-only rows, missing rows,
and residual field-level diffs. Usage: field_diff.py A.json B.json
"""
import json
import re
import sys


def norm(obj):
    if isinstance(obj, dict):
        return {k: norm(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [norm(v) for v in obj]
    if isinstance(obj, str):
        s = obj
        s = re.sub(r"\b\d{4}\d{4}T\d{9}Z\b", "<STAMP>", s)
        s = re.sub(r"[0-9a-f]{12,64}\.x86_64", "<BIN>", s)
        s = re.sub(r"\b[0-9a-f]{64}\b", "<SHA>", s)
        s = re.sub(r"\b\d{4,7}\b", "<PID>", s)          # pids / big ints
        s = re.sub(r"0x[0-9a-fA-F]+", "<HEX>", s)
        s = re.sub(r"\b[0-9a-f]{6,11}\b", "<HEX>", s)   # ASLR-ish
        s = re.sub(r"/home/vgpnk\S*/runs/\S+", "<RUN>", s)
        s = re.sub(r"\d+\.\d+", "<F>", s)
        return s
    if isinstance(obj, float):
        return "<F>"
    if isinstance(obj, int) and abs(obj) > 9999:
        return "<PID>"
    return obj


def main():
    a = json.load(open(sys.argv[1]))
    b = json.load(open(sys.argv[2]))
    ra = {r["case"]: r for r in a["results"]}
    rb = {r["case"]: r for r in b["results"]}
    shared = sorted(set(ra) & set(rb))
    print(f"A={sys.argv[1]}")
    print(f"B={sys.argv[2]}")
    print(f"shared={len(shared)} new_only={sorted(set(rb)-set(ra))} "
          f"base_only={sorted(set(ra)-set(rb))}")
    verdict_diffs = []
    field_diffs = []
    for case in shared:
        if ra[case].get("verdict") != rb[case].get("verdict"):
            verdict_diffs.append(case)
        na, nb = norm(ra[case]), norm(rb[case])
        if na != nb:
            keys = sorted({k for k in set(na) | set(nb)
                           if na.get(k) != nb.get(k)})
            field_diffs.append((case, keys))
    print(f"verdict_diffs={verdict_diffs}")
    print("field_diff_rows:")
    for case, keys in field_diffs:
        print(f"  {case}: {keys}")


if __name__ == "__main__":
    main()
