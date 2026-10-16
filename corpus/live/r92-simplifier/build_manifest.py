#!/usr/bin/env python3
"""Build MANIFEST.sha256 for corpus/live/r92-simplifier receipts.

Covers every file under the receipt dir except MANIFEST.sha256 itself,
scratch trees and run snapshot trees (regenerable Godot project copies):
  - fold-runs/*/scratch, */xdg-data, runs-*/**/scratch
"""
import hashlib
from pathlib import Path

HERE = Path(__file__).resolve().parent
SKIP_DIRS = {"scratch", "xdg-data", "missing-preset-scratch", ".godot", "__pycache__"}


def main():
    lines = []
    for p in sorted(HERE.rglob("*")):
        if not p.is_file():
            continue
        if p.name == "MANIFEST.sha256":
            continue
        if any(part in SKIP_DIRS for part in p.relative_to(HERE).parts):
            continue
        digest = hashlib.sha256(p.read_bytes()).hexdigest()
        lines.append("%s  %s" % (digest, p.relative_to(HERE)))
    (HERE / "MANIFEST.sha256").write_text("\n".join(lines) + "\n")
    print("MANIFEST.sha256: %d files" % len(lines))
    print("manifest sha256: %s"
          % hashlib.sha256((HERE / "MANIFEST.sha256").read_bytes()).hexdigest())


if __name__ == "__main__":
    main()
