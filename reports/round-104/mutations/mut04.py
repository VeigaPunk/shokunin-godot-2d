#!/usr/bin/env python3
"""r104-mut4 — probe-vs-gate consistency attack (KEY=M4).

Question this seat answers with measurement, not assertion:

  * Does the *landed* gate (`receipt_shape_flag` in corpus/fixtures/
    run_battery.py) reproduce the verdicts that r103 recorded — r103 recorded
    them against two PROTOTYPES (r103-receipt-shape-gate.py, mut05_gate.py),
    never against the predicate that actually landed?
  * Is the C3 probe design ("every shape flags as classified, green controls
    silent") a probe of the gate or a probe of itself? Fault-inject the gate
    and see which probe designs stay green.

Method (all read-only over the repo; run_battery.py is never executed):

  extract  Parse run_battery.py, drop the `__main__` guard, exec the module
           body in an isolated namespace. Assert no module-level call survives
           the strip, so nothing runs. The predicate is taken from the LIVE
           file — no copy, no drift.
  replay   Import r103's own shape builders (r103-receipt-shape-adversary.py
           for the 13 attack/corruption variants, mut05_gate_evasion.py for the
           10-shape evasion catalog) and run the LIVE predicate over the exact
           rows r103 shaped. Diff live flag-sets against r103's recorded JSON.
  power    Build gate mutants by asserted 1-line source splices of the live
           predicate, then score four candidate probe designs against the
           mutant matrix. A probe design that stays green under a broken gate
           is vacuous.
  emit     Write receipts to /var/tmp/r104-M4/receipts/.

Usage: python3 reports/round-104/mutations/mut04.py
         [extract|replay|power|census|tighten|all]

Exit 0 iff the harness ran and every phase that asserts a *specification*
holds. The replay phase asserts agreement between r103's recorded verdicts and
the landed gate; that assertion is currently FALSE (9/13 disagree) — the exit
code is 1 by design so a CI hook cannot mistake the disclosure for a pass.
Read `replay.json` / `power.json`, not the exit code, for the measurements.
"""
import argparse
import ast
import hashlib
import importlib.util
import json
import sys
from pathlib import Path

# Importing r103's builders would otherwise drop __pycache__ bytecode into
# reports/round-103/ — a shared tree this seat must not write to.
sys.dont_write_bytecode = True

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
FIXTURES = REPO / "corpus" / "fixtures"
BATTERY = FIXTURES / "run_battery.py"
R103 = REPO / "reports" / "round-103" / "mutations"
SCRATCH = Path("/var/tmp/r104-M4")
RECEIPTS = SCRATCH / "receipts"
ADVERSARY_JSON = R103 / "r103-receipt-shape-adversary.json"
ADVERSARY_PY = R103 / "r103-receipt-shape-adversary.py"
MUT05_PY = R103 / "mut05_gate_evasion.py"
# base runs the two r103 catalogs were built from (verbatim from their sources)
ADVERSARY_RUN = REPO / "corpus/live/runs/20261018T212500022987Z/verdicts.json"
MUT05_RUN = REPO / "corpus/live/runs/20261018T213443471189Z/verdicts.json"

REPORT = {"battery_sha256": None, "phases": {}}


# ------------------------------------------------------------------ extract
def load_live_module(path=BATTERY):
    """Exec run_battery.py's module body (no __main__ guard) in isolation.

    Returns (namespace, source_text, sha256). Asserts the strip left no
    module-level Call expression, so no fixture can be triggered by the exec.
    """
    src = path.read_text()
    tree = ast.parse(src)
    kept = [n for n in tree.body
            if not (isinstance(n, ast.If)
                    and ast.unparse(n.test) == "__name__ == '__main__'")]
    strays = [n.lineno for n in kept
              if isinstance(n, ast.Expr) and isinstance(n.value, ast.Call)]
    assert not strays, "module-level call survived the strip: %r" % strays
    ns = {"__name__": "r104_mut4_live", "__file__": str(path)}
    exec(compile(ast.Module(body=kept, type_ignores=[]), str(path), "exec"), ns)
    return ns, src, hashlib.sha256(src.encode()).hexdigest()


