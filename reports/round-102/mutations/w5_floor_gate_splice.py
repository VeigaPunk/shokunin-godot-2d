#!/usr/bin/env python3
"""W5 r102 — floor-gate splice for the export_launch_ row family.

Inserts two `sf_discriminations` clauses into corpus/fixtures/run_battery.py,
immediately after the r101 per-round gate (unique anchor, verified below):

  r102_expected_errors_all_matched   per-prefix dead-entry floor (r87-r101 shape)
  r102_export_launch_count_floor     family count floor (registered rows all ran;
                                     non-empty; --min-rows N freezes the count so a
                                     later partial drop of CASES+results together
                                     (r102-w6 cell G) also fires)

The r102-w6 seat owns the cases_integrity prefix tuple; this script owns the
floor side. Land both in the SAME splice as the C1 CASES rows: a gate-only
splice turns the next battery red (mirror of the r101 F2 defect; see --self-test
J-cell), a rows-only splice leaves the family floorless.

Modes:
  --check      (default) inspect the live file; exit 0 = POST-SPLICE (both keys
               exactly once), 2 = PRE-SPLICE (both absent), 1 = broken/duplicate.
  --self-test  apply to byte-copies under /var/tmp/r102-w5/ ONLY, py_compile
               them, extract the two expressions via AST and run counterfactuals
               against synthetic + real (r101 run-2) data. Never touches the repo.
  --apply      write the splice to --file (orchestrator use only; atomic,
               py_compile-gated, refuses if already spliced).

This seat did NOT run --apply and never executes run_battery.py.
"""
import argparse
import ast
import pathlib
import py_compile
import shutil
import subprocess
import sys
import tempfile

REPO = pathlib.Path(__file__).resolve().parents[3]
DEFAULT_FILE = REPO / "corpus/fixtures/run_battery.py"
RUN2 = REPO / "corpus/live/runs/20261018T202131127599Z/verdicts.json"
SCRATCH = pathlib.Path("/var/tmp/r102-w5")
PINNED_SHA = "bb8f79c92fbc6b7dc9b0c7d7adaffb4d103a51a368970a1b242a08f5915c1336"

GATE_KEY = "r102_expected_errors_all_matched"
COUNT_KEY = "r102_export_launch_count_floor"
PREFIX = "export_launch_"

ANCHOR = ('            if r["case"].startswith(("r101_seqfull_", "r101_ytrans_", "export_prod_"))\n'
          '            for e in r["entries"]),\n')


def make_chunk(min_rows):
    if min_rows is None:
        count_lines = ('            == sum(1 for c in CASES if c[0].startswith("export_launch_"))\n'
                       '            >= 1),')
    else:
        count_lines = f'            >= {min_rows}),'
    return (
        '        # r102 W5: the export_launch_ family ships with no expected_errors\n'
        '        # entries today (nested Godot output is redirected to scratch logs,\n'
        '        # never echoed - the export_prod.gd evidence rule), so this gate is\n'
        '        # vacuous-but-honest for it, carried so a future allowlist entry\n'
        '        # under the prefix cannot die silently; same named-by-round /\n'
        '        # covers-round-prefixes shape as r87-r101.\n'
        f'        "{GATE_KEY}": all(\n'
        '            not e["dead_in_run"]\n'
        '            for r in census_rows\n'
        f'            if r["case"].startswith(("{PREFIX}",))\n'
        '            for e in r["entries"]),\n'
        '        # r102 W5: export_launch_ family count floor - every registered row\n'
        '        # ran (execution-loop splice defects) and the family is non-empty\n'
        '        # (a full-family drop from CASES and results together still fires).\n'
        '        # A partial drop with CASES and results shrunk together is invisible\n'
        '        # here by construction; freeze --min-rows N when the row set lands.\n'
        f'        "{COUNT_KEY}": (\n'
        '            sum(1 for r in results if r["case"].startswith("export_launch_"))\n'
        f'{count_lines}\n')


def splice(src, min_rows=None):
    n = src.count(ANCHOR)
    if n != 1:
        raise SystemExit(f"anchor count = {n}, expected exactly 1; refusing")
    return src.replace(ANCHOR, ANCHOR + make_chunk(min_rows), 1)


def key_counts(src):
    return src.count(f'"{GATE_KEY}":'), src.count(f'"{COUNT_KEY}":')


def compile_ok(text, name):
    with tempfile.NamedTemporaryFile("w", suffix=".py", delete=False) as fh:
        fh.write(text)
        tmp = fh.name
    try:
        py_compile.compile(tmp, doraise=True)
    finally:
        pathlib.Path(tmp).unlink()
    return True


def extract_sf_value(src, key):
    tree = ast.parse(src)
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign) and any(
                getattr(t, "id", None) == "sf_discriminations" for t in node.targets):
            for k, v in zip(node.value.keys, node.value.values):
                if isinstance(k, ast.Constant) and k.value == key:
                    return compile(ast.Expression(v), "<sf>", "eval")
    return None


