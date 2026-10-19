#!/usr/bin/env python3
"""W5 r103 — cases_integrity + floor-gate splice for the export_div_ row family.

Two hunks against corpus/fixtures/run_battery.py (orchestrator applies):

  H1  cases_integrity prefix tuple gains "export_div_" (fail-closed existence
      + CASES uniqueness already in place; a rows-less splice turns the gate
      red by construction).
  H2  two sf_discriminations clauses inserted after the r102 gate anchor
      (unique, verified below):
        r103_expected_errors_all_matched   per-prefix dead-entry floor
        r103_export_div_count_floor        family count floor (all registered
                                           rows ran; non-empty; --min-rows N
                                           freezes the count so a partial drop
                                           of CASES+results together fires)

Atomicity: H1/H2 must land in the SAME splice as the C1 CASES rows. A gate-only
splice turns the next battery red (self-test cells M/P); a rows-only splice
leaves the family floorless.

Modes:
  --check      (default) inspect the live file; exit 0 = POST-SPLICE,
               2 = PRE-SPLICE, 1 = broken/partial/duplicate.
  --self-test  byte-copies under /var/tmp/r103-w5/ ONLY; py_compile; AST-
               extract the three expressions; run counterfactuals against
               synthetic + real (latest verdicts.json) data. Never touches the
               repo, never runs the battery.
  --patch-out  write the unified diff (a/ b/ labels) for the orchestrator.
  --apply      write the splice to --file (orchestrator use only; atomic,
               py_compile-gated, refuses if already spliced).

This seat did NOT run --apply and never executes run_battery.py.
"""
import argparse
import ast
import difflib
import hashlib
import json
import pathlib
import py_compile
import sys
import tempfile

REPO = pathlib.Path(__file__).resolve().parents[3]
DEFAULT_FILE = REPO / "corpus/fixtures/run_battery.py"
REAL_RUN = REPO / "corpus/live/runs/20261018T213443471189Z/verdicts.json"
SCRATCH = pathlib.Path("/var/tmp/r103-w5")
PINNED_SHA = "40440356f0bf04481f518adc332d1ebb7ba79213878a9f3836421a512828a5c4"

GATE_KEY = "r103_expected_errors_all_matched"
COUNT_KEY = "r103_export_div_count_floor"
PREFIX = "export_div_"

# H2 anchor: tail of the r102 gate clause (unique in the pinned file).
ANCHOR = ('            if r["case"].startswith("export_launch_")\n'
          '            for e in r["entries"]),\n')
# H1 anchor: the r102-extended cases_integrity tuple's last line.
TUPLE_ANCHOR = '                          "export_launch_"))),\n'
TUPLE_NEW = '                          "export_launch_", "export_div_"))),\n'


def make_chunk(min_rows):
    if min_rows is None:
        count_lines = ('            == sum(1 for c in CASES if c[0].startswith("export_div_"))\n'
                       '            >= 1),')
    else:
        count_lines = f'            >= {min_rows}),'
    return (
        '        # r103 W5: the export_div_ family ships with no expected_errors\n'
        '        # entries today (nested Godot export output is redirected to\n'
        '        # scratch logs, never echoed - the export_prod.gd evidence rule),\n'
        '        # so this gate is vacuous-but-honest for it, carried so a future\n'
        '        # allowlist entry under the prefix cannot die silently; same\n'
        '        # named-by-round / covers-round-prefixes shape as r87-r102.\n'
        f'        "{GATE_KEY}": all(\n'
        '            not e["dead_in_run"]\n'
        '            for r in census_rows\n'
        f'            if r["case"].startswith(("{PREFIX}",))\n'
        '            for e in r["entries"]),\n'
        '        # r103 W5: export_div_ family count floor - every registered row\n'
        '        # ran (execution-loop splice defects) and the family is non-empty\n'
        '        # (a full-family drop from CASES and results together still fires).\n'
        '        # A partial drop with CASES and results shrunk together is invisible\n'
        '        # here by construction; freeze --min-rows N once the row set lands.\n'
        f'        "{COUNT_KEY}": (\n'
        '            sum(1 for r in results if r["case"].startswith("export_div_"))\n'
        f'{count_lines}\n')


def splice(src, min_rows=None):
    n, t = src.count(ANCHOR), src.count(TUPLE_ANCHOR)
    if n != 1 or t != 1:
        raise SystemExit(f"anchor counts gate={n} tuple={t}, expected 1/1; refusing")
    src = src.replace(ANCHOR, ANCHOR + make_chunk(min_rows), 1)
    return src.replace(TUPLE_ANCHOR, TUPLE_NEW, 1)


def key_counts(src):
    return (src.count(f'"{GATE_KEY}":'), src.count(f'"{COUNT_KEY}":'),
            src.count('"export_div_"))),'))


