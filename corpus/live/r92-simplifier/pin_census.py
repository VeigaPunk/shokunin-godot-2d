#!/usr/bin/env python3
"""r92-simplifier pin<->emission census over committed receipts.

Per r92 row, over every verdicts.json given on the command line:
  * collect the emitted signature-bearing lines,
  * classify each as EXACT (line == pinned payload), PREFIX (line startswith
    payload, tail follows), or SUBSTRING (payload inside the line, the crash
    row's stdout-anchor shape),
  * census per-line field variance (fields compared only within the same
    emitted line),
  * census per-line run presence.

Usage: python3 pin_census.py <verdicts.json> [<verdicts.json> ...]
"""
import json
import sys
from pathlib import Path


def load_rows(paths):
    rows = {}
    for p in paths:
        payload = json.loads(Path(p).read_text())
        run = Path(p).parent.name
        for r in payload["results"]:
            case = r["case"]
            if not case.startswith("r92_"):
                continue
            lines = [l for l in r.get("output", []) if l.startswith("PASS ")
                     or (l.startswith("R92 ") and case == "r92_tilemap_nullts_crash")]
            rows.setdefault(case, []).append({
                "run": run, "exit": r["actual_exit"],
                "verdict": r["verdict"], "lines": lines,
                "signature": r["signature"]})
    return rows


def field_map(line):
    out = {}
    for p in line.split(" "):
        if "=" in p:
            k, _, v = p.partition("=")
            out[k] = v
    return out


def main():
    paths = sys.argv[1:]
    rows = load_rows(paths)
    print("receipt files: %d" % len(paths))
    print("r92 rows seen: %d" % len(rows))
    exact = prefix = substring = 0
    unmatched = 0
    for case in sorted(rows):
        recs = rows[case]
        sigs = recs[0]["signature"]
        sigs = list(sigs) if isinstance(sigs, (list, tuple)) else [sigs]
        runs = sorted({r["run"] for r in recs})
        exits = sorted({r["exit"] for r in recs})
        verdicts = sorted({r["verdict"] for r in recs})
        line_set = sorted({l for r in recs for l in r["lines"]})
        print()
        print("== %s ==" % case)
        print("  receipts=%d runs=%d exits=%s verdicts=%s distinct_lines=%d"
              % (len(recs), len(runs), exits, verdicts, len(line_set)))
        for line in line_set:
            present = sum(1 for r in recs if line in r["lines"])
            kind = "UNMATCHED"
            if line in sigs:
                kind = "EXACT"
            elif any(line.startswith(s) for s in sigs):
                kind = "PREFIX"
            elif any(s in line for s in sigs):
                kind = "SUBSTRING"
            if kind == "EXACT":
                exact += 1
            elif kind == "PREFIX":
                prefix += 1
            elif kind == "SUBSTRING":
                substring += 1
            else:
                unmatched += 1
            print("  %-9s presence=%d/%d %s" % (kind, present, len(recs), line[:150]))
        for s in sigs:
            n = sum(1 for r in recs for l in r["lines"] if s in l)
            print("  payload matched receipts: %d  sig=%s..." % (n, s[:70]))
        # per-line field variance
        for line in line_set:
            fmaps = [field_map(r_line) for r in recs for r_line in r["lines"]
                     if r_line == line]
            keys = sorted({k for f in fmaps for k in f})
            varying = {k: sorted({f.get(k, "<absent>") for f in fmaps})
                       for k in keys
                       if len({f.get(k, "<absent>") for f in fmaps}) > 1}
            print("  line fields=%d varying=%d %s"
                  % (len(keys), len(varying),
                     ("VARY " + json.dumps(varying)) if varying else ""))
    print()
    print("EXACT=%d PREFIX=%d SUBSTRING=%d UNMATCHED=%d" % (exact, prefix, substring, unmatched))
    print("ALL_SIGNATURES_ANCHORED=%s" % (unmatched == 0))


if __name__ == "__main__":
    main()
