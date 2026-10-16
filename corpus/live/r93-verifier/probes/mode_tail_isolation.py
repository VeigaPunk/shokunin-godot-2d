#!/usr/bin/env python3
"""r93 verifier — mode-tail isolation.

For every arm, compare this seat's fresh PASS line with the author's tracked
receipt for the same arm/rep, split both into `field=...` chunks, and list the
differing fields.  Then check that no differing field name occurs inside any r93
signature pinned on that arm: pinned content must be byte-stable while the
unpinned tails carry the run-to-run variation.
"""
import ast
import pathlib
import re
import sys

REPO = pathlib.Path("/home/vgpnk/Projects/shokunin/game-dev-2d-shokunin")
V = REPO / "corpus" / "live" / "r93-verifier"
A = REPO / "corpus" / "live" / "r93-author" / "fresh-reps"
FIX = V / "freeze" / "x" / "corpus" / "fixtures"

src = (FIX / "run_battery.py").read_text()
tree = ast.parse(src)
cases = None
for node in ast.walk(tree):
    if isinstance(node, ast.Assign) and getattr(node.targets[0], "id", "") == "CASES":
        cases = node.value.elts
        break
rows = [ast.literal_eval(e) for e in cases if ast.literal_eval(e)[0].startswith("r93_")]

FIELD = re.compile(r"(?<![A-Za-z0-9_])([a-z_0-9]+)=")


def fields(text):
    """split a PASS line into field chunks keyed by field name"""
    chunks = re.split(r"(?<=\s)(?=[a-z_0-9]+=)", text)
    out = {}
    for c in chunks:
        m = FIELD.match(c)
        if m:
            out.setdefault(m.group(1), []).append(c)
    return out


lines = []
violations = 0
for row in rows:
    name, script, flags, sig = row[0], row[1], row[2], row[4]
    stem, arm = script[:-3], flags[0].split("=", 1)[1]
    sig_fields = {m.group(1) for m in FIELD.finditer(sig)}
    for rep in (1, 2, 3):
        mine = V / "arms" / f"{stem}.{arm}.rep{rep}.out"
        auth = A / f"{stem}.{arm}.rep{rep}.out"
        if not (mine.is_file() and auth.is_file()):
            continue
        mline = [ln for ln in mine.read_text().splitlines() if ln.startswith("PASS ")]
        aline = [ln for ln in auth.read_text().splitlines() if ln.startswith("PASS ")]
        if len(mline) != 1 or len(aline) != 1:
            continue
        mf, af = fields(mline[0]), fields(aline[0])
        diff = {k for k in set(mf) | set(af) if mf.get(k) != af.get(k)}
        # a differing field is only a violation if the pinned substring itself
        # is not byte-present in both receipts (sub-field granularity: the await
        # row pins a prefix of `idle=[...]` and its tail is a mode)
        overlap = {k for k in diff & sig_fields
                   if not (sig in mline[0] and sig in aline[0])}
        if overlap:
            violations += 1
        if diff or overlap:
            lines.append(f"{name} rep{rep}: differing_fields={sorted(diff)} "
                         f"pinned_fields={sorted(sig_fields)} OVERLAP={sorted(overlap)}")

lines.append("")
lines.append(f"rows×reps with differing fields: {len(lines) - 1}; pinned/foreign overlap violations: {violations}")
(V / "probes" / "mode-tail-isolation.txt").write_text("\n".join(lines) + "\n")
print("\n".join(lines))
sys.exit(0 if violations == 0 else 1)
