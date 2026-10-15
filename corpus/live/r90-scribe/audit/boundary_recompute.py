#!/usr/bin/env python3
"""r90-scribe boundary-dossier recompute (read-only).

  1. receipt census: .out/.err/.rc/.wall counts, rc values, per-batch windows
  2. per-cell pass-line + rc uniqueness across all 82 cells
  3. scout-verbatim cells: byte-identity across base/L1/L2/par tiers (md5 of PASS+LF)
  4. md5 PASS-hash literals quoted in the report (§0/§2/§7)
  5. scout verbatim receipts vs the scout seat's own receipts (cross-seat identity)
  6. 30-tps pairing census (late_body / sync0) from retained receipts
"""
import hashlib
import pathlib
import re
import sys
from collections import Counter

REPO = pathlib.Path("/home/vgpnk/Projects/shokunin/game-dev-2d-shokunin")
B = REPO / "corpus/live/r90-boundary"
S = REPO / "corpus/live/r90-scout"


def pass_line(p):
    for l in p.read_text(errors="replace").splitlines():
        if l.startswith("PASS "):
            return l
    return None


def md5pass(p):
    pl = pass_line(p)
    return hashlib.md5((pl + "\n").encode()).hexdigest() if pl else None


def main() -> int:
    runs = B / "runs"
    outs = sorted(runs.glob("*.out"))
    errs = sorted(runs.glob("*.err"))
    rcs = sorted(runs.glob("*.rc"))
    walls = sorted(runs.glob("*.wall"))
    print(f"1. receipts out={len(outs)} err={len(errs)} rc={len(rcs)} wall={len(walls)}")
    print(f"   rc values: {Counter(r.read_text().strip() for r in rcs)}")
    print(f"   max wall: {max(float(w.read_text()) for w in walls):.2f}s")

    cells = {}
    for o in outs:
        cells.setdefault(o.name.split(".rep")[0], []).append(o)
    unstable = []
    for c, reps in sorted(cells.items()):
        sigs = {pass_line(p) for p in reps}
        rcv = {(p.with_suffix('.rc')).read_text().strip() for p in reps}
        if len(sigs) != 1 or len(rcv) != 1:
            unstable.append(c)
    print(f"2. cells={len(cells)} pass_or_rc_unstable={unstable}")

    groups = {}
    for o in outs:
        m = re.match(r"(l_|l2_|p_)?(sv_[a-z0-9_]+)\.rep\d+\.out$", o.name)
        if m:
            groups.setdefault(m.group(2), []).append(o)
    bad = 0
    for c, reps in sorted(groups.items()):
        hashes = {md5pass(p) for p in reps}
        if len(hashes) != 1:
            bad += 1
        print(f"3. {c:26s} reps={len(reps):2d} unique_pass_md5={len(hashes)}")
    print(f"   sv cells with >1 hash: {bad}")

    targets = {"764c523cd0c9": "sv_order", "3b6250190357": "sv_freezelock",
               "0c9cecc3d1ee": "sv_contacts"}
    for h, cell in targets.items():
        hits = [p.name for p in (runs.glob(f"{cell}.rep*.out")) if (md5pass(p) or "").startswith(h)]
        print(f"4. quoted hash {h}… -> {cell}: {len(hits)}/3 receipts match (md5 PASS-line+LF)")

    pairs = [("sv_order", "rb_order"), ("sv_damp", "rb_damp"), ("sv_write", "rb_write"),
             ("sv_impulse", "rb_impulse"), ("sv_comrefuse", "rb_comrefuse"),
             ("sv_freezelock", "rb_freezelock"), ("sv_contacts", "rb_contacts"),
             ("sv_gravity", "rb_gravity"), ("sv_gravity_t120", "rb_tps120_f120")]
    for bcell, scell in pairs:
        b = pass_line(runs / f"{bcell}.rep1.out")
        s = pass_line(S / "runs" / f"{scell}.rep1.out")
        print(f"5. {bcell:20s} == scout {scell:14s}: {b == s}")

    pairings = Counter()
    for o in outs:
        pl = pass_line(o)
        if not pl or "cb0_rel=" not in pl:
            continue
        m = re.search(r"cb0_rel=(-?\d+) obs0_rel=(-?\d+)", pl)
        if m:
            pairings[m.group(0)] += 1
    print(f"6. cb0_rel/obs0_rel census over all receipts: {dict(pairings)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
