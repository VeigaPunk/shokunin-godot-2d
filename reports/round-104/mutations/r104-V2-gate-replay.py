#!/usr/bin/env python3
"""r104-V2 — independent gate-evasion replay + tab-PASS false-positive census.

Verifier seat V2. Read-only over the repo: imports a COPY of
corpus/fixtures/run_battery.py from /var/tmp/r104-V2/ and calls
receipt_shape_flag directly. run_battery.py itself is NEVER executed.

Modes:
  --census            false-positive census for the tab-PASS tightening
  --replay            K>=8 synthetic shapes vs the CURRENT (unlanded) gate
  --replay-tightened  same shapes vs a locally tightened pass-line census
  --audit RUN         receipt_shape_audit over a stored run (control)
"""
import argparse
import copy
import hashlib
import importlib.util
import json
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
SCRATCH = Path("/var/tmp/r104-V2")
COPY = SCRATCH / "battery_copy.py"
RUN = REPO / "corpus/live/runs/20261019T005558434174Z/verdicts.json"

BANNER = ("Godot Engine v4.7.2.stable.arch_linux.ed1daf0bf "
          "(2026-08-17 01:18:38 UTC) - https://godotengine.org")
FORGED_BANNER = ("Godot Engine v9.9.9.stable.official.deadbeefcafe "
                 "- https://godotengine.org")

# Bases chosen to cover the gate's four clauses: plain row, DIAG-window row,
# multi-PASS grammar row, and SEQ-span row.
BASES = {
    "simple": "input_route",              # 1 PASS, no DIAG, no SEQ
    "diag":   "export_prod_base_pck",     # DIAG window, multi-PASS grammar
    "seq":    "r100b_seq_clean",          # SEQ span + 14-PASS grammar
    "launch": "export_launch_embed_boot", # DIAG window, 3 PASS
}


