#!/usr/bin/env python3
"""Build MANIFEST.sha256 for corpus/live/r93-simplifier.

Excludes transient Godot scratch trees (scratch/, missing-preset-scratch/,
.godot/, xdg-data/, out/) and __pycache__; covers scripts, receipts, the
committed snapshot, the folded harness and the launch projects.

Usage: python3 build_manifest.py
"""
import hashlib
from pathlib import Path

HERE = Path(__file__).resolve().parent
SKIP_DIRS = {"scratch", "missing-preset-scratch", ".godot", "xdg-data", "out",
             "__pycache__"}
SKIP_SUFFIX = (".pyc",)


def main():
    entries = []
    for p in sorted(HERE.rglob("*")):
        if p.is_dir():
            continue
        rel = p.relative_to(HERE)
        if any(part in SKIP_DIRS for part in rel.parts):
            continue
        if p.name.endswith(SKIP_SUFFIX):
            continue
        if p.name == "MANIFEST.sha256":
            continue
        # per-run launch-project copies are byte-copies of proj/ (skipped;
        # proj/ itself is covered)
        if len(rel.parts) >= 3 and rel.parts[0] == "fold-runs" and rel.parts[2] == "proj":
            continue
        h = hashlib.sha256(p.read_bytes()).hexdigest()
        entries.append((str(rel), h))
    out = HERE / "MANIFEST.sha256"
    out.write_text("".join("%s  %s\n" % (h, rel) for rel, h in entries))
    print("manifest entries: %d" % len(entries))
    print("manifest sha256: %s"
          % hashlib.sha256(out.read_bytes()).hexdigest())


if __name__ == "__main__":
    main()
