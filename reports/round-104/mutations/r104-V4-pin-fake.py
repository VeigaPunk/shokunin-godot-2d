#!/usr/bin/env python3
"""r104-ver4 — adversary replay against the LANDED receipt-shape predicate.

Target (read-only, never executed as a battery):
  corpus/fixtures/run_battery.py : receipt_shape_flag() / receipt_shape_audit()
The module is exec'd up to `def main():` so the gate code under test is used
verbatim (no reimplementation, no battery run).

Purpose: attack r103's "6 unflagged shapes are verdict-layer-harmless" claim by
escalating each of the 6 into a FAKED PIN — a tampered copy of a real green
stored record whose forged content the landed gate cannot distinguish from the
legitimate receipt.

Writes nothing into the repo. Reads one stored green verdicts.json.
"""
import argparse
import copy
import hashlib
import json
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[3] if len(Path(__file__).resolve().parents) > 3 else Path.cwd()
if not (REPO / "corpus/fixtures/run_battery.py").exists():
    REPO = Path.cwd()
BATTERY = REPO / "corpus/fixtures/run_battery.py"
GREEN = REPO / "corpus/live/runs/20261019T005558434174Z/verdicts.json"
CUT = "\ndef main():\n"

BANNER = ("Godot Engine v4.7.2.stable.arch_linux.ed1daf0bf "
          "(2026-08-17 01:18:38 UTC) - https://godotengine.org")
FORGED_BANNER = ("Godot Engine v9.9.9.stable.official.deadbeefcafe "
                 "- https://godotengine.org")


def load_gate():
    src = BATTERY.read_text()
    head, sep, _ = src.partition(CUT)
    if not sep:
        raise SystemExit("cut marker not found")
    ns = {"__name__": "r104_ver4_gate", "__file__": str(BATTERY)}
    exec(compile(head, str(BATTERY), "exec"), ns)
    return ns, head


def find_row(rows, case):
    for r in rows:
        if r.get("case") == case:
            return r
    raise SystemExit("no row for case %s" % case)


def tamper(row, op):
    """op: (kind, arg) with kind in replace/insert/append/delete."""
    out = copy.deepcopy(row)
    lines = list(out["output"])
    kind, a, b = op
    if kind == "replace":
        lines[a] = b
    elif kind == "insert":
        lines.insert(a, b)
    elif kind == "append":
        lines.append(b)
    elif kind == "delete":
        del lines[a]
    elif kind == "replace_all":
        lines = b
    else:
        raise SystemExit("bad op %s" % kind)
    out["output"] = lines
    return out


