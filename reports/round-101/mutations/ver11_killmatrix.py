#!/usr/bin/env python3
"""VER-11 kill-matrix evaluator (r101).

Reads the VER-11 probe receipts and the landed r100 CASES pins, then evaluates
every candidate pin shape over the real captured transcripts. No Godot call, no
run_battery.py execution: the landed row predicate is reproduced from the
harness source (`classify_process` + its per-row allowlist), everything else is
arithmetic on the captured bytes.

Transcripts: corpus/live/r101-ver11/receipts/seq_*.out/.err
Pins:        corpus/live/r101-ver11/pins.json (parsed from corpus/fixtures/run_battery.py)
Output:      corpus/live/r101-ver11/killmatrix.json + stdout table
"""
import ast
import hashlib
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
HARNESS = REPO / "corpus" / "fixtures" / "run_battery.py"
LIVE = REPO / "corpus" / "live" / "r101-ver11"
RECEIPTS = LIVE / "receipts"
ROWS = {"clean": "r100b_seq_clean", "noclean": "r100b_seq_noclean"}
ALLOW = {"r100b_seq_clean": ('ERROR: Parameter "t" is null.',),
         "r100b_seq_noclean": ('ERROR: Parameter "t" is null.',)}

# (arm, clean, receipt basename, forgery description)
ARMS = [
    ("base", "1", "seq_base_clean1", "control, unmutated fixture"),
    ("base", "0", "seq_base_clean0", "control, unmutated fixture"),
    ("forged_nopass", "1", "seq_forged_clean1", "extra non-PASS line 'FORGED r100_gui cursor ...' after hover"),
    ("forged_nopass", "0", "seq_forged_clean0", "extra non-PASS line 'FORGED r100_gui cursor ...' after hover"),
    ("forged_pass", "0", "seq_extra_pass_clean0", "extra PASS-dialect line 'PASS r100_gui hover FORGED_EXTRA_CELL_OUTPUT h0=P'"),
    ("substitute", "1", "seq_subst_clean1", "pinned cursor-c0 value replaced (30.0,14.0)->(99.0,99.0)"),
]