def eval_expr(expr, **ns):
    return eval(expr, {"__builtins__": __builtins__}, ns)


def entry(dead):
    return {"case": "x", "entries": [{"entry": "ERROR: e", "dead_in_run": dead}]}


def selftest():
    SCRATCH.mkdir(parents=True, exist_ok=True)
    orig = DEFAULT_FILE.read_text()
    import hashlib
    sha = hashlib.sha256(orig.encode()).hexdigest()
    print(f"target sha256={sha} pinned_match={sha == PINNED_SHA}")
    results = []

    spliced = splice(orig)
    p1 = SCRATCH / "run_battery_spliced.py"
    p1.write_text(spliced)
    compile_ok(spliced, str(p1))
    print("A py_compile spliced copy: PASS")

    gate = extract_sf_value(spliced, GATE_KEY)
    floor = extract_sf_value(spliced, COUNT_KEY)
    print("B both keys extracted via AST:", "PASS" if gate and floor else "FAIL")
    results += [bool(gate and floor)]

    live = [{"case": "export_launch_s02_embedded_quit_frames", "entries": [{"dead_in_run": False}]}]
    dead = [{"case": "export_launch_s02_nonembed_contrast", "entries": [{"dead_in_run": True}]}]
    out = [{"case": "r101_ytrans_census", "entries": [{"dead_in_run": True}]}]
    cells = {
        "C gate True on live entry": eval_expr(gate, census_rows=live) is True,
        "D gate False on dead entry": eval_expr(gate, census_rows=dead) is False,
        "E gate True on dead entry outside prefix": eval_expr(gate, census_rows=out) is True,
        "F gate True on empty census": eval_expr(gate, census_rows=[]) is True,
    }
    for k, v in cells.items():
        print(f"{'PASS' if v else 'FAIL'} {k}")
    results += list(cells.values())

    row = {"case": "export_launch_x"}
    cells = {
        "G floor True when k rows ran of k registered (k=3)":
            eval_expr(floor, results=[row] * 3, CASES=[("export_launch_x",)] * 3) is True,
        "H floor False when family absent from both (0==0 but !>=1)":
            eval_expr(floor, results=[], CASES=[]) is False,
        "I floor False when 2 ran of 3 registered":
            eval_expr(floor, results=[row] * 2, CASES=[("export_launch_x",)] * 3) is False,
    }
    for k, v in cells.items():
        print(f"{'PASS' if v else 'FAIL'} {k}")
    results += list(cells.values())

    spliced6 = splice(orig, min_rows=6)
    (SCRATCH / "run_battery_spliced_minrows6.py").write_text(spliced6)
    compile_ok(spliced6, "minrows6")
    floor6 = extract_sf_value(spliced6, COUNT_KEY)
    cells = {
        "J min-rows=6 True at 6 rows": eval_expr(floor6, results=[row] * 6, CASES=[]) is True,
        "K min-rows=6 False at 5 rows (partial drop fires)":
            eval_expr(floor6, results=[row] * 5, CASES=[]) is False,
    }
    for k, v in cells.items():
        print(f"{'PASS' if v else 'FAIL'} {k}")
    results += list(cells.values())

    # Real-data J-cell: the r101 run-2 artifact + the real CASES names.
    real = json.loads(RUN2.read_text())["results"]
    tree = ast.parse(orig)
    cases = next(n.value for n in ast.walk(tree)
                 if isinstance(n, ast.Assign)
                 and getattr(n.targets[0], "id", None) == "CASES")
    names = [ast.literal_eval(e)[0] for e in cases.elts]
    pre = eval_expr(floor, results=real, CASES=[(n,) for n in names])
    post = eval_expr(floor, results=real + [row, row],
                     CASES=[(n,) for n in names] + [("export_launch_x",)] * 2)
    cells = {
        "L floor False on real r101 run-2 (rows must land with the gate)": pre is False,
        "M floor True on real run-2 + 2 synthetic launch rows": post is True,
    }
    for k, v in cells.items():
        print(f"{'PASS' if v else 'FAIL'} {k}")
    results += list(cells.values())

    print("all_pass =", all(results))
    return 0 if all(results) else 1


def check(path):
    src = path.read_text()
    g, c = key_counts(src)
    n = src.count(ANCHOR)
    compile_ok(src, str(path))
    print(f"file={path} anchor_count={n} gate_key_count={g} count_key_count={c}")
    if g == 1 and c == 1:
        print("POST-SPLICE")
        return 0
    if g == 0 and c == 0:
        print("PRE-SPLICE")
        return 2
    print("BROKEN (duplicate/partial splice)")
    return 1


def apply_splice(path, min_rows):
    src = path.read_text()
    g, c = key_counts(src)
    if g or c:
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
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--min-rows", type=int, default=None)
    args = ap.parse_args()
    import json  # noqa: E402  (self-test only)
    if args.self_test:
        sys.exit(selftest())
    if args.apply:
        apply_splice(pathlib.Path(args.file), args.min_rows)
        sys.exit(0)
    sys.exit(check(pathlib.Path(args.file)))
