#!/usr/bin/env python3
"""r103 V11 — FLOOR-GATE PLAN for the `export_div_` family (seat V11).

Composes the C1 chain from the ACTUAL repo patch files and proves every floor-gate
claim by measurement:

  live run_battery.py
    + mutations/w5_export_div_v2.patch          (gates + cases_integrity prefix)
    + mutations/r103-V11-export_div_floor_amend.patch   (freeze N=2 + name floor)
    + mutations/r103-V11-export_div_rows.patch  (the 2 frozen CASES rows)

Findings proved here (see reports/round-103/r103-ver11.md):
  * `--min-rows N` as implemented in w5_export_div_gate_splice.py DROPS the
    `== sum(... CASES ...)` equality conjunct, silently trading one gate for
    another; the amend keeps equality AND the frozen floor.
  * the count floor alone cannot see a same-count rename; the row-NAME floor
    (new) closes it, superset-safe and fail-closed.
  * gate-only splice (rows absent) reds the battery -> the chain is atomic:
    rows + gates must land in one splice.

Hard rules: run_battery.py is NEVER executed (read + ast.parse only); nothing
outside /var/tmp/r103c-V11/ is written except the two V11 patch files under
reports/round-103/mutations/ (this seat's assigned files).
"""
import ast
import difflib
import hashlib
import json
import pathlib
import sys

REPO = pathlib.Path("/home/vgpnk/Projects/shokunin/game-dev-2d-shokunin")
LIVE = REPO / "corpus/fixtures/run_battery.py"
MUT = REPO / "reports/round-103/mutations"
PINNED_SHA = "40440356f0bf04481f518adc332d1ebb7ba79213878a9f3836421a512828a5c4"
RECEIPT = REPO / "corpus/live/runs/20261018T213443471189Z/verdicts.json"
BASE_PATCH = MUT / "w5_export_div_v2.patch"
AMEND_PATCH = MUT / "r103-V11-export_div_floor_amend.patch"
ROWS_PATCH = MUT / "r103-V11-export_div_rows.patch"
SCRATCH = pathlib.Path("/var/tmp/r103c-V11")
OUT = SCRATCH / "floorselftest.json"

COUNT_KEY = "r103_export_div_count_floor"
GATE_KEY = "r103_expected_errors_all_matched"
NAME_KEY = "r103_export_div_row_names"
FROZEN_ROWS = ("export_div_s02_user_iso", "export_div_s02_xdg_override")
MIN_ROWS = 2  # frozen floor: one row per landed s02 arm (iso, xdg)

COUNT_OLD = "            >= 1),"
COUNT_NEW = f"            >= {MIN_ROWS}),"

COMMENT_OLD = (
    "        # the trailing floor fires a full-family drop (0==0 but !>=1) and,\n"
    "        # once frozen to the exact registered count via --min-rows N, a\n"
    "        # synchronized partial drop below N. A synchronized drop that\n"
    "        # keeps >= N rows with CASES+results shrunk together is invisible\n"
    "        # by construction; freezing N to the exact count closes it.\n")
COMMENT_NEW = (
    "        # the trailing floor is FROZEN (r103 V11) to the registered family\n"
    "        # count N=2 - one row per landed s02 arm - so a full-family drop\n"
    "        # (0==0 but !>=2), a partial drop (1 of 2), and a synchronized\n"
    "        # CASES+results shrink below N all fire. Superset-safe: adding a\n"
    "        # row later never re-reds a landed round; re-freeze N in the same\n"
    "        # splice that lands any new export_div_ row.\n")

NAME_TUPLE = '",\n                         "'.join(FROZEN_ROWS)
NAME_CLAUSE = (
    '        # r103 V11 (floor-gate plan): the count floor above cannot see a\n'
    '        # CASES+results co-shrink that keeps the count at or above the\n'
    '        # floor with a swapped name (a copy-pasted sibling row name, a\n'
    '        # mistyped suffix) - 2 == 2 >= 2 stays green. This gate pins the\n'
    '        # frozen ROW-NAME set from the C1 row tuples: every frozen name\n'
    '        # must be registered in CASES and must have run. Superset-safe by\n'
    '        # construction (new rows added later never re-red a landed\n'
    '        # round); fail-closed on an empty family (all() over one frozen\n'
    '        # name is False, never a vacuous True).\n'
    f'        "{NAME_KEY}": all(\n'
    '            name in {c[0] for c in CASES}\n'
    '            and any(r["case"] == name for r in results)\n'
    '            for name in ("' + NAME_TUPLE + '")),\n')

