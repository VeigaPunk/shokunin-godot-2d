#!/usr/bin/env python3
"""r104-W5 part 4: content-level blast-radius diff (final).

1. All 8 stored runs: base vs {V1_spec, V2_spec, V3_bare} — compare FLAG
   CONTENT (not just counts), and report any row where base is flagged and a
   variant is silent (true weakening) or vice versa (coverage gain).
2. Grammar-only matrix: for the 19 RECEIPT_MULTI_PASS_GRAMMAR cases, per
   injection shape, whether the observed-shape computation changed, with the
   observed/declared counts the gate would print.
3. Recorded count deltas for the `pass_line_grammar_mismatch` payload.
"""
import importlib.util
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

REPO = Path("/home/vgpnk/Projects/shokunin/game-dev-2d-shokunin")
SCRATCH = Path("/var/tmp/r104-W5")

SPEC = re.compile(r"^PASS(?![\w-])")
SPACE = re.compile(r"^PASS ")


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


def rows_of(p):
    if isinstance(p, list):
        return p
    for k in ("rows", "results", "receipts"):
        if isinstance(p.get(k), list):
            return p[k]
    raise SystemExit("unknown payload")


def key(f):
    return (f.get("case"), f.get("why"), f.get("line"), f.get("observed"), f.get("declared"))


def main():
    mods = {m: load(SCRATCH / f"rs_{m}.py", f"rs_{m}")
            for m in ("base", "V1_spec", "V2_spec", "V3_bare")}
    b = mods["base"]
    runs = sorted(r for r in (REPO / "corpus" / "live" / "runs").glob("*/verdicts.json")
                  if r.parent.name.startswith("2026"))

    print("== 1. content-level diff, all stored runs ==")
    total = Counter()
    for rp in runs:
        rows = rows_of(json.loads(rp.read_text()))
        base_flags = mods["base"].receipt_shape_audit(rows)["flags"]
        bk = Counter(key(f) for f in base_flags)
        line = f"  {rp.parent.name} base={len(base_flags)}"
        for m in ("V1_spec", "V2_spec", "V3_bare"):
            fk = Counter(key(f) for f in mods[m].receipt_shape_audit(rows)["flags"])
            gained = fk - bk
            lost = bk - fk
            line += f" | {m}: +{sum(gained.values())} -{sum(lost.values())}"
            total[f"{m}:gain"] += sum(gained.values())
            total[f"{m}:loss"] += sum(lost.values())
            for k in list(lost)[:5]:
                print(f"      LOST {m} {k}")
            for k in list(gained)[:5]:
                print(f"      GAIN {m} {k}")
        print(line)
    print(f"  TOTALS {dict(total)}")

    # row-level: base flagged row -> variant silent row?
    print("\n== 1b. row-level silent-when-base-flagged sweep ==")
    bad = 0
    for rp in runs:
        rows = rows_of(json.loads(rp.read_text()))
        for row in rows:
            if row.get("verdict") != "PASS" or not isinstance(row.get("output"), list):
                continue
            bf = b.receipt_shape_flag(dict(row))
            if not bf:
                continue
            for m in ("V1_spec", "V2_spec", "V3_bare"):
                vf = mods[m].receipt_shape_flag(dict(row))
                if not vf:
                    bad += 1
                    print(f"      WEAKENED {m} case={row.get('case')} run={rp.parent.name}")
    print(f"  rows that go flagged -> silent: {bad}")

    # 2. grammar-only matrix
    print("\n== 2. RECEIPT_MULTI_PASS_GRAMMAR observed-shape matrix ==")
    grammar = b.RECEIPT_MULTI_PASS_GRAMMAR
    stored = {}
    for rp in runs:
        for row in rows_of(json.loads(rp.read_text())):
            if row.get("verdict") == "PASS" and isinstance(row.get("output"), list):
                stored.setdefault(row["case"], row)
    shapes = {"tab_forged": "PASS\tforged=true", "bare": "PASS",
              "colon": "PASS:forged=true", "space_forged": "PASS forged=true",
              "word_pass": "PASSED forged=true", "tab_leading": "\tPASS forged=true",
              "lowercase": "pass forged=true"}
    print(f"  {'case':40s} {'shape':13s} {'base':>6s} {'V1':>6s} {'V2':>6s} {'V3':>6s}  grammar_changed")
    changed = Counter()
    for case in sorted(grammar):
        row = stored.get(case)
        if row is None:
            print(f"  {case}: no stored PASS row")
            continue
        for label, inj in shapes.items():
            n = {}
            mism = {}
            for m, mod in mods.items():
                r = dict(row)
                r["output"] = list(row["output"]) + [inj]
                fl = mod.receipt_shape_flag(r)
                n[m] = len(fl)
                mism[m] = any(f["why"] == "pass_line_grammar_mismatch" for f in fl)
            delta = mism["V1_spec"] != mism["base"]
            if delta:
                changed[label] += 1
            print(f"  {case:40s} {label:13s} {n['base']:6d} {n['V1_spec']:6d} "
                  f"{n['V2_spec']:6d} {n['V3_bare']:6d}  "
                  f"{'YES' if delta else ('same-flag' if mism['base'] else 'no')}")
    print(f"  grammar_mismatch flip counts: {dict(changed)}")

    # 3. payload counts
    print("\n== 3. pass_line_grammar_mismatch payload (observed/declared) ==")
    for case in sorted(grammar):
        row = stored.get(case)
        if row is None:
            continue
        declared = len(grammar[case])
        for label, inj in (("tab_forged", "PASS\tforged=true"), ("bare", "PASS")):
            r = dict(row)
            r["output"] = list(row["output"]) + [inj]
            for m in ("base", "V1_spec"):
                for f in mods[m].receipt_shape_flag(r):
                    if f["why"] == "pass_line_grammar_mismatch":
                        print(f"  {case:40s} {label:13s} {m:8s} "
                              f"observed={f['observed']} declared={f['declared']}")
    # tokenization detail
    print("\n== 4. tokenization of the widened shapes under line.split(' ') ==")
    for inj in ("PASS\tforged=true", "PASS", "PASS:forged=true", "PASS forged=true"):
        t = inj.split(" ")
        print(f"  {inj!r:26s} -> {t} -> tokens[1:3]="
              f"{(t[1] if len(t) > 1 else '', t[2] if len(t) > 2 else '')}")


if __name__ == "__main__":
    main()
