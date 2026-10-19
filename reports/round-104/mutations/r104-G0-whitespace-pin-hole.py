#!/usr/bin/env python3
"""r104-G0 — the whitespace-shifted-PIN hole, and what the tightening closes.

The landed census is `line.startswith("PASS ")` on the RAW line (run_battery.py
:1904). The classifier's verdict authority is `signature in output` — a plain
SUBSTRING test on the merged blob (run_battery.py:2109).

Those two disagree on exactly one class: a line that CARRIES the pinned
substring but is not column-0 `PASS `-anchored. Such a line
  (a) satisfies the classifier (substring present) -> verdict stays PASS, and
  (b) is not counted by the census -> pass_lines=[] -> the gate's
      pass-accounting branch never runs on it.

That is the evasion the r103-routed "tab-PASS tightening" is for. This script
measures the class directly against the landed gate and classifier, and
measures the tightened rule's behaviour on the same inputs.

Read-only; run_battery.py is imported, never executed.
"""
import argparse
import ast
import copy
import importlib.util
import json
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
RB = REPO / "corpus" / "fixtures" / "run_battery.py"
RUNS = REPO / "corpus" / "live" / "runs"
BASE_RUN = RUNS / "20261018T213443471189Z" / "verdicts.json"
CASE = "input_route"


def load():
    spec = importlib.util.spec_from_file_location("rb_hole", RB)
    rb = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(rb)
    src = RB.read_text()
    tree = ast.parse(src)
    fn = None
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "classify_process":
            fn = ast.get_source_segment(src, node)
            break
    ns = {"re": re}
    exec(compile(fn, str(RB), "exec"), ns)
    return rb, ns["classify_process"]


def census_landed(out):
    return [l for l in out if l.startswith("PASS ")]


def census_tight(out):
    return [l for l in out if l.strip().startswith("PASS")]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--base-run", default=str(BASE_RUN))
    args = ap.parse_args()
    rb, classify = load()
    rows = json.loads(Path(args.base_run).read_bytes())["results"]
    rec = next(r for r in rows if r.get("case") == CASE)
    sig = rec["signature"]
    code, err, exp = rec["actual_exit"], rec["error"], rec["expected_exit"]
    allowed = tuple(rec.get("expected_errors") or ())
    out = list(rec["output"])
    pin_idx = next(i for i, l in enumerate(out) if sig in l)
    print("CASE=%s sig=%r" % (CASE, sig))
    print("PIN line idx=%d raw=%r" % (pin_idx, out[pin_idx]))
    print("BASELINE verdict=%s census_landed=%d census_tight=%d" %
          (classify(code, err, "\n".join(out), exp, sig, allowed),
           len(census_landed(out)), len(census_tight(out))))

    # variants that shift the pin line's leading whitespace, or prefix it
    variants = [
        ("V1_lead_tab", "\t" + out[pin_idx]),
        ("V2_lead_spaces", "    " + out[pin_idx]),
        ("V3_lead_nbsp", "\u00a0" + out[pin_idx]),
        ("V4_prefix_noise", "x\t" + out[pin_idx]),
        ("V5_lead_tab_forged_only", "\tPASS forged=true"),
        ("V6_plain_forged", "PASS forged=true"),
    ]
    print("\n%-26s %-9s %-8s %-8s %-8s %s" %
          ("variant", "verdict", "census_L", "census_T", "gate_L", "gate_T"))
    for name, line in variants:
        v = out[:pin_idx] + [line] + out[pin_idx + 1:]
        v = v if "forged_only" not in name and "plain_forged" not in name else out + [line]
        verdict = classify(code, err, "\n".join(v), exp, sig, allowed)
        cl, ct = len(census_landed(v)), len(census_tight(v))
        mutated = copy.deepcopy(rec)
        mutated["output"] = v
        gate_l = [f["why"] for f in rb.receipt_shape_flag(mutated)]
        # tightened gate: same predicate, but census widened
        gate_t = tightened_flag(rb, mutated)
        print("%-26s %-9s %-8d %-8d %-8s %s" %
              (name, verdict, cl, ct, gate_l or "-", gate_t or "-"))
    return 0


def tightened_flag(rb, row):
    """receipt_shape_flag with the census widened to 'PASS' after optional
    leading whitespace (the r103-routed tightening), everything else verbatim."""
    import types
    src = Path(rb.__file__).read_text()
    old = 'pass_lines = [line for line in output if line.startswith("PASS ")]'
    new = 'pass_lines = [line for line in output if line.strip().startswith("PASS")]'
    assert old in src, "census line not found verbatim"
    patched = src.replace(old, new)
    mod = types.ModuleType("rb_patched")
    mod.__dict__["__file__"] = rb.__file__
    exec(compile(patched, rb.__file__, "exec"), mod.__dict__)
    return [f["why"] for f in mod.receipt_shape_flag(row)]


if __name__ == "__main__":
    sys.exit(main())
