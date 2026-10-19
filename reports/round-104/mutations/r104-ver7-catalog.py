#!/usr/bin/env python3
"""r104-V7 — registration review probe (KEY=V7).

Imports the LANDED `receipt_shape_flag` predicate from a scratch copy of
corpus/fixtures/run_battery.py (never executed) and replays:
  A. the r103 mut05 10-shape evasion catalog (per r103-mut5.md table),
  B. tab/whitespace PASS-family shapes (C2a routing),
  C. multi-PASS grammar rows (registration contract for res_uid_*),
  D. registration-shape rows (a synthetic res_uid_s01 row vs CASES pins).

Read-only over the repo. No run_battery.py execution.
"""
import copy
import hashlib
import importlib.util
import json
import shutil
import sys
from pathlib import Path

REPO = Path("/home/vgpnk/Projects/shokunin/game-dev-2d-shokunin")
SCRATCH = Path("/var/tmp/r104-ver7")
GATE_SRC = REPO / "corpus/fixtures/run_battery.py"
RUN = REPO / "corpus/live/runs/20261018T213443471189Z/verdicts.json"

BANNER = ("Godot Engine v4.7.2.stable.arch_linux.ed1daf0bf "
          "(2026-08-17 01:18:38 UTC) - https://godotengine.org")
FORGED_BANNER = ("Godot Engine v9.9.9.stable.official.deadbeefcafe "
                 "- https://godotengine.org")

BASES = {
    "launch": "export_launch_embed_boot",
    "prod": "export_prod_base_pck",
    "seq": "r100b_seq_clean",
    "simple": "input_route",
}


