#!/usr/bin/env python3
"""r104-G0 — bounded exhaustive arrangement search over the simple row.

Goal: state the tab-PASS tightening's value precisely, separating
  (a) verdict-flip evasions  — a record whose own assertion failed but which
      classifies PASS, and
  (b) content-smuggling evasions — a forged line riding along unaccounted while
      the record's verdict stays PASS.

Search space (all built on the real green `input_route` record):
  * hide_pin in {no, yes}        — the row's own pinned line keeps or loses
                                   column-0 anchoring (tab-prefixed)
  * forged lines drawn from a set of 10 shapes, 0..2 of them, each either
    column-0 or tab-prefixed, inserted at every line position.

For every arrangement we record:
  verdict  = landed classify_process over the merged output
  gate_L   = landed receipt_shape_flag flags
  gate_T   = census-widened receipt_shape_flag flags

Read-only; run_battery.py is imported, never executed.
"""
import ast
import copy
import itertools
import json
import re
import sys
import types
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
RB = REPO / "corpus" / "fixtures" / "run_battery.py"
BASE = REPO / "corpus" / "live" / "runs" / "20261018T213443471189Z" / "verdicts.json"
CASE = "input_route"
OLD = 'pass_lines = [line for line in output if line.startswith("PASS ")]'
NEW = 'pass_lines = [line for line in output if line.strip().startswith("PASS")]'

FORGERIES = [
    "PASS forged=true",
    "PASS flooded=1 extra=true",
    "PASS r100_gui forged=1",
    "PASS forged=a",
    "EXPORT_LAUNCH_DIAG embed forged=true",
]


def load(src, name):
    mod = types.ModuleType(name)
    mod.__dict__["__file__"] = str(RB)
    exec(compile(src, str(RB), "exec"), mod.__dict__)
    return mod


def classify_fn():
    src = RB.read_text()
    tree = ast.parse(src)
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "classify_process":
            ns = {"re": re}
            exec(compile(ast.get_source_segment(src, node), str(RB), "exec"), ns)
            return ns["classify_process"]
    raise SystemExit("classify_process not found")


def main():
    src = RB.read_text()
    gL = load(src, "gL")
    gT = load(src.replace(OLD, NEW), "gT")
    classify = classify_fn()

    rows = json.loads(BASE.read_bytes())["results"]
    rec = next(r for r in rows if r.get("case") == CASE)
    pin = rec["signature"]
    code, err, exp = rec["actual_exit"], rec["error"], rec["expected_exit"]
    allowed = tuple(rec.get("expected_errors") or [])
    base_out = list(rec["output"])
    pin_idx = next(i for i, l in enumerate(base_out) if pin in l)

    n = 0
    silent_L = 0
    silent_T = 0
    flip = 0            # verdict PASS while the pinned line is not column-0 clean
    smuggle_L = []      # verdict PASS, landed gate silent, forged content present
    smuggle_T = []
    for hide_pin in (False, True):
        for k in (0, 1, 2):
            for combo in itertools.combinations(FORGERIES, k):
                for prefixed in itertools.product((False, True), repeat=k):
                    forged = [(("\t" if p else "") + f) for f, p in zip(combo, prefixed)]
                    for pos in range(len(base_out) + 1):
                        out = list(base_out)
                        if hide_pin:
                            out[pin_idx] = "\t" + out[pin_idx]
                        for j, fl in enumerate(forged):
                            out.insert(min(pos + j, len(out)), fl)
                        n += 1
                        v = classify(code, err, "\n".join(out), exp, pin, allowed)
                        row = {"case": CASE, "script": rec["script"],
                               "verdict": "PASS", "output": out}
                        fL = gL.receipt_shape_flag(row)
                        fT = gT.receipt_shape_flag(row)
                        if not fL:
                            silent_L += 1
                        if not fT:
                            silent_T += 1
                        forged_present = bool(forged)
                        if forged_present and not fL:
                            smuggle_L.append((hide_pin, combo, prefixed, pos, v))
                        if forged_present and not fT:
                            smuggle_T.append((hide_pin, combo, prefixed, pos, v))
                        if hide_pin and v:
                            flip += 1
    print("ARRANGEMENTS=%d" % n)
    print("gate_L silent=%d   gate_T silent=%d" % (silent_L, silent_T))
    print("verdict PASS with pin hidden (all are legit-pin substring cases) = %d" % flip)
    print("SMUGGLE_L (forged present, landed gate silent) = %d" % len(smuggle_L))
    print("SMUGGLE_T (forged present, tightened gate silent) = %d" % len(smuggle_T))
    print("\n--- SMUGGLE_L sample (first 8) ---")
    for s in smuggle_L[:8]:
        print("   hide_pin=%s forged=%s prefixed=%s pos=%d verdict=%s" % s)
    print("\n--- distinct forgery strings among SMUGGLE_L ---")
    seen = {}
    for hide_pin, combo, prefixed, pos, v in smuggle_L:
        for f, p in zip(combo, prefixed):
            seen[("\t" if p else "") + f] = seen.get(("\t" if p else "") + f, 0) + 1
    for k2, c in sorted(seen.items(), key=lambda x: -x[1]):
        print("   %-40r occurrences=%d" % (k2, c))
    return 0


if __name__ == "__main__":
    sys.exit(main())
