#!/usr/bin/env python3
"""r104-G0 — false-positive analysis for the tab-PASS tightening, measured by
running the REAL gate twice over every stored run: once as landed, once with
the census widened.

Widening (the r103-routed candidate), exactly one line changed:

    -  pass_lines = [line for line in output if line.startswith("PASS ")]
    +  pass_lines = [line for line in output if line.strip().startswith("PASS")]

A false positive is any row where the widened gate flags and the landed gate
does not. Both gates are executed from the landed source (never re-typed);
run_battery.py is imported, never executed.
"""
import json
import sys
import types
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
RB = REPO / "corpus" / "fixtures" / "run_battery.py"
RUNS = REPO / "corpus" / "live" / "runs"

OLD = 'pass_lines = [line for line in output if line.startswith("PASS ")]'
NEW = 'pass_lines = [line for line in output if line.strip().startswith("PASS")]'


def load(path_or_src, name):
    mod = types.ModuleType(name)
    mod.__dict__["__file__"] = str(RB)
    exec(compile(path_or_src, str(RB), "exec"), mod.__dict__)
    return mod


def main():
    src = RB.read_text()
    assert OLD in src, "census line not found verbatim"
    landed = load(src, "rb_landed")
    tight = load(src.replace(OLD, NEW), "rb_tight")
    print("LANDED_CENSUS=%r" % OLD.strip())
    print("TIGHT_CENSUS =%r" % NEW.strip())
    print("patch_sites=%d (occurrences of the census line in landed source)"
          % src.count(OLD))

    tot_rows = tot_landed = tot_tight = tot_fp = tot_closed = 0
    print("\n%-26s %8s %8s %8s %8s %8s" %
          ("run", "audited", "flags_L", "flags_T", "FP", "closed"))
    for p in sorted(RUNS.glob("*/verdicts.json")):
        rows = json.loads(p.read_bytes()).get("results", [])
        aL = landed.receipt_shape_audit(rows)
        aT = tight.receipt_shape_audit(rows)
        setL = {json.dumps(f, sort_keys=True) for f in aL["flags"]}
        setT = {json.dumps(f, sort_keys=True) for f in aT["flags"]}
        fp = setT - setL
        closed = setL - setT
        tot_rows += aL["audited"]
        tot_landed += len(aL["flags"])
        tot_tight += len(aT["flags"])
        tot_fp += len(fp)
        tot_closed += len(closed)
        print("%-26s %8d %8d %8d %8d %8d" %
              (p.parent.name, aL["audited"], len(aL["flags"]), len(aT["flags"]),
               len(fp), len(closed)))
        for f in sorted(fp)[:5]:
            print("    FP  %s" % f[:150])
        for f in sorted(closed)[:5]:
            print("    CLS %s" % f[:150])
    print("\nTOTAL audited=%d flags_landed=%d flags_tight=%d FP=%d closed=%d"
          % (tot_rows, tot_landed, tot_tight, tot_fp, tot_closed))
    print("FALSE_POSITIVE_RATE=%.4f%%" % (100.0 * tot_fp / max(tot_rows, 1)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
