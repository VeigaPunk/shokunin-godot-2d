#!/usr/bin/env python3
"""r104-V7 — PASS-line census + registration-contract probe (KEY=V7).

A. False-positive census: for every stored run, count lines that match each
   candidate "PASS-line" predicate, and list every line that a TIGHTENED
   predicate (all-PASS-prefixed) would newly census. Any such line on a green
   run is a false-positive cost of the tightening.
B. Registration contract: simulate adding a res_uid_* row to the gate's CASES
   table (monkeypatch CASES_SIG_BY_CASE) and measure the gate's behaviour for
   single-PASS / multi-PASS / pin-absent registered rows.
"""
import copy
import importlib.util
import json
import shutil
import sys
from pathlib import Path

REPO = Path("/home/vgpnk/Projects/shokunin/game-dev-2d-shokunin")
SCRATCH = Path("/var/tmp/r104-ver7")
GATE_SRC = REPO / "corpus/fixtures/run_battery.py"
RUNS = sorted((REPO / "corpus/live/runs").glob("*/verdicts.json"))

PREDS = {
    "P1_startswith_PASS_space": lambda l: l.startswith("PASS "),
    "P2_startswith_PASS": lambda l: l.startswith("PASS"),
    "P3_lstrip_startswith_PASS": lambda l: l.lstrip().startswith("PASS"),
    "P4_first_token_PASS": lambda l: l.split(None, 1)[0] == "PASS" if l.strip() else False,
}