def splice_mutant(live_ns, name, old, new):
    """1-line source splice of receipt_shape_flag; asserts a unique match."""
    fn = live_ns["receipt_shape_flag"]
    seg = live_ns["__src_segment__"]
    hits = seg.count(old)
    assert hits == 1, "%s: pattern occurs %d times" % (name, hits)
    mutated_seg = seg.replace(old, new)
    assert mutated_seg != seg
    body = ast.parse(mutated_seg.lstrip("\n")).body
    assert len(body) == 1 and isinstance(body[0], ast.FunctionDef)
    assert body[0].name == fn.__name__
    ns = dict(live_ns)
    exec(compile(ast.Module(body=body, type_ignores=[]), "<mutant:%s>" % name, "exec"), ns)
    return ns["receipt_shape_flag"]


# ------------------------------------------------------------------- replay
def _import_file(modname, path):
    spec = importlib.util.spec_from_file_location(modname, str(path))
    mod = importlib.util.module_from_spec(spec)
    sys.modules[modname] = mod
    spec.loader.exec_module(mod)
    return mod


def adversary_variants():
    """r103's 13 attack/corruption variants, rebuilt by r103's own builders."""
    mod = _import_file("r104_mut4_adversary", ADVERSARY_PY)
    corpus = json.loads(ADVERSARY_RUN.read_text())
    res = corpus["results"]
    mech = [r for r in res if r["case"] == "mechanic"][0]
    export = [r for r in res if r["case"] == "export_readiness"][0]
    rows = [("control_unmodified", mech)] + mod.attacks(mech) + mod.corruptions(mech, export)
    return mod, rows


def mut05_variants():
    """r103 mut05's 10 evasions + 4 green controls, rebuilt by its builders."""
    mod = _import_file("r104_mut4_mut05", MUT05_PY)
    rows = json.loads(MUT05_RUN.read_text())["results"]
    ev, cases = mod.build_evasions(rows)
    return mod, ev, cases


def flag_set(flags):
    return sorted({f.get("why", "?") for f in flags})


def audit_one_from(fn, row):
    """Replay one row through the LIVE production audit entry point.

    `receipt_shape_flag` alone raises TypeError on `output=None` — the guard
    lives in `receipt_shape_audit` (`if "script" in row and not isinstance(
    output, list)` -> fail_closed_missing_output). r103's prototype folded
    that guard into `audit_record`, so the only faithful comparison runs the
    same entry point the battery runs. The guard is mirrored verbatim here so
    a mutated `receipt_shape_flag` can be substituted for the live one; the
    dead-allowlist floor is dropped because a single row is never the full
    record set.
    """
    if row.get("verdict") != "PASS":
        return []
    output = row.get("output")
    if "script" in row and not isinstance(output, list):
        return [{"case": row.get("case"), "why": "fail_closed_missing_output"}]
    if not isinstance(output, list):
        return []
    return fn(row)


def audit_one(ns, row):
    return audit_one_from(ns["receipt_shape_flag"], row)


def phase_replay(live_ns):
    out = {"adversary": {}, "mut05": {}}
    # --- r103 adversary (13 variants) vs its recorded JSON
    _mod, rows = adversary_variants()
    recorded = json.loads(ADVERSARY_JSON.read_text())["variants"]
    agree = disagree = 0
    for name, row in rows:
        live = audit_one(live_ns, row)
        rec = recorded.get(name, None)
        rec_flagged = bool(rec)
        live_flagged = bool(live)
        # recorded vocabulary belongs to the r103 prototype; compare the
        # DECISION (flag / clean), not the flag name, across implementations.
        same = (rec is not None) and (rec_flagged == live_flagged)
        agree += same
        disagree += (not same)
        out["adversary"][name] = {
            "recorded_flags": rec, "live_flags": flag_set(live),
            "recorded_flagged": rec_flagged, "live_flagged": live_flagged,
            "decision_agrees": same,
        }
    out["adversary_summary"] = {
        "variants": len(rows), "decision_agree": agree, "decision_disagree": disagree,
        "recorded_json": str(ADVERSARY_JSON.relative_to(REPO)),
    }
    # --- mut05 10-shape catalog + green controls
    _m, ev, cases = mut05_variants()
    flagged = 0
    for name, row in ev:
        live = audit_one(live_ns, row)
        flagged += bool(live)
        out["mut05"][name] = {"live_flags": flag_set(live), "live_flagged": bool(live)}
    ctrl_silent = 0
    for k, row in cases.items():
        live = audit_one(live_ns, row)
        ctrl_silent += (not live)
        out["mut05"]["green_" + k] = {"live_flags": flag_set(live), "live_flagged": bool(live)}
    out["mut05_summary"] = {"shapes": len(ev), "shapes_flagged": flagged,
                            "controls": len(cases), "controls_silent": ctrl_silent}
    return out


