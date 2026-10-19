#!/usr/bin/env python3
r"""r104-G0 — PASS-prefix census over stored receipts + false-positive analysis
for the proposed 'PASS'-prefix-any-whitespace tightening of the gate's
pass-line census.

Read-only. Never executes corpus/fixtures/run_battery.py (imports it instead).

The landed census is `line.startswith("PASS ")` (4 sites in run_battery.py).
This script measures every axis the tightening touches, over all stored green
runs on disk:

  A. column-0 `^PASS[ \t]`      (the landed rule)
  B. column-0 PASS with separator widened to any whitespace / EOL
  C. leading whitespace tolerated too
  D. `^PASS\S`                  (PASS immediately followed by non-whitespace:
                                 the false-positive class, e.g. PASSWORD/PASSING)
"""
import argparse
import collections
import json
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
RUNS = REPO / "corpus" / "live" / "runs"

RULES = {
    "A_landed_col0_space": re.compile(r"^PASS[ \t]"),
    "B_col0_anyws": re.compile(r"^PASS(?:\s|$)"),
    "C_lead_anyws": re.compile(r"^\s*PASS(?:\s|$)"),
    "D_nonws_after": re.compile(r"^PASS\S"),
}
# specifically: leading whitespace THEN PASS — invisible to A and B, caught by C
LEAD = re.compile(r"^\s+PASS")


def iter_rows(paths):
    for p in paths:
        payload = json.loads(p.read_bytes())
        for r in payload.get("results", []):
            yield p.parent.name, r


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("runs", nargs="*")
    args = ap.parse_args()
    paths = [Path(x) for x in args.runs] or sorted(RUNS.glob("*/verdicts.json"))

    hits = collections.Counter()
    nonws = collections.Counter()
    lead = collections.Counter()
    examples = collections.defaultdict(list)
    per_run = {}
    totals = collections.Counter()

    for name, r in iter_rows(paths):
        out = r.get("output")
        if not isinstance(out, list):
            continue
        c = collections.Counter()
        for line in out:
            if not isinstance(line, str):
                continue
            totals["lines"] += 1
            for key, rx in RULES.items():
                if rx.match(line):
                    hits[key] += 1
                    c[key] += 1
            if RULES["D_nonws_after"].match(line):
                nonws[line.split(" ")[0][:24]] += 1
                examples["D_nonws"].append((name, r.get("case"), line[:90]))
            if LEAD.match(line):
                lead[line.lstrip()[:24]] += 1
                examples["lead"].append((name, r.get("case"), line[:90]))
        for key in RULES:
            per_run.setdefault(name, collections.Counter())[key] += c[key]
        totals["rows"] += 1

    print("RUNS=%d ROWS=%d LINES=%d" % (len(paths), totals["rows"], totals["lines"]))
    for key in RULES:
        print("RULE %-20s matches=%d" % (key, hits[key]))
    print("DELTA B_minus_A (anyws-after-PASS at col0) = %d" % (hits["B_col0_anyws"] - hits["A_landed_col0_space"]))
    print("DELTA C_minus_B (leading-ws PASS)            = %d" % (hits["C_lead_anyws"] - hits["B_col0_anyws"]))
    print("FPCLASS D (PASS + non-whitespace)            = %d" % hits["D_nonws_after"])
    if nonws:
        print("  distinct D prefixes: %s" % dict(nonws))
    if lead:
        print("  distinct leading-ws PASS prefixes: %s" % dict(lead))
    for kind in ("D_nonws", "lead"):
        print("--- %s examples (first 10) ---" % kind)
        for row in examples[kind][:10]:
            print("  run=%s case=%s line=%r" % row)
    print("--- per-run (A landed / C proposed) ---")
    for name in sorted(per_run):
        print("  %s A=%d C=%d" % (name, per_run[name].get("A_landed_col0_space", 0),
                                  per_run[name].get("C_lead_anyws", 0)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
