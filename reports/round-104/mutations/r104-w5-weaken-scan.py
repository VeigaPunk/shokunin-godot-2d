#!/usr/bin/env python3
"""r104-W5 part 3: spec-regex variants + full-corpus weakening scan.

Uses the r104-G1 spec clause `^PASS(?![\\w-])` (catches tab, bare, colon, but
not PASSED/PASS-x) as the tightened predicate.

Variants:
  base     HEAD
  V1_spec  census widened to the spec predicate ONLY
  V2_spec  census + the three SEQ/DIAG accounting predicates widened
  V3_bare  census widened to bare startswith("PASS") (no separator guard)

Scans EVERY stored PASS row (not just grammar cases) x injection shapes and
reports: new flags (coverage gain) and WEAKENING (base-flagged -> variant-silent).
"""
import importlib.util
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

REPO = Path("/home/vgpnk/Projects/shokunin/game-dev-2d-shokunin")
SCRATCH = Path("/var/tmp/r104-W5")

SPEC_PRED = 'RECEIPT_PASS_RE = re.compile(r"^PASS(?![\\w-])")\n'
ANSI_ANCHOR = 'RECEIPT_ANSI_ONLY_RE = re.compile(r"^(?:\\x1b\\[[0-9;]*m)+$")\n'
RE_CENSUS = '    pass_lines = [line for line in output if line.startswith("PASS ")]\n'
RE_SEQ_IN = '                if not (line.startswith("PASS ") or RECEIPT_SEQ_RE.match(line)):\n'
RE_SEQ_POST = '                if (line.startswith("PASS ") or RECEIPT_SEQ_RE.match(line)\n'
RE_DIAG = '            if (line.startswith("PASS ") or RECEIPT_BANNER_RE.match(line)\n'


def build(text, mode):
    if mode == "base":
        return text
    text = text.replace(ANSI_ANCHOR, ANSI_ANCHOR + SPEC_PRED, 1)
    new_census = ('    pass_lines = [line for line in output if line.startswith("PASS")]\n'
                  if mode == "V3_bare"
                  else '    pass_lines = [line for line in output if RECEIPT_PASS_RE.match(line)]\n')
    text = text.replace(RE_CENSUS, new_census, 1)
    if mode == "V2_spec":
        text = text.replace(RE_SEQ_IN,
                            '                if not (RECEIPT_PASS_RE.match(line) or RECEIPT_SEQ_RE.match(line)):\n', 1)
        text = text.replace(RE_SEQ_POST,
                            '                if (RECEIPT_PASS_RE.match(line) or RECEIPT_SEQ_RE.match(line)\n', 1)
        text = text.replace(RE_DIAG,
                            '            if (RECEIPT_PASS_RE.match(line) or RECEIPT_BANNER_RE.match(line)\n', 1)
    return text


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


