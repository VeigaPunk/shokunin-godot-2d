#!/usr/bin/env python3
"""r104-R2 — harmlessness discriminators for the 6 unflagged r103 evasion shapes.

Leg A (rescue): can the forged line substitute for the row's own pin? Delete the
legitimate pin line from the receipt and grade with the row's signature — a
forged line that supplies the pin would flip the grade. Negative control: the
same deletion on an untouched sibling.
Leg B (region): does the landed gate catch the same forged line when it lands in
a censused region (inside the SEQ span / after SEQ_END / inside a DIAG row)?
This separates 'accounted-by-design' from 'region-scoped gap'.
Leg C (class allowance): for diag-window rows, is the forged line admitted by
the class regex alone (banner / *_DIAG) regardless of its payload?
"""
import argparse
import ast
import hashlib
import importlib.util
import json
import sys

sys.dont_write_bytecode = True  # never leave __pycache__ in a shared reports/ tree
from pathlib import Path

REPO = Path("/home/vgpnk/Projects/shokunin/game-dev-2d-shokunin")
BATTERY = REPO / "corpus/fixtures/run_battery.py"
RUNS = sorted((REPO / "corpus/live/runs").glob("*/verdicts.json"))
MUT05 = REPO / "reports/round-103/mutations/mut05_gate_evasion.py"
GREEN = REPO / "corpus/live/runs/20261018T213443471189Z/verdicts.json"

UNFLAGGED = ["s1a_banner_forged_seq", "s1b_banner_dup_launch",
             "s2a_diag_other_family_simple", "s2b_diag_forged_launch",
             "s4a_tab_lead_simple", "s4d_tab_after_pass_simple"]


