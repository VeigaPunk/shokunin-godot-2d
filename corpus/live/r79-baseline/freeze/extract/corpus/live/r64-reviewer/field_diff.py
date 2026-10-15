#!/usr/bin/env python3
"""r64 reviewer: field-stability diff of a fresh verdicts.json vs a baseline
receipt, on the r62/r63-verifier tuple. Meta rows (no 'script' key) compare on
verdict only, per lane precedent."""
import json
import sys
from pathlib import Path

FIELDS = ("script", "flags", "expected_exit", "actual_exit", "signature",
          "verdict", "error")


def load(path):
    payload = json.loads(Path(path).read_text())
    return {r["case"]: r for r in payload["results"]}, payload


def key_tuple(record):
    return tuple(record.get(f) for f in FIELDS)


def main(new_path, base_path):
    new, new_payload = load(new_path)
    base, base_payload = load(base_path)
    shared = sorted(set(new) & set(base))
    mismatches = []
    for case in shared:
        n, b = new[case], base[case]
        if "script" in n and "script" in b:
            if key_tuple(n) != key_tuple(b):
                mismatches.append((case, key_tuple(b), key_tuple(n)))
        else:
            if n.get("verdict") != b.get("verdict"):
                mismatches.append((case, b.get("verdict"), n.get("verdict")))
    print(f"new_rows={len(new)} base_rows={len(base)} shared={len(shared)}")
    print(f"mismatches={len(mismatches)}")
    for m in mismatches:
        print("  MISMATCH", m)
    print(f"new_only={sorted(set(new) - set(base))}")
    print(f"base_only={sorted(set(base) - set(new))}")
    print(f"new_verdict={new_payload['verdict']} base_verdict={base_payload['verdict']}")
    # spoof discrimination dump
    spoof = next((r for r in new_payload["results"]
                  if r["case"] == "probe_descendant_signature_spoof"), None)
    if spoof:
        print("spoof_verdict=", spoof["verdict"])
        for k, v in spoof["discriminations"].items():
            print(f"  {k} = {v}")
        h = spoof["hold_arm"]
        print("  hold_arm: timed_out=%s child_exit_at_timeout=%s write_ppid=%s "
              "kernel_ppid=%s godot_pid=%s descendant_alive=%s inner=%s elapsed=%s"
              % (h["timed_out"], h["child_exit_at_timeout"], h["write_ppid"],
                 h["descendant_kernel_ppid_at_return"], h["godot_pid"],
                 h["descendant_alive_at_return"], h["inner_classification"],
                 h.get("elapsed_seconds")))
    forged = next((r for r in new_payload["results"]
                   if r["case"] == "descendant_pipe_forged_signature_release"), None)
    if forged:
        out = "\n".join(forged["output"])
        print("forged_row: verdict=%s exit=%s error=%r withheld_banner=%s write_ppid_line=%s"
              % (forged["verdict"], forged["actual_exit"], forged["error"],
                 "DESCENDANT_PIPE_FORGE child_signature=withheld" in out,
                 [l.strip() for l in forged["output"] if "write_ppid" in l]))


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
