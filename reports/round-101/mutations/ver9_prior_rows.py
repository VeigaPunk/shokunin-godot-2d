#!/usr/bin/env python3
"""r101-VER-9: orchestrator battery-regression comparator (prior-row stability).

Compares a current run_battery verdicts.json against the durable r100 baseline
(reports/round-101/mutations/ver9_baseline_r100.json) and enforces:

  C1 inventory     no prior case dropped; every current row PASS; battery PASS
  C2 7-field tuple (script, flags, expected_exit, actual_exit, signature,
                   verdict, error) value-set equality on every prior name
  C3 multiplicity  per-name execution count equals the baseline count, except
                   names carrying a recorded dedupe disposition (9ede7c50:
                   crash_spontaneous_sigabrt 3->1, crash_self_sigkill 2->1);
                   an extra *identical* copy is still a mismatch (forgery class)
  C4 only-new      rows added by this round are reported and, when
                   --expect-new-prefixes is given, must match those prefixes,
                   each prefix must be non-empty, and all new rows must PASS
  C5 probes        prior probe/meta rows present, verdict-identical, and every
                   baseline-true discrimination key still present and true
  C6 census guard  error-clause census: dead_entry_count not above baseline,
                   rows_with_expected_errors not below baseline
  C7 registry      --runner: CASES names unique, every baseline name present,
                   and per-name script/flags/expected_exit matching the
                   baseline value set (static, no battery run)

--registry-only runs just C7 (pre-flight, no receipt needed).  This script
never runs the battery and never writes into the repo's tracked fixtures; it
reads two JSON receipts (+ optional runner source) and prints/writes a report.

Usage:
  python3 ver9_prior_rows.py --baseline ver9_baseline_r100.json \
      --current /var/tmp/r101-integration/runs/<ts>/verdicts.json \
      --runner corpus/fixtures/run_battery.py \
      --expect-new-prefixes r101_ --report /var/tmp/r101-ver9/regression.json
Exit 0 = 0-mismatch PASS; exit 1 = any criterion failed.
"""
import argparse
import ast
import hashlib
import json
from collections import Counter
from pathlib import Path

FIELDS = ("script", "flags", "expected_exit", "actual_exit", "signature", "verdict", "error")


def canon(value):
    return json.dumps(value, sort_keys=True)


def tuple7(row):
    return tuple(canon(row.get(f)) for f in FIELDS)