# ------------------------------------------------------- pass-prefix census
def phase_census(live_ns):
    """False-positive census for C2(a): the tab-PASS tightening.

    The landed census reads `line.startswith("PASS ")` — a tab-separated
    `PASS\\tforged=1` is invisible to it. The tightening candidate widens the
    selector to `startswith("PASS")`. This phase measures that widening over
    EVERY stored green run: which real lines would the widened selector newly
    admit, and does the gate then flag any of them (false positive)?
    """
    runs = sorted((REPO / "corpus" / "live" / "runs").glob("*/verdicts.json"))
    narrow_sel = lambda line: line.startswith("PASS ")
    wide_sel = lambda line: line.startswith("PASS")
    shapes = {}
    rows = 0
    rows_with_wide_only = 0
    flags_narrow = flags_wide = 0
    per_run = {}
    for p in runs:
        payload = json.loads(p.read_text())
        run_flags = 0
        run_cases = set()
        for row in payload.get("results") or []:
            out = row.get("output")
            if not isinstance(out, list):
                continue
            rows += 1
            for line in out:
                if not isinstance(line, str):
                    continue
                if wide_sel(line) and not narrow_sel(line):
                    shapes.setdefault(line[:60], {"count": 0, "runs": set()})
                    shapes[line[:60]]["count"] += 1
                    shapes[line[:60]]["runs"].add(p.parent.name)
            if any(wide_sel(l) and not narrow_sel(l) for l in out if isinstance(l, str)):
                rows_with_wide_only += 1
            fl = audit_one(live_ns, row)
            flags_narrow += len(fl)
            flags_wide += len(fl)
            if fl:
                run_flags += len(fl)
                run_cases.add(row.get("case"))
        per_run[p.parent.name] = {"rows": len(payload.get("results") or []),
                                  "flags": run_flags, "cases": sorted(run_cases)}
    return {
        "runs": [p.parent.name for p in runs],
        "rows_scanned": rows,
        "wide_only_line_shapes": {k: {"count": v["count"], "runs": sorted(v["runs"])}
                                  for k, v in shapes.items()},
        "rows_containing_wide_only_lines": rows_with_wide_only,
        "flags_live_gate": flags_narrow,
        "flags_per_run": per_run,
        "note": "wide_sel here is diagnostic only; the live gate is unchanged.",
    }


