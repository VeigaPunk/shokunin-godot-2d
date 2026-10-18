#!/usr/bin/env python3
"""r102 scr4: repair the stale live-path citation in SCORECARD.md.

Replaces the dead token `.shokunin/game-dev-2d/corpus/` with `corpus/` on
SCORECARD.md lines 8/9/10 (the depth/coverage/calibration counting-command
rows). Exactly 3 occurrences exist, one per line (r102-ver11 sweep; scr4
re-measured). This is a same-length-unknown, line-local token replacement;
no other bytes of the 324-line file are touched.

Usage:
    python3 scr4-scorecard-cite-repair.py [path/to/SCORECARD.md]

Default target: <repo>/SCORECARD.md. Idempotent: a second run reports
"already repaired" and exits 0. Every guard is asserted before any write.
"""
import hashlib
import os
import sys

REPO = "/home/vgpnk/Projects/shokunin/game-dev-2d-shokunin"
OLD = b".shokunin/game-dev-2d/corpus/"
NEW = b"corpus/"

# (line_no, first-cell prefix, md5 of line incl. newline) — anchors measured by
# scr4 at HEAD 1392ca21 on 2026-10-18; ver11 md5s match (with-newline form).
ANCHORS = [
    (8, b"| depth | unscored |", "2158565982b31ebb050c7c56148e6860"),
    (9, b"| coverage | unscored |", "5734b6dbfabfc1fba1ce9904063bcdfe"),
    (10, b"| calibration | unscored |", "3a5f322f576e1e8952df398bf35cb61a"),
]


def main() -> int:
    target = sys.argv[1] if len(sys.argv) > 1 else os.path.join(REPO, "SCORECARD.md")
    raw = open(target, "rb").read()
    total = raw.count(OLD)
    if total == 0:
        assert b"python corpus/fixtures/run_battery.py" in raw, "post-state token missing"
        print(f"already repaired: 0 occurrences of {OLD!r} in {target}")
        return 0
    assert total == 3, f"expected 3 occurrences, found {total} — aborting"
    assert not os.path.exists(os.path.join(REPO, ".shokunin")), "dead path unexpectedly exists"

    lines = raw.split(b"\n")
    assert len(lines) >= 11, "file shorter than anchored lines"
    changed = []
    for lineno, prefix, want_md5 in ANCHORS:
        line = lines[lineno - 1]
        assert line.startswith(prefix), f"line {lineno} prefix drift: {line[:40]!r}"
        got_md5 = hashlib.md5(line + b"\n").hexdigest()
        assert got_md5 == want_md5, f"line {lineno} md5 drift: {got_md5} != {want_md5}"
        assert line.count(OLD) == 1, f"line {lineno} occurrence count != 1"
        lines[lineno - 1] = line.replace(OLD, NEW)
        changed.append((lineno, got_md5, hashlib.md5(lines[lineno - 1] + b"\n").hexdigest()))

    out = b"\n".join(lines)
    assert out.count(OLD) == 0, "replacement left residue"
    assert out.count(NEW + b"fixtures/run_battery.py") == 3, "expected 3 repaired commands"
    assert len(out) == len(raw) - total * (len(OLD) - len(NEW)), "unexpected length delta"

    with open(target, "wb") as fh:
        fh.write(out)
    for lineno, old_md5, new_md5 in changed:
        print(f"line {lineno}: {old_md5[:16]} -> {new_md5[:16]}")
    print(f"OK: 3 replacements in {target}; length delta {-total * (len(OLD) - len(NEW))}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