def load_cased(path):
    payload = json.loads(Path(path).read_bytes())
    rows = [x for x in payload["results"] if "script" in x]
    probes = {x["case"]: x for x in payload["results"] if "script" not in x}
    return payload, rows, probes


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--baseline", required=True, type=Path)
    ap.add_argument("--current", type=Path, default=None,
                    help="battery verdicts.json; omitted with --registry-only")
    ap.add_argument("--runner", type=Path, default=None)
    ap.add_argument("--registry-only", action="store_true",
                    help="pre-flight: static CASES check against the baseline, no receipt")
    ap.add_argument("--expect-new-prefixes", nargs="*", default=[])
    ap.add_argument("--report", type=Path, default=None)
    args = ap.parse_args()
    if not args.registry_only and args.current is None:
        ap.error("--current is required unless --registry-only")
    if args.registry_only and args.runner is None:
        ap.error("--registry-only requires --runner")

    base = json.loads(args.baseline.read_bytes())
    base_by = {}
    for x in base["cased_rows"]:
        base_by.setdefault(x["case"], []).append(x)
    base_probes = {p["case"]: p for p in base.get("probe_rows", [])}

    failures = []
    receipts = {}
    if args.registry_only:
        cur_payload, cur_rows, cur_probes = {}, [], {}
    else:
        cur_payload, cur_rows, cur_probes = load_cased(args.current)
        receipts = {"current_sha256": hashlib.sha256(args.current.read_bytes()).hexdigest()}

    if not args.registry_only:
        # ---- C1 inventory -------------------------------------------------
        cur_by = {}
        for x in cur_rows:
            cur_by.setdefault(x["case"], []).append(x)
        dropped = sorted(set(base_by) - set(cur_by))
        if dropped:
            failures.append({"class": "prior_case_dropped", "cases": dropped})
        non_pass = [x["case"] + f"={x.get('verdict')}" for x in cur_rows
                    if x.get("verdict") != "PASS"]
        if cur_payload.get("verdict") != "PASS":
            failures.append({"class": "battery_verdict", "value": cur_payload.get("verdict")})
        if non_pass:
            failures.append({"class": "non_pass_rows", "rows": non_pass})

        # ---- C2 7-field tuple + C3 multiplicity ---------------------------
        dispositions = base.get("multiplicity_dispositions", {})
        mismatches, multiplicity = [], []
        for name in sorted(set(base_by) & set(cur_by)):
            bvals = {tuple7(x) for x in base_by[name]}
            cvals = {tuple7(x) for x in cur_by[name]}
            for t in sorted(bvals - cvals):
                mismatches.append({"class": "prior_value_missing", "case": name,
                                   "tuple": dict(zip(FIELDS, t))})
            for t in sorted(cvals - bvals):
                mismatches.append({"class": "prior_value_drift", "case": name,
                                   "tuple": dict(zip(FIELDS, t))})
            expected = dispositions.get(name, {}).get("expected_current_copies",
                                                      len(base_by[name]))
            if len(cur_by[name]) != expected:
                multiplicity.append({"case": name, "baseline_copies": len(base_by[name]),
                                     "expected_current_copies": expected,
                                     "current_copies": len(cur_by[name])})
        if mismatches:
            failures.append({"class": "prior_tuple_mismatch", "count": len(mismatches)})
        if multiplicity:
            failures.append({"class": "multiplicity", "count": len(multiplicity)})

        # ---- C4 only-new --------------------------------------------------
        only_new = sorted(set(cur_by) - set(base_by))
        new_bad = sorted(n for n in only_new if cur_by[n][0].get("verdict") != "PASS")
        if new_bad:
            failures.append({"class": "new_row_non_pass", "cases": new_bad})
        prefix_census = {}
        if args.expect_new_prefixes:
            for p in args.expect_new_prefixes:
                hits = [n for n in only_new if n.startswith(p)]
                prefix_census[p] = len(hits)
                if not hits:
                    failures.append({"class": "new_prefix_empty", "prefix": p})
            stray = [n for n in only_new
                     if not any(n.startswith(p) for p in args.expect_new_prefixes)]
            if stray:
                failures.append({"class": "new_row_unexpected_prefix", "cases": stray})

        # ---- C5 probes ----------------------------------------------------
        probe_missing = sorted(set(base_probes) - set(cur_probes))
        probe_verdict_diff = [
            {"case": n, "baseline": base_probes[n]["verdict"],
             "current": cur_probes[n].get("verdict")}
            for n in sorted(set(base_probes) & set(cur_probes))
            if base_probes[n].get("verdict") != cur_probes[n].get("verdict")]
        disc_missing, disc_flipped, disc_added = [], [], {}
        for n in sorted(set(base_probes) & set(cur_probes)):
            bdisc = base_probes[n].get("discriminations", {})
            cdisc = cur_probes[n].get("discriminations", {})
            for k, v in bdisc.items():
                if k not in cdisc:
                    disc_missing.append({"case": n, "key": k})
                elif bool(cdisc[k]) != bool(v):
                    disc_flipped.append({"case": n, "key": k, "baseline": v,
                                         "current": cdisc[k]})
            extra = sorted(set(cdisc) - set(bdisc))
            if extra:
                disc_added[n] = extra
        if probe_missing:
            failures.append({"class": "prior_probe_dropped", "cases": probe_missing})
        if probe_verdict_diff:
            failures.append({"class": "probe_verdict_drift", "rows": probe_verdict_diff})
        if disc_flipped or disc_missing:
            failures.append({"class": "discriminations_not_preserved",
                             "flipped": disc_flipped, "missing": disc_missing})

        # ---- C6 census guard ----------------------------------------------
        census_guard = {"baseline": None, "current": None}
        bsurf = base_probes.get("probe_error_clause_surface", {}).get("census", {})
        csurf = cur_probes.get("probe_error_clause_surface", {}).get("census", {})
        if not csurf:
            failures.append({"class": "census_unavailable_in_current"})
        else:
            census_guard = {
                "baseline": {"rows_with_expected_errors": bsurf.get("rows_with_expected_errors"),
                             "dead_entry_count": bsurf.get("dead_entry_count")},
                "current": {"rows_with_expected_errors": csurf.get("rows_with_expected_errors"),
                            "dead_entry_count": csurf.get("dead_entry_count")},
            }
            if csurf.get("dead_entry_count", 0) > bsurf.get("dead_entry_count", 0):
                failures.append({"class": "census_dead_entry",
                                 "baseline": bsurf.get("dead_entry_count"),
                                 "current": csurf.get("dead_entry_count")})
            if (csurf.get("rows_with_expected_errors", 0)
                    < bsurf.get("rows_with_expected_errors", 0)):
                failures.append({"class": "census_row_floor",
                                 "baseline": bsurf.get("rows_with_expected_errors"),
                                 "current": csurf.get("rows_with_expected_errors")})
        only_new = sorted(set(cur_by) - set(base_by))
    else:
        cur_by, only_new = {}, []
        mismatches, multiplicity = [], []
        census_guard, prefix_census = {}, {}
        probe_missing, probe_verdict_diff = [], []
        disc_missing, disc_flipped, disc_added = [], [], {}

    # ---- C7 registry (static; doubles as the pre-flight check) -------------
    registry_new_prefix_census = {}
    if args.runner is not None:
        cases = None
        for node in ast.parse(Path(args.runner).read_bytes()).body:
            if isinstance(node, ast.Assign) and any(
                    getattr(t, "id", None) == "CASES" for t in node.targets):
                cases = ast.literal_eval(node.value)
        if cases is None:
            failures.append({"class": "runner_cases_missing"})
        else:
            reg = {c[0]: c for c in cases}
            names = [c[0] for c in cases]
            if len(set(names)) != len(names):
                failures.append({"class": "registry_duplicate_names",
                                 "dups": {k: v for k, v in Counter(names).items() if v > 1}})
            missing_reg = sorted(set(base_by) - set(reg))
            if missing_reg:
                failures.append({"class": "registry_prior_case_missing", "cases": missing_reg})
            static_mismatch = []
            for name, c in sorted(reg.items()):
                if name not in base_by:
                    continue
                for f, idx in (("script", 1), ("flags", 2), ("expected_exit", 3)):
                    want = {canon(x.get(f)) for x in base_by[name]}
                    if canon(c[idx]) not in want:
                        static_mismatch.append({"case": name, "field": f,
                                                "registry": c[idx],
                                                "baseline": sorted(want)})
            if static_mismatch:
                failures.append({"class": "registry_static_mismatch",
                                 "count": len(static_mismatch)})
            for p in args.expect_new_prefixes:
                hits = [n for n in reg if n.startswith(p)]
                registry_new_prefix_census[p] = len(hits)
                if not hits:
                    failures.append({"class": "registry_new_prefix_empty", "prefix": p})

    report = {
        "verdict": "PASS" if not failures else "FAIL",
        "mode": "registry_only" if args.registry_only else "receipt",
        "baseline_id": base.get("baseline_id"),
        "baseline_source_sha256": base.get("source_sha256"),
        **receipts,
        "tuple_fields": list(FIELDS),
        "criteria": {
            "prior_cases": len(base_by),
            "current_cases": len(cur_by),
            "only_new": only_new,
            "new_prefix_census": prefix_census,
            "prior_tuple_mismatches": len(mismatches),
            "multiplicity_violations": len(multiplicity),
            "probe_rows": len(base_probes),
            "discrimination_keys": sum(
                len(p.get("discriminations", {})) for p in base_probes.values()),
            "discrimination_keys_added": disc_added,
            "census_guard": census_guard,
            "registry_new_prefix_census": registry_new_prefix_census,
        },
        "mismatches": mismatches,
        "multiplicity": multiplicity,
        "probe": {"missing": probe_missing, "verdict_diffs": probe_verdict_diff,
                  "discrimination_missing": disc_missing,
                  "discrimination_flipped": disc_flipped},
        "failures": failures,
    }
    text = json.dumps(report, indent=1) + "\n"
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(text)
    print(text)
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