def build(rows):
    ir = find_row(rows, "input_route")
    seq = find_row(rows, "r100b_seq_clean")
    lb = find_row(rows, "export_launch_embed_boot")
    pd = find_row(rows, "export_prod_base_pck")
    ir_pin = "PASS route=parse_input_event-to-Node._input key=R receipt_count=1 frames=3"

    atk = []

    # ---- group 0: reconstruct the 10 r103 mut05 shapes (control group) ----
    atk.append(("s1a_banner_forged_seq", tamper(seq, ("insert", 2, FORGED_BANNER))))
    atk.append(("s1b_banner_dup_launch", tamper(lb, ("insert", 4, BANNER))))
    atk.append(("s2a_diag_other_family_simple",
                tamper(ir, ("insert", 3, "EXPORT_LAUNCH_DIAG embed forged=true"))))
    atk.append(("s2b_diag_forged_launch",
                tamper(lb, ("insert", 6, "EXPORT_LAUNCH_DIAG embed forged=1"))))
    atk.append(("s3a_flood5_simple",
                tamper(ir, ("replace_all", None,
                            ir["output"] + ["PASS flooded=%d extra=true" % n
                                            for n in range(1, 6)]))))
    atk.append(("s3b_flood1_seq",
                tamper(seq, ("append", None, "PASS r100_gui forged=1"))))
    atk.append(("s4a_tab_lead_simple", tamper(ir, ("append", None, "\tPASS forged=true"))))
    atk.append(("s4b_trail_space_simple", tamper(ir, ("append", None, ir["output"][-1] + " "))))
    atk.append(("s4c_trail_nbsp_simple", tamper(ir, ("append", None, "PASS forged=true\u00a0"))))
    atk.append(("s4d_tab_after_pass_simple", tamper(ir, ("append", None, "PASS\tforged=true"))))

    # ---- group 1: V4 escalations of the 6 unflagged shapes --------------
    # E1 tab-PASS FLOOD (the C2a grammar-invisible class, on the shape r103
    #    declared harmless).  Space-form flood s3a flags; tab-form must not.
    atk.append(("E1_tabpass_flood5_simple",
                tamper(ir, ("replace_all", None,
                            ir["output"] + ["PASS\tflooded=%d extra=true" % n
                                            for n in range(1, 6)]))))
    # E2 tab-PASS flood on the 14-PASS allowlisted grammar row: declared
    #    grammar is still satisfied because the census cannot see these lines.
    atk.append(("E2_tabpass_flood5_seq",
                tamper(seq, ("replace_all", None,
                             seq["output"] + ["PASS\tr100_gui forged=%d" % n
                                              for n in range(1, 6)]))))
    # E3 lead-tab flood (s4a escalated from 1 to 5 forged lines).
    atk.append(("E3_leadtab_flood5_simple",
                tamper(ir, ("replace_all", None,
                            ir["output"] + ["\tPASS forged=%d" % n for n in range(1, 6)]))))
    # E4 the row's own PASS receipt verb is REMOVED and re-emitted on a
    #    non-grammar line carrying the identical payload: pin still matches.
    atk.append(("E4_pin_on_tabline_simple",
                tamper(ir, ("replace_all", None,
                            [ir["output"][0], "", "PASS\t" + ir_pin]))))
    atk.append(("E5_pin_on_leadtab_simple",
                tamper(ir, ("replace_all", None,
                            [ir["output"][0], "", "\tPASS " + ir_pin]))))
    # E6 banner identity FORGED (not merely duplicated) on a non-DIAG row.
    atk.append(("E6_banner_forged_simple",
                tamper(ir, ("replace", 0, FORGED_BANNER))))
    # E7 banner-flood on a DIAG row: any number of banner-shaped lines allowed.
    atk.append(("E7_banner_forged_plus_dup_launch",
                tamper(lb, ("replace_all", None,
                            [FORGED_BANNER] + lb["output"] + [FORGED_BANNER]))))
    # E8 wholly FOREIGN designed verb inside a DIAG row (never printed by any
    #    fixture) — matches ^[A-Z][A-Z0-9_]*_DIAG\b, so the window admits it.
    atk.append(("E8_foreign_diag_verb_launch",
                tamper(lb, ("insert", 3, "FABRICATED_DIAG root=/forged/root ok=true"))))
    atk.append(("E9_foreign_diag_verb_prod",
                tamper(pd, ("insert", 3, "ZZ_DIAG forged=1"))))
    # E10 DIAG line injected into a row that has no DIAG family at all, then
    #     the whole receipt re-accounted by the DIAG window.
    atk.append(("E10_foreign_diag_into_simple",
                tamper(ir, ("insert", 3, "EXPORT_PROD_DIAG subdir root=/forged"))))
    # E11 non-ASCII / unicode whitespace line ending (NBSP flood).
    atk.append(("E11_nbsp_flood5_simple",
                tamper(ir, ("replace_all", None,
                            ir["output"] + ["PASS\tforged=%d\u00a0" % n for n in range(1, 6)]))))

    # E12 ANCHOR-ONLY fake: the receipt payload is dropped, only the anchor
    #     prefix survives — the gate's anchor test is a substring predicate.
    atk.append(("E12_anchor_only_leadtab",
                tamper(ir, ("replace_all", None,
                            [ir["output"][0], "",
                             "\tPASS route=parse_input_event-to-Node._input"]))))
    # E13 legit-anchor + foreign junk tail on a grammar-form PASS line.
    atk.append(("E13_anchor_junk_tail",
                tamper(ir, ("replace", 2,
                            ir_pin + " EXFIL forged=1"))))
    # E14 ERROR-token bypass: `diagnostic_pinned` is computed from any line
    #     containing the anchor that also contains "ERROR:" — that short-
    #     circuits the pass_line_unanchored check for the whole row.
    atk.append(("E14_error_token_bypass",
                tamper(ir, ("replace", 2,
                            "PASS route=parse_input_event-to-Node._input ERROR: forged"))))
    # E15 same bypass, but the whole receipt verb is moved onto a tab line.
    atk.append(("E15_error_token_tabline",
                tamper(ir, ("replace_all", None,
                            [ir["output"][0], "",
                             "PASS\troute=parse_input_event-to-Node._input ERROR: forged"]))))
    # E16 banner forged + whole receipt replaced by an anchor-only tab line.
    atk.append(("E16_forged_banner_anchor_only",
                tamper(ir, ("replace_all", None,
                            [FORGED_BANNER, "",
                             "\tPASS route=parse_input_event-to-Node._input"]))))

    # E17 DIAGNOSTIC-PINNED SHORT-CIRCUIT (pure logic hole, no whitespace
    #     trick): a decoy line that merely CONTAINS the anchor and the
    #     substring "ERROR:" sets diagnostic_pinned=True for the whole row,
    #     which skips the pass_line_unanchored check — so a completely
    #     foreign PASS line is accepted.
    atk.append(("E17_diagpin_decoy_error",
                tamper(ir, ("replace_all", None,
                            [ir["output"][0], "",
                             "ERROR: route=parse_input_event-to-Node._input bogus",
                             "PASS forged=true"]))))
    # E18 same short-circuit, no ERROR: needed on the forged line itself, and
    #     the decoy is an ordinary non-PASS line.
    atk.append(("E18_diagpin_decoy_after",
                tamper(ir, ("replace_all", None,
                            [ir["output"][0], "",
                             "PASS completely_foreign=1",
                             "   ERROR: route=parse_input_event-to-Node._input decoy"]))))
    # E19 the legitimate receipt line is DELETED entirely; only the decoy
    #     remains, so the row never prints its own pin at all.
    atk.append(("E19_pin_deleted_decoy_only",
                tamper(ir, ("replace_all", None,
                            [ir["output"][0], "",
                             "PASS forged=1",
                             "ERROR: route=parse_input_event-to-Node._input decoy"]))))

    # E20 the short-circuit armed with the FULL anchor text: the decoy line
    #     carries the complete pin AND "ERROR:", so diagnostic_pinned=True;
    #     the row's actual PASS receipt is replaced by a foreign one.
    atk.append(("E20_diagpin_full_anchor_decoy",
                tamper(ir, ("replace_all", None,
                            [ir["output"][0], "",
                             "ERROR: " + ir_pin,
                             "PASS forged=true"]))))
    # E21 same, but the row emits NO PASS line at all — only the decoy.
    atk.append(("E21_diagpin_no_pass_at_all",
                tamper(ir, ("replace_all", None,
                            [ir["output"][0], "",
                             "ERROR: " + ir_pin]))))
    # E22 the forged PASS line itself carries the anchor, so it is both the
    #     decoy and the receipt — pin satisfied by a line that is a foreign verb.
    atk.append(("E22_diagpin_self_decoy",
                tamper(ir, ("replace_all", None,
                            [ir["output"][0], "",
                             "ERROR: " + ir_pin,
                             "PASS " + ir_pin + " forged=1"]))))

    # E23 FULL-STACK FAKE on a diagnostic-pinned row: save_process_missing
    #     legitimately carries a comma-suffixed (prefix) expected_errors entry
    #     that its own anchor satisfies. Replacing its real PASS receipt with a
    #     foreign one keeps BOTH layers happy: the gate short-circuits on
    #     diagnostic_pinned, and the process classifier never inspects the PASS
    #     line at all (its signature is the ERROR: text).
    sp = find_row(rows, "save_process_missing")
    sp_pin = "ERROR: SAVE PROCESS EXPECTED NEGATIVE: missing file rejected signature=FILE_NOT_FOUND"
    atk.append(("E23_saveprocess_forged_pass",
                tamper(sp, ("replace_all", None,
                            [sp["output"][0], "",
                             "PASS save_process forged=true exfil=1"] + sp["output"][3:]))))
    atk.append(("E24_saveprocess_error_junk",
                tamper(sp, ("replace", 3, sp_pin + ", EXFIL forged=1"))))
    # E25 both at once: forged PASS receipt + ERROR junk, whole row still green.
    atk.append(("E25_saveprocess_both",
                tamper(sp, ("replace_all", None,
                            [sp["output"][0], "",
                             "PASS save_process forged=true exfil=1",
                             sp_pin + ", EXFIL forged=1"] + sp["output"][4:]))))

    # ---- green controls (the untampered bases) ----
    ctl = [("green_simple", ir), ("green_seq", seq),
           ("green_launch", lb), ("green_prod", pd)]
    return atk, ctl


