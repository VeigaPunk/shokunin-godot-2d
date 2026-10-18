#!/usr/bin/env python3
"""r101-ver12 floor-gate census checker.

Static, read-only audit of `corpus/fixtures/run_battery.py` (parsed with ast;
never executed, imported, or run). Answers, for new row families (default
`export_prod`, `r101_`), whether the dead-entry floor for that family is LIVE
once the rows land:

  * every family CASES row is registered — CASES is the only discovery path
    (`for case in CASES: execute(*case)` -> `results` -> `census_rows`);
  * every family `expected_errors` dict key has a CASES row (an orphan key is
    dead-by-construction: no row ever emits it);
  * every family fixture FILE on disk is referenced by a CASES row's script
    field — the battery copies the whole fixtures dir into scratch, but a file
    with no CASES row never executes and never reaches the census;
  * a `*_expected_errors_all_matched` gate covers every family row prefix
    (an uncovered family makes the family gate vacuous);
  * `cases_integrity`'s non-empty-coverage prefix list pins the family
    (`all()` over zero matching rows is True — the drop/rename hole).

Mutants are applied IN MEMORY to the parsed structures (no battery copies, no
/tmp writes — this host's tmpfs is quota-bound under sibling swarms). The
planned gate expression is the literal text recommended for landing, so its
eval is a real syntax/semantics check of the snippet, not a paraphrase.

Exit 0 iff every family verdict is PASS or PLANNED_GAP (family entirely
absent: no rows, no dict keys, no fixture files — reports `recommend=`).

Usage:
  python3 ver12_census_check.py
  python3 ver12_census_check.py --plant export_prod --plant-gate --plant-integrity
  python3 ver12_census_check.py --plant export_prod --plant-gate --plant-integrity \
      --drop-case export_prod_s01            # dropped row, entry kept -> FAIL
"""
import argparse
import ast
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
DEFAULT_BATTERY = REPO / "corpus" / "fixtures" / "run_battery.py"

GATE_KEY = "r101_expected_errors_all_matched"
GATE_PREFIXES = ["export_prod_", "r101_"]
GATE_EXPR = (
    'all(\n'
    '            not e["dead_in_run"]\n'
    '            for r in census_rows\n'
    '            if r["case"].startswith(("export_prod_", "r101_"))\n'
    '            for e in r["entries"])')


def parse_battery(path):
    src = path.read_text()
    tree = ast.parse(src)
    info = {"cases": [], "entries": {}, "gates": {}, "integrity": []}
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            targets = [t.id for t in node.targets if isinstance(t, ast.Name)]
            if "CASES" in targets and isinstance(node.value, ast.List):
                for elt in node.value.elts:
                    if isinstance(elt, ast.Tuple) and len(elt.elts) >= 5:
                        name, script = elt.elts[0], elt.elts[1]
                        if isinstance(name, ast.Constant) and isinstance(script, ast.Constant):
                            info["cases"].append((name.value, script.value))
            if "expected_errors" in targets:
                # Source: `expected_errors = { ... }.get(name, ())` — unwrap
                # the Call/Attribute to the literal Dict before key-walking.
                value = node.value
                if isinstance(value, ast.Call) and isinstance(value.func, ast.Attribute):
                    value = value.func.value
                if isinstance(value, ast.Dict):
                    for k, v in zip(value.keys, value.values):
                        if isinstance(k, ast.Constant) and isinstance(k.value, str):
                            entries = ([e.value for e in v.elts if isinstance(e, ast.Constant)]
                                       if isinstance(v, (ast.Tuple, ast.List)) else [])
                            info["entries"][k.value] = entries
    for node in ast.walk(tree):
        if not (isinstance(node, ast.Assign) and isinstance(node.value, ast.Dict)):
            continue
        if not any(isinstance(t, ast.Name) and t.id == "sf_discriminations"
                   for t in node.targets):
            continue
        for key, val in zip(node.value.keys, node.value.values):
            if not isinstance(key, ast.Constant):
                continue
            if key.value.endswith("_expected_errors_all_matched"):
                info["gates"][key.value] = {
                    "prefixes": startswith_prefixes(val),
                    "expr": ast.get_source_segment(src, val)}
            if key.value == "cases_integrity":
                for sub in ast.walk(val):
                    if (isinstance(sub, ast.Tuple) and len(sub.elts) >= 3
                            and all(isinstance(e, ast.Constant)
                                    and isinstance(e.value, str) for e in sub.elts)):
                        info["integrity"] = [e.value for e in sub.elts]
    return info


