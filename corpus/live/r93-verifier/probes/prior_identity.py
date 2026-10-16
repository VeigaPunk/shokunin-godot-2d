#!/usr/bin/env python3
"""r93 verifier — battery row identity / stability across reps.

Compares every completed battery rep (this seat's runs/*/verdicts.json) with the
author's two green runs and the r92 verifier's two greens, at two granularities:

  pin-shape   (verdict, actual_exit, error, signature byte-present in output)
              — the meaningful identity for both full-line and clause pins
  strict      (verdict, actual_exit, error, full PASS line)
              — expected to differ on the deliberately unpinned mode tails

Also reports per-row pin-shape stability across this seat's reps and the
observed r93 PASS line vs the committed signature.
"""
import ast
import json
import pathlib
import re
import sys
from collections import defaultdict

REPO = pathlib.Path("/home/vgpnk/Projects/shokunin/game-dev-2d-shokunin")
V = REPO / "corpus" / "live" / "r93-verifier"
OUT = []


def p(s=""):
    OUT.append(str(s))


def load(path):
    d = json.loads(pathlib.Path(path).read_text())
    return {r["case"]: r for r in d["results"]}, d["verdict"]


def lines_of(r):
    out = r.get("output") or []
    return out if isinstance(out, list) else out.splitlines()


def sigs_of(r):
    sig = r.get("signature")
    if isinstance(sig, list):
        return tuple(sig)
    return (sig,)


def pin_shape(r):
    if "actual_exit" not in r:
        return ("META", r.get("verdict"), r.get("error"))
    present = tuple(s in "\n".join(lines_of(r)) for s in sigs_of(r))
    return (r["verdict"], r["actual_exit"], r["error"], present)


def strict_shape(r):
    if "actual_exit" not in r:
        return ("META", r.get("verdict"), r.get("error"))
    m = [ln for ln in lines_of(r) if ln.startswith("PASS ")]
    return (r["verdict"], r["actual_exit"], r["error"], m[0] if len(m) == 1 else tuple(m))


mine = []
for run in sorted((V / "runs").glob("*/verdicts.json")):
    rows, verdict = load(run)
    mine.append((run.parent.name, verdict, rows))

p(f"this seat's completed battery reps: {len(mine)}")
for stamp, verdict, rows in mine:
    bad = sorted(c for c, r in rows.items() if r["verdict"] != "PASS")
    r93 = [c for c in rows if c.startswith("r93_")]
    p(f"  {stamp}: verdict={verdict} rows={len(rows)} r93_pass={sum(1 for c in r93 if rows[c]['verdict']=='PASS')}/{len(r93)} failing={bad}")

auth = {}
for name in ("runs1", "runs2", "runs3"):
    for run in sorted((REPO / "corpus/live/r93-author" / name).glob("*/verdicts.json")):
        rows, verdict = load(run)
        auth[name] = (verdict, rows)
p("")
p("--- author runs ---")
for name, (verdict, rows) in auth.items():
    bad = sorted(c for c, r in rows.items() if r["verdict"] != "PASS")
    p(f"  {name}: verdict={verdict} rows={len(rows)} failing={bad}")

p("")
p("--- pin-shape identity vs author greens ---")
for stamp, verdict, rows in mine:
    for aname in ("runs1", "runs3"):
        arows = auth[aname][1]
        diff = [c for c in sorted(set(rows) | set(arows))
                if c not in rows or c not in arows or pin_shape(rows[c]) != pin_shape(arows[c])]
        p(f"  {stamp} vs {aname}: pin-shape mismatches={len(diff)} {diff[:12]}")

p("")
p("--- strict-shape identity vs author greens (mode tails allowed to differ) ---")
for stamp, verdict, rows in mine:
    for aname in ("runs1", "runs3"):
        arows = auth[aname][1]
        diff = [c for c in sorted(set(rows) | set(arows))
                if c not in rows or c not in arows or strict_shape(rows[c]) != strict_shape(arows[c])]
        r93diff = [c for c in diff if c.startswith("r93_")]
        p(f"  {stamp} vs {aname}: strict mismatches={len(diff)} (r93 of them: {len(r93diff)})")

p("")
p("--- r93 strict mismatches vs the author greens, row by row ---")
for stamp, verdict, rows in mine:
    for aname in ("runs1", "runs3"):
        arows = auth[aname][1]
        for c in sorted(rows):
            if not c.startswith("r93_"):
                continue
            if c in arows and strict_shape(rows[c]) != strict_shape(arows[c]):
                p(f"  {stamp} vs {aname}: {c}")

p("")
p("--- pre-existing rows: pin-shape vs r92 verifier greens ---")
r92 = []
for run in sorted((REPO / "corpus/live/r92-verifier/runs").glob("*/verdicts.json")):
    rows, verdict = load(run)
    if verdict == "PASS":
        r92.append((run.parent.name, rows))
for stamp, verdict, rows in mine:
    for r92stamp, r92rows in r92:
        diff = [c for c, r in rows.items() if not c.startswith("r93_")
                and (c not in r92rows or pin_shape(r) != pin_shape(r92rows[c]))]
        p(f"  {stamp} vs r92green {r92stamp}: pre-existing pin-shape mismatches={len(diff)} {sorted(diff)[:10]}")

p("")
p("--- per-row pin-shape stability across this seat's reps ---")
shapes = defaultdict(set)
for stamp, verdict, rows in mine:
    for case, r in rows.items():
        shapes[case].add(pin_shape(r))
unstable = sorted(c for c, s in shapes.items() if len(s) > 1)
p(f"  rows with >1 pin-shape: {len(unstable)} of {len(shapes)} {unstable}")

# r93 observed PASS line vs committed signature
src = (V / "freeze/x/corpus/fixtures/run_battery.py").read_text()
tree = ast.parse(src)
for node in ast.walk(tree):
    if isinstance(node, ast.Assign) and getattr(node.targets[0], "id", "") == "CASES":
        cases = node.value.elts
        break
meta = {ast.literal_eval(e)[0]: ast.literal_eval(e) for e in cases}
p("")
p("--- r93 observed PASS line vs committed signature (per rep) ---")
for stamp, verdict, rows in mine:
    exact = tail = missing = 0
    for case, r in rows.items():
        if not case.startswith("r93_"):
            continue
        sig = meta[case][4]
        obs = next((ln for ln in lines_of(r) if sig in ln), None)
        if obs is None:
            missing += 1
        elif obs == sig:
            exact += 1
        else:
            tail += 1
    p(f"  {stamp}: full-line-equal={exact} clause-contains={tail} missing={missing}")

(V / "probes" / "prior-identity.txt").write_text("\n".join(OUT) + "\n")
print("\n".join(OUT))
sys.exit(0)
