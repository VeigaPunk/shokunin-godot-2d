#!/usr/bin/env python3
"""r92 verifier — receipts manifest.

sha256 over every seat receipt under corpus/live/r92-verifier/, excluding the
three regenerable scratch trees (frozen extraction `tree/`, launch project
`arms/proj/`, and the battery's per-run scratch/xdg-data/missing-preset dirs).
The exclusion set is printed at the top so the manifest's scope is auditable.
"""
import hashlib
import pathlib

V = pathlib.Path("/home/vgpnk/Projects/shokunin/game-dev-2d-shokunin/corpus/live/r92-verifier")
EXCLUDE_DIRS = ("tree", "arms/proj")
EXCLUDE_PARTS = ("scratch", "xdg-data", "missing-preset-scratch", "__pycache__")
EXCLUDE_NAMES = {"manifest.sha256"}

lines = []
n_excl = 0
for path in sorted(V.rglob("*")):
    rel = path.relative_to(V)
    if not path.is_file():
        continue
    if any(str(rel).startswith(d + "/") for d in EXCLUDE_DIRS):
        n_excl += 1
        continue
    if set(rel.parts) & set(EXCLUDE_PARTS):
        n_excl += 1
        continue
    if rel.name in EXCLUDE_NAMES:
        continue
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    lines.append(f"{digest}  {rel}")

header = [
    "# scope: every receipt under corpus/live/r92-verifier/ EXCEPT the regenerable",
    "#        scratch trees: tree/ (frozen extraction of 5900431's corpus/fixtures),",
    "#        arms/proj/ (launch project copy), and any runs/*/{scratch,xdg-data,",
    "#        missing-preset-scratch}/ battery scratch.",
    f"# excluded files: {n_excl}",
    f"# covered files: {len(lines)}",
]
out = V / "manifest.sha256"
out.write_text("\n".join(header + lines) + "\n")
print("\n".join(header))