def load(path, tag):
    spec = importlib.util.spec_from_file_location("h_%s" % tag, path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def classifier_ns():
    src = BATTERY.read_text()
    tree = ast.parse(src)
    seg = next(ast.get_source_segment(src, n) for n in ast.walk(tree)
               if isinstance(n, ast.FunctionDef) and n.name == "classify_process")
    ns = {}
    exec("import re\n" + seg, ns)
    return ns["classify_process"], hashlib.sha256(seg.encode()).hexdigest()


def main():
    gate = load(BATTERY, "gate")
    spec = importlib.util.spec_from_file_location("m5", MUT05)
    m5 = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m5)
    data, run_sha = m5.load_run()
    ev, cases = m5.build_evasions(data["results"])
    ev = dict(ev)
    cp, cp_sha = classifier_ns()
    print("LIVE_BATTERY sha256=%s" % hashlib.sha256(BATTERY.read_bytes()).hexdigest())
    print("classify_process sha256=%s" % cp_sha)

    # ---- Leg A: rescue test (does the forgery substitute for the row's pin?)
    print("\n### LEG A — rescue: delete the pin line, grade with/without forgery")
    for name in UNFLAGGED:
        row = ev[name]
        base = None
        for k in m5.BASES:
            if cases[k]["case"] == row["case"]:
                base = cases[k]
        sig = row.get("signature")
        alts = [sig] if isinstance(sig, str) else (sig or [])
        forged = [l for l in row["output"] if l not in base["output"]]
        for alt in alts:
            anchor = alt.split("\n")[0].strip()
            keep = [l for l in base["output"] if anchor not in l]
            deleted = len(base["output"]) - len(keep)
            g_intact = cp(base.get("actual_exit"), base.get("error"),
                          "\n".join(base["output"]), base.get("expected_exit"), alt,
                          tuple(base.get("expected_errors") or ()))
            g_depin = cp(base.get("actual_exit"), base.get("error"),
                         "\n".join(keep), base.get("expected_exit"), alt,
                         tuple(base.get("expected_errors") or ()))
            g_rescue = cp(base.get("actual_exit"), base.get("error"),
                          "\n".join(keep + forged), base.get("expected_exit"), alt,
                          tuple(base.get("expected_errors") or ()))
            print("%-28s anchor=%-34s deleted=%d intact=%s depinned=%s rescued=%s"
                  % (name, anchor[:34], deleted, g_intact, g_depin, g_rescue))

    # ---- Leg B: region move — does the gate catch the same line in-span/tail?
    print("\n### LEG B — region move (same forged line, censused region)")
    seq = ev["s1a_banner_forged_seq"]
    base_seq = cases["seq"]
    fb = "Godot Engine v9.9.9.stable.official.deadbeefcafe - https://godotengine.org"
    diag = "EXPORT_LAUNCH_DIAG embed forged=true"
    simple = cases["simple"]
    moves = []
    # The stored record's `output` carries NO SEQ_* / *_DIAG line (those live in
    # the row's PIN, which is not part of the receipt), so the seq/launch rows
    # below are region-class `no_census` as stored. Synthesise the declared
    # window explicitly to test the span/tail branches the way a row that
    # declares one would be audited.
    out = list(base_seq["output"])
    pass_only = [l for l in out if l.startswith("PASS ")]
    span = ["Godot Engine v4.7.2.stable.arch_linux.ed1daf0bf"] \
        + ["SEQ_BEGIN cells=14 clean=1 pins=14"] + pass_only \
        + ["SEQ_CENSUS identical=10 divergent_n=4 divergent=[cursor|touch|subvp|warp]"] \
        + ["SEQ_END digest=" + "0" * 64]
    span_row = dict(base_seq, output=span)
    bi = next(i for i, l in enumerate(span) if l.startswith("SEQ_BEGIN"))
    ei = next(i for i, l in enumerate(span) if l.startswith("SEQ_END"))
    moves.append(("banner_in_span", dict(span_row, output=span[:bi + 1] + [fb] + span[bi + 1:])))
    moves.append(("banner_in_tail", dict(span_row, output=span[:ei + 1] + [fb] + span[ei + 1:])))
    moves.append(("banner_on_declared_span_ctl", span_row))
    # a simple row declares neither -> the same line anywhere is uncensused
    moves.append(("banner_on_simple", dict(simple, output=list(simple["output"]) + [fb])))
    moves.append(("diag_on_simple", dict(simple, output=list(simple["output"]) + [diag])))
    launch = cases["launch"]
    moves.append(("diag_on_launch_row", dict(launch, output=list(launch["output"]) + [diag])))
    for tag, r in moves:
        fl = gate.receipt_shape_flag(r)
        print("%-22s case=%-26s flags=%d %s" % (
            tag, r["case"], len(fl), sorted({f["why"] for f in fl})))

    # ---- Leg C: class allowance on diag-window rows
    print("\n### LEG C — class allowance (diag-window rows admit by regex alone)")
    for label, line in [("forged_banner", fb),
                        ("forged_diag", "EXPORT_LAUNCH_DIAG totally different payload"),
                        ("forged_diag_extra", "EXPORT_LAUNCH_DIAG embed forged=1"),
                        ("plain_foreign", "TOTALLY FOREIGN LINE xyz")]:
        r = dict(launch, output=list(launch["output"]) + [line])
        fl = gate.receipt_shape_flag(r)
        print("%-18s -> flags=%d %s" % (label, len(fl), sorted({f["why"] for f in fl})))

    # ---- Leg D: FAIL receipts + forgery across ALL stored FAILs
    print("\n### LEG D — FAIL receipts: does any forgery flip the grade?")
    fails = []
    for p in RUNS:
        d = json.loads(p.read_bytes())
        for r in d.get("results", []):
            if r.get("verdict") == "FAIL" and isinstance(r.get("output"), list) and r.get("signature"):
                fails.append((p.parent.name, r))
    forged_all = []
    for name in UNFLAGGED:
        base = None
        for k in m5.BASES:
            if cases[k]["case"] == ev[name]["case"]:
                base = cases[k]
        forged_all += [l for l in ev[name]["output"] if l not in base["output"]]
    print("FAIL receipts=%d  forged lines=%d" % (len(fails), len(forged_all)))
    flips = 0
    for rn, fr in fails:
        alt = fr["signature"]
        alts = [alt] if isinstance(alt, str) else alt
        for a in alts:
            before = cp(fr.get("actual_exit"), fr.get("error"), "\n".join(fr["output"]),
                        fr.get("expected_exit"), a, tuple(fr.get("expected_errors") or ()))
            after = cp(fr.get("actual_exit"), fr.get("error"),
                       "\n".join(fr["output"] + forged_all), fr.get("expected_exit"), a,
                       tuple(fr.get("expected_errors") or ()))
            if before != after:
                flips += 1
                print("  FLIP", rn, fr["case"], before, after)
    print("FAIL-grade flips caused by the 6 shapes' forgeries = %d" % flips)
    return 0


if __name__ == "__main__":
    sys.exit(main())
