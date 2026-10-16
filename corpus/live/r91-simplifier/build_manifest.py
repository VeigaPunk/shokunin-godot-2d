#!/usr/bin/env python3
"""Build MANIFEST.sha256 over this seat's receipt corpus.

Excluded (regenerable snapshot/run copies, r90-simplifier precedent):
  fold-scratch/**, **/scratch/**, **/missing-preset-scratch/**, **/xdg-data/**,
  **/__pycache__/**, MANIFEST.sha256 itself.
Everything else — scripts, receipts, battery verdicts.json, stdout logs, the
committed-fixture snapshot and the folded proposal tree — is covered.
"""
import hashlib
from pathlib import Path

HERE = Path(__file__).resolve().parent
SKIP_DIRS = {"fold-scratch", "scratch", "missing-preset-scratch", "xdg-data",
             "__pycache__"}
SKIP_NAMES = {"MANIFEST.sha256"}

rows = []
for p in sorted(HERE.rglob("*")):
    if not p.is_file():
        continue
    rel = p.relative_to(HERE)
    if any(part in SKIP_DIRS for part in rel.parts):
        continue
    if p.name in SKIP_NAMES:
        continue
    rows.append((str(rel), hashlib.sha256(p.read_bytes()).hexdigest()))

out = HERE / "MANIFEST.sha256"
out.write_text("".join("%s  %s\n" % (sha, rel) for rel, sha in rows))
total = hashlib.sha256(out.read_bytes()).hexdigest()
print("manifest: %d files, sha256 %s" % (len(rows), total))
print("excluded dirs: %s" % ", ".join(sorted(SKIP_DIRS)))
