#!/usr/bin/env python3
"""r93-reviewer: pin presence across the frozen r93-boundary corpus.

For every r93 row, count the boundary receipts of its arm that contain the
row's pinned substring(s). 14/14 for the nine byte-stable arms, 16/16 for the
mode and r93b arms (the boundary ran the scout cells 14x and its own 6 arms
16x across 7 launch conditions).
"""
import pathlib
import re
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import ufo_r93

BOUNDARY = pathlib.Path("corpus/live/r93-boundary/runs")


def main():
    C, rows = ufo_r93.load_rows()
    per_arm = {}
    for f in BOUNDARY.glob("*.out"):
        m = re.match(r"[a-z0-9]+_([a-z_]+)\.rep\d+\.out$", f.name)
        if m:
            per_arm.setdefault(m.group(1), []).append(f)
    bad = []
    for case, row in sorted(rows.items()):
        arm = [x.removeprefix("--arm=") for x in row["flags"] if x.startswith("--arm=")][0]
        files = per_arm.get(arm, [])
        if not files:
            print(f"{case:34s} NO-ARM-RECEIPTS")
            bad.append(case)
            continue
        sigs = ufo_r93.sigs_of(row)
        hits = sum(1 for f in files if any(s in f.read_text() for s in sigs))
        print(f"{case:34s} {hits}/{len(files)}")
        if hits != len(files):
            bad.append(case)
    print(f"\nrows={len(rows)} all-pins-in-all-boundary-receipts={not bad} bad={bad}")


if __name__ == "__main__":
    main()
