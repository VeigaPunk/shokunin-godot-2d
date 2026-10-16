#!/usr/bin/env python3
"""r93 verifier — signature coverage over the committed r93 measurement corpora.

For every committed r93 row, every line-anchored `PASS <stem> <arm> ` receipt in
the r93-scout, r93-boundary and r93-author corpora (plus this seat's fresh arms)
must contain the row's signature byte-exactly; full-line pins must equal the
whole line. Also counts cross-arm hits (a signature appearing in a receipt of a
different arm) — the forgeability question.
"""
import ast
import pathlib
import re
import sys
from collections import defaultdict

REPO = pathlib.Path("/home/vgpnk/Projects/shokunin/game-dev-2d-shokunin")
V = REPO / "corpus" / "live" / "r93-verifier"
FIX = V / "freeze" / "x" / "corpus" / "fixtures"

src = (FIX / "run_battery.py").read_text()
tree = ast.parse(src)
cases = None
for node in ast.walk(tree):
    if isinstance(node, ast.Assign) and getattr(node.targets[0], "id", "") == "CASES":
        cases = node.value.elts
        break
rows = [ast.literal_eval(e) for e in cases if ast.literal_eval(e)[0].startswith("r93_")]

CORPORA = [
    REPO / "corpus" / "live" / "r93-scout" / "runs",
    REPO / "corpus" / "live" / "r93-boundary" / "runs",
    REPO / "corpus" / "live" / "r93-author" / "fresh-reps",
    V / "arms",
]

lines = []
receipts = []  # (path, pass_line)
for corpus in CORPORA:
    if not corpus.is_dir():
        continue
    for p in sorted(corpus.rglob("*.out")):
        if "proj" in p.parts:
            continue
        for ln in p.read_text(errors="replace").splitlines():
            if re.match(r"^PASS (anim_lattice|r93b_anim) ", ln):
                receipts.append((p, ln))

lines.append(f"receipts with a PASS line: {len(receipts)}")
by_arm = defaultdict(int)
for p, ln in receipts:
    m = re.match(r"^PASS (\S+) (\S+) ", ln)
    by_arm[f"{m.group(1)}.{m.group(2)}"] += 1
for k in sorted(by_arm):
    lines.append(f"  arm {k:24s} receipts={by_arm[k]}")

# arm -> pass lines
arm_lines = defaultdict(list)
for p, ln in receipts:
    m = re.match(r"^PASS (\S+) (\S+) ", ln)
    arm_lines[f"{m.group(1)}.{m.group(2)}"].append((p, ln))

lines.append("")
lines.append("--- per-row coverage ---")
total = {"EXACT": 0, "TAIL": 0, "MISS": 0}
for r in rows:
    name, script, flags, sig = r[0], r[1], r[2], r[4]
    arm = f"{script[:-3]}.{flags[0].split('=', 1)[1]}"
    exact = tail = miss = 0
    for p, ln in arm_lines[arm]:
        if ln == sig:
            exact += 1
        elif sig in ln:
            tail += 1
        else:
            miss += 1
    total["EXACT"] += exact
    total["TAIL"] += tail
    total["MISS"] += miss
    lines.append(f"  {name:36s} arm={arm:22s} receipts={len(arm_lines[arm]):4d} exact={exact:4d} tail={tail:4d} miss={miss:4d}")

lines.append("")
lines.append(f"totals: EXACT={total['EXACT']} TAIL={total['TAIL']} MISS={total['MISS']}")

# cross-arm hits: signature appears in a PASS line of a different arm
lines.append("")
lines.append("--- cross-arm hits (signature in a foreign arm's PASS line) ---")
cross = 0
for r in rows:
    name, script, flags, sig = r[0], r[1], r[2], r[4]
    own = f"{script[:-3]}.{flags[0].split('=', 1)[1]}"
    hits = defaultdict(int)
    for arm, lst in arm_lines.items():
        if arm == own:
            continue
        for p, ln in lst:
            if sig in ln:
                hits[arm] += 1
    if hits:
        cross += 1
        lines.append(f"  {name}: " + ", ".join(f"{a}={n}" for a, n in sorted(hits.items())))
if not cross:
    lines.append("  none")

# fallback-forgery check: does any signature match the unknown-arm fallback?
lines.append("")
lines.append("--- unknown-arm fallback lines in the corpora ---")
fb = sorted({ln for p, ln in receipts if "unknown arm=" in ln})
lines.append(f"  fallback PASS lines={len(fb)}")
for ln in fb[:5]:
    lines.append(f"    {ln!r}")
for r in rows:
    if r[4] in "\n".join(fb):
        lines.append(f"  !! signature of {r[0]} matches a fallback line")

(V / "probes" / "signature-coverage.txt").write_text("\n".join(lines) + "\n")
print("\n".join(lines))
sys.exit(0)
