#!/usr/bin/env python3
"""r93-reviewer: build corpus/live/r93-reviewer/manifest.sha256 over every
artefact under the seat directory (excluding the manifest itself)."""
import hashlib
import pathlib

HERE = pathlib.Path(__file__).resolve().parent.parent


def main():
    entries = []
    for f in sorted(HERE.rglob("*")):
        if not f.is_file():
            continue
        if f.name == "manifest.sha256":
            continue
        rel = "./" + str(f.relative_to(HERE))
        entries.append(f"{hashlib.sha256(f.read_bytes()).hexdigest()}  {rel}")
    out = HERE / "manifest.sha256"
    out.write_text("\n".join(entries) + "\n")
    print(f"{len(entries)} entries -> {out}")


if __name__ == "__main__":
    main()
