#!/usr/bin/env python3
"""Field-diff two run_battery verdicts.json receipts on the lane's 7-field tuple.

Ordinary rows compare (script, flags, expected_exit, actual_exit, signature,
verdict, error); meta/probe rows (no 'script' key) compare on verdict only —
same convention as r63/r64 reviewers.
"""
import json
import sys

TUPLE = ("script", "flags", "expected_exit", "actual_exit", "signature",
         "verdict", "error")


def key_of(row):
    if "script" in row:
        return (row["script"], json.dumps(row.get("flags", [])))
    return ("__meta__", row["case"])


def shape(row):
    if "script" in row:
        return tuple(row.get(f) for f in TUPLE)
    return (row.get("verdict"),)


def main(new_path, base_path):
    new = {key_of(r): r for r in json.load(open(new_path))["results"]}
    base = {key_of(r): r for r in json.load(open(base_path))["results"]}
    shared = sorted(set(new) & set(base))
    mismatches = []
    for k in shared:
        if shape(new[k]) != shape(base[k]):
            mismatches.append((k, shape(base[k]), shape(new[k])))
    print(f"new_rows={len(new)} base_rows={len(base)} shared={len(shared)}")
    print(f"new_only={sorted(set(new) - set(base))}")
    print(f"base_only={sorted(set(base) - set(new))}")
    print(f"mismatches={len(mismatches)}")
    for k, b, n in mismatches:
        print(f"  MISMATCH {k}\n    base={b}\n    new ={n}")
    return 0 if not mismatches else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1], sys.argv[2]))
