#!/usr/bin/env python3
"""r87-simplifier: payload-alphabet audit for the 25 new cells across all r87 runs.

For every r87 battery run on disk, collect the distinct PASS payloads of the
new cells and check membership in the CASES whitelist (tuple rows: any-of).
"""
import glob
import json
import sys
from pathlib import Path

ROOT = Path("/home/vgpnk/Projects/shokunin/game-dev-2d-shokunin")
sys.path.insert(0, str(ROOT / "corpus/fixtures"))
import run_battery  # noqa: E402  (imports CASES; main() guarded)

CASES = {c[0]: c[4] for c in run_battery.CASES}
NEW = [c for c in CASES if c.startswith("input_lattice_") or c in ("r87_edge_jpbe", "ei_bound_refusal")]

RUNS = sorted(glob.glob(str(ROOT / "corpus/live/r87-author/runs*/**/verdicts.json"), recursive=True))
RUNS += sorted(glob.glob(str(ROOT / "corpus/live/r87-verifier/runs*/**/verdicts.json"), recursive=True))
RUNS += sorted(glob.glob(str(ROOT / "corpus/live/r87-reviewer/runs-canon/**/verdicts.json"), recursive=True))
RUNS += sorted(glob.glob(str(ROOT / "corpus/live/r87-simplifier/before/**/verdicts.json"), recursive=True))
RUNS += sorted(glob.glob(str(ROOT / "corpus/live/r87-simplifier/after/**/verdicts.json"), recursive=True))

alpha = {c: {} for c in NEW}
for p in RUNS:
    tag = p.split("corpus/live/")[1].split("/verdicts.json")[0]
    d = json.loads(Path(p).read_text())
    for r in d["results"]:
        c = r["case"]
        if c not in alpha:
            continue
        ei_lines = []
        for line in r["output"]:
            if line.startswith("ei="):
                ei_lines.append(line)
                continue
            if ei_lines:
                alpha[c].setdefault("\n".join(ei_lines), set()).add(tag)
                ei_lines = []
            if line.startswith("PASS input_lattice") or line.startswith("PASS r87_edge"):
                alpha[c].setdefault(line, set()).add(tag)
        if ei_lines:
            alpha[c].setdefault("\n".join(ei_lines), set()).add(tag)

bad = []
print(f"runs audited: {len(RUNS)}")
for c in NEW:
    sig = CASES[c]
    allowed = set(sig) if isinstance(sig, (tuple, list)) else {sig}
    payloads = alpha[c]
    offpin = [l for l in payloads if l not in allowed]
    verdict = "OK" if not offpin else "OFF-PIN"
    print(f"{verdict:8} {c:32} distinct={len(payloads)} "
          f"whitelist={len(allowed)} runs={len({t for s in payloads.values() for t in s})}")
    if offpin:
        bad.append(c)
        for l in offpin:
            print("   OFF-PIN:", l[:200])

print("ALPHABET-AUDIT", "PASS" if not bad else f"FAIL {bad}")
