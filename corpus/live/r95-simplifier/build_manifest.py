#!/usr/bin/env python3
"""r95-simplifier receipts manifest.

Covers every artefact under corpus/live/r95-simplifier/ EXCEPT the per-run Godot
scratch trees (fold-runs/*/scratch*, ff-runs/*/scratch) — the r92/r93/r94
precedent: scratch copies are regenerable launch projects, not evidence.
Top-level battery stdout logs and per-run verdicts.json files are included.

Usage: python3 build_manifest.py > MANIFEST.sha256
"""
import hashlib
from pathlib import Path

HERE = Path(__file__).resolve().parent
SKIP_DIRS = {"runs-control1", "runs-control2", "runs-fold-gate", "runs-fold-battery"}
KEEP_IN_SKIP = {"verdicts.json"}


def sha256(p):
    h = hashlib.sha256()
    with p.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def main():
    entries = []
    for p in sorted(HERE.rglob("*")):
        if not p.is_file():
            continue
        rel = p.relative_to(HERE)
        if rel.name == "MANIFEST.sha256":
            continue
        if any(part.startswith("scratch") for part in rel.parts):
            continue
        if rel.parts and rel.parts[0] in SKIP_DIRS and rel.name not in KEEP_IN_SKIP:
            continue
        entries.append((sha256(p), str(rel)))
    for sha, rel in entries:
        print("%s  %s" % (sha, rel))
    print("# files: %d" % len(entries))


if __name__ == "__main__":
    main()
