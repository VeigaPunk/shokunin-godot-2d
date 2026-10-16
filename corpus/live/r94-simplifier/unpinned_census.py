#!/usr/bin/env python3
"""r94-simplifier unpinned-tail census.

For every r94 row: take the committed signature (the pinned prefix), strip it
from every receipt line that carries it across the whole r94 receipt corpus
(scout canonical/loadtest, boundary 6 conditions, author battery runs), and
record the remaining tail verbatim — the deliberately unpinned measurement
surface. Also checks the converse: that nothing BEFORE the signature boundary
varies (i.e. the pinned block itself is byte-stable).

Usage: python3 unpinned_census.py > unpinned-census.txt
"""
import ast
import json
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent.parent
HARNESS = HERE / "committed-fixtures" / "run_battery.py"


def load_cases():
    src = HARNESS.read_text()
    tree = ast.parse(src)
    cases = {}
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign) and getattr(node.targets[0], "id", "") == "CASES":
            for elt in node.value.elts:
                t = ast.literal_eval(elt)
                cases[t[0]] = {"script": t[1], "flags": t[2], "exit": t[3], "sig": t[4]}
    return {k: v for k, v in cases.items() if k.startswith("r94_")}


def lines_for(case):
    out = []
    for p in sorted((REPO / "corpus/live/r94-scout/runs").rglob("r94_particles_%s.rep*.out" % case.split("r94_particles_")[1])):
        out.append(("scout/" + p.parent.name, p.read_text(errors="replace")))
    for p in sorted((REPO / "corpus/live/r94-boundary/runs").rglob("%s.rep*.out" % case)):
        out.append(("boundary/" + p.parent.name, p.read_text(errors="replace")))
    for stamp in ["20261016T055703426158Z", "20261016T060430025246Z"]:
        vp = REPO / "corpus/live/runs" / stamp / "verdicts.json"
        if vp.is_file():
            d = json.loads(vp.read_text())
            for r in d["results"]:
                if r["case"] == case:
                    out.append(("battery/" + stamp, "\n".join(r["output"])))
    return out


def main():
    cases = load_cases()
    for case, row in sorted(cases.items()):
        sig = row["sig"]
        tails = {}
        prefix_varies = []
        n = 0
        for src, text in lines_for(case):
            for line in text.splitlines():
                if sig not in line:
                    continue
                n += 1
                tail = line.split(sig, 1)[1]
                tails.setdefault(tail, []).append(src)
        print("== %s" % case)
        print("   receipts carrying the signature: %d  distinct tails: %d" % (n, len(tails)))
        for tail, srcs in sorted(tails.items(), key=lambda kv: -len(kv[1])):
            print("     [%2d] %s" % (len(srcs), (tail[:180] + "…") if len(tail) > 180 else tail))
        print()


if __name__ == "__main__":
    main()