def corpus_mode(ns, rows, atk, names):
    """Whole-corpus verdict channel: tamper ONE row inside the full stored run
    and read the gate's real verdict (receipt_shape_audit over all rows)."""
    audit = ns["receipt_shape_audit"]
    base = audit(rows)
    print("\n== WHOLE-CORPUS AUDIT (receipt_shape_audit, %d rows) ==" % len(rows))
    print("%-32s BASELINE audited=%d flags=%d" % ("green corpus", base["audited"],
                                                  len(base["flags"])))
    sel = set(names) if names else None
    for name, row in atk:
        if sel and name not in sel:
            continue
        swapped = []
        for r in rows:
            if r.get("case") == row["case"] and r is not None and swapped == []:
                swapped.append(row)
            else:
                swapped.append(r)
        a = audit(swapped)
        print("%-32s audited=%d flags=%d %s" % (
            name, a["audited"], len(a["flags"]),
            "GREEN-VERDICT" if not a["flags"] else "FLAGGED"))


def main():
    global BATTERY
    ap = argparse.ArgumentParser()
    ap.add_argument("--json-out")
    ap.add_argument("--gate-path", default=str(BATTERY))
    args = ap.parse_args()

    BATTERY = Path(args.gate_path)

    ns, head = load_gate()
    flag = ns["receipt_shape_flag"]
    audit = ns["receipt_shape_audit"]
    gate_sha = hashlib.sha256(BATTERY.read_bytes()).hexdigest()
    print("GATE=%s sha256=%s exec_head_bytes=%d" % (BATTERY, gate_sha, len(head)))
    print("CASES=%d grammar_rows=%d derived_evidence=%s" % (
        len(ns["CASES"]), len(ns["RECEIPT_MULTI_PASS_GRAMMAR"]),
        sorted(ns["RECEIPT_SHAPE_DERIVED_EVIDENCE"])))

    raw = GREEN.read_bytes()
    data = json.loads(raw)
    rows = data["results"]
    print("GREEN=%s sha256=%s rows=%d verdict=%s" % (
        GREEN, hashlib.sha256(raw).hexdigest(), len(rows), data["verdict"]))

    atk, ctl = build(rows)
    print("\n== ATTACKS ==")
    out = []
    for name, row in atk:
        row["verdict"] = "PASS"          # tampering does not touch the verdict field
        row["case"] = row["case"]        # unchanged
        flags = flag(row)
        reasons = [f.get("why") for f in flags]
        print("%-32s n_out=%2d %s %s" % (
            name, len(row["output"]), "FLAG" if flags else "CLEAN", reasons))
        out.append({"name": name, "case": row["case"], "n_out": len(row["output"]),
                    "flagged": bool(flags), "reasons": reasons})

    print("\n== GREEN CONTROLS ==")
    for name, row in ctl:
        flags = flag(row)
        print("%-32s n_out=%2d %s %s" % (
            name, len(row["output"]), "FLAG" if flags else "CLEAN",
            [f.get("why") for f in flags]))
        out.append({"name": name, "case": row["case"], "n_out": len(row["output"]),
                    "flagged": bool(flags), "reasons": [f.get("why") for f in flags]})

    # whole-corpus audit: does the tampered row survive receipt_shape_audit too?
    print("\n== AUDIT (receipt_shape_audit over a single-row corpus) ==")
    for name, row in atk:
        a = audit([row])
        print("%-32s audited=%d flags=%d %s" % (
            name, a["audited"], len(a["flags"]),
            [f.get("why") for f in a["flags"] if f.get("why") != "dead_shape_allowlist_entry"]))

    corpus_mode(ns, rows, atk, set(
        ["E1_tabpass_flood5_simple", "E4_pin_on_tabline_simple",
         "E12_anchor_only_leadtab", "E14_error_token_bypass",
         "E16_forged_banner_anchor_only", "E6_banner_forged_simple",
         "E8_foreign_diag_verb_launch", "s4a_tab_lead_simple",
         "E20_diagpin_full_anchor_decoy", "E23_saveprocess_forged_pass",
         "E25_saveprocess_both"]))

    if args.json_out:
        Path(args.json_out).write_text(json.dumps(
            {"gate": str(BATTERY), "gate_sha256": gate_sha,
             "green": str(GREEN), "results": out}, indent=1) + "\n")
        print("\nWROTE %s" % args.json_out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
