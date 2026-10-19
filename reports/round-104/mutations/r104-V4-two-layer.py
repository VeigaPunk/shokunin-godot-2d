#!/usr/bin/env python3
"""r104-ver4 — two-layer check: does a faked pin survive BOTH the shape gate
(receipt_shape_flag) and the process classifier (classify_process)?

classify_process is a nested function inside run_battery.py's main(), so it is
reconstructed by exec'ing its exact source text with the 4-space indent
removed — no reimplementation.
"""
import json
import re
import sys
from pathlib import Path

REPO = Path.cwd()
B = REPO / "corpus/fixtures/run_battery.py"
GREEN = REPO / "corpus/live/runs/20261019T005558434174Z/verdicts.json"


def load():
    src = B.read_text()
    head = src.partition("\ndef main():\n")[0]
    ns = {"__name__": "g", "__file__": str(B)}
    exec(compile(head, str(B), "exec"), ns)
    i = src.index("    def classify_process(")
    j = src.index("    def classify_streams(")
    body = src[i:j].rstrip()
    body = "\n".join(l[4:] if l.startswith("    ") else l for l in body.splitlines())
    g = {}
    exec(body, g)
    return ns, g["classify_process"]


def main():
    ns, cp = load()
    flag = ns["receipt_shape_flag"]
    d = json.loads(GREEN.read_bytes())
    rows = {r["case"]: r for r in d["results"]}
    sp = rows["save_process_missing"]
    ir = rows["input_route"]
    sp_pin = ("ERROR: SAVE PROCESS EXPECTED NEGATIVE: missing file rejected "
              "signature=FILE_NOT_FOUND")
    ir_pin = "PASS route=parse_input_event-to-Node._input key=R receipt_count=1 frames=3"
    sp_ee = sp["expected_errors"]
    ir_ee = ir["expected_errors"] if ir.get("expected_errors") else ()

    print("save_process_missing expected_errors=%r" % (sp_ee,))
    print("input_route expected_errors=%r" % (ir_ee,))

    cases = [
        ("green_save_process", sp["output"], sp_pin, sp_ee, "save_process_missing"),
        ("green_input_route", ir["output"], ir_pin, ir_ee, "input_route"),
        ("E23_saveprocess_forged_pass",
         [sp["output"][0], "", "PASS save_process forged=true exfil=1"] + sp["output"][3:],
         sp_pin, sp_ee, "save_process_missing"),
        ("E24_saveprocess_error_junk",
         [sp["output"][0], "", sp["output"][2], sp_pin + ", EXFIL forged=1"] + sp["output"][4:],
         sp_pin, sp_ee, "save_process_missing"),
        ("E25_saveprocess_both",
         [sp["output"][0], "", "PASS save_process forged=true exfil=1",
          sp_pin + ", EXFIL forged=1"] + sp["output"][4:],
         sp_pin, sp_ee, "save_process_missing"),
        ("E20_diagpin_full_anchor_decoy",
         [ir["output"][0], "", "ERROR: " + ir_pin, "PASS forged=true"],
         ir_pin, ir_ee, "input_route"),
        ("E1_tabpass_flood5_simple",
         ir["output"] + ["PASS\tflooded=%d extra=true" % n for n in range(1, 6)],
         ir_pin, ir_ee, "input_route"),
        ("E4_pin_on_tabline_simple",
         [ir["output"][0], "", "PASS\t" + ir_pin], ir_pin, ir_ee, "input_route"),
        ("E12_anchor_only_leadtab",
         [ir["output"][0], "", "\tPASS route=parse_input_event-to-Node._input"],
         ir_pin, ir_ee, "input_route"),
    ]

    print("\n%-34s %-12s %-10s %s" % ("case", "gate", "classifier", "double-fake?"))
    for name, lines, pin, ee, case in cases:
        row = {"case": case, "verdict": "PASS", "output": lines}
        if ee:
            row["expected_errors"] = ee
        g = flag(row)
        out = "\n".join(lines) + "\n"
        c = cp(0, None, out, 0, pin, ee or ())
        verdict = "ACCEPTED" if (not g and c) else ("gate-caught" if g else "classifier-caught")
        print("%-34s %-12s %-10s %s" % (
            name, "CLEAN" if not g else "FLAG(%s)" % ",".join(f["why"] for f in g),
            c, verdict))


if __name__ == "__main__":
    sys.exit(main())
