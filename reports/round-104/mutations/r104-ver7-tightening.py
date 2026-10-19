#!/usr/bin/env python3
"""r104-V7 — tightened-PASS-predicate discrimination probe (KEY=V7).

Builds three text-mutated copies of the landed gate in scratch (the shared
file is NEVER edited) and replays the r104-V7 catalog through each:

  V0 = landed                : `line.startswith("PASS ")`
  Va = census-only tightening: census at the `pass_lines = [...]` site only
  Vb = census + permit lists : every `startswith("PASS ")` becomes the
                               tightened predicate

The question the C2a routing asks: does extending the pass-line census to all
PASS-prefixed lines (a) flag more evasions and (b) false-positive on green?
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
RUNS = sorted((REPO / "corpus/live/runs").glob("*/verdicts.json"))

BANNER = ("Godot Engine v4.7.2.stable.arch_linux.ed1daf0bf "
          "(2026-08-17 01:18:38 UTC) - https://godotengine.org")
FORGED_BANNER = ("Godot Engine v9.9.9.stable.official.deadbeefcafe "
                 "- https://godotengine.org")
BASES = {"launch": "export_launch_embed_boot", "prod": "export_prod_base_pck",
         "seq": "r100b_seq_clean", "simple": "input_route"}

CENSUS_SITE = 'pass_lines = [line for line in output if line.startswith("PASS ")]'
OLD_PRED = 'line.startswith("PASS ")'
NEW_PRED_CENSUS = 'line.lstrip().startswith("PASS")'


def variant_text(kind):
    src = GATE_SRC.read_text()
    if kind == "V0":
        return src
    assert src.count(CENSUS_SITE) == 1, src.count(CENSUS_SITE)
    if kind == "Va":
        return src.replace(CENSUS_SITE, CENSUS_SITE.replace(OLD_PRED, NEW_PRED_CENSUS))
    if kind == "Vb":
        n = src.count(OLD_PRED)
        assert n == 4, n
        return src.replace(OLD_PRED, NEW_PRED_CENSUS)
    raise SystemExit("bad kind")


def load_variant(kind):
    path = SCRATCH / ("gate_%s.py" % kind)
    text = variant_text(kind)
    path.write_text(text)
    spec = importlib.util.spec_from_file_location("r104v7_%s" % kind, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod, hashlib.sha256(text.encode()).hexdigest()[:16]


def mutate(row, ops):
    out = copy.deepcopy(row)
    lines = list(out["output"])
    for kind, idx, line in ops:
        lines.insert(idx, line) if kind == "insert" else lines.append(line)
    out["output"] = lines
    return out


def catalog(base):
    ev = []
    wl = base["simple"]["output"][-1]
    ev.append(("s1a_banner_forged_seq", mutate(base["seq"], [("insert", 2, FORGED_BANNER)])))
    ev.append(("s1b_banner_dup_launch", mutate(base["launch"], [("insert", 4, BANNER)])))
    ev.append(("s2a_diag_other_family_simple", mutate(base["simple"], [("insert", 3, "EXPORT_LAUNCH_DIAG embed forged=true")])))
    ev.append(("s2b_diag_forged_launch", mutate(base["launch"], [("insert", 6, "EXPORT_LAUNCH_DIAG embed forged=1")])))
    ev.append(("s3a_flood5_simple", mutate(base["simple"], [("append", None, "PASS flooded=%d extra=true" % n) for n in range(1, 6)])))
    ev.append(("s3b_flood1_seq", mutate(base["seq"], [("append", None, "PASS r100_gui forged=1")])))
    ev.append(("s4a_tab_lead_simple", mutate(base["simple"], [("append", None, "\tPASS forged=true")])))
    ev.append(("s4b_trail_space_simple", mutate(base["simple"], [("append", None, wl + " ")])))
    ev.append(("s4c_trail_nbsp_simple", mutate(base["simple"], [("append", None, "PASS forged=true\u00a0")])))
    ev.append(("s4d_tab_after_pass_simple", mutate(base["simple"], [("append", None, "PASS\tforged=true")])))
    ev.append(("t1_two_space_after_pass", mutate(base["simple"], [("append", None, "PASS  forged=true")])))
    ev.append(("t2_tab_lead_two_space", mutate(base["simple"], [("append", None, "\tPASS  forged=true")])))
    ev.append(("t3_pass_tab_only", mutate(base["simple"], [("append", None, "PASS\t")])))
    ev.append(("t4_pass_nbsp_after", mutate(base["simple"], [("append", None, "PASS\u00a0forged=true")])))
    ev.append(("t5_pass_cr_after", mutate(base["simple"], [("append", None, "PASS\rforged=true")])))
    ev.append(("t6_pass_tab_pin_inside", mutate(base["simple"], [("append", None, "PASS\tsomething route=parse_input_event-to-Node._input")])))
    ev.append(("t7_space_lead_pin_inside", mutate(base["simple"], [("append", None, "   PASS route=parse_input_event-to-Node._input")])))
    # window-internal whitespace-PASS: inside a DIAG window (launch) and a SEQ span (seq)
    ev.append(("w1_tab_pass_in_diag_window", mutate(base["launch"], [("insert", 3, "\tPASS export_launch forged=true")])))
    ev.append(("w2_tab_pass_in_seq_span", mutate(base["seq"], [("insert", 4, "\tPASS r100_gui forged=true")])))
    ev.append(("w3_pass_tab_in_diag_window", mutate(base["launch"], [("insert", 3, "PASS\texport_launch forged=true")])))
    ev.append(("w4_pass_tab_in_seq_span", mutate(base["seq"], [("insert", 4, "PASS\tr100_gui forged=true")])))
    ev.append(("g1_grammar_row_extra_pass", mutate(base["seq"], [("append", None, "PASS r100_gui forged=1")])))
    ev.append(("g2_grammar_row_intact", mutate(base["seq"], [])))
    return ev


def green_rows(mod):
    out = []
    for rp in RUNS:
        for r in json.loads(rp.read_bytes())["results"]:
            if r.get("verdict") != "PASS":
                continue
            if not isinstance(r.get("output"), list):
                continue
            out.append((rp.parent.name, r))
    return out


def main():
    SCRATCH.mkdir(parents=True, exist_ok=True)
    mods = {}
    for kind in ("V0", "Va", "Vb"):
        mod, sha = load_variant(kind)
        mods[kind] = mod
        print("VARIANT %s sha=%s bytes=%d" % (kind, sha,
              (SCRATCH / ("gate_%s.py" % kind)).stat().st_size))
    by_case = {}
    for r in json.loads(RUN.read_bytes())["results"]:
        by_case.setdefault(r.get("case"), r)
    base = {k: by_case[v] for k, v in BASES.items()}
    cat = catalog(base)

    print()
    print("== discrimination per variant (flags>0 == evasion killed) ==")
    hdr = "%-34s %-4s %-4s %-4s" % ("shape", "V0", "Va", "Vb")
    print(hdr)
    table = {}
    for name, row in cat:
        cells = []
        for kind in ("V0", "Va", "Vb"):
            f = mods[kind].receipt_shape_flag(row)
            cells.append(len(f))
        table[name] = cells
        print("%-34s %-4d %-4d %-4d" % (name, cells[0], cells[1], cells[2]))
    print()
    print("== green false-positive census (all stored PASS rows w/ stdout) ==")
    greens = green_rows(mods["V0"])
    print("green rows scanned = %d" % len(greens))
    for kind in ("V0", "Va", "Vb"):
        n_flag = 0
        examples = []
        for run, r in greens:
            f = mods[kind].receipt_shape_flag(r)
            if f:
                n_flag += 1
                if len(examples) < 5:
                    examples.append((run, r.get("case"), f))
        print("%s flagged_rows=%d %s" % (kind, n_flag, json.dumps(examples)[:600]))
    print()
    print("== newly-killed by tightening ==")
    for name, cells in table.items():
        if cells[0] == 0 and cells[1] > 0:
            print("  Va kills %s" % name)
        if cells[1] == 0 and cells[2] > 0:
            print("  Vb kills (beyond Va) %s" % name)
        if cells[1] > 0 and cells[2] == 0:
            print("  !! REGRESSION Vb un-kills %s" % name)
    (SCRATCH / "v7-tightening.json").write_text(json.dumps(
        {"table": table, "green": {k: None for k in ("V0", "Va", "Vb")}},
        indent=1) + "\n")


if __name__ == "__main__":
    sys.exit(main())
