#!/usr/bin/env python3
"""r104 V3: drive the r103-mut5 evasion shapes (10) + 2 new adversarial shapes
against BOTH landed receipt-shape gates and report the per-shape verdict.

  gate A (in-battery):  receipt_shape_audit / receipt_shape_flag imported from a
                        scratch copy of HEAD corpus/fixtures/run_battery.py
  gate B (standalone):  audit / audit_record imported from
                        reports/round-103/mutations/r103-receipt-shape-gate.py

Usage: python3 r104-ver3-evasion-matrix.py <head_run_battery.py> <gate.py> <out.json>
"""
import copy
import importlib.util
import json
import sys
from pathlib import Path

REPO = Path("/home/vgpnk/Projects/shokunin/game-dev-2d-shokunin")
RUN = REPO / "corpus/live/runs/20261018T213443471189Z/verdicts.json"
OUT = Path(sys.argv[3])

BANNER = ("Godot Engine v4.7.2.stable.arch_linux.ed1daf0bf "
          "(2026-08-17 01:18:38 UTC) - https://godotengine.org")
FORGED_BANNER = ("Godot Engine v9.9.9.stable.official.deadbeefcafe "
                 "- https://godotengine.org")
BASES = {"launch": "export_launch_embed_boot", "prod": "export_prod_base_pck",
         "seq": "r100b_seq_clean", "simple": "input_route"}


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def mutate(row, ops, label):
    out = copy.deepcopy(row)
    lines = list(out["output"])
    for kind, idx, line in ops:
        lines.insert(idx, line) if kind == "insert" else lines.append(line)
    out["output"] = lines
    out["_mut_note"] = label
    return out


def build(rows):
    by = {}
    for key, case in BASES.items():
        by[key] = next(r for r in rows if r["case"] == case)
    ev = []
    ev.append(("s1a_banner_forged_seq", mutate(by["seq"], [("insert", 2, FORGED_BANNER)], "forged banner idx2")))
    ev.append(("s1b_banner_dup_launch", mutate(by["launch"], [("insert", 4, BANNER)], "banner duplicate idx4")))
    ev.append(("s2a_diag_other_family_simple", mutate(by["simple"], [("insert", 3, "EXPORT_LAUNCH_DIAG embed forged=true")], "foreign DIAG into input_route")))
    ev.append(("s2b_diag_forged_launch", mutate(by["launch"], [("insert", 6, "EXPORT_LAUNCH_DIAG embed forged=1")], "forged same-family DIAG")))
    ev.append(("s3a_flood5_simple", mutate(by["simple"], [("append", None, f"PASS flooded={n} extra=true") for n in range(1, 6)], "5 forged PASS appended")))
    ev.append(("s3b_flood1_seq", mutate(by["seq"], [("append", None, "PASS r100_gui forged=1")], "1 forged PASS appended to 14-PASS row")))
    wl = by["simple"]["output"][-1]
    ev.append(("s4a_tab_lead_simple", mutate(by["simple"], [("append", None, "\tPASS forged=true")], "leading-tab PASS")))
    ev.append(("s4b_trail_space_simple", mutate(by["simple"], [("append", None, wl + " ")], "trailing-space duplicate")))
    ev.append(("s4c_trail_nbsp_simple", mutate(by["simple"], [("append", None, "PASS forged=true\u00a0")], "trailing NBSP")))
    ev.append(("s4d_tab_after_pass_simple", mutate(by["simple"], [("append", None, "PASS\tforged=true")], "TAB after PASS token")))
    # V3 new shapes: export-artifact tampering on the row that actually carries one
    er = next(r for r in rows if r["case"] == "export_readiness")
    a = copy.deepcopy(er)
    a["export_artifact"] = dict(a["export_artifact"], artifact_bytes=a["export_artifact"]["artifact_bytes"] + 1)
    ev.append(("V3a_export_bytes_tamper", a))
    b = copy.deepcopy(er)
    b["export_artifact"] = dict(b["export_artifact"], artifact_sha256="NOPE")
    ev.append(("V3b_export_digest_tamper", b))
    return ev, by


def main():
    gate_a = load(Path(sys.argv[1]), "v3_gate_a")
    gate_b = load(Path(sys.argv[2]), "v3_gate_b")
    payload = json.loads(RUN.read_text())
    rows = payload["results"]
    ev, by = build(rows)
    census = gate_b.build_census(str(REPO / "corpus" / "fixtures"))
    allowlist = json.loads((REPO / "reports/round-103/mutations/r103-w4-census.json").read_text())

    report = {"run": str(RUN), "shapes": [], "green_controls": {}}
    print(f"{'shape':<34} {'A:in-battery':<14} {'B:standalone':<14} notes")
    for name, row in ev:
        fa = gate_a.receipt_shape_audit([row])["flags"]
        fb = gate_b.audit_record(row, census, allowlist, 0) or []
        fa = [f for f in fa if f.get("why") != "dead_shape_allowlist_entry"]
        print(f"{name:<34} {('FLAG' if fa else 'miss'):<14} {('FLAG' if fb else 'miss'):<14} "
              f"{[f.get('why') for f in fa]} / {fb}")
        report["shapes"].append({"shape": name, "gate_a_flags": fa, "gate_b_flags": fb,
                                 "a_caught": bool(fa), "b_caught": bool(fb)})
    for key, row in by.items():
        fa = [f for f in gate_a.receipt_shape_audit([row])["flags"]
              if f.get("why") != "dead_shape_allowlist_entry"]
        fb = gate_b.audit_record(row, census, allowlist, 0) or []
        print(f"{'green_control:' + key:<34} {('FLAG' if fa else 'clean'):<14} {('FLAG' if fb else 'clean'):<14} {fa} / {fb}")
        report["green_controls"][key] = {"gate_a_flags": fa, "gate_b_flags": fb}
    a_hits = sum(1 for s in report["shapes"] if s["a_caught"])
    b_hits = sum(1 for s in report["shapes"] if s["b_caught"])
    report["gate_a_caught"] = f"{a_hits}/{len(ev)}"
    report["gate_b_caught"] = f"{b_hits}/{len(ev)}"
    print(f"TOTAL gate_a(in-battery)={a_hits}/{len(ev)}  gate_b(standalone)={b_hits}/{len(ev)}")
    OUT.write_text(json.dumps(report, indent=1) + "\n")
    print(f"artifact={OUT}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
