#!/usr/bin/env python3
"""r93 verifier — receipts manifest.

Covers every file under corpus/live/r93-verifier/ EXCEPT the declared scratch
trees (byte-copies of the frozen fixtures or per-run battery scratch):

  freeze/x/**                     frozen `git archive HEAD corpus/fixtures` tree
  arms/proj/**                    scratch project copy of the frozen fixtures
  gate-probe/mutant/**            mutant harness tree (scratch copy + one edit)
  **/scratch/**                   battery per-run scratch project
  **/xdg-data/**                  battery per-run user:// isolation dir
  **/missing-preset-scratch/**

Scope header is line 1 of manifest.sha256; the manifest itself is excluded.
"""
import hashlib
import pathlib
import sys

V = pathlib.Path("/home/vgpnk/Projects/shokunin/game-dev-2d-shokunin/corpus/live/r93-verifier")
SCRATCH = ("/scratch/", "/xdg-data/", "/missing-preset-scratch/")
PREFIX = ("freeze/x/", "arms/proj/", "gate-probe/mutant/")


def excluded(r):
    if r.startswith(PREFIX):
        return True
    return any(s in r for s in SCRATCH)


files = []
for p in sorted(V.rglob("*")):
    if not p.is_file():
        continue
    r = str(p.relative_to(V))
    if r == "manifest.sha256" or excluded(r):
        continue
    files.append((r, p))

lines = ["# scope: every file under corpus/live/r93-verifier except the declared scratch trees "
         "freeze/x/ arms/proj/ gate-probe/mutant/ and **/{scratch,xdg-data,missing-preset-scratch}/ "
         "and manifest.sha256 itself"]
for r, p in files:
    lines.append(f"{hashlib.sha256(p.read_bytes()).hexdigest()}  {r}")
(V / "manifest.sha256").write_text("\n".join(lines) + "\n")
print(f"manifest entries={len(files)}")
sys.exit(0)