def load_gate():
    SCRATCH.mkdir(parents=True, exist_ok=True)
    copy_path = SCRATCH / "gate.py"
    shutil.copyfile(GATE_SRC, copy_path)
    spec = importlib.util.spec_from_file_location("r104v7_gate", copy_path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def census():
    print("== A. PASS-line predicate census over stored runs ==")
    totals = {k: 0 for k in PREDS}
    rows_total = 0
    newly = {}
    for rp in RUNS:
        data = json.loads(rp.read_bytes())
        rows = data["results"]
        rows_total += len(rows)
        counts = {k: 0 for k in PREDS}
        for r in rows:
            out = r.get("output")
            if not isinstance(out, list):
                continue
            for line in out:
                if not isinstance(line, str):
                    continue
                for k, fn in PREDS.items():
                    if fn(line):
                        counts[k] += 1
        for k in PREDS:
            totals[k] += counts[k]
        # newly-censused lines = P3 minus P1
        extra = []
        for r in rows:
            out = r.get("output")
            if not isinstance(out, list):
                continue
            for line in out:
                if isinstance(line, str) and PREDS["P3_lstrip_startswith_PASS"](line) \
                        and not PREDS["P1_startswith_PASS_space"](line):
                    extra.append((r.get("case"), line))
        if extra:
            newly[str(rp.parent.name)] = extra
        print("%-28s rows=%3d P1=%4d P2=%4d P3=%4d P4=%4d  newly(P3-P1)=%d"
              % (rp.parent.name, len(rows), counts["P1_startswith_PASS_space"],
                 counts["P2_startswith_PASS"], counts["P3_lstrip_startswith_PASS"],
                 counts["P4_first_token_PASS"], len(extra)))
    print("TOTAL rows=%d  P1=%d P2=%d P3=%d P4=%d"
          % (rows_total, totals["P1_startswith_PASS_space"],
             totals["P2_startswith_PASS"], totals["P3_lstrip_startswith_PASS"],
             totals["P4_first_token_PASS"]))
    print("NEWLY_CENSUSED_RUNS=%s" % json.dumps(
        {k: len(v) for k, v in newly.items()}))
    for run, items in newly.items():
        for case, line in items[:12]:
            print("   NEW %-28s %-26s %r" % (run, case, line[:90]))
    # any line where P2 differs from P1 -> 'PASS'-prefix but not 'PASS '
    diff = []
    for rp in RUNS:
        for r in json.loads(rp.read_bytes())["results"]:
            out = r.get("output")
            if not isinstance(out, list):
                continue
            for line in out:
                if isinstance(line, str) and PREDS["P2_startswith_PASS"](line) \
                        and not PREDS["P1_startswith_PASS_space"](line):
                    diff.append((rp.parent.name, r.get("case"), line))
    print("P2_minus_P1 (any 'PASS'-prefixed, non-'PASS '-prefixed line) = %d"
          % len(diff))
    for run, case, line in diff[:20]:
        print("   D %-26s %-26s %r" % (run, case, line[:90]))
    return newly, diff


def registration(mod):
    print()
    print("== B. registration contract (simulated CASES entry for res_uid_s01) ==")
    flag = mod.receipt_shape_flag
    banner = ("Godot Engine v4.7.2.stable.arch_linux.ed1daf0bf "
              "(2026-08-17 01:18:38 UTC) - https://godotengine.org")
    # Case A: properly registered, one PASS line == pin
    mod.CASES_SIG_BY_CASE["res_uid_s01_roundtrip"] = (
        "PASS res_uid s01 uid_roundtrip=true")
    row1 = {"case": "res_uid_s01_roundtrip", "verdict": "PASS",
            "output": [banner, "", "PASS res_uid s01 uid_roundtrip=true"],
            "expected_errors": []}
    print("A1 registered single-PASS row         flags=%s" % json.dumps(flag(row1)))
    # Case B: registered, but the fixture prints 2 PASS lines (per-arm style)
    row2 = copy.deepcopy(row1)
    row2["output"] = [banner, "",
                      "PASS res_uid s01 uid_roundtrip=true",
                      "PASS res_uid s01 cache_identity=true"]
    print("A2 registered 2-PASS row, no grammar  flags=%s" % json.dumps(flag(row2)))
    # Case C: registered WITH a grammar declaration -> silent
    mod.RECEIPT_MULTI_PASS_GRAMMAR["res_uid_s01_roundtrip"] = (
        ("res_uid", "s01"), ("res_uid", "s01"))
    print("A3 + RECEIPT_MULTI_PASS_GRAMMAR entry flags=%s" % json.dumps(flag(row2)))
    # Case D: registered, PASS line does not carry the pin
    row4 = copy.deepcopy(row1)
    row4["output"] = [banner, "", "PASS res_uid s01 other=true"]
    print("A4 registered, PASS line off-pin      flags=%s" % json.dumps(flag(row4)))
    # Case E: registered, verdict PASS but pin absent entirely
    row5 = copy.deepcopy(row1)
    row5["output"] = [banner, "", "res_uid s01 done"]
    print("A5 registered, pin absent             flags=%s" % json.dumps(flag(row5)))
    # Case F: registered with a multi-line pin (signature list) -> anchors
    mod.CASES_SIG_BY_CASE["res_uid_s02"] = ["PASS res_uid s02 a=true",
                                            "PASS res_uid s02 b=true"]
    row6 = {"case": "res_uid_s02", "verdict": "PASS",
            "output": [banner, "", "PASS res_uid s02 a=true"],
            "expected_errors": []}
    print("A6 list-pin registered, 1 of 2 lines  flags=%s" % json.dumps(flag(row6)))
    # Case G: expected_errors-shaped registration (diagnostic-pinned row)
    mod.CASES_SIG_BY_CASE["res_uid_s03"] = "ERROR: res_uid s03 refused"
    row7 = {"case": "res_uid_s03", "verdict": "PASS",
            "output": [banner, "", "PASS res_uid s03 refused=true",
                       "ERROR: res_uid s03 refused"],
            "expected_errors": ["ERROR: res_uid s03 refused"]}
    print("A7 diagnostic-pinned registration     flags=%s" % json.dumps(flag(row7)))
    # Case H: unregistered res_uid case (F5 skip) -> silent by design
    row8 = {"case": "res_uid_s09_unregistered", "verdict": "PASS",
            "output": [banner, "", "PASS junk"], "expected_errors": []}
    print("A8 UNREGISTERED case (F5 skip)        flags=%s" % json.dumps(flag(row8)))


def main():
    mod = load_gate()
    print("GATE_SRC=%s" % GATE_SRC)
    census()
    registration(mod)


if __name__ == "__main__":
    sys.exit(main())