def main():
    base_text = (REPO / "corpus" / "fixtures" / "run_battery.py").read_text()
    mods = {}
    for m in ("base", "V1_spec", "V2_spec", "V3_bare"):
        p = SCRATCH / f"rs_{m}.py"
        p.write_text(build(base_text, m))
        mods[m] = load(p, f"rs_{m}")
    b = mods["base"]
    print("spec predicate:", SPEC_PRED.strip())

    runs = sorted(r for r in (REPO / "corpus" / "live" / "runs").glob("*/verdicts.json")
                  if r.parent.name.startswith("2026"))

    # corpus-level flag comparison, all rows
    print("\n== corpus-level (all rows, no injection) ==")
    for rp in runs:
        rows = rows_of(json.loads(rp.read_text()))
        out = {}
        for m, mod in mods.items():
            out[m] = mod.receipt_shape_audit(rows)
        print(f"  {rp.parent.name} rows={len(rows)} audited={out['base']['audited']} " +
              " ".join(f"{m}={len(out[m]['flags'])}" for m in mods))

    # per-row injection scan
    print("\n== per-row injection scan (all stored PASS rows) ==")
    stored = {}
    for rp in runs:
        for row in rows_of(json.loads(rp.read_text())):
            if row.get("verdict") == "PASS" and isinstance(row.get("output"), list):
                stored.setdefault(row["case"], (row, rp.parent.name))
    print(f"  distinct stored PASS cases: {len(stored)}")

    INJ = {
        "tab_forged": "PASS\tforged=true",
        "bare": "PASS",
        "colon": "PASS:forged=true",
        "space_forged": "PASS forged=true",
        "word_pass": "PASSED forged=true",
        "tab_anchored": None,   # filled per-row: "PASS\t" + anchor text
    }
    gain = Counter()
    weaken = Counter()
    weaken_examples = defaultdict(list)
    flagged_by_variant = defaultdict(Counter)
    for case, (row, runname) in sorted(stored.items()):
        pin = b.CASES_SIG_BY_CASE.get(case)
        anchors = [s.split("\n")[0].strip() for s in ([pin] if isinstance(pin, str) else (pin or []))]
        shapes = dict(INJ)
        shapes["tab_anchored"] = "PASS\t" + (anchors[0] if anchors else "x")
        for pos in ("end", "start", "mid"):
            for label, inj in shapes.items():
                r0 = dict(row)
                out = list(row["output"])
                if pos == "end":
                    out = out + [inj]
                elif pos == "start":
                    out = [inj] + out
                else:
                    out = out[:len(out) // 2] + [inj] + out[len(out) // 2:]
                r0["output"] = out
                res = {m: frozenset(f["why"] for f in mods[m].receipt_shape_flag(r0))
                       for m in mods}
                for m in ("V1_spec", "V2_spec", "V3_bare"):
                    if res[m] - res["base"]:
                        gain[(m, label, pos)] += 1
                    if res["base"] - res[m]:
                        weaken[(m, label, pos)] += 1
                        if len(weaken_examples[(m, label, pos)]) < 3:
                            weaken_examples[(m, label, pos)].append(
                                (case, runname, sorted(res["base"]), sorted(res[m])))
                if not res["base"]:
                    flagged_by_variant["base"][label] += 1
                for m in ("V1_spec", "V2_spec", "V3_bare"):
                    if res[m]:
                        flagged_by_variant[m][label] += 1

    print("\n  -- WEAKENING (base flagged, variant silent) --")
    if not weaken:
        print("     none")
    for k in sorted(weaken):
        print(f"     {k[0]:8s} {k[1]:14s} pos={k[2]:6s} n={weaken[k]}")
        for ex in weaken_examples[k]:
            print(f"        case={ex[0]} run={ex[1]} base={ex[2]} var={ex[3]}")
    print("\n  -- GAIN (variant flags what base missed), top 20 --")
    for k, n in gain.most_common(20):
        print(f"     {k[0]:8s} {k[1]:14s} pos={k[2]:6s} n={n}")
    print("\n  -- escape count (no variant flags), by shape --")
    for label in INJ:
        row = " ".join(f"{m}={flagged_by_variant[m][label]}" for m in
                       ("base", "V1_spec", "V2_spec", "V3_bare"))
        print(f"     {label:14s} {row}")

    # non-grammar DIAG rows: the V2 accounting hole
    print("\n== V2 accounting hole probe (non-grammar DIAG rows) ==")
    DIAG_RE = re.compile(r"^[A-Z][A-Z0-9_]*_DIAG\b")
    ng_diag = [(c, v) for c, v in stored.items()
               if c not in b.RECEIPT_MULTI_PASS_GRAMMAR
               and any(DIAG_RE.match(l) for l in v[0]["output"])]
    print(f"  non-grammar DIAG cases: {[c for c, _ in ng_diag]}")
    for case, (row, _r) in ng_diag:
        pin = b.CASES_SIG_BY_CASE.get(case)
        anchors = [s.split("\n")[0].strip() for s in ([pin] if isinstance(pin, str) else (pin or []))]
        inj = "PASS\t" + (anchors[0] if anchors else "x")
        r0 = dict(row)
        r0["output"] = list(row["output"]) + [inj]
        res = {m: sorted(f["why"] for f in mods[m].receipt_shape_flag(r0)) for m in mods}
        print(f"  {case:36s} inj={inj[:50]!r}")
        for m in mods:
            print(f"      {m:8s} {res[m]}")


if __name__ == "__main__":
    main()