# ------------------------------------------------- tab-PASS tightening test
def phase_tighten(live_ns):
    """Measure the C2(a) tightening on the shape family it targets.

    Widening the census selector to `startswith("PASS")` only helps if the
    widened pass-line list is then *accounted* — the current account compares
    `line.split(" ")`, which for `PASS\\tforged=1` yields tokens
    ["PASS\\tforged=1"] and therefore observed=("","") — silently equal to a
    one-element grammar entry, or empty against a one-PASS row. This phase
    measures the pre-tightening and post-tightening verdicts on the tab family
    and the false-positive set the tightening creates on real stored rows.
    """
    _m, ev, cases = mut05_variants()
    tab_shapes = [(n, r) for n, r in ev if n.startswith("s4")]
    # post-tightening predicate: same source with the selector widened, and the
    # token split made whitespace-agnostic so the account can actually see it.
    fn_tight = splice_mutant(
        live_ns, "tighten_pass_prefix",
        '    pass_lines = [line for line in output if line.startswith("PASS ")]',
        '    pass_lines = [line for line in output if line.startswith("PASS")]')
    fn_strip = splice_mutant(
        live_ns, "tighten_pass_lstrip",
        '    pass_lines = [line for line in output if line.startswith("PASS ")]',
        '    pass_lines = [line for line in output if line.strip().startswith("PASS")]')
    out = {"tab_family": {}, "real_rows": {}}
    for name, row in tab_shapes:
        pre = audit_one_from(live_ns["receipt_shape_flag"], row)
        post = audit_one_from(fn_tight, row)
        post2 = audit_one_from(fn_strip, row)
        out["tab_family"][name] = {
            "pre": flag_set(pre), "post_wide": flag_set(post), "post_lstrip": flag_set(post2),
            "pre_flagged": bool(pre), "post_wide_flagged": bool(post),
            "post_lstrip_flagged": bool(post2)}
    # false-positive sweep of the widened selector over every stored row
    fp = 0
    fp_lstrip = 0
    for p in sorted((REPO / "corpus" / "live" / "runs").glob("*/verdicts.json")):
        for row in json.loads(p.read_text()).get("results") or []:
            if not isinstance(row.get("output"), list):
                continue
            pre = audit_one_from(live_ns["receipt_shape_flag"], row)
            post = audit_one_from(fn_tight, row)
            post2 = audit_one_from(fn_strip, row)
            if post and not pre:
                fp += 1
                out["real_rows"].setdefault(p.parent.name, []).append(
                    {"case": row.get("case"), "post": flag_set(post)})
            if post2 and not pre:
                fp_lstrip += 1
                out["real_rows"].setdefault("lstrip:" + p.parent.name, []).append(
                    {"case": row.get("case"), "post": flag_set(post2)})
    out["false_positives_from_tightening"] = fp
    out["false_positives_from_lstrip"] = fp_lstrip
    return out


# -------------------------------------------------------------------- power
MUTANTS = [
    ("M0_live_verbatim", None),
    ("M1_always_flag", ("def receipt_shape_flag(row):", "def receipt_shape_flag(row):\n    return [{\"case\": row.get(\"case\"), \"why\": \"MUTANT_always\"}]")),
    ("M2_always_silent", ("def receipt_shape_flag(row):", "def receipt_shape_flag(row):\n    return []")),
    ("M3_unknown_case_failclosed",
     ('    if case not in CASES_SIG_BY_CASE:\n        return []\n',
      '    if case not in CASES_SIG_BY_CASE:\n        return [{"case": case, "why": "MUTANT_unknown"}]\n')),
    ("M4_pass_census_off",
     ('    pass_lines = [line for line in output if line.startswith("PASS ")]',
      '    pass_lines = []')),
    ("M5_span_check_off",
     ("    if begins or ends:\n", "    if False and (begins or ends):\n")),
    ("M6_derived_evidence_off",
     ('        return []\n    pin = CASES_SIG_BY_CASE.get(case)',
      '        pass\n    pin = CASES_SIG_BY_CASE.get(case)')),
    ("M7_pass_prefix_space_only",
     ('    pass_lines = [line for line in output if line.startswith("PASS ")]',
      '    pass_lines = [line for line in output if line.startswith("PASS")]')),
    ("M8_case_lookup_off",
     ('    if case not in CASES_SIG_BY_CASE:\n        return []\n', '    pass\n')),
]


def build_mutants(live_ns):
    fns = {}
    for name, splice in MUTANTS:
        if splice is None:
            fns[name] = live_ns["receipt_shape_flag"]
            continue
        old, new = splice
        fns[name] = splice_mutant(live_ns, name, old, new)
    return fns


def probe_designs():
    """Candidate C3 probe designs, each a predicate over (shape verdicts, control verdicts)."""
    return {
        "P0_any_shape_flags": lambda s, c: any(v for _n, v in s),
        "P1_all_shapes_flag": lambda s, c: all(v for _n, v in s),
        "P2_all_flag_and_controls_silent": lambda s, c: all(v for _n, v in s) and not any(c),
        "P3_controls_silent_only": lambda s, c: not any(c),
    }


