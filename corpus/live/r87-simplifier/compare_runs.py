#!/usr/bin/env python3
"""r87-simplifier: before/after battery verdict-tuple + output compare.

Reuses the r79-baseline differ's row definitions (godot_tuple / norm).
Writes receipts: tuples-before.txt, tuples-after.txt, compare.txt
"""
import glob
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path("/home/vgpnk/Projects/shokunin/game-dev-2d-shokunin")
sys.path.insert(0, str(ROOT / "corpus/live/r87-baseline"))
from compare import godot_tuple, godot_output_norm  # noqa: E402

OUT = ROOT / "corpus/live/r87-simplifier/receipts"
OUT.mkdir(exist_ok=True)

before_p = sorted(glob.glob(str(ROOT / "corpus/live/r87-simplifier/before/*/verdicts.json")))[-1]
after_p = sorted(glob.glob(str(ROOT / "corpus/live/r87-simplifier/after/*/verdicts.json")))[-1]
B = json.loads(Path(before_p).read_text())
A = json.loads(Path(after_p).read_text())
b = {r["case"]: r for r in B["results"]}
a = {r["case"]: r for r in A["results"]}

BIMODAL = {"input_lattice_api_press", "input_lattice_press_phys", "input_lattice_release_edge",
           "input_lattice_ui_ns", "input_lattice_pre_frame"}

common = sorted(set(b) & set(a))
mism, out_diff, out_same, out_missing = [], [], 0, 0
lines = []
for c in common:
    tb, ta = godot_tuple(b[c]), godot_tuple(a[c])
    if tb != ta:
        mism.append(c)
    ob, oa = godot_output_norm(b[c]), godot_output_norm(a[c])
    if ob is None or oa is None:
        out_missing += 1
    elif ob == oa:
        out_same += 1
    else:
        out_diff.append(c)

lines.append(f"before={before_p} verdict={B['verdict']} rows={len(B['results'])}")
lines.append(f"after ={after_p} verdict={A['verdict']} rows={len(A['results'])}")
lines.append(f"common={len(common)} new_only={sorted(set(a)-set(b))} old_only={sorted(set(b)-set(a))}")
lines.append(f"tuple_mismatches={len(mism)} {mism}")
lines.append(f"output-normalized identical={out_same} differing={out_diff} not-carried={out_missing}")

for c in mism:
    lines.append(f"--- TUPLE-MISMATCH {c}")
    keys = sorted(set(b[c]) | set(a[c]))
    for k in keys:
        if b[c].get(k) != a[c].get(k) and k not in ("command", "xdg_data_home", "artifact"):
            lines.append(f"    {k}: BEFORE={str(b[c].get(k))[:300]}")
            lines.append(f"    {k}: AFTER ={str(a[c].get(k))[:300]}")

# byte-level payload compare for the 25 new cells
NEW = [c for c in common if c.startswith("input_lattice_") or c in ("r87_edge_jpbe", "ei_bound_refusal")]
lines.append(f"\nnew cells: {len(NEW)}")
for c in NEW:
    ob, oa = godot_output_norm(b[c]), godot_output_norm(a[c])
    payload_b = [l for l in (ob or "").splitlines() if l.startswith(("PASS input_lattice", "PASS r87_edge", "ei="))]
    payload_a = [l for l in (oa or "").splitlines() if l.startswith(("PASS input_lattice", "PASS r87_edge", "ei="))]
    tag = "SAME" if payload_b == payload_a else ("BIMODAL-OK" if c in BIMODAL else "DIFF")
    lines.append(f"{tag} {c}: before_verdict={b[c]['verdict']} after_verdict={a[c]['verdict']} "
                 f"payload_equal={payload_b == payload_a}")
    if payload_b != payload_a and c not in BIMODAL:
        for x in payload_b:
            if x not in payload_a:
                lines.append(f"    only-before: {x[:200]}")
        for x in payload_a:
            if x not in payload_b:
                lines.append(f"    only-after : {x[:200]}")

# tuple sets for diffing
for name, d in (("before", b), ("after", a)):
    p = OUT / f"tuples-{name}.txt"
    p.write_text("\n".join(json.dumps([c, godot_tuple(d[c])], sort_keys=True) for c in sorted(d)) + "\n")
    lines.append(f"tuples-{name}.txt sha256={hashlib.sha256(p.read_bytes()).hexdigest()}")

(OUT / "compare.txt").write_text("\n".join(lines) + "\n")
print("\n".join(lines))
