#!/usr/bin/env python3
"""r104 V3: independent replay of the LANDED receipt-shape gate.

Imports `receipt_shape_flag` / `receipt_shape_audit` from a scratch copy of the
HEAD `corpus/fixtures/run_battery.py` (never executed as a script) and drives
them with (a) every stored r103 verdicts.json and (b) 12 synthetic
discrimination shapes on mutated copies of green records.

Usage: python3 r104-ver3-replay.py <run_battery.py copy> <out.json> [verdicts.json ...]
"""
import copy
import importlib.util
import json
import sys
from pathlib import Path

SRC = Path(sys.argv[1])
OUT = Path(sys.argv[2])
RUNS = [Path(p) for p in sys.argv[3:]]


def load_module(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def audit(module, records):
    return module.receipt_shape_audit(records)


def main():
    module = load_module(SRC, "landed_run_battery_ver3")
    has_flag = hasattr(module, "receipt_shape_flag")
    has_audit = hasattr(module, "receipt_shape_audit")
    report = {
        "module": str(SRC),
        "has_receipt_shape_flag": has_flag,
        "has_receipt_shape_audit": has_audit,
        "cases_rows": len(module.CASES),
        "grammar_rows": len(module.RECEIPT_MULTI_PASS_GRAMMAR),
        "runs": {},
        "probes": [],
    }
    print(f"module={SRC} receipt_shape_flag={has_flag} receipt_shape_audit={has_audit} "
          f"CASES={len(module.CASES)} grammar={len(module.RECEIPT_MULTI_PASS_GRAMMAR)}")

    for run in RUNS:
        payload = json.loads(run.read_text())
        records = payload["results"]
        result = audit(module, records)
        green = [r for r in records if r.get("verdict") == "PASS"]
        print(f"run={run.parent.name} stored_verdict={payload.get('verdict')} "
              f"rows={len(records)} pass_rows={len(green)} audited={result['audited']} "
              f"flags={len(result['flags'])}")
        for flag in result["flags"]:
            print(f"   FLAG {flag}")
        report["runs"][run.parent.name] = {
            "stored_verdict": payload.get("verdict"),
            "rows": len(records),
            "pass_rows": len(green),
            "audited": result["audited"],
            "flags": result["flags"],
        }

    # ---- discrimination probes -------------------------------------------------
    green_run = json.loads(RUNS[0].read_text())
    by_case = {r["case"]: r for r in green_run["results"]}

    def seq_case():
        for cand in ("r101_seqfull_clean", "r100b_seq_clean", "r98b_seq_clean"):
            if cand in by_case:
                return by_case[cand]
        return None

    def base_row():
        for case, row in by_case.items():
            if row.get("verdict") == "PASS" and isinstance(row.get("output"), list):
                if module.CASES_SIG_BY_CASE.get(case) and "export_artifact" not in row:
                    return row
        return None

    def probe(name, mutate, expect):
        """Drive the row through the REAL in-battery path (receipt_shape_audit),
        and separately record whether the bare predicate survives the row."""
        victim = copy.deepcopy(green_run["results"])
        row = mutate(victim)
        result = audit(module, [row])
        flags = result["flags"]
        caught = any(expect in json.dumps(f) for f in flags)
        try:
            raw = module.receipt_shape_flag(row) if has_flag else None
            raw_outcome = {"ok": True, "flags": raw}
        except Exception as exc:                      # noqa: BLE001 - boundary datum
            raw_outcome = {"ok": False, "exception": f"{type(exc).__name__}: {exc}"}
        print(f"probe={name!r} expect={expect!r} caught={caught} flags={flags} "
              f"bare_predicate={raw_outcome}")
        report["probes"].append({"probe": name, "expect_label_contains": expect,
                                 "flags": flags, "caught": caught,
                                 "bare_predicate": raw_outcome})
        return caught

    # A1: foreign line injected INSIDE a declared SEQ_BEGIN..SEQ_END span
    def a1_span_splice(recs):
        target = seq_case()
        out = list(target["output"])
        b = next(i for i, l in enumerate(out) if l.startswith("SEQ_BEGIN"))
        e = next(i for i, l in enumerate(out) if l.startswith("SEQ_END"))
        out.insert(min(b + 3, e), "FOREIGN_EXTRA injected=into_span")
        row = dict(target)
        row["output"] = out
        return row

    # A2/A3: forged PASS line outside the span
    def a2_post_span_pass(recs):
        target = seq_case()
        row = dict(target)
        row["output"] = list(target["output"]) + ["PASS cargo_cult=true forged=post_span"]
        return row

    def a3_pre_span_pass(recs):
        target = seq_case()
        row = dict(target)
        row["output"] = ["PASS cargo_cult=true forged=pre_span"] + list(target["output"])
        return row

    # A4: output dropped
    def a4_drop_output(recs):
        row = dict(base_row())
        row.pop("output")
        return row

    # A5: verdict flipped off PASS (gate only audits PASS rows)
    def a5_flip_verdict(recs):
        row = dict(seq_case())
        row["verdict"] = "FAIL"
        return row

    # A6/A7: export artifact binding
    def a6_export_bytes(recs):
        row = dict(by_case["export_readiness"])
        row["export_artifact"] = dict(row["export_artifact"], artifact_bytes=row["export_artifact"]["artifact_bytes"] + 1)
        return row

    def a7_export_digest(recs):
        row = dict(by_case["export_readiness"])
        row["export_artifact"] = dict(row["export_artifact"], artifact_sha256="NOPE")
        return row

    # A8: forgery matching the declared diagnostic-pinned allowance
    def a8_allowlist_forgery(recs):
        row = dict(by_case["save_process_missing"])
        row["output"] = list(row["output"]) + ["PASS save_process missing=true pid=999 path=/tmp/forged"]
        return row

    # A9: TAB-prefixed PASS line (the r103 routed "grammar-invisible" shape)
    def a9_tab_pass(recs):
        row = dict(base_row())
        row["output"] = list(row["output"]) + ["PASS\ttab_forged=true"]
        return row

    # A10: anchor line duplicated (multiplicity)
    def a10_anchor_dup(recs):
        row = dict(base_row())
        case = row["case"]
        pin = module.CASES_SIG_BY_CASE[case]
        anchor = (pin if isinstance(pin, str) else pin[0]).split("\n")[0].strip()
        out = list(row["output"])
        for i, line in enumerate(out):
            if anchor in line:
                out.insert(i + 1, line)
                break
        row["output"] = out
        return row

    # A11: non-text line in output (fail-closed shape)
    def a11_non_text(recs):
        row = dict(base_row())
        row["output"] = list(row["output"]) + [None]
        return row

    # A12: dead grammar allowlist entry (drop a grammar row from the record set)
    def a12_dead_entry(recs):
        return dict(seq_case())

    probe("A1 foreign line inside SEQ span", a1_span_splice, "foreign_in_span")
    probe("A2 forged PASS line after span", a2_post_span_pass, "pass_line_unanchored")
    probe("A3 forged PASS line before span", a3_pre_span_pass, "pass_line_unanchored")
    probe("A4 output field dropped", a4_drop_output, "fail_closed_missing_output")
    probe("A5 verdict flipped PASS->FAIL (gate scope)", a5_flip_verdict, "pass_line")
    probe("A6 export artifact bytes != pin bytes", a6_export_bytes, "derived_evidence_unbound")
    probe("A7 export artifact digest malformed", a7_export_digest, "derived_evidence_unbound")
    probe("A8 declared diagnostic-pinned forgery", a8_allowlist_forgery, "pass_line")
    probe("A9 TAB-prefixed PASS line", a9_tab_pass, "pass_line")
    probe("A10 duplicated anchor line", a10_anchor_dup, "anchor_line_multiplicity")
    probe("A11 non-text output line", a11_non_text, "fail_closed_non_text_line")

    # A12 is a whole-record-set shape, not a single row: run it on the audit entry point
    victim = [r for r in green_run["results"] if r.get("case") != "r101_seqfull_clean"]
    result = audit(module, victim)
    caught = any(f.get("why") == "dead_shape_allowlist_entry" for f in result["flags"])
    print(f"probe='A12 grammar row dropped from record set' expect='dead_shape_allowlist_entry' caught={caught} flags={result['flags']}")
    report["probes"].append({"probe": "A12 grammar row dropped from record set",
                             "expect_label_contains": "dead_shape_allowlist_entry",
                             "flags": result["flags"], "caught": caught})

    OUT.write_text(json.dumps(report, indent=2) + "\n")
    print(f"artifact={OUT}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