def compile_ok(text, name):
    with tempfile.NamedTemporaryFile("w", suffix=".py", delete=False) as fh:
        fh.write(text)
        tmp = fh.name
    try:
        py_compile.compile(tmp, doraise=True)
    finally:
        pathlib.Path(tmp).unlink()
    return True


def extract_sf_values(src, keys):
    tree = ast.parse(src)
    out = {}
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign) and any(
                getattr(t, "id", None) == "sf_discriminations" for t in node.targets):
            for k, v in zip(node.value.keys, node.value.values):
                if isinstance(k, ast.Constant) and k.value in keys:
                    out[k.value] = compile(ast.Expression(v), "<sf>", "eval")
    return out


def extract_func(src, name):
    tree = ast.parse(src)
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == name:
            mod = ast.Module(body=[node], type_ignores=[])
            ns = {}
            exec(compile(mod, "<extract>", "exec"), ns)  # noqa: S102 (pinned source)
            return ns[name]
    return None


def eval_expr(expr, **ns):
    return eval(expr, {"__builtins__": __builtins__}, ns)


def entry(dead):
    return {"case": "x", "entries": [{"entry": "ERROR: e", "dead_in_run": dead}]}


def selftest():
    SCRATCH.mkdir(parents=True, exist_ok=True)
    orig = DEFAULT_FILE.read_text()
    sha = hashlib.sha256(orig.encode()).hexdigest()
    print(f"target sha256={sha} pinned_match={sha == PINNED_SHA}")
    ok = []

    spliced = splice(orig)
    (SCRATCH / "run_battery_spliced.py").write_text(spliced)
    compile_ok(spliced, "spliced")
    print("PASS A py_compile spliced copy (both hunks)")
    ok.append(True)

    vals = extract_sf_values(spliced, (GATE_KEY, COUNT_KEY, "cases_integrity"))
    have = set(vals) == {GATE_KEY, COUNT_KEY, "cases_integrity"}
    print(("PASS" if have else "FAIL") + " B three expressions extracted via AST")
    ok.append(have)
    gate, floor, ci = vals.get(GATE_KEY), vals.get(COUNT_KEY), vals.get("cases_integrity")

    live = [{"case": "export_div_s01_a", "entries": [{"dead_in_run": False}]}]
    dead = [{"case": "export_div_s02_b", "entries": [{"dead_in_run": True}]}]
    out = [{"case": "export_launch_embed_boot", "entries": [{"dead_in_run": True}]}]
    cells = {
        "C gate True on live entry": eval_expr(gate, census_rows=live) is True,
        "D gate False on dead entry under prefix": eval_expr(gate, census_rows=dead) is False,
        "E gate True on dead entry outside prefix": eval_expr(gate, census_rows=out) is True,
        "F gate True on empty census (vacuous-but-honest)": eval_expr(gate, census_rows=[]) is True,
    }
    for k, v in cells.items():
        print(f"{'PASS' if v else 'FAIL'} {k}")
    ok += list(cells.values())

    row = {"case": "export_div_s01_a"}
    cells = {
        "G floor True when k rows ran of k registered (k=3)":
            eval_expr(floor, results=[row] * 3, CASES=[("export_div_s01_a",)] * 3) is True,
        "H floor False when family absent from both (0==0 but !>=1)":
            eval_expr(floor, results=[], CASES=[]) is False,
        "I floor False when 2 ran of 3 registered":
            eval_expr(floor, results=[row] * 2, CASES=[("export_div_s01_a",)] * 3) is False,
    }
    for k, v in cells.items():
        print(f"{'PASS' if v else 'FAIL'} {k}")
    ok += list(cells.values())

    spliced6 = splice(orig, min_rows=6)
    (SCRATCH / "run_battery_spliced_minrows6.py").write_text(spliced6)
    compile_ok(spliced6, "minrows6")
    floor6 = extract_sf_values(spliced6, (COUNT_KEY,))[COUNT_KEY]
    cells = {
        "J min-rows=6 True at 6 rows": eval_expr(floor6, results=[row] * 6, CASES=[]) is True,
        "K min-rows=6 False at 5 rows (partial drop fires)":
            eval_expr(floor6, results=[row] * 5, CASES=[]) is False,
    }
    for k, v in cells.items():
        print(f"{'PASS' if v else 'FAIL'} {k}")
    ok += list(cells.values())

    cases_uniq = [("export_div_s01_a",), ("r101_seqfull_clean",)]
    cells = {
        "L cases_integrity True with export_div row present":
            eval_expr(ci, CASES=cases_uniq,
                      results=[{"case": "export_div_s01_a"}]) is True,
        "M cases_integrity False with zero export_div rows (fail-closed)":
            eval_expr(ci, CASES=cases_uniq,
                      results=[{"case": "r101_seqfull_clean"}]) is False,
        "N cases_integrity False on duplicate CASES name (uniqueness intact)":
            eval_expr(ci, CASES=[("export_div_s01_a",), ("export_div_s01_a",)],
                      results=[{"case": "export_div_s01_a"}]) is False,
    }
    for k, v in cells.items():
        print(f"{'PASS' if v else 'FAIL'} {k}")
    ok += list(cells.values())

    # Real-data cells: latest battery artifact (554 rows, 0 export_div rows).
    real = json.loads(REAL_RUN.read_text())["results"]
    names = [r["case"] for r in real]
    n_div = sum(1 for n in names if n.startswith(PREFIX))
    cells = {
        f"O floor False on real artifact ({len(real)} rows, {n_div} export_div)":
            eval_expr(floor, results=real, CASES=[(n,) for n in names]) is False,
        "P cases_integrity False on real artifact (gate needs the rows)":
            eval_expr(ci, CASES=[(n,) for n in names], results=real) is False,
    }
    synth = real + [{"case": "export_div_s01_a"}, {"case": "export_div_s02_b"}]
    cells["Q floor+ci True after 2 synthetic export_div rows"] = (
        eval_expr(floor, results=synth,
                  CASES=[(n,) for n in names] + [("export_div_s01_a",), ("export_div_s02_b",)]) is True
        and eval_expr(ci, CASES=[(n,) for n in names] + [("export_div_s01_a",), ("export_div_s02_b",)],
                      results=synth) is True)
    for k, v in cells.items():
        print(f"{'PASS' if v else 'FAIL'} {k}")
    ok += list(cells.values())

    # R: reconstruct census_rows from the real artifact with the pinned
    # surface_allowed_error matcher; gate must be True (vacuous on real rows)
    # and the reconstruction must reproduce the artifact's dead_entry_count.
    matcher = extract_func(orig, "surface_allowed_error")
    census, dead = [], 0
    for r in real:
        entries = r.get("expected_errors") or []
        if not entries or not isinstance(r.get("output"), list):
            continue
        recs = []
        for e in entries:
            matched = [ln for ln in r["output"] if matcher(ln, e)]
            dead += 0 if matched else 1
            recs.append({"entry": e, "dead_in_run": not matched})
        census.append({"case": r["case"], "entries": recs})
    art_dead = [x for x in real if x["case"] == "probe_error_clause_surface"][0]["census"]["dead_entry_count"]
    cells = {
        f"R census reconstruction dead={dead} == artifact {art_dead}":
            dead == art_dead and dead == 0,
        "R2 gate True over reconstructed real census (no export_div entries)":
            eval_expr(gate, census_rows=census) is True,
    }
    for k, v in cells.items():
        print(f"{'PASS' if v else 'FAIL'} {k}")
    ok += list(cells.values())

    print("all_pass =", all(ok))
    return 0 if all(ok) else 1


