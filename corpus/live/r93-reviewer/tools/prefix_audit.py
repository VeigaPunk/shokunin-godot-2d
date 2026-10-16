#!/usr/bin/env python3
"""r93-reviewer prefix/byte-stability audit.

For every r93 row and every rep receipt in a directory:
  - locate the PASS line of the row's arm,
  - report whether each candidate pin is a byte-substring,
  - for full-line pins report prefix length (tail length, 0 = full-line match),
  - report rep-level PASS-line uniqueness per arm.

usage: prefix_audit.py <receipts-dir> [--reps 5] [--json out.json]
"""
import argparse
import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import ufo_r93


def pass_line(out, arm):
    for line in out.splitlines():
        if line.startswith("PASS ") and (f" anim_lattice {arm}" in line or f" r93b_anim {arm}" in line):
            return line
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("dir", type=pathlib.Path)
    ap.add_argument("--reps", type=int, default=5)
    ap.add_argument("--json", type=pathlib.Path, default=None)
    args = ap.parse_args()
    C, rows = ufo_r93.load_rows()
    records = []
    for case, row in sorted(rows.items()):
        script = row["script"]
        arm = [f.removeprefix("--arm=") for f in row["flags"] if f.startswith("--arm=")][0]
        stem = script[:-3] if script.endswith('.gd') else script
        if True:
            sigs = ufo_r93.sigs_of(rows[case])
            plines, hits, prefixes = [], [], []
            for rep in range(1, args.reps + 1):
                f = args.dir / f"{arm}.rep{rep}.out"
                if not f.is_file():
                    f = args.dir / f"{stem}.{arm}.rep{rep}.out"
                if not f.is_file():
                    continue
                out = f.read_text()
                pl = pass_line(out, arm)
                plines.append(pl)
                hit = next((i for i, s in enumerate(sigs) if s in out), None)
                hits.append(hit)
                if pl is None:
                    prefixes.append("no-pass-line")
                elif hit is not None and pl.startswith(sigs[hit]):
                    prefixes.append(f"tail={len(pl) - len(sigs[hit])}")
                elif hit is not None:
                    prefixes.append("substring-not-prefix")
                else:
                    prefixes.append("no-pin-hit")
            records.append({"case": case, "script": script, "arm": arm,
                            "pins": len(sigs), "hits": hits, "prefix": prefixes,
                            "line_uniq": len(set(plines)),
                            "lines": sorted(set(p for p in plines if p))})
            print(f"{case:34s} pins={len(sigs)} hits={hits} prefix={prefixes} line_uniq={len(set(plines))}",
                  flush=True)
    if args.json:
        args.json.write_text(json.dumps({"dir": str(args.dir), "rows": records}, indent=1))
    bad = [r["case"] for r in records if any(h is None for h in r["hits"])]
    print(f"\nrows={len(records)} all-hits={not bad} bad={bad}")


if __name__ == "__main__":
    main()