ROW_ANCHOR = "     'PASS export_launch hole rc=124 class=project_data_missing pck_hint=true stdout_bytes=0'),\n"
ROW_BLOCK = (
    "    # r103 — C1: export_div_ family (see reports/round-103/r103-E0-spec.md,\n"
    "    # r103-ver11.md). Order is load-bearing: arm=xdg reuses arm=iso's exported\n"
    "    # binary and reads back arm=iso's xdgA store (adjacent-row pattern, cf. r102\n"
    "    # export_launch neg). Both pins stop before the `proj=` host path AND before\n"
    "    # xdg_a_store= (measured standalone: `[<missing>]`), so the rows are run-dir /\n"
    "    # row-order independent substrings of the merged output.\n"
    "    ('export_div_s02_user_iso', 'export_div_s02.gd', [\"--arm=iso\"], 0,\n"
    "     'PASS export_div s02 arm=iso r1_read=none r1_exit=0 r2_read=run1 r2_exit=0 store=[run1,run2] store_under_xdg=true userdir_under_xdg=true home_store_absent=true'),\n"
    "    ('export_div_s02_xdg_override', 'export_div_s02.gd', [\"--arm=xdg\"], 0,\n"
    "     'PASS export_div s02 arm=xdg r3_read=none r3_exit=0 store_b=[run3] store_b_under_xdg=true r3_userdir_under_xdg=true r4_read=none r4_exit=0 store_c=[run4] r4_userdir_under_home=true'),\n")

log = []


def rec(cell, ok, detail):
    log.append({"cell": cell, "ok": bool(ok), "detail": detail})
    print(f"{'PASS' if ok else 'FAIL'} {cell}: {detail}")
    return bool(ok)


def parse_hunks(patch_text):
    """[(old_start_1based, body_lines)] — body keeps the ' '/'+'/'-' prefixes."""
    hunks, cur, start = [], None, None
    for l in patch_text.splitlines():
        if l.startswith(("---", "+++")):
            continue
        if l.startswith("@@"):
            if cur is not None:
                hunks.append((start, cur))
            start = int(l.split(" ")[1].split(",")[0].lstrip("-"))
            cur = []
            continue
        if cur is not None:
            cur.append(l)
    if cur is not None:
        hunks.append((start, cur))
    return hunks


def apply_unified(src, patch_text):
    """Exact-context unified-diff applier (bounded offset search), enough here."""
    lines = src.splitlines(keepends=True)
    offset = 0
    for old_start, body in parse_hunks(patch_text):
        first_ctx = next((l[1:] for l in body if l.startswith(" ")), "")
        target = old_start - 1 + offset
        if not (0 <= target < len(lines)
                and lines[target].rstrip("\n") == first_ctx.rstrip("\n")):
            lo, hi = max(0, target - 200), min(len(lines), target + 200)
            found = [i for i in range(lo, hi)
                     if lines[i].rstrip("\n") == first_ctx.rstrip("\n")]
            assert found, f"anchor not found near old_start={old_start}"
            target = min(found, key=lambda i: abs(i - target))
        out, i = lines[:target], target
        for l in body:
            if l.startswith("+"):
                out.append(l[1:] + "\n")
                offset += 1
            elif l.startswith(" "):
                assert lines[i].rstrip("\n") == l[1:].rstrip("\n"), f"ctx @{i}"
                out.append(lines[i])
                i += 1
            elif l.startswith("-"):
                assert lines[i].rstrip("\n") == l[1:].rstrip("\n"), f"del @{i}"
                i += 1
                offset -= 1
        out.extend(lines[i:])
        lines = out
    return "".join(lines)


def amend(src):
    """Freeze the count floor to N and append the row-name floor."""
    assert src.count(COUNT_OLD) == 1 and src.count(COMMENT_OLD) == 1, "amend anchors"
    out = src.replace(COMMENT_OLD, COMMENT_NEW, 1)
    out = out.replace(COUNT_OLD, COUNT_NEW + "\n" + NAME_CLAUSE.rstrip("\n"), 1)
    return out


def add_rows(src):
    assert src.count(ROW_ANCHOR) == 1, "row anchor"
    return src.replace(ROW_ANCHOR, ROW_ANCHOR + ROW_BLOCK, 1)


def make_patch(before, after):
    return "".join(difflib.unified_diff(
        before.splitlines(keepends=True), after.splitlines(keepends=True),
        fromfile="a/corpus/fixtures/run_battery.py",
        tofile="b/corpus/fixtures/run_battery.py"))


def sf_expressions(src, keys):
    out = {}
    for node in ast.walk(ast.parse(src)):
        if isinstance(node, ast.Assign) and any(
                getattr(t, "id", None) == "sf_discriminations" for t in node.targets):
            for k, v in zip(node.value.keys, node.value.values):
                if isinstance(k, ast.Constant) and k.value in keys:
                    out[k.value] = compile(ast.Expression(v), "<sf>", "eval")
    return out


