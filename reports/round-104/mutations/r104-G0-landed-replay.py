#!/usr/bin/env python3
"""r104-G0 — replay the r103 evasion catalog against the LANDED gate.

r103's adjudicator reported "4/10 shapes flag, 6 accounted/harmless", but that
was measured against a derived 186 KB prototype (mut05_gate.py), not against
`receipt_shape_flag` as landed in corpus/fixtures/run_battery.py. This script
imports the landed gate and the landed classifier and replays:

  * the 10 r103 synthetic evasion shapes (reconstructed verbatim from
    reports/round-103/r103-mut5.md §4 table),
  * green controls (the unmodified base records),
  * out-of-sample silence over every stored verdicts.json on disk.

Read-only; run_battery.py is imported, never executed.
"""
import argparse
import copy
import hashlib
import importlib.util
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
RB = REPO / "corpus" / "fixtures" / "run_battery.py"
RUNS = REPO / "corpus" / "live" / "runs"
# green r102 run used by r103-mut5 as the evasion base
BASE_RUN = RUNS / "20261018T213443471189Z" / "verdicts.json"

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


def load_rb():
    spec = importlib.util.spec_from_file_location("rb_landed", RB)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def find_row(rows, case):
    for i, r in enumerate(rows):
        if r.get("case") == case:
            return i, r
    raise SystemExit("base row not found: %s" % case)


def mutate(row, ops):
    out = copy.deepcopy(row)
    lines = list(out["output"])
    for kind, idx, line in ops:
        if kind == "insert":
            lines.insert(idx, line)
        else:
            lines.append(line)
    out["output"] = lines
    return out


def build(rows):
    base = {}
    for k, case in BASES.items():
        base[k] = find_row(rows, case)[1]
    ev = []
    ev.append(("s1a_banner_foreign", mutate(base["seq"], [("insert", 2, FORGED_BANNER)])))
    ev.append(("s1b_banner_dup", mutate(base["launch"], [("insert", 4, BANNER)])))
    ev.append(("s2a_diag_foreign", mutate(base["simple"],
                                         [("insert", 3, "EXPORT_LAUNCH_DIAG embed forged=true")])))
    ev.append(("s2b_diag_same_family", mutate(base["launch"],
                                              [("insert", 6, "EXPORT_LAUNCH_DIAG embed forged=1")])))
    ev.append(("s3a_pass_flood5", mutate(base["simple"],
                                         [("append", None, "PASS flooded=%d extra=true" % n)
                                          for n in range(1, 6)])))
    ev.append(("s3b_pass_flood1_seq", mutate(base["seq"],
                                             [("append", None, "PASS r100_gui forged=1")])))
    wl = base["simple"]["output"][-1]
    ev.append(("s4a_tab_lead", mutate(base["simple"], [("append", None, "\tPASS forged=true")])))
    ev.append(("s4b_trail_space", mutate(base["simple"], [("append", None, wl + " ")])))
    ev.append(("s4c_trail_nbsp", mutate(base["simple"], [("append", None, "PASS forged=true\u00a0")])))
    ev.append(("s4d_tab_after_pass", mutate(base["simple"], [("append", None, "PASS\tforged=true")])))
    return ev, base


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--base-run", default=str(BASE_RUN))
    args = ap.parse_args()
    rb = load_rb()
    gate = rb.receipt_shape_flag
    audit = rb.receipt_shape_audit

    raw = Path(args.base_run).read_bytes()
    data = json.loads(raw)
    rows = data["results"]
    print("BASE_RUN=%s sha256=%s rows=%d" % (args.base_run,
                                             hashlib.sha256(raw).hexdigest(), len(rows)))
    print("GATE=receipt_shape_flag (landed, run_battery.py)  CASES_SIG_BY_CASE=%d"
          % len(rb.CASES_SIG_BY_CASE))

    ev, base = build(rows)
    flagged = 0
    print("\n=== EVASIONS (tampered copies of real green records) ===")
    for name, row in ev:
        fl = gate(row)
        if fl:
            flagged += 1
        print("EVASION %-22s flagged=%-5s n_flags=%d :: %s"
              % (name, bool(fl), len(fl),
                 "; ".join("%s%s" % (f["why"], "" if "observed" not in f else
                                     "(obs=%s decl=%s)" % (f.get("observed"), f.get("declared")))
                           for f in fl)[:160]))
    print("EVASION_SUMMARY flagged=%d/%d" % (flagged, len(ev)))

    print("\n=== GREEN CONTROLS (unmodified bases) ===")
    for k, row in base.items():
        fl = gate(row)
        print("CONTROL %-8s silent=%s :: %s" % (k, not fl,
                                                "; ".join(f["why"] for f in fl)[:120]))

    print("\n=== OUT-OF-SAMPLE SILENCE (all stored runs) ===")
    total_rows = total_flags = 0
    for p in sorted(RUNS.glob("*/verdicts.json")):
        payload = json.loads(p.read_bytes())
        res = audit(payload.get("results", []))
        total_rows += res["audited"]
        total_flags += len(res["flags"])
        print("AUDIT %s audited=%d flags=%d %s"
              % (p.parent.name, res["audited"], len(res["flags"]),
                 json.dumps(res["flags"][:3])[:150] if res["flags"] else ""))
    print("AUDIT_TOTAL audited=%d flags=%d" % (total_rows, total_flags))
    return 0


if __name__ == "__main__":
    sys.exit(main())