def make_patch(orig, min_rows=None):
    new = splice(orig, min_rows)
    diff = difflib.unified_diff(
        orig.splitlines(keepends=True), new.splitlines(keepends=True),
        fromfile="a/corpus/fixtures/run_battery.py",
        tofile="b/corpus/fixtures/run_battery.py")
    return "".join(diff)


def check(path):
    src = path.read_text()
    g, c, t = key_counts(src)
    compile_ok(src, str(path))
    print(f"file={path} sha256={hashlib.sha256(src.encode()).hexdigest()}")
    print(f"gate_key_count={g} count_key_count={c} tuple_patched={t} "
          f"anchor_gate={src.count(ANCHOR)} anchor_tuple={src.count(TUPLE_ANCHOR)}")
    if g == 1 and c == 1 and t == 1:
        print("POST-SPLICE")
        return 0
    if g == 0 and c == 0 and t == 0:
        print("PRE-SPLICE")
        return 2
    print("BROKEN (duplicate/partial splice)")
    return 1


def apply_splice(path, min_rows):
    src = path.read_text()
    g, c, t = key_counts(src)
    if g or c or t:
        raise SystemExit("already spliced; refusing (use --check)")
    new = splice(src, min_rows)
    compile_ok(new, str(path))
    tmp = path.with_suffix(".py.w5tmp")
    tmp.write_text(new)
    tmp.replace(path)
    print(f"applied to {path}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--file", default=str(DEFAULT_FILE))
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--patch-out", nargs="?", const=str(SCRATCH / "w5_export_div.patch"))
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--min-rows", type=int, default=None)
    args = ap.parse_args()
    if args.self_test:
        sys.exit(selftest())
    if args.patch_out:
        SCRATCH.mkdir(parents=True, exist_ok=True)
        p = pathlib.Path(args.patch_out)
        p.write_text(make_patch(DEFAULT_FILE.read_text(), args.min_rows))
        print(f"patch written to {p} ({p.stat().st_size} bytes)")
        sys.exit(0)
    if args.apply:
        apply_splice(pathlib.Path(args.file), args.min_rows)
        sys.exit(0)
    sys.exit(check(pathlib.Path(args.file)))
