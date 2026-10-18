#!/usr/bin/env python3
"""r102-S3 focused interleaved A/B: for each volatile row, alternate base/folded
launches (4 reps each, row-major) and print the token value-sets that vary —
inside a tree, and between trees. Reuses the staged scratch trees (same bytes
the sweep ran on). Battery never run.
"""
import importlib.util
import json
import re
import sys

REPO = "/home/vgpnk/Projects/shokunin/game-dev-2d-shokunin"
spec = importlib.util.spec_from_file_location("s3verify", f"{REPO}/reports/round-102/mutations/r102-S3-verify.py")
V = importlib.util.module_from_spec(spec)
spec.loader.exec_module(V)

ROWS = {r["name"]: r for r in json.load(open("/var/tmp/r102-S3/rows.json"))}
TREES = {
    "base": "/var/tmp/r102-S3/scratch/base",
    "fold": "/var/tmp/r102-S3/scratch",  # per-row fold tree chosen below
}
CASES = [
    ("r94_particles_cpu_lifetime", "scratch/particles"),
    ("r94_particles_cpu_expl", "scratch/particles"),
    ("r94_particles_cpu_speed_pre", "scratch/particles"),
    ("r94_particles_cpu_pause", "scratch/particles"),
    ("r95b_order_canon", "scratch/r95"),
    ("r95b_order_celloff_x0", "scratch/r95"),
]
REPS = 4
TOK = re.compile(r"([A-Za-z_][\w]*)=([^\s\]]+)")


def tokens(row_name, out):
    line = next((l for l in out.splitlines() if l.startswith("PASS ")), None)
    if line is None:
        return {}
    d = {}
    for k, val in TOK.findall(line):
        d.setdefault(k, set()).add(val)
    return d


data = {}
for rep in range(REPS):
    for name, foldtree in CASES:
        r = ROWS[name]
        for side, tree in (("base", "/var/tmp/r102-S3/scratch/base"),
                           ("fold", f"/var/tmp/r102-S3/{foldtree}")):
            res = V.run_one(tree, r["fixture"], r["flags"], 25)
            data.setdefault(name, {}).setdefault(side, []).append(res["out"])
            print(f"rep{rep} {name:28s} {side} rc={res['rc']} bytes={len(res['out'])}")

print("\n== token value-set comparison (base vs fold) ==")
for name, _ in CASES:
    sets = {}
    for side in ("base", "fold"):
        d = {}
        for out in data[name][side]:
            for k, vs in tokens(name, out).items():
                d.setdefault(k, set()).update(vs)
        sets[side] = d
    interesting = []
    keys = set(sets["base"]) | set(sets["fold"])
    for k in sorted(keys):
        b, f = sets["base"].get(k, set()), sets["fold"].get(k, set())
        if len(b) > 1 or len(f) > 1 or b != f:
            interesting.append((k, sorted(b), sorted(f)))
    print(f"-- {name}")
    for k, b, f in interesting:
        print(f"   {k}: base{sorted(b)} fold{sorted(f)}")
    if not interesting:
        print("   (every token single-valued and identical across both trees, all reps)")

json.dump({n: d for n, d in data.items()}, open("/var/tmp/r102-S3/res/ab_raw.json", "w"), indent=1)
print("wrote /var/tmp/r102-S3/res/ab_raw.json")
