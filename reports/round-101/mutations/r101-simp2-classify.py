#!/usr/bin/env python3
"""r101 SIMP-2 — classify recorded row outputs against the battery's own CASES
pins (parsed read-only from run_battery.py via ast; the battery is NOT run).

Usage: classify.py committed.json [folded.json ...]
Per side, per row: rc == expected_rc, signature substring present (the battery's
own acceptance shape for these rows), plus the row's PASS/FAIL line echoed.
"""
import ast
import json
import pathlib
import sys

RB = pathlib.Path("/var/tmp/r101-simp2/corpus/fixtures/run_battery.py")


def load_cases():
    tree = ast.parse(RB.read_text())
    best = None
    for node in ast.walk(tree):
        if isinstance(node, ast.List) and len(node.elts) > 400:
            if best is None or len(node.elts) > len(best.elts):
                best = node
    cases = {}
    for el in best.elts:
        if not isinstance(el, ast.Tuple) or len(el.elts) < 5:
            continue
        try:
            name, script, flags, rc, sig = (ast.literal_eval(e) for e in el.elts[:5])
        except ValueError:
            continue
        if isinstance(name, str) and isinstance(script, str):
            cases[name] = {"script": script, "flags": flags, "rc": rc, "sig": sig}
    return cases


def main():
    cases = load_cases()
    print(f"CASES parsed: {len(cases)}")
    for path in sys.argv[1:]:
        data = json.loads(pathlib.Path(path).read_text())
        ok = bad = 0
        tail = []
        for name in sorted(data):
            if name not in cases:
                continue
            c = cases[name]
            out, rc = data[name]["out"], data[name]["rc"]
            sig_ok = c["sig"] in out
            rc_ok = rc == c["rc"]
            ok += 1 if (sig_ok and rc_ok) else 0
            bad += 0 if (sig_ok and rc_ok) else 1
            if not (sig_ok and rc_ok):
                tail.append(f"  FAIL {name}: sig={sig_ok} rc={rc} expected={c['rc']}")
        print(f"{path}: rows_checked={ok + bad} pass={ok} fail={bad}")
        for t in tail:
            print(t)
    return 0


if __name__ == "__main__":
    sys.exit(main())
