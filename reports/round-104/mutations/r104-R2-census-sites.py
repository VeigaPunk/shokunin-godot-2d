#!/usr/bin/env python3
"""r104-R2 — site-specific census-tightening variants + full-corpus green silence.

The predicate `line.startswith("PASS ")` occurs 4x in `receipt_shape_flag`
(census + 3 membership tests). A blunt textual replacement tightens the census
AND loosens the span/diag windows. This harness separates the sites by AST
function-body position and measures each variant:
  V0 live         (no change)
  V1 census-only  (tighten only the pass-line census)
  V2 all-sites    (blunt textual replacement of all 4 occurrences)
Plus a green-silence sweep of V0/V1/V2 over every stored run.
"""
import argparse
import ast
import hashlib
import importlib.util
import json
import shutil
import sys

sys.dont_write_bytecode = True  # never leave __pycache__ in a shared reports/ tree
from pathlib import Path

REPO = Path("/home/vgpnk/Projects/shokunin/game-dev-2d-shokunin")
BATTERY = REPO / "corpus/fixtures/run_battery.py"
SCRATCH = Path("/var/tmp/r104-R2")
RUNS = sorted((REPO / "corpus/live/runs").glob("*/verdicts.json"))
MUT05 = REPO / "reports/round-103/mutations/mut05_gate_evasion.py"

OLD = 'line.startswith("PASS ")'
NEW = 'line.lstrip().startswith("PASS")'


def sha256(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def sites():
    """1-based line numbers of OLD inside receipt_shape_flag, in source order."""
    src = BATTERY.read_text()
    tree = ast.parse(src)
    fn = next(n for n in ast.walk(tree)
              if isinstance(n, ast.FunctionDef) and n.name == "receipt_shape_flag")
    return [fn.lineno + i for i, l in enumerate(
        src.splitlines()[fn.lineno - 1:fn.end_lineno]) if OLD in l]


def write_variant(tag, replace_lines):
    """replace_lines: set of 1-based line numbers to rewrite with NEW."""
    src = BATTERY.read_text()
    out = []
    for i, line in enumerate(src.splitlines(keepends=True), 1):
        if i in replace_lines and OLD in line:
            line = line.replace(OLD, NEW)
        out.append(line)
    SCRATCH.mkdir(parents=True, exist_ok=True)
    dst = SCRATCH / ("variant_%s.py" % tag)
    dst.write_text("".join(out))
    return dst


def load(path, tag):
    spec = importlib.util.spec_from_file_location("v_%s" % tag, path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def load_evasions():
    spec = importlib.util.spec_from_file_location("mut05b", MUT05)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    data, run_sha = m.load_run()
    ev, cases = m.build_evasions(data["results"])
    return m, data, run_sha, ev, cases


def variants():
    print("BATTERY sha256=%s" % sha256(BATTERY))
    s = sites()
    print("OLD-predicate sites inside receipt_shape_flag (1-based): %s" % s)
    census = {s[0]}
    v1 = write_variant("census_only", census)
    v2 = write_variant("all_sites", set(s))
    print("V1 census-only sha256=%s" % sha256(v1))
    print("V2 all-sites   sha256=%s" % sha256(v2))
    return s, v1, v2


def shape_matrix(v1, v2):
    m, data, run_sha, ev, cases = load_evasions()
    mods = {"V0_live": load(BATTERY, "live"), "V1_census": load(v1, "c1"),
            "V2_allsites": load(v2, "c2")}
    print("\n%-30s %-9s %-9s %-9s" % ("shape", "V0_live", "V1_census", "V2_all"))
    flips = {"V1": [], "V2": []}
    for name, row in ev:
        cells = []
        for k, mod in mods.items():
            fl = mod.receipt_shape_flag(row)
            cells.append("%d:%s" % (len(fl), ",".join(sorted({f["why"] for f in fl}))[:38]))
        print("%-30s %-9s %-9s %-9s" % (name, *[c.split(":")[0] for c in cells]))
        for k in ("V1", "V2"):
            if not mods["V0_live"].receipt_shape_flag(row) and \
               mods[{"V1": "V1_census", "V2": "V2_allsites"}[k]].receipt_shape_flag(row):
                flips[k].append(name)
    print("\nV1 newly-flags: %s" % flips["V1"])
    print("V2 newly-flags: %s" % flips["V2"])
    print("\nDETAIL (why sets):")
    for name, row in ev:
        for k, mod in mods.items():
            fl = mod.receipt_shape_flag(row)
            if fl:
                print("  %-28s %-11s %s" % (name, k, sorted({f["why"] for f in fl})))
    return flips


def green_silence(v1, v2):
    mods = {"V0_live": load(BATTERY, "gl"), "V1_census": load(v1, "g1"),
            "V2_allsites": load(v2, "g2")}
    print("\n%-34s %-12s %-9s %-9s" % ("run", "V0_flags/aud", "V1", "V2"))
    tot = {k: 0 for k in mods}
    for p in RUNS:
        d = json.loads(p.read_bytes())
        rows = d.get("results", [])
        line = [p.parent.name]
        for k, mod in mods.items():
            r = mod.receipt_shape_audit(rows)
            tot[k] += len(r["flags"])
            line.append("%d/%d" % (len(r["flags"]), r["audited"]))
        print("%-34s %-12s %-9s %-9s" % tuple(line))
    print("\nTOTAL FLAGS over %d runs: %s" % (len(RUNS), tot))
    return tot


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--variants", action="store_true")
    ap.add_argument("--shapes", action="store_true")
    ap.add_argument("--green", action="store_true")
    ap.add_argument("--all", action="store_true")
    a = ap.parse_args()
    s, v1, v2 = variants()
    if a.all or a.shapes:
        print("\n### SHAPE MATRIX"); shape_matrix(v1, v2)
    if a.all or a.green:
        print("\n### GREEN SILENCE"); green_silence(v1, v2)
    return 0


if __name__ == "__main__":
    sys.exit(main())
