#!/usr/bin/env python3
"""r95-simplifier HEAD/custody check: the landing bytes at the worktree HEAD.

Pins the commit under audit (9cd47507), the sha256 of the three landed files in
the committed tree (git show) and in the worktree, and the sha256 of the two
frozen probe copies the fixtures claim to be byte-identical to. Zero writes to
tracked files; reads only.

Usage: python3 head_check.py > head-check.txt
"""
import hashlib
import subprocess
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
LANDING = "9cd475078dfb8c7df1d394c68d81a1dce14d585b"  # r95 author
FILES = [
    "corpus/fixtures/dss_lattice.gd",
    "corpus/fixtures/r95b_order.gd",
    "corpus/fixtures/run_battery.py",
    "reports/round-95/r95-author.md",
]
FROZEN = [
    ("corpus/live/r95-scout/probes/dss_lattice.gd", "corpus/fixtures/dss_lattice.gd"),
    ("corpus/live/r95-boundary/probes/r95b_order.gd", "corpus/fixtures/r95b_order.gd"),
]


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def git(*args) -> str:
    return subprocess.run(["git", "-C", str(REPO)] + list(args),
                          capture_output=True, text=True, check=True).stdout


def main() -> None:
    head = git("rev-parse", "HEAD").strip()
    print("HEAD: %s" % head)
    print("landing commit under audit: %s" % LANDING)
    print("HEAD == landing: %s" % (head == LANDING))
    print("subject: %s" % git("log", "-1", "--format=%s", LANDING).strip())
    print("worktree dirty (tracked): %r"
          % git("status", "--porcelain", "--untracked-files=no").strip())
    print()
    print("== landed files: committed tree vs worktree ==")
    for rel in FILES:
        committed = subprocess.run(
            ["git", "-C", str(REPO), "show", "%s:%s" % (LANDING, rel)],
            capture_output=True, check=True).stdout
        csha = hashlib.sha256(committed).hexdigest()
        wpath = REPO / rel
        wsha = sha(wpath) if wpath.exists() else "<missing>"
        print("  %-42s committed=%s worktree=%s identical=%s"
              % (rel, csha, wsha, csha == wsha))
    print()
    print("== fixture <-> frozen probe byte identity ==")
    for frozen_rel, fixture_rel in FROZEN:
        fz = REPO / frozen_rel
        fx = REPO / fixture_rel
        fzsha = sha(fz) if fz.exists() else "<missing>"
        fxsha = sha(fx)
        print("  %-44s %s" % (frozen_rel, fzsha))
        print("  %-44s %s  identical=%s" % (fixture_rel, fxsha, fzsha == fxsha))
    print()
    print("== harness citation of the fixture shas ==")
    harness = (REPO / "corpus/fixtures/run_battery.py").read_text().splitlines()
    for i, l in enumerate(harness, 1):
        if "sha256" in l and ("dss_lattice" in l or "r95b_order" in l
                              or "77ae4adb" in l or "4f7e945e" in l):
            print("  line=%-5d %s" % (i, l.strip()))


if __name__ == "__main__":
    main()
