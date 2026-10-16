#!/usr/bin/env python3
"""r91 verifier — tail-variance vs pin-stability across all battery runs and
fresh-arm receipts. Prints, per nav row, the observed value sets of every tail
field (the fields the row deliberately leaves unpinned)."""
import ast
import glob
import json
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parents[4]
V = ROOT / "corpus/live/r91-verifier"
HARNESS = V / "tree/corpus/fixtures/run_battery.py"

tree = ast.parse(HARNESS.read_text())
cases = None
for node in tree.body:
    if isinstance(node, ast.Assign) and any(
            isinstance(t, ast.Name) and t.id == "CASES" for t in node.targets):
        cases = ast.literal_eval(node.value)
nav = {c[0]: c for c in cases if c[0].startswith("nav_lattice_")}

TAILS = {
    "nav_lattice_path": ["settle=", "iter="],
    "nav_lattice_query": ["settle=", "iter="],
    "nav_lattice_sync": ["dis_same=", "chg_iter_same=", "chg_iter_settled=", "gate=",
                         "ladder=", "first_reach=", "first_reach_sync="],
    "nav_lattice_region": ["dis_same=", "settle=", "iter="],
    "nav_lattice_agent": ["walk_steps=", "reached_at=", "first_reachable="],
    "nav_lattice_avoid": ["seq_a=", "seq_b=", "vel_a=", "vel_b=", "sum_max=", "settle="],
    "nav_lattice_bake": ["iter_b=", "settle_a=", "settle_b="],
    "nav_lattice_link": ["fwd_disabled_same=", "settle=", "iter=", "link_iter="],
}


def tail_fields(line, sig):
    tail = line[len(sig):]
    out = {}
    for tok in tail.split():
        if "=" in tok:
            k, _, v = tok.partition("=")
            out[k + "="] = v
    return out


sources = {}
# battery runs (5)
for p in sorted(glob.glob(str(V / "runs/2026*/verdicts.json"))):
    tag = "run-" + pathlib.Path(p).parent.name[-6:]
    d = json.loads(pathlib.Path(p).read_text())
    for r in d["results"]:
        if r["case"] in nav and r.get("verdict") == "PASS":
            line = next((l for l in r["output"] if l.startswith(r["signature"])), None)
            if line:
                sources.setdefault(r["case"], {})[tag] = tail_fields(line, r["signature"])
# fresh arms
for f in sorted(glob.glob(str(V / "arms/*.rep*.out"))):
    name = pathlib.Path(f).name.split(".")[0]
    case = "nav_lattice_" + name
    if case not in nav:
        continue
    sig = nav[case][4]
    text = pathlib.Path(f).read_text()
    line = next((l for l in text.splitlines() if l.startswith(sig)), None)
    if line:
        sources.setdefault(case, {})["fresh-" + pathlib.Path(f).name] = tail_fields(line, sig)

for case, obs in sources.items():
    if case not in TAILS:
        continue
    print(f"== {case} ({len(obs)} observations) ==")
    for field in TAILS[case]:
        vals = sorted({o.get(field, "<absent>") for o in obs.values()})
        if len(vals) == 1:
            print(f"   {field:22s} constant={vals[0]}")
        else:
            print(f"   {field:22s} n_distinct={len(vals)} values={vals[:8]}")