def load_gate():
    SCRATCH.mkdir(parents=True, exist_ok=True)
    copy_path = SCRATCH / "gate.py"
    shutil.copyfile(GATE_SRC, copy_path)
    src = copy_path.read_bytes()
    spec = importlib.util.spec_from_file_location("r104v7_gate", copy_path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    print("GATE_COPY=%s sha256=%s bytes=%d"
          % (copy_path, hashlib.sha256(src).hexdigest(), len(src)))
    return mod


def rows_by_case():
    data = json.loads(RUN.read_bytes())
    out = {}
    for r in data["results"]:
        out.setdefault(r.get("case"), r)
    return out, data["results"]


def mutate(row, ops, label):
    out = copy.deepcopy(row)
    lines = list(out["output"])
    for kind, idx, line in ops:
        if kind == "insert":
            lines.insert(idx, line)
        else:
            lines.append(line)
    out["output"] = lines
    out["_mut_note"] = label
    return out


def build_catalog(base):
    ev = []
    flood5 = ["PASS flooded=%d extra=true" % n for n in range(1, 6)]
    wl = base["simple"]["output"][-1]
    # A: r103 mut05 10 shapes
    ev.append(("s1a_banner_forged_seq", mutate(base["seq"], [("insert", 2, FORGED_BANNER)], "forged banner idx2")))
    ev.append(("s1b_banner_dup_launch", mutate(base["launch"], [("insert", 4, BANNER)], "exact banner dup idx4")))
    ev.append(("s2a_diag_other_family_simple", mutate(base["simple"], [("insert", 3, "EXPORT_LAUNCH_DIAG embed forged=true")], "foreign DIAG into input_route")))
    ev.append(("s2b_diag_forged_launch", mutate(base["launch"], [("insert", 6, "EXPORT_LAUNCH_DIAG embed forged=1")], "forged same-family DIAG")))
    ev.append(("s3a_flood5_simple", mutate(base["simple"], [("append", None, ln) for ln in flood5], "5 forged PASS appended to 1-PASS row")))
    ev.append(("s3b_flood1_seq", mutate(base["seq"], [("append", None, "PASS r100_gui forged=1")], "1 forged PASS on 14-PASS row")))
    ev.append(("s4a_tab_lead_simple", mutate(base["simple"], [("append", None, "\tPASS forged=true")], "leading-tab forged PASS")))
    ev.append(("s4b_trail_space_simple", mutate(base["simple"], [("append", None, wl + " ")], "trailing-space dup of legit PASS")))
    ev.append(("s4c_trail_nbsp_simple", mutate(base["simple"], [("append", None, "PASS forged=true\u00a0")], "trailing NBSP forged PASS")))
    ev.append(("s4d_tab_after_pass_simple", mutate(base["simple"], [("append", None, "PASS\tforged=true")], "TAB after PASS token")))
    # B: whitespace-PASS family extension (C2a)
    ev.append(("t1_two_space_after_pass", mutate(base["simple"], [("append", None, "PASS  forged=true")], "two spaces after PASS")))
    ev.append(("t2_tab_lead_two_space", mutate(base["simple"], [("append", None, "\tPASS  forged=true")], "tab-lead + two-space")))
    ev.append(("t3_pass_tab_only", mutate(base["simple"], [("append", None, "PASS\t")], "PASS + TAB, no payload")))
    ev.append(("t4_pass_nbsp_after", mutate(base["simple"], [("append", None, "PASS\u00a0forged=true")], "NBSP after PASS token")))
    ev.append(("t5_pass_cr_after", mutate(base["simple"], [("append", None, "PASS\rforged=true")], "CR after PASS token")))
    ev.append(("t6_pass_tab_pin_inside", mutate(base["simple"], [("append", None, "PASS\tsomething route=parse_input_event-to-Node._input")], "PASS-TAB carrying the row pin substring")))
    # C: multi-PASS grammar contract
    ev.append(("g1_grammar_row_extra_pass", mutate(base["seq"], [("append", None, "PASS r100_gui forged=1")], "grammar row +1 PASS")))
    ev.append(("g2_grammar_row_intact", mutate(base["seq"], [], "grammar row intact"), "grammar row intact"))
    # D: registration-shape synthetic res_uid row (not a CASES row at all)
    syn = {"case": "res_uid_s01_pack", "script": "res_uid_s01.gd",
           "verdict": "PASS", "signature": "PASS res_uid s01 uid_roundtrip=true",
           "output": [BANNER, "", "PASS res_uid s01 uid_roundtrip=true"],
           "expected_errors": []}
    ev.append(("d1_res_uid_unregistered", syn, "res_uid row with no CASES entry"))
    ev.append(("d3_res_uid_pin_mismatch", {**syn, "signature": "PASS res_uid s01 OTHER=true"},
               "res_uid row: CASES-pin absent -> fail_closed path (case not in CASES)"))
    syn2 = copy.deepcopy(syn)
    syn2["output"] = [BANNER, "", "PASS res_uid s01 uid_roundtrip=true", "PASS res_uid s01 extra=true"]
    ev.append(("d2_res_uid_unregistered_twopass", syn2, "res_uid row, 2 PASS, unregistered"))
    ev.append(("d4_registered_case_unregistered_script",
               {**base["simple"], "case": "input_route", "output": [BANNER, "", "PASS route=parse_input_event-to-Node._input key=R", "PASS extra=1"]},
               "registered case, 2 PASS -> unaccounted_pass_lines"))
    return ev


def main():
    mod = load_gate()
    flag = mod.receipt_shape_flag
    by_case, all_rows = rows_by_case()
    print("RUN=%s rows=%d cases=%d" % (RUN, len(all_rows), len(by_case)))
    base = {k: by_case[v] for k, v in BASES.items()}
    for k, v in base.items():
        print("BASE %-7s case=%-26s n_out=%d" % (k, v["case"], len(v["output"])))
    catalog = build_catalog(base)

    results = []
    for entry in catalog:
        name, row = entry[0], entry[1]
        note = entry[2] if len(entry) > 2 else row.get("_mut_note", "")
        f = flag(row)
        results.append({"name": name, "note": note, "n_flags": len(f),
                        "flags": f})
        print("%-30s flags=%d %s" % (name, len(f),
                                     json.dumps(f)[:220]))
    # green controls: the 4 unmutated bases must be silent
    for k in BASES:
        f = flag(base[k])
        print("green_%-7s flags=%d %s" % (k, len(f), json.dumps(f)[:160]))
        results.append({"name": "green_%s" % k, "n_flags": len(f), "flags": f})
    (SCRATCH / "v7-catalog-results.json").write_text(
        json.dumps({"run": str(RUN), "results": results}, indent=1,
                   ensure_ascii=False) + "\n")
    print("WROTE %s" % (SCRATCH / "v7-catalog-results.json"))


if __name__ == "__main__":
    sys.exit(main())
