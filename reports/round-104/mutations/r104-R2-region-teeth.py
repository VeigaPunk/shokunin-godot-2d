#!/usr/bin/env python3
"""r104-R2 — region-scoped teeth of the landed receipt-shape gate.

Corrected region model (measured from the live source):
  `receipt_shape_flag` has exactly two non-PASS censuses:
    (1) the declared SEQ span — output lines strictly between a line starting
        `SEQ_BEGIN` and one starting `SEQ_END`;
    (2) the DIAG window — the WHOLE receipt, active only if some output line
        matches `^[A-Z][A-Z0-9_]*_DIAG\\b`.
  Rows with neither (no SEQ_* line, no *_DIAG line) get no non-PASS census at all.

Leg B: place one foreign line in each region class on the SAME base row family
       and record whether the gate flags it.
Leg C: class allowance — banner-shaped and *_DIAG-shaped lines inside a DIAG
       window are admitted by regex regardless of payload.
Leg R: reach census — how many live PASS rows fall in each region class.
Leg D: FAIL-receipt rescue — can the forged lines flip a FAIL grade?
"""
import argparse
import ast
import collections
import hashlib
import importlib.util
import json
import sys
from pathlib import Path

sys.dont_write_bytecode = True  # never leave __pycache__ in a shared reports/ tree

REPO = Path("/home/vgpnk/Projects/shokunin/game-dev-2d-shokunin")
BATTERY = REPO / "corpus/fixtures/run_battery.py"
RUNS = sorted((REPO / "corpus/live/runs").glob("*/verdicts.json"))
MUT05 = REPO / "reports/round-103/mutations/mut05_gate_evasion.py"

BANNER = "Godot Engine v4.7.2.stable.arch_linux.ed1daf0bf (2026-08-17 01:18:38 UTC) - https://godotengine.org"
FORGED_BANNER = "Godot Engine v9.9.9.stable.official.deadbeefcafe - https://godotengine.org"
FORGED_DIAG = "EXPORT_LAUNCH_DIAG embed forged=true"
PLAIN = "TOTALLY FOREIGN LINE xyz"
UNFLAGGED = ["s1a_banner_forged_seq", "s1b_banner_dup_launch",
             "s2a_diag_other_family_simple", "s2b_diag_forged_launch",
             "s4a_tab_lead_simple", "s4d_tab_after_pass_simple"]


def load(path, tag):
    spec = importlib.util.spec_from_file_location("x_%s" % tag, path)
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


def region_class(row):
    out = row.get("output") or []
    has_seq = any(l.startswith(("SEQ_BEGIN", "SEQ_END")) for l in out)
    has_diag = any(ast_ok(l) for l in out)
    if has_diag:
        return "diag_window"
    if has_seq:
        return "seq_span"
    return "no_census"


def ast_ok(line):
    import re
    return bool(re.match(r"^[A-Z][A-Z0-9_]*_DIAG\b", line))


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
    print("BASE_RUN sha256=%s rows=%d" % (run_sha, len(data["results"])))
    print("classify_process sha256=%s" % cp_sha)

    print("\n### LEG B — region move: same foreign line, different region class")
    probes = [("forged_banner", FORGED_BANNER), ("forged_diag", FORGED_DIAG),
              ("plain_foreign", PLAIN)]
    for fam, line in [("launch(diag)", "launch"), ("prod(diag)", "prod"),
                      ("simple(none)", "simple"), ("seq(none)", "seq")]:
        base = cases[line]
        for tag, ln in probes:
            r = dict(base, output=list(base["output"]) + [ln])
            fl = gate.receipt_shape_flag(r)
            print("  %-14s %-14s case=%-26s flags=%d %s"
                  % (fam, tag, r["case"], len(fl), sorted({f["why"] for f in fl})))

    print("\n### LEG C — class allowance inside a DIAG window (payload ignored?)")
    launch = cases["launch"]
    for tag, ln in [("real_banner_dup", BANNER), ("forged_banner", FORGED_BANNER),
                    ("forged_diag_same_family", FORGED_DIAG),
                    ("forged_diag_other_family", "TOTALLY_OTHER_DIAG forged=1"),
                    ("plain", PLAIN)]:
        r = dict(launch, output=list(launch["output"]) + [ln])
        fl = gate.receipt_shape_flag(r)
        print("  %-26s flags=%d %s" % (tag, len(fl), sorted({f["why"] for f in fl})))

    print("\n### LEG R — reach census over live PASS rows (region class)")
    tot = collections.Counter()
    per = collections.Counter()
    for p in RUNS:
        d = json.loads(p.read_bytes())
        for r in d.get("results", []):
            if r.get("verdict") != "PASS" or not isinstance(r.get("output"), list):
                continue
            c = region_class(r)
            tot[c] += 1
            per[(p.parent.name, c)] += 1
    print("  region class totals: %s" % dict(tot))
    for k in sorted(per):
        print("    %-30s %-12s %d" % (k[0], k[1], per[k]))

    print("\n### LEG D — FAIL-receipt rescue (all stored FAIL rows x 6 forgeries)")
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
    flips = 0
    for rn, fr in fails:
        alt = fr["signature"]
        for a in ([alt] if isinstance(alt, str) else alt):
            before = cp(fr.get("actual_exit"), fr.get("error"), "\n".join(fr["output"]),
                        fr.get("expected_exit"), a, tuple(fr.get("expected_errors") or ()))
            after = cp(fr.get("actual_exit"), fr.get("error"),
                       "\n".join(fr["output"] + forged_all), fr.get("expected_exit"), a,
                       tuple(fr.get("expected_errors") or ()))
            if before != after:
                flips += 1
                print("  FLIP", rn, fr["case"], before, after)
    print("  FAIL receipts=%d  forged lines injected=%d  grade flips=%d"
          % (len(fails), len(forged_all), flips))
    return 0


if __name__ == "__main__":
    sys.exit(main())
