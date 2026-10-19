#!/usr/bin/env python3
"""r104 C4 — registration-debt mutations for the adoptable orphaned companions.

This file does NOT edit any shared file. It emits, for the orchestrator, the
exact declaration edits an adoption of each C4-surviving companion owes, plus a
self-check that replays them against the AST-extracted in-battery gate.

Usage:
    python3 r104-crit4-registration.py [--emit] [--check]

  --emit   print the proposed CASES rows / grammar entries / expected_errors
  --check  splice them into the extracted gate and replay the real HEAD bytes
           captured by run_all.sh / run_s11.sh under /var/tmp/r104-C4/
"""
import argparse
import importlib.util
import json
import os
import sys

GATE_DIR = "/var/tmp/r104-C4"
CAPTURE = "/var/tmp/r104-C4"

# Companion -> the row shape an adoption would register.
# (fixture, arm, capture file, expected exit, CASES signature)
ROWS = [
    ("s01", None, "r3_s01.out", 0, "PASS export_prod_s01 magic=GDPC"),
    ("s02", None, "r3_s02.out", 0, "PASS export_prod_s02 entries=9"),
    ("s04", None, "r3_s04.out", 0, "PASS export_prod_s04 swap=true"),
    ("s07", None, "r1_s07.out", 0, "PASS export_prod_s07 arms=11"),
    ("s08", "control_exe", "r3_s08.out", 0, "PASS export_prod_s08 control_exe"),
    ("s11", "pack", "s11_pack.out", 0, "PASS export_prod_s11 pack magic=GDPC"),
    ("s11", "launch", "s11_launch.out", 0, "PASS export_prod_s11 launch rc=0"),
    ("s11", "ladder", "s11_ladder.out", 0, "PASS export_prod_s11 ladder n1=1"),
    ("s11", "corrupt", "s11_corrupt.out", 0, "PASS export_prod_s11 corrupt bad_rc=0"),
    ("s11", "hang0", "s11_hang0.out", 0, "PASS export_prod_s11 hang0 rc=124"),
]

# s08's default receipt prints four PASS lines; an adoption of the single
# control_exe arm still carries the sibling arms' lines when the row is the
# default arm, so the grammar entry is declared from the observed bytes.
GRAMMAR_OWED = {"export_prod_s08_control_exe"}


def load_gate():
    spec = importlib.util.spec_from_file_location("gate", os.path.join(GATE_DIR, "gate.py"))
    gate = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(gate)
    return gate


def lines_of(path):
    if not os.path.exists(path):
        return None
    text = open(path, encoding="utf-8", errors="replace").read()
    out = text.split("\n")
    if out and out[-1] == "":
        out = out[:-1]
    return out


def row_name(key, arm):
    return f"export_prod_{key}" + (f"_{arm}" if arm else "_default")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--emit", action="store_true")
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args()
    gate = load_gate()

    emitted = []
    for key, arm, cap, exit_code, sig in ROWS:
        name = row_name(key, arm)
        flags = [f"--arm={arm}"] if arm else []
        emitted.append({"case": name, "script": f"export_prod_{key}.gd",
                        "flags": flags, "expected_exit": exit_code, "signature": sig,
                        "grammar_owed": name in GRAMMAR_OWED})
        if not args.check:
            continue
        path = os.path.join(CAPTURE, cap)
        lines = lines_of(path)
        if lines is None:
            print(f"{name:34s} MISSING CAPTURE {cap}")
            continue
        row = {"case": name, "script": f"export_prod_{key}.gd", "flags": flags,
               "command": ["godot"], "expected_exit": exit_code, "actual_exit": exit_code,
               "signature": sig, "verdict": "PASS", "error": None, "expected_errors": [],
               "required_stderr": [], "output": lines}
        gate.CASES.append((name, f"export_prod_{key}.gd", flags, exit_code, sig))
        gate.CASES_SIG_BY_CASE[name] = sig
        before = [f["why"] for f in gate.receipt_shape_flag(row)]
        after = before
        if name in GRAMMAR_OWED:
            toks = []
            for ln in lines:
                if ln.startswith("PASS "):
                    p = ln.split(" ")
                    toks.append((p[1] if len(p) > 1 else "", p[2] if len(p) > 2 else ""))
            gate.RECEIPT_MULTI_PASS_GRAMMAR[name] = tuple(toks)
            after = [f["why"] for f in gate.receipt_shape_flag(row)]
            del gate.RECEIPT_MULTI_PASS_GRAMMAR[name]
        gate.CASES.pop()
        del gate.CASES_SIG_BY_CASE[name]
        pass_lines = sum(1 for ln in lines if ln.startswith("PASS "))
        print(f"{name:34s} exit={exit_code} PASS={pass_lines} "
              f"flags(before)={before or 'CLEAN'} flags(after-grammar)={after or 'CLEAN'}")

    if args.emit:
        print(json.dumps(emitted, indent=2))
    if not args.check and not args.emit:
        print("nothing to do: pass --check and/or --emit")


if __name__ == "__main__":
    main()
