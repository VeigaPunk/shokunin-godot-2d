#!/usr/bin/env python3
"""r95-simplifier pin<->emission census over the independent r95 receipts.

Sources scanned (read-only):
  corpus/live/r95-scout/runs/**/*.out             (scout matrix, 211 receipts)
  corpus/live/r95-boundary/runs/**/*.out          (boundary matrix, 261 receipts)
  corpus/live/runs/<stamp>/verdicts.json          (author battery runs, 4)

Rows are matched to receipts by the receipt stem the probe convention assigns
(`dss_<arm>[_rev]` / `r95b_order_<variant>`), so a `periodx_k2` receipt is not
counted as evidence for the `periodx_k10` row. For every row: receipt count,
pin-hit count (committed signature substring, the battery's own criterion),
distinct PASS payloads (byte-stability), and the author-run verdict.

Also: the r95 expected_errors/required_stderr allowlist census and the
floor-gate prefix table from the committed harness.

Usage: python3 pin_census.py > pin-census.txt
"""
import ast
import json
import re
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
CF = HERE / "committed-fixtures"
REPO = HERE.parents[2]

RUNS = [
    REPO / "corpus" / "live" / "r95-scout" / "runs",
    REPO / "corpus" / "live" / "r95-boundary" / "runs",
]
AUTHOR_RUNS = [
    REPO / "corpus" / "live" / "runs" / s / "verdicts.json"
    for s in ("20261016T064148780406Z", "20261016T064742446822Z",
              "20261016T065335715243Z", "20261016T065922894811Z")
]


def rows():
    tree = ast.parse((CF / "run_battery.py").read_text())
    cases = {}
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign) and getattr(node.targets[0], "id", "") == "CASES":
            for elt in node.value.elts:
                t = ast.literal_eval(elt)
                cases[t[0]] = {"script": t[1], "flags": list(t[2]), "signature": t[4]}
    return {k: v for k, v in cases.items()
            if k.startswith("dss_lattice_") or k.startswith("r95b_order_")}


def stem_of(row, spec):
    arm = spec["flags"][0].split("=", 1)[1] if spec["flags"] else "?"
    if row.startswith("dss_lattice_"):
        return "dss_%s%s" % (arm, "_rev" if "--rev" in spec["flags"] else "")
    return row.removeprefix("r95b_order_")


def main():
    r95 = rows()
    by_stem = defaultdict(list)
    total = 0
    for src in RUNS:
        for p in sorted(src.rglob("*.out")):
            stem = re.sub(r"\.rep\d*\.out$", "", p.name)
            by_stem[stem].append((p, p.read_text(errors="replace")))
            total += 1
    print("receipts scanned (.out): %d   distinct stems: %d" % (total, len(by_stem)))

    author = {}
    for vp in AUTHOR_RUNS:
        if vp.exists():
            data = json.loads(vp.read_text())
            for rec in data.get("results", []):
                author.setdefault(rec["case"], []).append(rec.get("verdict"))
    print("author-run verdict records: %d cases x %d runs"
          % (len(author), len(AUTHOR_RUNS)))

    print()
    print("== per-row pin census (stem-matched receipts) ==")
    print("%-34s %-16s %-6s %-7s %-9s %-9s" % ("row", "stem", "recs", "pin-hit", "distinct", "author"))
    miss = []
    for row, spec in sorted(r95.items()):
        stem = stem_of(row, spec)
        recs = by_stem.get(stem, [])
        hits = [r for r in recs if spec["signature"] in r[1]]
        distinct = len({r[1] for r in recs})
        av = author.get(row, [])
        av_s = "%d/%d" % (sum(1 for v in av if v == "PASS"), len(av))
        print("%-34s %-16s %-6d %-7d %-9d %-9s" % (row, stem, len(recs), len(hits), distinct, av_s))
        if recs and len(hits) != len(recs):
            miss.append((row, stem, len(recs), len(hits)))
        if not recs:
            miss.append((row, stem, 0, 0))
    print()
    print("rows with zero stem-matched receipts: %s"
          % ", ".join(r for r, s, n, h in miss if n == 0) or "none")
    print("rows with pin-hits < receipts: %s"
          % (", ".join("%s %d/%d" % (r, h, n) for r, s, n, h in miss if n > 0) or "none"))

    # allowlist + gate census
    src = (CF / "run_battery.py").read_text()
    tree = ast.parse(src)
    exp_err, req_err = {}, {}
    for node in ast.walk(tree):
        if isinstance(node, ast.Dict):
            keys = {k.value for k in node.keys if isinstance(k, ast.Constant)}
            is_req = "r92_tilemap_nullts_crash" in keys
            for k, v in zip(node.keys, node.values):
                if not isinstance(k, ast.Constant):
                    continue
                key = str(k.value)
                if not (key.startswith("dss_lattice_") or key.startswith("r95b_order_")):
                    continue
                if isinstance(v, (ast.Tuple, ast.List)):
                    (req_err if is_req else exp_err)[key] = ast.literal_eval(v)
    print()
    print("== r95 allowlist census ==")
    print("  expected_errors entries: %d  rows: %d"
          % (sum(len(v) for v in exp_err.values()), len(exp_err)))
    print("  required_stderr entries: %d  rows: %d"
          % (sum(len(v) for v in req_err.values()), len(req_err)))
    err_receipts = [(p, l) for ps in by_stem.values() for p, t in ps
                    for l in t.splitlines() if l.startswith("ERROR:")]
    print("  ERROR: lines across all r95 receipts: %d (in %d receipts)"
          % (len(err_receipts), len({p for p, _ in err_receipts})))
    for p, l in err_receipts[:6]:
        print("      %s: %s" % (p.relative_to(REPO), l.strip()[:100]))

    lines = src.splitlines()
    print()
    print("== floor gates (prefixes) ==")
    for i, l in enumerate(lines):
        if "expected_errors_all_matched" in l:
            m = re.search(r'startswith\(\(?([^)]*)\)?\)', "\n".join(lines[i:i + 9]))
            print("  line=%-5d %-52s %s" % (i + 1, l.strip().rstrip('":'),
                                            re.findall(r'"([^"]+)"', m.group(1)) if m else "?"))


if __name__ == "__main__":
    main()
