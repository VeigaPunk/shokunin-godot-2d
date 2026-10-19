#!/usr/bin/env python3
"""W10 audit harness: run the frozen receipt-shape gate over (a) the two stored
r102 green runs and (b) adversarial record mutations built in memory from those
runs. Read-only over the repo; writes evidence JSON under /var/tmp/r103c-W10/.
"""
import copy, json, re, sys
from pathlib import Path
# The gate fragment is destined for run_battery.py, which already imports `re`
# at module level; exec it in a namespace that supplies `re` so the fragment
# stays byte-identical to what the patch inserts.
_gate_ns = {"re": re}
exec(open(str(Path(__file__).with_name("r103-W10-receipt_gate_impl.py"))).read(), _gate_ns)
receipt_shape_audit = _gate_ns["receipt_shape_audit"]
RECEIPT_MULTI_PASS_GRAMMAR = _gate_ns["RECEIPT_MULTI_PASS_GRAMMAR"]

GREEN = [
    "corpus/live/runs/20261018T212500022987Z/verdicts.json",
    "corpus/live/runs/20261018T213443471189Z/verdicts.json",
]
OUT = str(Path(__file__).with_name("r103-W10-audit_evidence.json"))


def load(path):
    d = json.load(open(path))
    return d["results"]


def find(rows, case):
    return next(r for r in rows if r["case"] == case)


def adversary_cases(green_rows):
    """Return list of (name, rows, expected_flag_why) built from green records."""
    tests = []

    def mutated(case, fn):
        rows = copy.deepcopy(green_rows)
        fn(find(rows, case))
        return rows

    def ins_after(row, idx, line):
        row["output"].insert(idx, line)

    # A1: foreign non-PASS line INSIDE the DIAG window (mut09 A1 shape).
    t = mutated("export_launch_stock_boot",
                lambda r: ins_after(r, 4, "FOREIGN_EXTRA injected=into_span"))
    tests.append(("A1_diag_foreign_in_span", t, "foreign_in_diag_window"))

    # A2: foreign line appended to the DIAG receipt tail (mut09 A2 shape).
    t = mutated("export_launch_stock_boot",
                lambda r: r["output"].append("FOREIGN_EXTRA injected=post_span"))
    tests.append(("A2_diag_foreign_post_span", t, "foreign_in_diag_window"))

    # A3: foreign line before the banner (mut09 A3 shape).
    t = mutated("export_launch_stock_boot",
                lambda r: ins_after(r, 0, "FOREIGN_EXTRA injected=pre_span"))
    tests.append(("A3_diag_foreign_pre_span", t, "foreign_in_diag_window"))

    # A4: forged extra PASS line appended to a single-PASS DIAG row.
    t = mutated("export_prod_main_scene_swap",
                lambda r: r["output"].append(
                    "PASS export_prod forged=1 site=foreign"))
    tests.append(("A4_diag_forged_pass_line", t, "unaccounted_pass_lines"))

    # A5: foreign line inside the SEQ span (SF1 shape).
    t = mutated("r101_seqfull_clean",
                lambda r: ins_after(r, 4, "FOREIGN_EXTRA injected=into_seq_span"))
    tests.append(("A5_seq_foreign_in_span", t, "foreign_in_span"))

    # A6: foreign line after SEQ_END, before the allowlisted error block (SF2).
    def a6(r):
        idx = next(i for i, l in enumerate(r["output"]) if l.startswith("SEQ_END"))
        r["output"].insert(idx + 1, "FOREIGN_EXTRA injected=after_seq_end")
    tests.append(("A6_seq_foreign_after_span", mutated("r101_seqfull_clean", a6),
                  "foreign_after_span"))

    # A7: forged PASS line inside the SEQ span (PASS-line flood inside span).
    t = mutated("r101_seqfull_clean",
                lambda r: ins_after(r, 4, "PASS r100_gui forged census site=foreign"))
    tests.append(("A7_seq_forged_pass_in_span", t, "pass_line_grammar_mismatch"))

    # A8: substitution inside a multi-PASS row (keeps count, swaps family).
    def a8(r):
        for i, line in enumerate(r["output"]):
            if line.startswith("PASS r100_gui localpos"):
                r["output"][i] = "PASS foreign_fixture forged=1 swapped=1"
                return
    tests.append(("A8_multi_pass_swap", mutated("r101_seqfull_clean", a8),
                  "pass_line_grammar_mismatch"))

    # A9: fail-closed — PASS row with a script but no stored output.
    t = mutated("mechanic", lambda r: r.__setitem__("output", None))
    tests.append(("A9_fail_closed_missing_output", t,
                  "fail_closed_missing_output"))

    # A10: fail-closed — PASS row whose signature field is gone.
    t = mutated("mechanic", lambda r: r.__setitem__("signature", None))
    tests.append(("A10_fail_closed_missing_signature", t,
                  "fail_closed_missing_signature"))

    # A11: duplicate anchor line (multiplicity 2 without declaration).
    def a11(r):
        anchor = r["signature"] if isinstance(r["signature"], str) \
            else r["signature"][0].split("\n")[0]
        r["output"].append(anchor)
    tests.append(("A11_duplicate_anchor_line", mutated("input_lattice_release_edge", a11),
                  "anchor_line_multiplicity"))

    # A11b: fail-closed — a non-text line object in the record.
    t = mutated("mechanic", lambda r: r["output"].append(["PASS forged"]))
    tests.append(("A11b_fail_closed_non_text_line", t, "fail_closed_non_text_line"))

    # A11c: unanchored forged PASS line on a diagnostic-pinned row (the
    # carve-out's own adversary: a foreign PASS line on save_process_missing
    # cannot hide behind the diagnostic pin).
    t = mutated("save_process_missing",
                lambda r: r["output"].append("PASS save_process forged=true"))
    tests.append(("A11c_diag_pinned_forged_pass", t, "unaccounted_pass_lines"))

    # A12: dead allowlist entry — the multi row disappears entirely.
    t = [r for r in copy.deepcopy(green_rows) if r["case"] != "export_launch_stock_boot"]
    tests.append(("A12_dead_allowlist_entry", t, "dead_shape_allowlist_entry"))

    # A13/C1: derived-evidence unbound — export_artifact bytes doctored.
    t = mutated("export_readiness",
                lambda r: r["export_artifact"].__setitem__("artifact_bytes", 1))
    tests.append(("A13_derived_evidence_unbound", t, "derived_evidence_unbound"))

    # N1 (negative control, disclosed ceiling): r102-mut9 §3.1 shape — the
    # foreign line lands on the LAUNCHED fixture, never in the stored record
    # (nested stdout is redirected); the record stays byte-identical.
    t = copy.deepcopy(green_rows)
    tests.append(("N1_ceiling_record_identical", t, None))

    return tests