def probe_designs_table(expected):
    """Designs that carry a per-shape expectation table (the C3 wording read
    literally: "every shape flags as classified"). `expected` maps shape name
    -> bool as recorded from the live gate at M0."""
    def p4(s, c):
        if any(c):
            return False
        return all(bool(v) == expected.get(n, False) for n, v in s)

    def p5(s, c):
        # weaker: only the shape-layer flag class must flag; clean-class shapes
        # are not required to stay silent.
        if any(c):
            return False
        return all(bool(v) for n, v in s if expected.get(n, False))

    return {"P4_expectation_table_all": p4, "P5_flag_class_only": p5}


def phase_power(live_ns):
    fns = build_mutants(live_ns)
    _m, ev, cases = mut05_variants()
    _a, adv = adversary_variants()
    # Union catalog: mut05's 10 shaped evasions + r103's 13 adversary variants
    # minus its control, so the matrix binds both flag classes the two r103
    # catalogs recorded.
    union = [(n, r) for n, r in ev] + [(n, r) for n, r in adv if n != "control_unmodified"]
    live_flag = live_ns["receipt_shape_flag"]
    controls = [bool(live_flag(r)) for r in cases.values()]
    expected = {n: bool(audit_one_from(live_flag, r)) for n, r in union}
    out = {"mutant_rows": {}, "probe_matrix": {}, "notes": {},
           "expected_table": expected, "catalog_size": len(union)}
    for mname, fn in fns.items():
        shape_verdicts = [(n, bool(audit_one_from(fn, r))) for n, r in union]
        ctl_verdicts = [bool(audit_one_from(fn, r)) for r in cases.values()]
        out["mutant_rows"][mname] = {
            "shapes_flagged": sum(v for _n, v in shape_verdicts),
            "controls_flagged": sum(ctl_verdicts),
            "control_truth": sum(controls),
        }
    designs = dict(probe_designs())
    designs.update(probe_designs_table(expected))
    for pname, pred in designs.items():
        row = {}
        for mname, fn in fns.items():
            s = [(n, bool(audit_one_from(fn, r))) for n, r in union]
            c = [bool(audit_one_from(fn, r)) for r in cases.values()]
            row[mname] = "GREEN" if pred(s, c) else "RED"
        out["probe_matrix"][pname] = row
    out["notes"]["vacuous_designs"] = sorted(
        p for p, row in out["probe_matrix"].items()
        if row["M1_always_flag"] == "GREEN" and row["M2_always_silent"] == "GREEN")
    out["notes"]["ground_truth_controls_silent"] = not any(controls)
    for pname, row in out["probe_matrix"].items():
        caught = sum(1 for m, v in row.items() if m != "M0_live_verbatim" and v == "RED")
        out["notes"].setdefault("design_score", {})[pname] = {
            "m0_green": row["M0_live_verbatim"] == "GREEN",
            "mutants_caught": caught, "mutants_total": len(row) - 1,
        }
    return out


