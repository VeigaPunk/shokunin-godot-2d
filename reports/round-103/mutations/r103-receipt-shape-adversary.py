#!/usr/bin/env python3
"""r103 receipt-shape META gate — G2/G4 adversary proofs + W7 mut09 replay.

Builds synthetic attacked/corrupted variants of a stored GREEN verdict record
and runs the offline auditor (r103-receipt-shape-gate.py) over each variant.
Control = the unmodified record (must flag nothing).

Attack set (G2):
  A1 mut09 in-span foreign line (r102-mut9 §2 A1 bytes)
  A2 mut09 post-span foreign line
  A3 mut09 pre-span foreign line
  A4 PASS-line flood (forged receipt line appended)
  A5 engine-banner spoof (second banner line mid-stream)
  A6 cross-script splice (valid line vocabulary, wrong script's output)
Corruption set (G4):
  C1 output key dropped
  C2 output set to null (process-bearing row)
  C3 PASS verdict with error set
  C4 expected_exit tampered
  C5 signature rewritten to text absent from output
  C6 export artifact binding mismatch (executable_bytes vs artifact_bytes)
"""
import copy
import json
import sys
import os

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import importlib.util

spec = importlib.util.spec_from_file_location("gate", os.path.join(HERE, "r103-receipt-shape-gate.py"))
gate = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gate)

# r102-mut9 §2 exact foreign lines
A1_LINE = "FOREIGN_EXTRA injected=into_span"
A2_LINE = "FOREIGN_EXTRA injected=post_span"
A3_LINE = "FOREIGN_EXTRA injected=pre_span"


def attacks(rec):
    out = []
    base = copy.deepcopy(rec)

    def ins(line, pos):
        r = copy.deepcopy(base)
        o = list(r["output"])
        o.insert(pos, line)
        r["output"] = o
        return r

    out.append(("A1_mut09_in_span", ins(A1_LINE, 2)))            # between banner/blank and receipt
    out.append(("A2_mut09_post_span", ins(A2_LINE, len(base["output"]))))
    out.append(("A3_mut09_pre_span", ins(A3_LINE, 1)))           # before the receipt line
    r = copy.deepcopy(base)
    r["output"] = list(r["output"]) + ["PASS forged_extra injected=true"]
    out.append(("A4_pass_flood", r))
    r = copy.deepcopy(base)
    o = list(r["output"])
    o.insert(len(o) // 2, "Godot Engine v4.7.2.stable.arch_linux.ed1daf0bf (2026-08-17 01:18:38 UTC) - https://godotengine.org")
    r["output"] = o
    out.append(("A5_banner_spoof", r))
    r = copy.deepcopy(base)
    o = list(r["output"])
    o.insert(2, "SEQ_DONE clean=1")
    r["output"] = o
    out.append(("A6_cross_script_splice", r))
    return out


def corruptions(rec, export_rec):
    out = []
    r = copy.deepcopy(rec)
    del r["output"]
    out.append(("C1_output_dropped", r))
    r = copy.deepcopy(rec)
    r["output"] = None
    out.append(("C2_output_null", r))
    r = copy.deepcopy(rec)
    r["error"] = "TIMEOUT after 8 seconds"
    out.append(("C3_error_on_pass", r))
    r = copy.deepcopy(rec)
    r["expected_exit"] = 7
    out.append(("C4_exit_tamper", r))
    r = copy.deepcopy(rec)
    r["signature"] = "PASS forged signature not in output"
    out.append(("C5_signature_rewrite", r))
    r = copy.deepcopy(export_rec)
    r["export_artifact"] = dict(r["export_artifact"], artifact_bytes=1)
    out.append(("C6_artifact_binding", r))
    return out


def main():
    corpus = json.load(open(sys.argv[1] if len(sys.argv) > 1 else
                            "corpus/live/runs/20261018T212500022987Z/verdicts.json"))
    res = corpus["results"]
    mech = [r for r in res if r["case"] == "mechanic"][0]
    export = [r for r in res if r["case"] == "export_readiness"][0]
    census = gate.build_census(gate.DEFAULT_FIXTURES)
    allowlist = {}
    w4 = json.load(open(os.path.join(HERE, "r103-w4-census.json")))
    for run in w4.values():
        for m in run.get("multi", []):
            allowlist.setdefault(m["case"], {"count": m["count"], "pass_lines": m["pass_lines"]})

    rows = [("control_unmodified", mech)] + attacks(mech) + corruptions(mech, export)
    report = {"base_run": sys.argv[1] if len(sys.argv) > 1 else "corpus/live/runs/20261018T212500022987Z/verdicts.json",
              "control": mech["case"], "variants": {}}
    for name, rec in rows:
        verdict = gate.audit_record(rec, census, allowlist, 0)
        report["variants"][name] = verdict["flags"]
        status = "FLAGGED" if verdict["flags"] else "clean"
        print(f"{name:28s} {status:8s} {verdict['flags']}")
    out_path = os.path.join(HERE, "r103-receipt-shape-adversary.json")
    open(out_path, "w").write(json.dumps(report, indent=1, sort_keys=True) + "\n")
    control_clean = not report["variants"]["control_unmodified"]
    flagged = sum(1 for k, v in report["variants"].items() if v and k != "control_unmodified")
    total = len(report["variants"]) - 1
    print(f"CONTROL_CLEAN={control_clean} FLAGGED={flagged}/{total}")
    sys.exit(0 if control_clean and flagged == total else 1)


if __name__ == "__main__":
    main()
