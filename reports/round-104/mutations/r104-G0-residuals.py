#!/usr/bin/env python3
"""r104-G0 — residual-class probes: R-A1 (forged *_DIAG self-admission) and
R-A2 (generic foreign line on an ordinary row).

Both are classes the tab-PASS tightening does NOT close. Measured against the
landed gate and the census-widened gate; run_battery.py is imported, never run.
"""
import copy
import json
import sys
import types
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
RB = REPO / "corpus" / "fixtures" / "run_battery.py"
BASE = REPO / "corpus" / "live" / "runs" / "20261018T213443471189Z" / "verdicts.json"
OLD = 'pass_lines = [line for line in output if line.startswith("PASS ")]'
NEW = 'pass_lines = [line for line in output if line.strip().startswith("PASS")]'


def load(src, name):
    mod = types.ModuleType(name)
    mod.__dict__["__file__"] = str(RB)
    exec(compile(src, str(RB), "exec"), mod.__dict__)
    return mod


def main():
    src = RB.read_text()
    gL = load(src, "gL")
    gT = load(src.replace(OLD, NEW), "gT")
    rows = json.loads(BASE.read_bytes())["results"]
    by = {}
    for r in rows:
        by.setdefault(r.get("case"), r)

    print("RECEIPT_DIAG_RE=%r" % gL.RECEIPT_DIAG_RE.pattern)
    print("  match column-0 'EXPORT_LAUNCH_DIAG x' = %s"
          % bool(gL.RECEIPT_DIAG_RE.match("EXPORT_LAUNCH_DIAG x")))
    print("  match tab-prefixed '\\tEXPORT_LAUNCH_DIAG x' = %s"
          % bool(gL.RECEIPT_DIAG_RE.match("\tEXPORT_LAUNCH_DIAG x")))

    print("\n=== R-A1: forged *_DIAG line on an ordinary row (input_route) ===")
    rec = by["input_route"]
    for tag, line in (("col0_DIAG", "EXPORT_LAUNCH_DIAG embed forged=true"),
                      ("tab_DIAG", "\tEXPORT_LAUNCH_DIAG embed forged=true"),
                      ("col0_OTHER_DIAG", "SAVE_DIAG forged=true")):
        out = list(rec["output"]) + [line]
        row = {"case": "input_route", "script": rec["script"], "verdict": "PASS",
               "output": out}
        fL = [f["why"] for f in gL.receipt_shape_flag(row)]
        fT = [f["why"] for f in gT.receipt_shape_flag(row)]
        window = any(gL.RECEIPT_DIAG_RE.match(l) for l in out)
        print("  %-16s window_opens=%-5s L=%-4s T=%-4s %s"
              % (tag, window, bool(fL), bool(fT), fL or "-"))

    print("\n=== R-A2: generic foreign line on ordinary rows ===")
    for case in ("input_route", "tween_flash"):
        r = by[case]
        print("  CASE %s sig=%r" % (case, r["signature"][:50]))
        for line in ("FOREIGN_EXTRA", "totally foreign text", "\tFOREIGN_TAB"):
            out = list(r["output"]) + [line]
            row = {"case": case, "script": r["script"], "verdict": "PASS", "output": out}
            fL = [f["why"] for f in gL.receipt_shape_flag(row)]
            fT = [f["why"] for f in gT.receipt_shape_flag(row)]
            print("    inject %-24r L=%-4s T=%-4s %s" % (line, bool(fL), bool(fT), fL or "-"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