def startswith_prefixes(node):
    prefixes = []
    for call in ast.walk(node):
        if not (isinstance(call, ast.Call) and isinstance(call.func, ast.Attribute)
                and call.func.attr == "startswith" and call.args):
            continue
        arg = call.args[0]
        if isinstance(arg, ast.Constant) and isinstance(arg.value, str):
            prefixes.append(arg.value)
        elif isinstance(arg, ast.Tuple):
            prefixes.extend(e.value for e in arg.elts
                            if isinstance(e, ast.Constant) and isinstance(e.value, str))
    return sorted(set(prefixes))


def family_report(info, files, families):
    referenced = {script for _, script in info["cases"]}
    out = []
    for fam in families:
        rows = [(n, s) for n, s in info["cases"] if n.startswith(fam)]
        entries = {k: v for k, v in info["entries"].items() if k.startswith(fam)}
        names = {n for n, _ in info["cases"]}
        orphan_entries = sorted(set(entries) - names)
        missing_files = sorted(n for n, s in rows
                               if not s.startswith("__") and s not in files)
        disk_files = sorted(f for f in files if f.startswith(fam) and f != "run_battery.py")
        orphan_files = [f for f in disk_files if f not in referenced]
        covering = {k: v["prefixes"] for k, v in info["gates"].items()
                    if any(n.startswith(p) for n, _ in rows for p in v["prefixes"])}
        pinned = [p for p in info["integrity"] if fam.startswith(p) or p.startswith(fam)]
        defects = []
        if rows:
            if not covering:
                defects.append("gate_missing")
            if not pinned:
                defects.append("integrity_unpinned")
            if orphan_entries:
                defects.append("dict_entry_orphan")
            if orphan_files:
                defects.append("fixture_file_unreferenced")
            if missing_files:
                defects.append("fixture_file_missing")
            verdict = "PASS" if not defects else "FAIL"
        elif entries:
            # Rows gone but family dict keys remain: a dropped/renamed row —
            # the exact forge this seat guards.
            defects.append("rows_missing")
            defects.append("dict_entry_orphan")
            verdict = "FAIL"
        elif any(s.startswith(fam) for s in referenced):
            # A family fixture is wired to a case whose NAME carries a foreign
            # prefix: the r101 gate sees zero rows (vacuous) and some other
            # round's gate appears to cover it — coverage by collision.
            defects.append("row_under_foreign_prefix")
            verdict = "FAIL"
        elif disk_files:
            defects.append("rows_missing")
            defects.append("fixture_file_unreferenced")
            verdict = "FAIL"
        else:
            verdict = "PLANNED_GAP"
        out.append({"family": fam, "rows": len(rows), "row_names": [n for n, _ in rows],
                    "entries": len(entries), "orphan_entries": orphan_entries,
                    "disk_files": len(disk_files), "orphan_files": orphan_files,
                    "missing_files": missing_files, "covering": covering,
                    "pinned": pinned, "verdict": verdict, "defects": defects})
    return out


def vacuity_demo(info, gate_key, row_prefix):
    """Eval the REAL submitted gate expression on synthetic census_rows."""
    gate = info["gates"].get(gate_key)
    if not gate:
        return None
    base = [{"case": "x_probe", "entries": []}]
    fam = [{"case": row_prefix + "alpha", "entries": [
        {"entry": "ERROR: planted", "shape": "exact", "dead_in_run": False}]}]
    row = fam[0]
    return {"gate": gate_key, "prefixes": gate["prefixes"],
            "family_present": eval(gate["expr"], {"census_rows": base + fam}),
            "family_dropped": eval(gate["expr"], {"census_rows": base}),
            "family_renamed": eval(gate["expr"], {"census_rows": base + [
                {"case": "other_prefixed_alpha", "entries": row["entries"]}]})}


