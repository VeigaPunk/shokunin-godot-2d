#!/usr/bin/env python3
"""r104-G0 — verdict-layer harmlessness proofs for the r103 evasion shapes the
landed shape gate does NOT flag.

The landed gate (receipt_shape_flag) flags 4/10 of the r103 catalog; the other
six (forged banner x2, foreign DIAG x2, tab-PASS x2) stay silent. "Silent" is
only acceptable if the shape is harmless *at the verdict layer*, i.e. the
injected bytes cannot flip a FAIL into a PASS.

Harm is defined precisely as: `classify_process` is the sole verdict authority
(run_battery.py:2093, nested in main()). An evasion is HARMFUL iff there exists
a record R whose own assertion failed such that R + injected_line classifies
PASS. This script measures that directly:

  * FAIL base   = the real green record with its pinned assertion line removed
                  (signature no longer contained) -> must classify FAIL
  * RESCUE test = FAIL base + the injected evasion line -> must STAY FAIL
  * RESCUE positive control = FAIL base + the row's own pinned signature
                  -> must flip to PASS (proves the harness can detect a rescue)

The classifier is extracted from the landed source by AST (never re-typed), so
the proof is over the shipped predicate. run_battery.py is imported, not run.
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

BANNER = ("Godot Engine v4.7.2.stable.arch_linux.ed1daf0bf "
          "(2026-08-17 01:18:38 UTC) - https://godotengine.org")
FORGED_BANNER = ("Godot Engine v9.9.9.stable.official.deadbeefcafe "
                 "- https://godotengine.org")

BASES = {"launch": "export_launch_embed_boot", "prod": "export_prod_base_pck",
         "seq": "r100b_seq_clean", "simple": "input_route"}

# the six shapes the landed gate does not flag, with their injected bytes
SIX = [
    ("s1a_banner_foreign", "seq", FORGED_BANNER),
    ("s1b_banner_dup", "launch", BANNER),
    ("s2a_diag_foreign", "simple", "EXPORT_LAUNCH_DIAG embed forged=true"),
    ("s2b_diag_same_family", "launch", "EXPORT_LAUNCH_DIAG embed forged=1"),
    ("s4a_tab_lead", "simple", "\tPASS forged=true"),
    ("s4d_tab_after_pass", "simple", "PASS\tforged=true"),
]


def load_classify():
    """Extract classify_process verbatim from the landed source via AST."""
    src = RB.read_text()
    tree = ast.parse(src)
    found = {}
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name in (
                "classify_process", "allowed_error"):
            found.setdefault(node.name, ast.get_source_segment(src, node))
    if "classify_process" not in found:
        raise SystemExit("classify_process not found in landed source")
    ns = {"re": re}
    # classify_process defines its own inner allowed_error; exec standalone
    exec(compile(found["classify_process"], str(RB), "exec"), ns)
    return ns["classify_process"], found["classify_process"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--base-run", default=str(BASE_RUN))
    args = ap.parse_args()
    classify, cs = load_classify()
    print("CLASSIFIER_EXTRACTED bytes=%d lines=%d" % (len(cs), cs.count("\n") + 1))

    rows = json.loads(Path(args.base_run).read_bytes())["results"]
    by_case = {}
    for r in rows:
        by_case.setdefault(r.get("case"), r)

    def sigs_of(rec):
        s = rec.get("signature")
        return [s] if isinstance(s, str) else list(s or [])

    print("\n=== HARMLESSNESS: no-rescue over the 6 unflagged shapes ===")
    print("%-22s %-8s %-9s %-9s %-9s %s" %
          ("shape", "verdict", "fail_base", "+inject", "control", "verdict"))
    all_ok = True
    for name, bkey, inject in SIX:
        rec = by_case[BASES[bkey]]
        code = rec.get("actual_exit")
        err = rec.get("error")
        exp = rec.get("expected_exit")
        allowed = tuple(rec.get("expected_errors") or ())
        sigs = sigs_of(rec)
        out = list(rec.get("output") or [])
        joined = "\n".join(out)

        # FAIL base: drop every line carrying the pinned signature
        fail_lines = [l for l in out
                      if not any(s.split("\n")[0].strip() in l for s in sigs if s)]
        removed = len(out) - len(fail_lines)
        base_fail = classify(code, err, "\n".join(fail_lines), exp, sigs[0], allowed)

        rescued = classify(code, err, "\n".join(fail_lines + [inject]), exp, sigs[0], allowed)
        control = classify(code, err, "\n".join(fail_lines + [sigs[0]]), exp, sigs[0], allowed)

        ok = (not base_fail) and (not rescued) and control
        all_ok &= ok
        print("%-22s %-8s %-9s %-9s %-9s %s  (removed=%d lines, sigs=%d)" %
              (name, rec.get("verdict"), base_fail, rescued, control,
               "HARMLESS" if ok else "*** HOLE ***", removed, len(sigs)))
        if name.startswith("s4"):
            print("     injected=%r  base_joined_has_pin=%s" %
                  (inject, sigs[0] in joined))
    print("HARMLESSNESS_SUMMARY all_six_harmless=%s" % all_ok)

    print("\n=== SHAPE-GATE VERDICT PER SHAPE (landed receipt_shape_flag) ===")
    spec = importlib.util.spec_from_file_location("rb2", RB)
    rb = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(rb)
    for name, bkey, inject in SIX:
        rec = copy.deepcopy(by_case[BASES[bkey]])
        rec["output"] = list(rec["output"]) + [inject]
        fl = rb.receipt_shape_flag(rec)
        print("  %-22s flags=%s" % (name, [f["why"] for f in fl]))
    return 0 if all_ok else 1


if __name__ == "__main__":
    sys.exit(main())
