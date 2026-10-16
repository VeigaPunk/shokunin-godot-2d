#!/usr/bin/env python3
"""r94-simplifier signature-head check.

Confirms (a) the CASES table has no duplicate case names, (b) the census
signature is byte-equal to the full emitted line, and (c) every r94 signature
is a unique contiguous head of the corresponding scout canonical rep1 line
(the author's H1, re-checked independently).

Usage: python3 head_check.py > head-check.txt
"""
import ast
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent.parent
HARNESS = HERE / "committed-fixtures" / "run_battery.py"


def main():
    src = HARNESS.read_text()
    tree = ast.parse(src)
    cases = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign) and getattr(node.targets[0], "id", "") == "CASES":
            for elt in node.value.elts:
                cases.append(ast.literal_eval(elt))
    names = [c[0] for c in cases]
    print("total rows: %d  unique names: %d" % (len(cases), len(set(names))))
    print("duplicate case names: %s"
          % [k for k, v in Counter(names).items() if v > 1])

    r94 = [c for c in cases if c[0].startswith("r94_")]
    print("r94 rows: %d" % len(r94))

    sig = [c[4] for c in r94 if c[0] == "r94_particles_census"][0]
    line = [l for l in (REPO / "corpus/live/r94-scout/runs/r94_particles_census.rep1.out").read_text().splitlines()
            if l.startswith("PASS particles_lattice census")][0]
    print("census sig len: %d  emitted line len: %d  sig==line: %s"
          % (len(sig), len(line), sig == line))

    ok = True
    for c in r94:
        arm = c[2][0].split("=", 1)[1]
        p = REPO / ("corpus/live/r94-scout/runs/r94_particles_%s.rep1.out" % arm)
        if not p.is_file():
            print("MISSING receipt: %s" % p)
            ok = False
            continue
        lines = [l for l in p.read_text().splitlines()
                 if l.startswith("PASS particles_lattice " + arm)]
        m = [l for l in lines if l.startswith(c[4])]
        if len(m) != 1:
            print("NOT-A-UNIQUE-HEAD: %s lines=%d heads=%d" % (c[0], len(lines), len(m)))
            ok = False
    print("all 19 signatures are unique contiguous heads of their scout rep1 line: %s" % ok)


if __name__ == "__main__":
    main()