def sha(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()


def harness_classify():
    tree = ast.parse(HARNESS.read_text())
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "classify_process":
            mod = ast.Module(body=[node], type_ignores=[])
            ast.fix_missing_locations(mod)
            ns = {}
            exec(compile(mod, "<classify_process>", "exec"), ns)
            return ns["classify_process"]
    raise SystemExit("classify_process not found")


def cell_lines(text):
    return [ln for ln in text.splitlines() if ln.startswith("PASS r100_gui ")]


def cell_of(line):
    return line.split()[2]


def merged(name):
    return (RECEIPTS / f"{name}.out").read_text() + (RECEIPTS / f"{name}.err").read_text()


def main():
    pins = {r["name"]: r for r in json.loads((LIVE / "pins.json").read_text())}
    classify = harness_classify()
    out = {"receipts": {}, "divergence_census": {}, "predicates": {}, "offy": {}}

    texts = {(a, c, n): merged(n) for a, c, n, _ in ARMS}
    for (a, c, n), text in texts.items():
        pass_lines = cell_lines(text)
        out["receipts"][n] = {"merged_sha256": sha(text), "merged_lines": len(text.splitlines()),
                              "pass_r100_gui_lines": len(pass_lines),
                              "cells_in_order": [cell_of(l) for l in pass_lines]}

    # ---- divergence census: replay cell vs the landed fresh-process pin -----
    for clean, row_name in (("1", ROWS["clean"]), ("0", ROWS["noclean"])):
        replay = cell_lines(texts[("base", clean, f"seq_base_clean{clean}")])
        census = {}
        for line in replay:
            cell = cell_of(line)
            fresh = pins.get(f"r100_gui_{cell}", {}).get("evidence")
            if fresh is None:
                census[cell] = "no-fresh-row"
            elif line == fresh:
                census[cell] = "identical"
            else:
                i = next((k for k, (x, y) in enumerate(zip(line, fresh)) if x != y),
                         min(len(line), len(fresh)))
                census[cell] = {"state": "diverges", "first_diff_col": i,
                                "replay": line[max(0, i - 15):i + 55],
                                "fresh": fresh[max(0, i - 15):i + 55]}
        out["divergence_census"][f"clean={clean}"] = {
            "pinned_by_seq_row": row_name,
            "seq_row_pin_cell": cell_of(pins[row_name]["evidence"]),
            "cells": census,
            "diverging": [c for c, v in census.items() if v not in ("identical", "no-fresh-row")],
            "identical_count": sum(1 for v in census.values() if v == "identical")}

    # ---- predicate matrix ---------------------------------------------------
    def p_landed(text, pin, code, row):
        return classify(code, None, text, 0, pin, ALLOW[row]), None

    def p_block(text, pin, code, row):
        ok = pin in text
        detail = None
        if not ok:
            lines = text.splitlines()
            exp = pin.splitlines()
            for k, want in enumerate(exp):
                got = lines[k] if k < len(lines) else "<EOF>"
                if got != want:
                    detail = {"first_mismatch_line": k, "expected": want[:110], "actual": got[:110]}
                    break
            if detail is None:
                detail = {"note": "block absent but every line matched at same index"}
        return ok, detail

    def p_ordered(text, pin, code, row):
        return cell_lines(text) == pin.splitlines()[:-1], None

    def p_multiset(text, pin, code, row):
        want = pin.splitlines()[:-1]
        have = cell_lines(text)
        return sorted(have) == sorted(want), {"extra": [l[:70] for l in have if l not in want][:4]}

    def p_count(text, pin, code, row):
        n = len(cell_lines(text))
        return n == 14, {"pass_line_count": n}

    PREDS = [("landed_1line_pin", p_landed), ("full_replay_block_pin", p_block),
             ("ordered_14cell_equality", p_ordered), ("line_multiset_equality", p_multiset),
             ("pass_line_count_14", p_count)]

    blocks = {}
    for clean, row_name in (("1", ROWS["clean"]), ("0", ROWS["noclean"])):
        base = texts[("base", clean, f"seq_base_clean{clean}")]
        blocks[clean] = "\n".join(cell_lines(base) + [f"SEQ_DONE clean={clean}"])
        table = {}
        for a, c, n, desc in ARMS:
            if c != clean:
                continue
            text = texts[(a, c, n)]
            verdicts = {}
            for key, fn in PREDS:
                pin = pins[row_name]["evidence"] if key == "landed_1line_pin" else blocks[clean]
                ok, detail = fn(text, pin, 0, row_name)
                verdicts[key] = {"verdict": "PASS" if ok else "FAIL", "detail": detail}
            table[f"{a}/{n}"] = {
                "forgery": desc, "verdicts": verdicts,
                "battery_stdout_prefix": f"{verdicts['landed_1line_pin']['verdict']} {row_name}: exit=0 signature="
                                         + repr(pins[row_name]["evidence"])[:64] + "...",
                "postfix_stdout_prefix": f"{verdicts['full_replay_block_pin']['verdict']} {row_name}: exit=0 signature="
                                         + repr(blocks[clean])[:56] + f"...({len(blocks[clean])}B)"}
        out["predicates"][f"clean={clean}"] = {
            "row": row_name, "block_sha256": sha(blocks[clean]),
            "block_bytes": len(blocks[clean]), "block_lines": len(blocks[clean].splitlines()),
            "arms": table}

    # ---- offy dead-flag census (bytes) --------------------------------------
    arm_text = {n: (RECEIPTS / f"{n}.out").read_text() for n in
                ("offy_absent", "offy_1000", "offy_999999", "offy_x1000")}
    pass_sha = {n: sha("\n".join(l for l in t.splitlines() if l.startswith("PASS")))
                for n, t in arm_text.items()}
    fixture = (REPO / "corpus/fixtures/r95b_order.gd").read_text()
    celloff = fixture.split("func _arm_celloff")[1].split("# --------------------------------------------------------------- rigid")[0]
    out["offy"] = {
        "pass_line_sha256": pass_sha,
        "pass_line_identical_1000_vs_absent": pass_sha["offy_1000"] == pass_sha["offy_absent"],
        "pass_line_identical_999999_vs_absent": pass_sha["offy_999999"] == pass_sha["offy_absent"],
        "whole_output_identical_999999_vs_absent": arm_text["offy_999999"] == arm_text["offy_absent"],
        "whole_output_diff_1000_vs_absent": [l for l in arm_text["offy_1000"].splitlines()
                                            if l not in arm_text["offy_absent"].splitlines()],
        "off_x_pin_changes": pass_sha["offy_x1000"] != pass_sha["offy_absent"],
        "fixture_offy_occurrences": fixture.count("offy"),
        "celloff_body_offy_occurrences": celloff.count("offy"),
        "row_definition": "run_battery.py:1004 flags=[--arm=celloff, --off=0, --offy=1000]",
    }
    (LIVE / "killmatrix.json").write_text(json.dumps(out, indent=1) + "\n")

    print("== divergence census ==")
    for k, v in out["divergence_census"].items():
        print(f"{k}: ident={v['identical_count']}/14 diverging={v['diverging']}")
    print("== predicate matrix ==")
    for k, v in out["predicates"].items():
        print(f"{k} row={v['row']} block={v['block_lines']} lines/{v['block_bytes']}B sha={v['block_sha256'][:16]}")
        for arm, t in v["arms"].items():
            print(f"  {arm:26s} " + " ".join(f"{p}={x['verdict']}" for p, x in t["verdicts"].items()))
            print(f"      battery_now : {t['battery_stdout_prefix']}")
            print(f"      battery_fix : {t['postfix_stdout_prefix']}")
            d = t["verdicts"]["full_replay_block_pin"]["detail"]
            if d:
                print(f"      first mismatch: {d}")
    print("== offy ==")
    print(json.dumps(out["offy"], indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
