#!/usr/bin/env python3
"""r102-V11 independent verifier for S4's BEFORE->AFTER pair set.

Checks, without editing anything:
  1. Every pair's BEFORE equals the live file's line at the cited number.
  2. Every AFTER equals the documented substitution applied to BEFORE,
     and contains no residual `.shokunin/game-dev-2d/` token.
  3. Duplicate pair anchors; pair-file coverage math.
  4. Independent coverage sweep of the S4 surface (SCORECARD.md, PROVINCE.md,
     corpus/lessons/**): every line containing `.shokunin` is PAIRED, LEAVE
     (absolute old-root class), or UNCOVERED. UNCOVERED is the residual set.
"""
import re
import sys
from pathlib import Path

REPO = Path("/home/vgpnk/Projects/shokunin/game-dev-2d-shokunin")
PAIRS_TXT = REPO / "reports/round-102/mutations/s4_cite_pairs.txt"
ABS_ROOT = "/home/vgpnk/Projects/prymeagnt/game-dev-2d/.shokunin/game-dev-2d/"
RULE_C = (".shokunin/game-dev-2d/corpus/", "corpus/")
RULE_R = (".shokunin/game-dev-2d/reports/", "reports/")
EXPLICIT = {
    "Only writes `.shokunin/game-dev-2d/**` and its own reports. Domain source trees are read-only.":
    "Only writes this repository's tree (`./**`) and its own reports. Domain source trees are read-only.",
}


def subst(line):
    new = line.replace(*RULE_C).replace(*RULE_R)
    if new in EXPLICIT:
        new = EXPLICIT[new]
    return new


def main():
    text = PAIRS_TXT.read_text()
    blocks = re.split(r"^### ", text, flags=re.M)[1:]
    pairs, leave = [], []
    for b in blocks:
        head, _, body = b.partition("\n")
        if head.startswith("NOT-REPAIRABLE"):
            leave += [l for l in body.splitlines() if l.startswith("LEAVE ")]
            continue
        fname, lno = head.rsplit(":", 1)
        lines = body.split("\n")
        before = lines[0][len("BEFORE "):] if lines[0].startswith("BEFORE ") else None
        after = lines[1][len("AFTER  "):] if len(lines) > 1 and lines[1].startswith("AFTER  ") else None
        pairs.append((fname, int(lno), before, after))

    bad_before, bad_after, dupes = [], [], []
    seen = set()
    for fname, lno, before, after in pairs:
        key = (fname, lno)
        if key in seen:
            dupes.append(key)
        seen.add(key)
        p = REPO / fname
        live = p.read_text().splitlines()
        actual = live[lno - 1] if 0 < lno <= len(live) else "<NO SUCH LINE>"
        if actual != before:
            bad_before.append((fname, lno, actual[:60], (before or "<none>")[:60]))
        expect = subst(before) if before is not None else "<none>"
        if after != expect:
            bad_after.append((fname, lno, expect[:60], (after or "<none>")[:60]))
        if after is not None and ".shokunin" in after:
            bad_after.append((fname, lno, "<residual .shokunin in AFTER>", after[:60]))

    pair_anchor = {(f, l) for f, l, _, _ in pairs}
    leave_anchor = set()
    for row in leave:
        m = re.match(r"LEAVE (\S+):(\d+) ", row)
        if m:
            leave_anchor.add((m.group(1), int(m.group(2))))

    # independent sweep of the S4 surface
    surface = [REPO / "SCORECARD.md", REPO / "PROVINCE.md"] + sorted(
        p for p in (REPO / "corpus/lessons").glob("*") if p.is_file())
    uncovered = []
    per_class = {}
    for p in surface:
        rel = p.relative_to(REPO).as_posix()
        cls = ("shared" if rel in ("SCORECARD.md", "PROVINCE.md")
               else "lessons." + (p.suffix.lstrip(".") or "none"))
        try:
            lines = p.read_text(errors="replace").splitlines()
        except Exception as e:
            print("READ FAIL", rel, e)
            continue
        for i, line in enumerate(lines, 1):
            if ".shokunin" not in line:
                continue
            key = (rel, i)
            if key in pair_anchor:
                per_class[(cls, "PAIRED")] = per_class.get((cls, "PAIRED"), 0) + 1
            elif key in leave_anchor:
                per_class[(cls, "LEAVE")] = per_class.get((cls, "LEAVE"), 0) + 1
            else:
                kind = "ABS-class" if ABS_ROOT in line else (
                    "rel-corpus" if RULE_C[0] in line else (
                        "rel-reports" if RULE_R[0] in line else "other-shokunin"))
                per_class[(cls, "UNCOVERED:" + kind)] = per_class.get((cls, "UNCOVERED:" + kind), 0) + 1
                uncovered.append((rel, i, kind, line[:100]))

    print("== pair statistics ==")
    print("pairs:", len(pairs), " leave rows:", len(leave),
          " distinct pair files:", len({f for f, _, _, _ in pairs}),
          " duplicate anchors:", len(dupes))
    exts = {}
    for f, _, _, _ in pairs:
        exts[Path(f).suffix] = exts.get(Path(f).suffix, 0) + 1
    print("pair target extensions:", exts)
    print("== BEFORE mismatches:", len(bad_before), "=~")
    for row in bad_before[:20]:
        print("  ", row)
    print("== AFTER mismatches/residuals:", len(bad_after), "=~")
    for row in bad_after[:20]:
        print("  ", row)
    print("== sweep classification (class, verdict) ==")
    for k in sorted(per_class):
        print(f"   {k[0]:14s} {k[1]:22s} {per_class[k]}")
    print("== UNCOVERED rows:", len(uncovered), "=~")
    for rel, i, kind, head in uncovered[:60]:
        print(f"   {rel}:{i} [{kind}] {head}")
    return 0 if not (bad_before or bad_after or dupes) else 1


if __name__ == "__main__":
    sys.exit(main())
