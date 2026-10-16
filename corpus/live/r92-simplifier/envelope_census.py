#!/usr/bin/env python3
"""r92-simplifier: committed nav-receipt envelope census.

Scans every committed receipt under corpus/live/{r92-scout,r92-boundary,
r92-author} for 'PASS tilemap_lattice nav ' lines and partitions them by
the two whitelisted payloads (regions_f1=1 vs regions_f1=0), plus a
'neither' bucket. Also censuses the nullts crash receipts (rc files) and
the 13 non-nav r92 rows' line uniqueness across the committed corpus.

Usage: python3 envelope_census.py
"""
import re
from pathlib import Path

REPO = Path("/home/vgpnk/Projects/shokunin/game-dev-2d-shokunin")
ROOTS = [REPO / "corpus/live" / d for d in
         ("r92-scout", "r92-boundary", "r92-author", "r92-simplifier")]

NAV = "PASS tilemap_lattice nav "
PAYLOAD_F1_1 = " regions_f1=1 "
PAYLOAD_F1_0 = " regions_f1=0 "


def main():
    nav_receipts = []
    for root in ROOTS:
        for p in root.rglob("*"):
            if not p.is_file() or p.stat().st_size > 4_000_000:
                continue
            try:
                text = p.read_text(errors="replace")
            except OSError:
                continue
            for line in text.splitlines():
                if line.startswith(NAV):
                    nav_receipts.append((str(p.relative_to(REPO)), line))
    one = [r for r in nav_receipts if PAYLOAD_F1_1 in r[1] + " "]
    zero = [r for r in nav_receipts if PAYLOAD_F1_0 in r[1] + " "]
    other = [r for r in nav_receipts if r not in one and r not in zero]
    print("committed nav receipts: %d" % len(nav_receipts))
    print("  payload[0] regions_f1=1: %d" % len(one))
    print("  payload[1] regions_f1=0: %d" % len(zero))
    print("  neither: %d" % len(other))
    for path, line in other[:10]:
        print("    NEITHER %s: %s" % (path, line[:160]))
    # f2 must be 1 in both payloads
    f2_bad = [r for r in nav_receipts if " regions_f2=1 " not in r[1] + " "]
    print("  regions_f2 != 1: %d" % len(f2_bad))
    # distinct lines per payload
    print("  distinct payload[0] lines: %d" % len({r[1] for r in one}))
    print("  distinct payload[1] lines: %d" % len({r[1] for r in zero}))
    # where do the receipts come from
    from collections import Counter
    print("  by seat:", Counter(p.split("/")[2] for p, _ in nav_receipts))

    # non-nav r92 rows: distinct emitted lines across the committed corpus
    print()
    print("committed PASS lines per non-nav r92 row:")
    for arm in ("census", "atlas", "cells", "custom", "terrain", "pattern",
                "encoding", "fixinvalid", "srcids", "physics", "timing",
                "quadrant"):
        pref = "PASS tilemap_lattice %s " % arm
        lines = set()
        for root in ROOTS:
            for p in root.rglob("*"):
                if not p.is_file() or p.stat().st_size > 4_000_000:
                    continue
                try:
                    text = p.read_text(errors="replace")
                except OSError:
                    continue
                for line in text.splitlines():
                    if line.startswith(pref):
                        lines.add(line)
        print("  %-11s receipts=%d distinct_lines=%d" % (arm, len(lines), len(lines)))
        for line in sorted(lines)[:2]:
            print("      %s" % line[:120])
    # nullts rc census
    print()
    print("nullts crash receipts (rc files):")
    from collections import Counter
    rcs = Counter()
    for root in ROOTS:
        for p in root.rglob("nullts*.rc"):
            rcs[p.read_text().strip()] += 1
    print("  ", dict(rcs))


if __name__ == "__main__":
    main()
