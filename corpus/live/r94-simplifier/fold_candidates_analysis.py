#!/usr/bin/env python3
"""r94-simplifier fold-candidate byte analysis (post-processes the JSON).

The raw comparison counts a pair "different" when stdout bytes differ — but the
timing arms carry documented ±1-tick measured tails that vary run-to-run
WITHIN one fixture. This script separates the two sources:

  * pinned prefix  = the committed signature block (before " | ")
  * measured tail  = everything after it (the deliberately unpinned surface)

and compares (a) committed-vs-folded cross pairs, (b) committed-vs-committed
internal pairs, (c) folded-vs-folded internal pairs. If the cross mismatch rate
is no worse than the internal rate and every cross pair keeps an identical
prefix, the −3-line fold is invisible to everything the battery pins.

Usage: python3 fold_candidates_analysis.py > fold-candidates-analysis.txt
"""
import json
from itertools import combinations
from pathlib import Path

HERE = Path(__file__).resolve().parent
DATA = json.loads((HERE / "fold-candidates-verification.json").read_text())


def split_line(stdout):
    lines = [l for l in stdout.splitlines() if l.startswith("PASS ")]
    line = lines[0] if lines else ""
    if " | " in line:
        prefix, tail = line.split(" | ", 1)
    else:
        prefix, tail = line, ""
    return prefix, tail


def diff_tokens(a, b):
    ta, tb = a.split(), b.split()
    out = []
    for x, y in zip(ta, tb):
        if x != y:
            out.append("%s -> %s" % (x, y))
    if len(ta) != len(tb):
        out.append("token-count %d vs %d" % (len(ta), len(tb)))
    return out


def main():
    total_cross = total_int_c = total_int_f = 0
    all_prefix_stable = True
    print("== per-arm byte analysis (committed c1..c3 vs folded f1..f3) ==")
    for arm, rows in sorted(DATA["per_arm"].items()):
        c = [split_line(r["committed"]["stdout"]) for r in rows]
        f = [split_line(r["folded"]["stdout"]) for r in rows]
        prefixes = {p for p, _ in c} | {p for p, _ in f}
        prefix_stable = len(prefixes) == 1
        all_prefix_stable &= prefix_stable

        cross = []
        for i in range(len(rows)):
            if c[i] != f[i]:
                cross.append({"rep": i + 1, "prefix_eq": c[i][0] == f[i][0],
                              "tail_diff": diff_tokens(c[i][1], f[i][1])})
        internal_c = []
        for i, j in combinations(range(len(rows)), 2):
            if c[i] != c[j]:
                internal_c.append((i + 1, j + 1))
        internal_f = []
        for i, j in combinations(range(len(rows)), 2):
            if f[i] != f[j]:
                internal_f.append((i + 1, j + 1))

        total_cross += len(cross)
        total_int_c += len(internal_c)
        total_int_f += len(internal_f)
        print("%-16s prefix_stable=%s  cross_mismatch=%d/%d (prefix_eq all=%s)  "
              "internal_committed=%d/%d  internal_folded=%d/%d"
              % (arm, prefix_stable, len(cross), len(rows),
                 all(x["prefix_eq"] for x in cross),
                 len(internal_c), 3, len(internal_f), 3))
        for x in cross:
            print("    cross rep%d prefix_eq=%s tail_diff=%s"
                  % (x["rep"], x["prefix_eq"], x["tail_diff"] or "none"))
        if internal_c:
            print("    internal committed differing rep pairs: %s" % (internal_c,))
        if internal_f:
            print("    internal folded differing rep pairs: %s" % (internal_f,))

    print()
    print("== summary ==")
    print("arms: %d  pairs: %d" % (len(DATA["per_arm"]), DATA["pairs"]))
    print("cross committed-vs-folded mismatching pairs: %d" % total_cross)
    print("internal committed-vs-committed mismatching pairs (same fixture): %d" % total_int_c)
    print("internal folded-vs-folded mismatching pairs (same fixture): %d" % total_int_f)
    print("every arm's pinned prefix byte-stable across all 6 receipts: %s" % all_prefix_stable)


if __name__ == "__main__":
    main()
