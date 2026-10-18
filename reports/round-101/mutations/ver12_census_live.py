#!/usr/bin/env python3
"""r101-ver12 live-census pin: execute the battery's REAL census code.

The battery is never run. Instead the census machinery is sliced out of
`corpus/fixtures/run_battery.py` by AST line range and exec'd in a scratch
namespace against synthetic `results` rows:

  * `classify_process`          (battery 1725-1742)
  * `surface_allowed_error`     (3643-3654)
  * `entry_shape`               (3656-3661)
  * the census loop + `dead_entries` comprehension (3663-3707, verbatim slice)

so `dead_entry_count` is measured by the shipping implementation, not by a
paraphrase. Reported per scenario: dead_entry_count, dead_entries, and the
value of the submitted per-round gate expression evaluated over census_rows.

Usage: python3 ver12_census_live.py [--battery PATH]
"""
import argparse
import ast
import textwrap
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
DEFAULT_BATTERY = REPO / "corpus" / "fixtures" / "run_battery.py"


def slice_functions(src, tree, names):
    out = {}
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name in names:
            out[node.name] = textwrap.dedent(ast.get_source_segment(src, node))
    return out


def slice_census(src, tree):
    loop = None
    dead = None
    for node in ast.walk(tree):
        if (isinstance(node, ast.For) and getattr(node.iter, "id", None) == "results"
                and any(isinstance(c, ast.Call) and getattr(c.func, "id", "") == "surface_allowed_error"
                        for c in ast.walk(node))):
            loop = node
        if isinstance(node, ast.Assign) and any(
                isinstance(t, ast.Name) and t.id == "dead_entries" for t in node.targets):
            dead = node
    assert loop is not None and dead is not None and dead.lineno > loop.lineno, \
        "census slice anchors not found (battery layout changed)"
    lines = src.splitlines()
    return textwrap.dedent("\n".join(lines[loop.lineno - 1:dead.end_lineno]))


def census_count(ns, results):
    ns["results"] = results
    ns["census_rows"] = []  # battery line 3663, immediately before the slice
    exec(compile(NS_CENSUS, "<census-slice>", "exec"), ns)
    return len(ns["dead_entries"]), ns["dead_entries"], ns["census_rows"]


def row(case, output, entries, signature="PASS ok", exit_code=0):
    return {"case": case, "verdict": "PASS", "actual_exit": exit_code, "error": None,
            "expected_exit": 0, "signature": signature, "output": output,
            "expected_errors": list(entries)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--battery", type=Path, default=DEFAULT_BATTERY)
    args = ap.parse_args()
    src = args.battery.read_text()
    tree = ast.parse(src)
    ns = {}
    funcs = slice_functions(src, tree, {"classify_process", "surface_allowed_error",
                                        "entry_shape"})
    global NS_CENSUS
    NS_CENSUS = slice_census(src, tree)
    ns["re"] = __import__("re")
    for name, body in funcs.items():
        exec(compile(body, f"<{name}>", "exec"), ns)
    print(f"ver12_census_live battery={args.battery}")
    print(f"sliced={sorted(funcs)} census_slice_lines={len(NS_CENSUS.splitlines())}")

    # (a) a dead entry in the shape a real battery row can have: the captured
    # output is clean and carries the signature (so the row's own verdict is
    # still PASS), the allowlisted line is simply never emitted. The entry
    # dies silently unless the census counts it and a gate consumes the count.
    dead_row = row("export_prod_s01", ["PASS ok", "no error here"],
                   ["ERROR: planted never-emitted diagnostic"])
    count, dead, rows = census_count(dict(ns), [dead_row])
    print(f"scenario=dead_entry_silent dead_entry_count={count} "
          f"dead={[d['case'] + ':' + d['shape'] for d in dead]} "
          f"census_rows={len(rows)} row_verdict={rows[0]['verdict']} "
          f"any_entry_matched={rows[0]['any_entry_matched']} "
          f"bare_rejects={rows[0]['bare_classification_rejects']} "
          f"allowlisted_passes={rows[0]['allowlisted_classification_passes']}")

    # (a2) the unfaithful shape: dead entry AND the row fails bare (no
    # signature) — the census reports the same dead count but the row's own
    # verdict already fails, so the death is loud.
    loud_row = row("export_prod_s01", ["PASS export_prod s01", "no error here"],
                   ["ERROR: planted never-emitted diagnostic"])
    count_l, dead_l, rows_l = census_count(dict(ns), [loud_row])
    print(f"scenario=dead_entry_loud dead_entry_count={count_l} "
          f"census_rows={len(rows_l)} any_entry_matched={rows_l[0]['any_entry_matched']} "
          f"bare_rejects={rows_l[0]['bare_classification_rejects']}")

    # (b) the same entry, emitted: the floor's other direction.
    ok_row = row("export_prod_s01", ["PASS export_prod s01",
                                     "ERROR: planted never-emitted diagnostic"],
                 ["ERROR: planted never-emitted diagnostic"])
    count_ok, dead_ok, rows_ok = census_count(dict(ns), [ok_row])
    print(f"scenario=live_entry dead_entry_count={count_ok} dead={dead_ok} "
          f"census_rows={len(rows_ok)} any_entry_matched={rows_ok[0]['any_entry_matched']}")

    # (c) entry-less row: out of census scope entirely (no row record at all).
    plain = row("r101_probe_plain", ["PASS r101 probe"], [])
    count_p, dead_p, rows_p = census_count(dict(ns), [plain])
    print(f"scenario=entryless_row dead_entry_count={count_p} census_rows={len(rows_p)}")

    # (d) sentinel-path ceiling: a row resolved by a custom classifier never
    # gets the dict applied (source: `expected_errors = ()` then `if passed is
    # None:`), so its row carries [] and the census cannot see it.
    sentinel = row("export_readiness", ["[ DONE ]"], [])
    sentinel["expected_exit"] = 0
    count_s, dead_s, rows_s = census_count(dict(ns), [sentinel])
    print(f"scenario=sentinel_path_row dead_entry_count={count_s} census_rows={len(rows_s)}")

    guard = "if passed is None:" in src and "expected_errors = ()" in src
    print(f"static=dict_applied_only_when_passed_is_none {guard} "
          f"lines={src.count('if passed is None:')}")

    gate_expr = ('all(not e["dead_in_run"] for r in census_rows '
                 'if r["case"].startswith(("export_prod_", "r101_")) '
                 'for e in r["entries"])')
    for label, rows_sel in (("healthy", rows_ok), ("dead", rows)):
        print(f"gate_on_{label}={eval(gate_expr, {'census_rows': rows_sel})}")


if __name__ == "__main__":
    main()