def main():
    evidence = {"green": [], "adversaries": []}
    green_cache = {}
    for path in GREEN:
        rows = load(path)
        audit = receipt_shape_audit(rows)
        green_cache[path] = rows
        rec = {"run": path, "audited": audit["audited"],
               "flag_count": len(audit["flags"]), "flags": audit["flags"][:10]}
        evidence["green"].append(rec)
        print(f"GREEN {path}: audited={rec['audited']} flags={rec['flag_count']}")
        for f in rec["flags"][:10]:
            print("   FLAG", f)

    base = green_cache[GREEN[1]]
    for name, rows, expected in adversary_cases(base):
        audit = receipt_shape_audit(rows)
        whys = sorted({f["why"] for f in audit["flags"]})
        caught = (expected in whys) if expected else True
        rec = {"test": name, "expected": expected, "flags": len(audit["flags"]),
               "flagged_rows": sorted({f["case"] for f in audit["flags"]})[:8],
               "whys": whys[:8], "verdict": "FLAGGED" if audit["flags"] else "SILENT",
               "killed": bool(audit["flags"])}
        evidence["adversaries"].append(rec)
        print(f"ADV {name}: verdict={rec['verdict']} flags={rec['flags']} "
              f"whys={whys[:4]} rows={rec['flagged_rows'][:4]}")

    json.dump(evidence, open(OUT, "w"), indent=1)
    print("wrote", OUT)
    ok = all(not g["flag_count"] for g in evidence["green"])
    print("GREEN_ALL_SILENT:", ok)


if __name__ == "__main__":
    main()
