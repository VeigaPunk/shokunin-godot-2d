#!/usr/bin/env python3
"""r104-connector — PASS-prefix census divergence probe (read-only).

Measures, over the stored receipts and against the LANDED gate predicate:

  1. the landed census form (`line.startswith("PASS ")`, run_battery.py:1904)
     vs the r103-G0 *proposal* form (`^\\s*PASS(\\b|$|[:=])`);
  2. which synthetic evasion shapes each form can see;
  3. the false-positive surface of the widening on real receipt bytes;
  4. the real gate's flag set per shape (imported, not reimplemented);
  5. the same flag set under a one-line census mutant.

Never executes run_battery.py as a program (no --probe flags); it only
imports the module for its pure predicates.
"""
import copy
import glob
import importlib.util
import json
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
RB = REPO / "corpus" / "fixtures" / "run_battery.py"

LANDED = lambda line: line.startswith("PASS ")
PROPOSAL = re.compile(r"^\s*PASS(\b|$|[:=])")

SHAPES = {
    "space_PASS": "PASS r100_gui forged=1",
    "tab_after_PASS": "PASS\tforged=true",
    "lead_tab": "\tPASS forged=true",
    "lead_space": "  PASS forged=true",
    "lead_2tab": "\t\tPASS forged=true",
    "PASS_equals": "PASS=forged",
    "PASS_colon": "PASS:forged",
    "PASS_bare": "PASS",
    "PASS_word_concat": "PASSED_forged=1",
    "PASS_dash": "PASS-forged",
}


def load_module(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def load_mutant():
    src = RB.read_text()
    old = '    pass_lines = [line for line in output if line.startswith("PASS ")]'
    new = ('    _PASS_LINE_RE = re.compile(r"^\\s*PASS(?:\\b|$|[:=])")\n'
           '    pass_lines = [line for line in output if _PASS_LINE_RE.match(line)]')
    assert src.count(old) == 1, "census line not unique: %d" % src.count(old)
    tmp = Path("/var/tmp/r104-connector/run_battery_mutant.py")
    tmp.parent.mkdir(parents=True, exist_ok=True)
    tmp.write_text(src.replace(old, new))
    return load_module(tmp, "rb_mutant")


def receipts():
    return sorted(glob.glob(str(REPO / "corpus" / "live" / "runs" / "*" / "verdicts.json")))


def main():
    print("== 1. predicate divergence on synthetic shapes ==")
    print(f"{'shape':18s} {'landed':>7s} {'proposal':>9s}")
    for name, line in SHAPES.items():
        print(f"{name:18s} {str(bool(LANDED(line))):>7s} {str(bool(PROPOSAL.match(line))):>9s}")

    print("\n== 2/3. real receipt bytes ==")
    files = receipts()
    print("verdicts.json files:", len(files))
    tot = div = lead = rows = 0
    for rp in files:
        for r in json.load(open(rp))["results"]:
            rows += 1
            for line in r.get("output") or []:
                if not isinstance(line, str):
                    continue
                if PROPOSAL.match(line):
                    tot += 1
                    if not LANDED(line):
                        div += 1
                        print("  DIVERGENT:", repr(line[:80]), "case", r.get("case"))
                if re.match(r"^\s+PASS", line):
                    lead += 1
    print(f"rows={rows} proposal_matches={tot} diverging_from_landed={div} leading_ws_PASS={lead}")

    print("\n== 4/5. real gate vs one-line census mutant, per shape ==")
    rb = load_module(RB, "rb_real")
    rbm = load_mutant()
    run = REPO / "corpus" / "live" / "runs" / "20261018T213443471189Z" / "verdicts.json"
    rows_ = json.load(open(run))["results"]
    by = {r["case"]: r for r in rows_}

    def mut(base_case, ops, label):
        r = copy.deepcopy(by[base_case])
        out = list(r["output"])
        for kind, idx, line in ops:
            out.insert(idx, line) if kind == "insert" else out.append(line)
        r["output"] = out
        r["_mut"] = label
        return r

    wl = by["input_route"]["output"][-1]
    shapes = []
    for name, case in (("CTRL_simple", "input_route"), ("CTRL_seq", "r100b_seq_clean"),
                       ("CTRL_launch", "export_launch_embed_boot"), ("CTRL_prod", "export_prod_base_pck")):
        shapes.append((name, copy.deepcopy(by[case])))
    shapes += [
        ("s1a_banner_forged_seq", mut("r100b_seq_clean", [("insert", 2,
            "Godot Engine v9.9.9.stable.official.deadbeefcafe - https://godotengine.org")], "forged banner")),
        ("s2a_diag_other_simple", mut("input_route", [("insert", 3,
            "EXPORT_LAUNCH_DIAG embed forged=true")], "foreign diag")),
        ("s2b_diag_forged_launch", mut("export_launch_embed_boot", [("insert", 6,
            "EXPORT_LAUNCH_DIAG embed forged=1")], "forged diag")),
        ("s3a_flood5_simple", mut("input_route", [("append", None,
            "PASS flooded=%d extra=true" % n) for n in range(1, 6)], "flood5")),
        ("s3b_flood1_seq", mut("r100b_seq_clean", [("append", None, "PASS r100_gui forged=1")], "flood1")),
        ("s4a_tab_lead_simple", mut("input_route", [("append", None, "\tPASS forged=true")], "lead tab")),
        ("s4b_trail_space_simple", mut("input_route", [("append", None, wl + " ")], "trail space")),
        ("s4c_trail_nbsp_simple", mut("input_route", [("append", None, "PASS forged=true\u00a0")], "nbsp")),
        ("s4d_tab_after_pass_simple", mut("input_route", [("append", None, "PASS\tforged=true")], "tab after PASS")),
        ("s4e_lead_space", mut("input_route", [("append", None, "  PASS forged=true")], "lead space")),
        ("s4f_PASS_equals", mut("input_route", [("append", None, "PASS=forged")], "PASS=")),
        ("s4g_PASS_bare", mut("input_route", [("append", None, "PASS")], "bare PASS")),
    ]
    print(f"{'shape':26s} {'before':>7s} {'after':>6s}  why_after")
    for name, row in shapes:
        f0 = rb.receipt_shape_flag(copy.deepcopy(row))
        f1 = rbm.receipt_shape_flag(copy.deepcopy(row))
        print(f"{name:26s} {len(f0):>7d} {len(f1):>6d}  {[x.get('why') for x in f1]}")

    print("\n== 5b. real receipts under the mutant census ==")
    for rp in files:
        d = json.load(open(rp))
        audit = [r for r in d["results"] if isinstance(r.get("output"), list)]
        n = sum(1 for r in audit if rbm.receipt_shape_flag(r))
        print(f"  {Path(rp).parent.name} rows={len(d['results'])} "
              f"auditable={len(audit)} flagged={n}")


if __name__ == "__main__":
    sys.exit(main())
