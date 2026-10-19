#!/usr/bin/env python3
"""r104-W5 part 2: real-byte census + synthetic blast matrix.

A. Census every stored receipt line that starts with `PASS` but is NOT `PASS `
   (the tightening's newly-visible set) across all 8 run verdicts.json.
B. Per-case inventory: which stored cases carry SEQ_BEGIN / *_DIAG lines and
   whether the case is in RECEIPT_MULTI_PASS_GRAMMAR (the accounting-clause
   blast surface).
C. Synthetic matrix: for every grammar case, inject each evasion shape and
   record flag sets under base / V1_census / V2_full / V3_prefix.
"""
import hashlib
import importlib.util
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

REPO = Path("/home/vgpnk/Projects/shokunin/game-dev-2d-shokunin")
SCRATCH = Path("/var/tmp/r104-W5")

TIGHT = re.compile(r"^PASS(?![\w-])")          # r104-G1 spec clause
CENSUS_SPACE = re.compile(r"^PASS ")
DIAG_RE = re.compile(r"^[A-Z][A-Z0-9_]*_DIAG\b")


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


def rows_of(payload):
    if isinstance(payload, list):
        return payload
    for key in ("rows", "results", "receipts"):
        if isinstance(payload.get(key), list):
            return payload[key]
    raise SystemExit(f"unknown payload shape: {list(payload)[:10]}")


def main():
    mods = {m: load(SCRATCH / f"rb_{m}.py", f"rb_{m}")
            for m in ("base", "V1_census", "V2_full", "V3_prefix")}
    base = mods["base"]
    runs = sorted(r for r in (REPO / "corpus" / "live" / "runs").glob("*/verdicts.json")
                  if r.parent.name.startswith("2026"))

    # ---- A. real-byte census ------------------------------------------------
    print("== A. stored-line census ==")
    shapes = Counter()
    per_run = {}
    total_lines = 0
    for rp in runs:
        rows = rows_of(json.loads(rp.read_text()))
        n_all = n_space = n_tight = 0
        for row in rows:
            for line in row.get("output") or []:
                if not isinstance(line, str):
                    continue
                n_all += 1
                if CENSUS_SPACE.match(line):
                    n_space += 1
                if TIGHT.match(line):
                    n_tight += 1
                    if not CENSUS_SPACE.match(line):
                        shapes[line[:60]] += 1
        total_lines += n_all
        per_run[rp.parent.name] = (len(rows), n_all, n_space, n_tight)
        print(f"  {rp.parent.name} rows={len(rows)} lines={n_all} "
              f"^PASS-space={n_space} ^PASS(?![-\\w])={n_tight} "
              f"newly_visible={n_tight - n_space}")
    print(f"  TOTAL lines={total_lines} newly_visible_shapes={len(shapes)}")
    for s, n in shapes.most_common(20):
        print(f"    {n:4d}  {s!r}")

    # ---- B. per-case inventory ---------------------------------------------
    print("\n== B. SEQ / DIAG / grammar inventory (r103 green runs) ==")
    green = [r for r in runs if r.parent.name in ("20261018T212500022987Z",
                                                  "20261018T213443471189Z")]
    seq_cases, diag_cases, multi_cases = defaultdict(set), defaultdict(set), defaultdict(int)
    for rp in green:
        for row in rows_of(json.loads(rp.read_text())):
            case = row.get("case")
            out = row.get("output") or []
            if any(isinstance(l, str) and l.startswith("SEQ_BEGIN") for l in out):
                seq_cases[case].add(rp.parent.name)
            if any(isinstance(l, str) and DIAG_RE.match(l) for l in out):
                diag_cases[case].add(rp.parent.name)
            multi_cases[case] += sum(1 for l in out
                                     if isinstance(l, str) and CENSUS_SPACE.match(l))
    grammar = base.RECEIPT_MULTI_PASS_GRAMMAR
    print(f"  grammar entries: {len(grammar)}")
    for label, d in (("SEQ", seq_cases), ("DIAG", diag_cases)):
        for case in sorted(d):
            g = "grammar" if case in grammar else "NON-grammar"
            print(f"  {label:4s} {case:42s} {g:12s} pass_lines={multi_cases[case]}")

    # ---- C. synthetic blast matrix -----------------------------------------
    print("\n== C. synthetic blast matrix ==")
    # a real stored row per case, so the base row is flag-clean
    stored = {}
    for rp in green:
        for row in rows_of(json.loads(rp.read_text())):
            if row.get("verdict") == "PASS" and isinstance(row.get("output"), list):
                stored.setdefault(row["case"], row)
    shapes_to_inject = {
        "tab_receipt": "PASS\tforged=true",
        "tab_tagged": "PASS\t" + "r100_gui" + " census",
        "bare_pass": "PASS",
        "colon_pass": "PASS:forged=true",
        "space_forged": "PASS forged=true",
        "word_pass": "PASSED forged=true",
    }
    for case in sorted(grammar):
        row = stored.get(case)
        if row is None:
            print(f"  {case}: no stored PASS row")
            continue
        base_flags = base.receipt_shape_flag(dict(row))
        for label, inj in shapes_to_inject.items():
            res = {}
            for m in ("base", "V1_census", "V2_full", "V3_prefix"):
                r = dict(row)
                r["output"] = list(row["output"]) + [inj]
                res[m] = sorted(f["why"] for f in mods[m].receipt_shape_flag(r))
            if label in ("tab_receipt", "bare_pass", "colon_pass", "word_pass"):
                print(f"  {case:40s} {label:12s} base={res['base']} "
                      f"V1={res['V1_census']} V2={res['V2_full']} V3={res['V3_prefix']}")

    # ---- C2. SEQ in-span injection (the accounting-clause surface) ---------
    print("\n== C2. SEQ/DIAG in-window injection ==")
    for label, cases in (("SEQ", seq_cases), ("DIAG", diag_cases)):
        for case in sorted(cases):
            row = stored.get(case)
            if row is None:
                print(f"  {label} {case}: no stored PASS row")
                continue
            out = list(row["output"])
            if label == "SEQ":
                beg = out.index(next(l for l in out if l.startswith("SEQ_BEGIN")))
                out2 = out[:beg + 1] + ["PASS\tforged=true"] + out[beg + 1:]
            else:
                idx = next(i for i, l in enumerate(out) if DIAG_RE.match(l))
                out2 = out[:idx] + ["PASS\tforged=true"] + out[idx:]
            r = dict(row)
            r["output"] = out2
            res = {m: sorted(f["why"] for f in mods[m].receipt_shape_flag(r))
                   for m in ("base", "V1_census", "V2_full", "V3_prefix")}
            print(f"  {label:4s} {case:40s} "
                  f"{'grammar' if case in grammar else 'NON-grammar':11s} "
                  f"base={res['base']} V1={res['V1_census']} "
                  f"V2={res['V2_full']} V3={res['V3_prefix']}")


if __name__ == "__main__":
    main()