def extract_cases(src):
    for node in ast.parse(src).body:
        if isinstance(node, ast.Assign) and getattr(node.targets[0], "id", "") == "CASES":
            return ast.literal_eval(node.value)
    return []


def clause_text(src, key):
    lines = src.splitlines()
    i = next(n for n, l in enumerate(lines) if f'"{key}":' in l)
    depth, out = 0, []
    for l in lines[i:]:
        out.append(l)
        depth += l.count("(") - l.count(")")
        if depth == 0 and len(out) > 1:
            break
    return "\n".join(out)


def ev(expr, **ns):
    g = {"__builtins__": __builtins__}
    g.update(ns)
    return eval(expr, g)


def main(write_patches=False):
    ok = True
    live_src = LIVE.read_text()
    actual = hashlib.sha256(live_src.encode()).hexdigest()
    ok &= rec("A live run_battery.py sha == pinned", actual == PINNED_SHA,
              f"sha256={actual[:16]}…")

    base = apply_unified(live_src, BASE_PATCH.read_text())
    amended = amend(base)
    composed = add_rows(amended)
    for tag, src in (("basev2", base), ("amended", amended), ("composed", composed)):
        p = SCRATCH / f"floor_{tag}.py"
        p.write_text(src)
        try:
            compile(src, str(p), "exec")
        except SyntaxError as e:
            ok &= rec(f"B {tag} compiles", False, str(e))
            return 1
    ok &= rec("B chain basev2 -> amended -> composed all compile", True,
              "from the repo patch files, ast.parse + compile")

    if write_patches:
        AMEND_PATCH.write_text(make_patch(base, amended))
        ROWS_PATCH.write_text(make_patch(amended, composed))
        print(f"wrote {AMEND_PATCH.name} + {ROWS_PATCH.name}")
        return 0

    ok &= rec("C shipped amend patch reproduces the in-memory amend",
              make_patch(base, amended) == AMEND_PATCH.read_text()
              and apply_unified(base, AMEND_PATCH.read_text()) == amended,
              f"{AMEND_PATCH.name} sha={hashlib.sha256(AMEND_PATCH.read_bytes()).hexdigest()[:16]}…")
    ok &= rec("D shipped rows patch applies to the amended base",
              apply_unified(amended, ROWS_PATCH.read_text()) == composed,
              f"{ROWS_PATCH.name} sha={hashlib.sha256(ROWS_PATCH.read_bytes()).hexdigest()[:16]}…")

    v1 = REPO / "reports/round-103/mutations/w5_export_div_gate_splice.py"
    v1_src = v1.read_text()
    ok &= rec("E v1 tool --min-rows N drops the CASES equality conjunct (defect)",
              "count_lines = f'            >= {min_rows}),'" in v1_src
              and "CASES" not in v1_src.split("count_lines = f")[1][:60],
              "v1 line: count_lines = f'            >= {min_rows}),' replaces the "
              "results==CASES line; the amend keeps both conjuncts")

    exprs = sf_expressions(composed, (COUNT_KEY, NAME_KEY, GATE_KEY, "cases_integrity"))
    ok &= rec("F AST-extracted gates from the composed file",
              set(exprs) == {COUNT_KEY, NAME_KEY, GATE_KEY, "cases_integrity"},
              f"keys={sorted(exprs)}")
    a_count = clause_text(composed, COUNT_KEY)
    ok &= rec("G frozen count clause = equality AND >= 2",
              "== sum(1 for c in CASES" in a_count and a_count.rstrip().endswith(">= 2),"),
              f"clause tail={a_count.splitlines()[-1].strip()!r}")

    live_results = json.loads(RECEIPT.read_text())["results"]
    live_cases = extract_cases(live_src)
    fam_r = [r for r in live_results if str(r["case"]).startswith("export_div_")]
    fam_c = [c for c in live_cases if str(c[0]).startswith("export_div_")]
    ok &= rec("H receipt replay baseline (r102 receipt, 554 rows; 0 family rows)",
              len(live_cases) == 536 and len(live_results) == 554
              and not fam_c and not fam_r,
              f"CASES={len(live_cases)} receipt={len(live_results)} source="
              f"{RECEIPT.parent.name}/verdicts.json")

    cases = extract_cases(composed)
    fam = [str(c[0]) for c in cases if str(c[0]).startswith("export_div_")]
    ok &= rec("I composed CASES gains exactly the 2 frozen rows in order",
              fam == list(FROZEN_ROWS) and len(cases) == len(live_cases) + 2,
              f"family={fam} CASES {len(live_cases)}->{len(cases)}")

    R1, R2 = FROZEN_ROWS
    two = [{"case": R1}, {"case": R2}]
    one = [{"case": R1}]
    C2, C1 = [(R1,), (R2,)], [(R1,)]
    floor, namefloor = exprs[COUNT_KEY], exprs[NAME_KEY]
    syn = live_results + two
    cells = {
        "J floor: 2/2 registered+ran -> True": ev(floor, results=two, CASES=C2) is True,
        "K floor: 1/2 partial drop -> False": ev(floor, results=one, CASES=C2) is False,
        "L floor: equality - 3 ran of 2 registered -> False":
            ev(floor, results=two + [{"case": R1}], CASES=C2) is False,
        "M floor: equality - 2 registered, 1 ran -> False":
            ev(floor, results=one, CASES=C2) is False,
        "N floor: 0/0 family gone -> False": ev(floor, results=[], CASES=[]) is False,
        "O floor: gate-only (rows unlanded) vs real receipt -> False (atomicity)":
            ev(floor, results=live_results, CASES=live_cases) is False,
        "P name floor: frozen names registered+ran -> True":
            ev(namefloor, results=two, CASES=C2) is True,
        "Q name floor: same-count RENAME -> False (closes the count hole)":
            ev(namefloor, results=[{"case": R1 + "X"}, {"case": R2}],
               CASES=[(R1 + "X",), (R2,)]) is False,
        "R name floor: one row dropped from CASES+results -> False":
            ev(namefloor, results=one, CASES=C1) is False,
        "S name floor: superset (3 rows) -> True":
            ev(namefloor, results=two + [{"case": "export_div_s03_extra"}],
               CASES=C2 + [("export_div_s03_extra",)]) is True,
        "T name floor: empty family -> False (never vacuous)":
            ev(namefloor, results=[], CASES=[]) is False,
        "U name floor: registered but never ran -> False":
            ev(namefloor, results=one, CASES=C2) is False,
        "V dead-entry gate: vacuous True over the empty family census (by design)":
            ev(exprs[GATE_KEY], census_rows=[]) is True,
        "W composed gates ALL green over receipt+2 family rows":
            ev(floor, results=syn, CASES=cases) is True
            and ev(namefloor, results=syn, CASES=cases) is True
            and ev(exprs["cases_integrity"], results=syn, CASES=cases) is True,
    }
    for k, v in cells.items():
        ok &= rec(k, v, "eval on AST-extracted composed expressions")

    sig = {str(c[0]): c[4] for c in cases if str(c[0]).startswith("export_div_")}
    caps = {k: (SCRATCH / v).read_text() for k, v in (
        ("battery_iso", "stdout_iso.txt"),
        ("battery_xdg", "stdout_xdg.txt"),
        ("standalone_xdg", "standalone/stdout_xdg.txt"))}
    ok &= rec("X both pins are substrings of the real captures (battery + standalone)",
              sig[R1] in caps["battery_iso"] and sig[R2] in caps["battery_xdg"]
              and sig[R2] in caps["standalone_xdg"],
              f"iso pin {len(sig[R1])} B, xdg pin {len(sig[R2])} B")
    battery_xdg_line = next(l for l in caps["battery_xdg"].splitlines()
                            if l.startswith("PASS export_div s02 arm=xdg"))
    ok &= rec("Y untruncated xdg pin would MISS the standalone capture (why truncated)",
              battery_xdg_line not in caps["standalone_xdg"]
              and "xdg_a_store=[run1,run2]" in battery_xdg_line,
              "full line carries xdg_a_store=[run1,run2]; standalone shows [<missing>]")
    errs = {k: (v.count("ERROR:"), v.count("SCRIPT ERROR"), len(v))
            for k, v in caps.items()}
    ok &= rec("Z family captures are ERROR-clean (no expected_errors entries needed)",
              all(e[0] == 0 and e[1] == 0 for e in errs.values()),
              "; ".join(f"{k}: ERROR={e[0]} SCRIPT={e[1]} bytes={e[2]}"
                        for k, e in errs.items()))

    OUT.write_text(json.dumps({
        "seat": "V11", "frozen_min_rows": MIN_ROWS, "frozen_rows": list(FROZEN_ROWS),
        "live_sha256": actual, "live_cases_rows": len(live_cases),
        "composed_cases_rows": len(cases),
        "receipt": str(RECEIPT), "receipt_rows": len(live_results),
        "base_patch": str(BASE_PATCH), "amend_patch": str(AMEND_PATCH),
        "rows_patch": str(ROWS_PATCH), "pins": sig, "cells": log,
        "all_pass": bool(ok)}, indent=2))
    print(f"\n{'ALL CELLS PASS' if ok else 'SOME CELLS FAILED'} — "
          f"{sum(1 for c in log if c['ok'])}/{len(log)}; evidence {OUT}")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main(write_patches="--write-patches" in sys.argv))
