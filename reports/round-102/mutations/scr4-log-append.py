#!/usr/bin/env python3
"""r102 scr4: guarded append of the ROUND 102 entry to LOG.md.

Usage:
    python3 scr4-log-append.py --entry reports/round-102/r102-scr4-entry.md [--log LOG.md]

Guards (all asserted before any write):
  1. LOG.md's last non-empty line is the known r101 final line (ROUTED tail).
  2. `ROUND 102` occurs 0 times in LOG.md (no double-append).
  3. Entry begins with `- ROUND 102 (2026-10-18):` and contains no `«`/`»`
     and no `TBD` — the fill tokens of the draft must be resolved first.
  4. Entry ends with exactly one newline; blank-line separation preserved.

Post-conditions: `ROUND 102` occurs exactly once; line count grew by exactly
the entry's line count.
"""
import argparse

R101_FINAL = "  unrelated); 3D side-round deferred via L0 (3D lane under parallel r104)."


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--entry", required=True)
    ap.add_argument("--log", default="/home/vgpnk/Projects/shokunin/game-dev-2d-shokunin/LOG.md")
    args = ap.parse_args()

    entry = open(args.entry, encoding="utf-8").read()
    log = open(args.log, encoding="utf-8").read()

    assert entry.startswith("- ROUND 102 (2026-10-18):"), "entry does not start with the round header"
    for bad in ("«", "»", "TBD"):
        assert bad not in entry, f"unresolved fill token in entry: {bad!r}"
    assert entry.endswith("\n") and not entry.endswith("\n\n"), "entry must end with exactly one newline"
    assert log.count("ROUND 102") == 0, "LOG.md already carries a ROUND 102 entry"
    lines = log.split("\n")
    last_nonempty = [l for l in lines if l.strip()][-1]
    assert last_nonempty == R101_FINAL, f"LOG.md tail drift: {last_nonempty[:60]!r}"

    new_log = log + "\n" + entry
    assert new_log.count("ROUND 102") == 1, "post-append token count != 1"
    assert new_log.count("\n") == log.count("\n") + entry.count("\n") + 1, "line-count delta unexpected"

    with open(args.log, "w", encoding="utf-8") as fh:
        fh.write(new_log)
    print(f"OK: appended {entry.count(chr(10))} lines to {args.log}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