# --------------------------------------------------------------------- main
def emit(name, payload):
    RECEIPTS.mkdir(parents=True, exist_ok=True)
    p = RECEIPTS / ("%s.json" % name)
    p.write_text(json.dumps(payload, indent=1, sort_keys=True, default=str) + "\n")
    print("WROTE %s (%d bytes)" % (p, p.stat().st_size))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("phase", nargs="?", default="all",
                    choices=["extract", "replay", "power", "census", "tighten", "all"])
    args = ap.parse_args()
    SCRATCH.mkdir(parents=True, exist_ok=True)
    live_ns, src, sha = load_live_module()
    fn_def = [n for n in ast.parse(src).body
              if isinstance(n, ast.FunctionDef) and n.name == "receipt_shape_flag"][0]
    live_ns["__src_segment__"] = ast.get_source_segment(src, fn_def)
    REPORT["battery_sha256"] = sha
    print("BATTERY sha256=%s bytes=%d" % (sha, len(src)))
    print("LIVE_PREDICATE cases=%d sig_by_case=%d grammar=%d derived=%s" % (
        len(live_ns["CASES"]), len(live_ns["CASES_SIG_BY_CASE"]),
        len(live_ns["RECEIPT_MULTI_PASS_GRAMMAR"]),
        sorted(live_ns["RECEIPT_SHAPE_DERIVED_EVIDENCE"])))
    ok = True
    if args.phase in ("extract", "all"):
        ex = {"battery_sha256": sha, "cases": len(live_ns["CASES"]),
              "grammar_rows": len(live_ns["RECEIPT_MULTI_PASS_GRAMMAR"]),
              "derived_evidence": sorted(live_ns["RECEIPT_SHAPE_DERIVED_EVIDENCE"]),
              "segment_lines": live_ns["__src_segment__"].count("\n")}
        REPORT["phases"]["extract"] = ex
        emit("extract", ex)
    if args.phase in ("replay", "all"):
        rp = phase_replay(live_ns)
        REPORT["phases"]["replay"] = rp
        emit("replay", rp)
        a = rp["adversary_summary"]
        m = rp["mut05_summary"]
        print("ADVERSARY variants=%d decision_agree=%d disagree=%d" % (
            a["variants"], a["decision_agree"], a["decision_disagree"]))
        for n, v in rp["adversary"].items():
            print("  %-26s rec_flagged=%-5s live_flagged=%-5s agree=%s live=%s" % (
                n, v["recorded_flagged"], v["live_flagged"], v["decision_agrees"],
                v["live_flags"]))
        print("MUT05 shapes=%d flagged=%d controls=%d silent=%d" % (
            m["shapes"], m["shapes_flagged"], m["controls"], m["controls_silent"]))
        for n, v in rp["mut05"].items():
            print("  %-30s flagged=%-5s %s" % (n, v["live_flagged"], v["live_flags"]))
        ok &= (a["decision_disagree"] == 0)
    if args.phase in ("census", "all"):
        cs = phase_census(live_ns)
        REPORT["phases"]["census"] = cs
        emit("census", cs)
        print("CENSUS rows_scanned=%d wide_only_shapes=%d rows_with_wide_only=%d flags=%d" % (
            cs["rows_scanned"], len(cs["wide_only_line_shapes"]),
            cs["rows_containing_wide_only_lines"], cs["flags_live_gate"]))
        for k, v in cs["flags_per_run"].items():
            print("  run=%s rows=%d flags=%d %s" % (k, v["rows"], v["flags"], v["cases"]))
        for k, v in cs["wide_only_line_shapes"].items():
            print("  WIDE_ONLY %r count=%d runs=%s" % (k, v["count"], v["runs"]))
    if args.phase in ("tighten", "all"):
        tg = phase_tighten(live_ns)
        REPORT["phases"]["tighten"] = tg
        emit("tighten", tg)
        print("TIGHTEN tab family (pre -> post_wide / post_lstrip):")
        for n, v in tg["tab_family"].items():
            print("  %-30s pre=%-5s post_wide=%-5s post_lstrip=%-5s" % (
                n, v["pre_flagged"], v["post_wide_flagged"], v["post_lstrip_flagged"]))
            print("      pre=%s" % v["pre"])
            print("      wide=%s" % v["post_wide"])
            print("      lstrip=%s" % v["post_lstrip"])
        print("TIGHTEN false_positives wide=%d lstrip=%d" % (
            tg["false_positives_from_tightening"], tg["false_positives_from_lstrip"]))
        for k, v in tg["real_rows"].items():
            print("  FP %s %s" % (k, v))
    if args.phase in ("power", "all"):
        pw = phase_power(live_ns)
        REPORT["phases"]["power"] = pw
        emit("power", pw)
        print("POWER mutants: shapes_flagged / controls_flagged")
        for n, v in pw["mutant_rows"].items():
            print("  %-28s shapes=%2d controls=%d" % (
                n, v["shapes_flagged"], v["controls_flagged"]))
        print("POWER probe matrix (rows=design, cols=mutant):")
        cols = list(MUTANTS)
        print("  %-34s %s" % ("design", " ".join("%-7s" % c[0].split("_")[0] for c in cols)))
        for pname, row in pw["probe_matrix"].items():
            print("  %-34s %s" % (pname, " ".join("%-7s" % row[c[0]] for c in cols)))
        print("VACUOUS_DESIGNS=%s" % pw["notes"]["vacuous_designs"])
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
