#!/usr/bin/env python3
"""r101 SIMP-1 patch generator: emit ready-to-apply unified diffs (git -p1 paths)."""
from __future__ import annotations

import difflib
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import simp1  # noqa: E402

OUT = simp1.REPO / "reports" / "round-101" / "mutations"

SETS = {
    "r91-nav_lattice": ("f_nav", ["nav_lattice.gd"]),
    "r98-canvas_lattice": ("f_canvas", ["canvas_lattice.gd"]),
    "r98-r98b_attack": ("f_attack", ["r98b_attack.gd"]),
    "r98-r98b_rksenum": ("f_rksenum", ["r98b_rksenum.gd"]),
    "r99-audio_lattice": ("f_audio", ["audio_lattice.gd"]),
}


def diff_one(fname: str, folded_tree: str) -> str:
    base = (simp1.WORK / "trees" / "base" / fname).read_text().splitlines(keepends=True)
    fold = (simp1.WORK / "trees" / folded_tree / fname).read_text().splitlines(keepends=True)
    return "".join(difflib.unified_diff(
        base, fold,
        fromfile="a/corpus/fixtures/" + fname,
        tofile="b/corpus/fixtures/" + fname,
        n=3))


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    all_text = []
    for key, (tree, files) in SETS.items():
        text = "".join(diff_one(f, tree) for f in files)
        p = OUT / ("r101-simp1-%s.patch" % key)
        p.write_text(text)
        all_text.append(text)
        print(p, len(text.splitlines()), "lines")
    combined = "".join(diff_one(f, "f_all") for f in
                       ["nav_lattice.gd", "canvas_lattice.gd", "r98b_attack.gd", "r98b_rksenum.gd",
                        "audio_lattice.gd"])
    p = OUT / "r101-simp1-all.patch"
    p.write_text(combined)
    print(p, len(combined.splitlines()), "lines")
    # line census
    for f in ["nav_lattice.gd", "canvas_lattice.gd", "r98b_attack.gd", "r98b_rksenum.gd", "audio_lattice.gd"]:
        b = len((simp1.WORK / "trees" / "base" / f).read_text().splitlines())
        a = len((simp1.WORK / "trees" / "f_all" / f).read_text().splitlines())
        print("%-20s base=%d folded=%d delta=%d" % (f, b, a, a - b))


if __name__ == "__main__":
    main()