def apply_mutations(info, files, args):
    """In-memory only: no source file is written for any mutant."""
    if args.plant:
        for fam in args.plant.split(","):
            case = f"{fam.rstrip('_')}_s01"
            script = case + ".gd"
            info["cases"].append((case, script))
            info["entries"][case] = ["ERROR: planted r101 dead-entry probe"]
            files.add(script)
    if args.plant_gate:
        info["gates"][GATE_KEY] = {"prefixes": list(GATE_PREFIXES), "expr": GATE_EXPR}
    if args.plant_integrity:
        for p in GATE_PREFIXES:
            if p not in info["integrity"]:
                info["integrity"].append(p)
    for spec in args.drop_case or []:
        info["cases"] = [c for c in info["cases"] if c[0] != spec]
    for spec in args.rename_case or []:
        old, new = spec.split("=", 1)
        info["cases"] = [((new, s) if n == old else (n, s)) for n, s in info["cases"]]
    for spec in args.rename_entry or []:
        old, new = spec.split("=", 1)
        if old in info["entries"]:
            info["entries"][new] = info["entries"].pop(old)
    for name in args.orphan_fixture or []:
        files.add(name)
    for name in args.no_fixture or []:
        files.discard(name)
    for key in args.strip_gate or []:
        info["gates"].pop(key, None)
    for p in args.strip_integrity or []:
        info["integrity"] = [q for q in info["integrity"] if q != p]
    return info, files


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--battery", type=Path, default=DEFAULT_BATTERY)
    ap.add_argument("--fixtures", type=Path, default=None)
    ap.add_argument("--families", default="export_prod,r101_")
    ap.add_argument("--plant", default="", help="comma families to plant (row+entry+file)")
    ap.add_argument("--plant-gate", action="store_true")
    ap.add_argument("--plant-integrity", action="store_true")
    ap.add_argument("--drop-case", action="append")
    ap.add_argument("--rename-case", action="append")
    ap.add_argument("--rename-entry", action="append")
    ap.add_argument("--orphan-fixture", action="append")
    ap.add_argument("--no-fixture", action="append")
    ap.add_argument("--strip-gate", action="append")
    ap.add_argument("--strip-integrity", action="append")
    args = ap.parse_args()
    fixtures = args.fixtures or args.battery.parent
    info = parse_battery(args.battery)
    files = {p.name for p in fixtures.iterdir() if p.is_file()}
    info, files = apply_mutations(info, files, args)
    families = [f for f in args.families.split(",") if f]

    print(f"ver12_census_check battery={args.battery} fixtures={fixtures}")
    print(f"cases_rows={len(info['cases'])} "
          f"cases_unique={len({n for n, _ in info['cases']})}")
    print("gates=" + json.dumps({k: v["prefixes"] for k, v in info["gates"].items()},
                                sort_keys=True))
    print("integrity_prefixes=" + ",".join(info["integrity"]))
    print("census_scope=results_rows_with_nonempty_expected_errors "
          "(3663-3707); results only from CASES (2303); fixtures copied "
          "whole-dir into scratch (1675-1681)")
    # Global floor: EVERY entry-bearing case must be matched by some gate's
    # prefix, regardless of round. An entry whose case prefix no gate matches
    # can die silently — the per-round gates are prefix-scoped, the census
    # count itself is data, not a failure.
    entry_cases = sorted(info["entries"])
    uncovered = [c for c in entry_cases
                 if not any(c.startswith(p) for v in info["gates"].values()
                            for p in v["prefixes"])]
    print(f"entry_cases={len(entry_cases)} "
          f"entries_gated={len(entry_cases) - len(uncovered)} "
          f"uncovered_entry_cases={','.join(uncovered) or 'none'}")

    verdicts = []
    for rep in family_report(info, files, families):
        print(f"family={rep['family']} rows={rep['rows']} entries={rep['entries']} "
              f"orphan_entries={len(rep['orphan_entries'])} "
              f"fixture_files={rep['disk_files']} "
              f"orphan_fixture_files={len(rep['orphan_files'])} "
              f"missing_fixture_files={len(rep['missing_files'])} "
              f"covering_gates={','.join(rep['covering']) or 'none'} "
              f"integrity_pinned={bool(rep['pinned'])} "
              f"verdict={rep['verdict']} defects={','.join(rep['defects']) or 'none'}")
        for name in rep["row_names"]:
            print(f"  row={name}")
        for key in rep["orphan_entries"]:
            print(f"  orphan_entry={key}")
        for f in rep["orphan_files"]:
            print(f"  unreferenced_fixture={f}")
        if rep["verdict"] == "PLANNED_GAP":
            print(f"  recommend=gate {GATE_KEY} prefixes={GATE_PREFIXES} "
                  f"expr_sha_ok={eval(GATE_EXPR, {'census_rows': []}) is True} "
                  f"+ cases_integrity prefixes {GATE_PREFIXES}")
        verdicts.append(rep["verdict"])

    demo = vacuity_demo(info, "r100_expected_errors_all_matched", "r100b_")
    if demo:
        print(f"demo=gate_vacuity gate={demo['gate']} prefixes={demo['prefixes']} "
              f"family_present={demo['family_present']} "
              f"family_dropped={demo['family_dropped']} "
              f"family_renamed={demo['family_renamed']}")
    sys.exit(0 if all(v in ("PASS", "PLANNED_GAP") for v in verdicts) else 1)


if __name__ == "__main__":
    main()