def load_mod(path=COPY):
    spec = importlib.util.spec_from_file_location("r104_v2_battery", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def sha_text(s):
    return hashlib.sha256(s.encode()).hexdigest()


def load_rows(run=RUN):
    raw = Path(run).read_bytes()
    return json.loads(raw)["results"], hashlib.sha256(raw).hexdigest()


def find(rows, case):
    for i, r in enumerate(rows):
        if r.get("case") == case:
            return i, r
    raise SystemExit("base row not found: %s" % case)


def mut(row, ops, note):
    out = copy.deepcopy(row)
    lines = list(out["output"])
    for kind, idx, line in ops:
        if kind == "insert":
            lines.insert(idx, line)
        else:
            lines.append(line)
    out["output"] = lines
    out["_note"] = note
    return out


def build(rows):
    base = {k: find(rows, v)[1] for k, v in BASES.items()}
    ev = []
    # s1 banner forgery (pre/inside/post DIAG window)
    ev.append(("s1a_banner_forged_diag",
               mut(base["diag"], [("insert", 1, FORGED_BANNER)],
                   "forged banner line at idx1 of export_prod_base_pck")))
    ev.append(("s1b_banner_dup_diag",
               mut(base["diag"], [("append", None, BANNER)],
                   "exact banner duplicate appended")))
    # s2 DIAG-prefixed foreign payload
    ev.append(("s2a_diag_foreign_simple",
               mut(base["simple"], [("append", None,
                                     "EXPORT_PROD_DIAG base forged=1")],
                   "foreign DIAG verb into a no-DIAG row")))
    ev.append(("s2b_diag_forged_launch",
               mut(base["launch"], [("append", None,
                                     "EXPORT_LAUNCH_DIAG embed forged=1")],
                   "forged same-family DIAG payload")))
    # s3 PASS-flood
    ev.append(("s3a_flood5_simple",
               mut(base["simple"], [("append", None, "PASS forged=%d" % n)
                                    for n in range(5)],
                   "5 forged PASS lines appended to a 1-PASS row")))
    ev.append(("s3b_flood1_grammar_seq",
               mut(base["seq"], [("append", None, "PASS r100_gui forged=1")],
                   "1 forged PASS line on a 14-PASS grammar row")))
    # s4 whitespace-evasion family (the C2a target)
    ev.append(("s4a_tab_lead_simple",
               mut(base["simple"], [("append", None, "\tPASS forged=true")],
                   "leading-TAB forged PASS line")))
    ev.append(("s4b_trailing_space_dup_simple",
               mut(base["simple"], [("append", None,
                                     base["simple"]["output"][-1] + " ")],
                   "trailing-space duplicate of the legit PASS line")))
    ev.append(("s4c_trailing_nbsp_simple",
               mut(base["simple"], [("append", None, "PASS forged=true\u00a0")],
                   "trailing NBSP (U+00A0)")))
    ev.append(("s4d_tab_after_pass_simple",
               mut(base["simple"], [("append", None, "PASS\tforged=true")],
                   "TAB after the PASS token (r103-routed grammar hole)")))
    ev.append(("s4e_tab_after_pass_grammar_seq",
               mut(base["seq"], [("append", None, "PASS\tr100_gui forged=1")],
                   "TAB-separated forged line on a grammar row")))
    # s5 foreign content inside a declared SEQ span
    ev.append(("s5a_foreign_in_seq_span",
               mut(base["seq"], [("insert", 3, "foreign spliced line")],
                   "foreign line inside the SEQ span")))
    return ev, base


def census(rows_all):
    """False-positive census: every PASS-prefixed line in every stored run."""
    pat_space = re.compile(r"^PASS ")
    pat_tight = re.compile(r"^PASS(?=\s|$)")
    tot_space = tot_tight = 0
    fp = []
    for row in rows_all:
        out = row.get("output")
        if not isinstance(out, list):
            continue
        for line in out:
            if not isinstance(line, str):
                continue
            if pat_space.match(line):
                tot_space += 1
            if pat_tight.match(line):
                tot_tight += 1
                if not pat_space.match(line):
                    fp.append((row.get("case"), line[:70]))
    return tot_space, tot_tight, fp


def tightened_flag(mod, row):
    """The CURRENT gate, with only the pass-line census tightened to
    ^PASS followed by any whitespace (or end)."""
    out = row.get("output")
    if not isinstance(out, list):
        return []
    flags = []
    case = row.get("case")
    pass_lines = [l for l in out if re.match(r"^PASS(?=\s|$)", l)]
    grammar = mod.RECEIPT_MULTI_PASS_GRAMMAR.get(case)
    if grammar is not None:
        observed = []
        for line in pass_lines:
            t = line.split()
            observed.append((t[1] if len(t) > 1 else "",
                             t[2] if len(t) > 2 else ""))
        if sorted(observed) != sorted(grammar):
            flags.append("pass_line_grammar_mismatch")
    else:
        if len(pass_lines) > 1:
            flags.append("unaccounted_pass_lines")
    return flags


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--census", action="store_true")
    ap.add_argument("--replay", action="store_true")
    ap.add_argument("--replay-tightened", action="store_true")
    ap.add_argument("--audit")
    args = ap.parse_args()
    mod = load_mod()
    print("BATTERY_COPY=%s sha256=%s" % (COPY, hashlib.sha256(COPY.read_bytes()).hexdigest()))
    print("CASES=%d grammar_rows=%d" % (len(mod.CASES), len(mod.RECEIPT_MULTI_PASS_GRAMMAR)))

    if args.audit:
        rows, sh = load_rows(args.audit)
        res = mod.receipt_shape_audit(rows)
        print("AUDIT %s sha=%s audited=%d flags=%d" %
              (args.audit, sh, res["audited"], len(res["flags"])))
        for f in res["flags"][:20]:
            print("  FLAG", json.dumps(f)[:160])
        return 0

    rows, run_sha = load_rows()
    print("RUN=%s sha256=%s rows=%d" % (RUN, run_sha, len(rows)))

    if args.census:
        sp, ti, fp = census(rows)
        print("CENSUS PASS-space=%d PASS-tight=%d false_positive_candidates=%d"
              % (sp, ti, len(fp)))
        for c, l in fp[:20]:
            print("  FP case=%s line=%r" % (c, l))
        return 0

    ev, _ = build(rows)
    if args.replay or args.replay_tightened:
        print("--- replay: %d shapes vs CURRENT gate" % len(ev))
        for name, row in ev:
            cur = mod.receipt_shape_flag(row)
            why = [f.get("why") for f in cur]
            if args.replay_tightened:
                tight = tightened_flag(mod, row)
                print("%-28s current=%s tightened=%s" %
                      (name, why or "UNFLAGGED", tight or "UNFLAGGED"))
            else:
                print("%-28s current=%s" % (name, why or "UNFLAGGED"))
        # green controls must stay clean
        print("--- green controls (unmutated bases)")
        for k, r in sorted(build(rows)[1].items()):
            print("%-28s current=%s" % ("green_" + k,
                                        [f.get("why") for f in mod.receipt_shape_flag(r)] or "UNFLAGGED"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
