#!/usr/bin/env python3
"""r94-simplifier receipts manifest.

Covers every artefact under corpus/live/r94-simplifier/ EXCEPT the per-run Godot
scratch trees (runs-*/<stamp>/scratch, fold-runs/.../scratch*) — the r92/r93
precedent: scratch copies are regenerable launch projects, not evidence.
Top-level battery stdout logs and per-run verdicts.json files are included.

Usage: python3 build_manifest.py > MANIFEST.sha256
"""
import hashlib
from pathlib import Path

HERE = Path(__file__).resolve().parent
SKIP_DIRS = {"runs-control1", "runs-control2", "runs-fold-gate", "runs-fold-candidates"}
SKIP_PARTS = {"scratch"}


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
        if rel.parts and rel.parts[0] in SKIP_DIRS:
            # keep the verdicts.json / stdout of a run, drop the scratch tree
            if not (rel.name == "verdicts.json" or rel.name.endswith(".stdout")
                    or rel.name == "fold-verification.json"):
                continue
        if any(part.startswith("scratch") for part in rel.parts):
            continue
        entries.append((sha256(p), str(rel)))
    for sha, rel in entries:
        print("%s  %s" % (sha, rel))
    print("# files: %d" % len(entries))


if __name__ == "__main__":
    main()
