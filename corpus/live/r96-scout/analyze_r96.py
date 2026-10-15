#!/usr/bin/env python3
"""r96-scout analyzer — per-cell byte-stability of the canonical receipts.

For each cell: reps, distinct stdout, distinct stderr, rc set, and the set of
PASS lines. UNSTABLE cells are printed loudly; any ERROR: line in stderr is listed
so the row's expected_errors can be built.
"""
import json
import pathlib
import re

HERE = pathlib.Path(__file__).parent
RUNS = HERE / "runs"

CELLS = ["census", "pack_basic", "ownership", "formats", "det", "uid", "takeover",
         "cache", "subres", "extres", "editstate", "refuse", "edges"]

report = {"cells": {}, "unstable": [], "error_lines": {}, "pass_lines": {}}
for cell in CELLS:
    outs = sorted(RUNS.glob(f"r96_{cell}.rep*.out"))
    errs = sorted(RUNS.glob(f"r96_{cell}.rep*.err"))
    rcs = sorted(RUNS.glob(f"r96_{cell}.rep*.rc"))
    o_uniq = {p.read_text() for p in outs}
    e_uniq = {p.read_text() for p in errs}
    rc_set = {int(p.read_text().strip()) for p in rcs}
    passes = set()
    for p in outs:
        for line in p.read_text().splitlines():
            if line.startswith("PASS scene_io_lattice"):
                passes.add(line)
    err_lines = set()
    for p in errs:
        for line in p.read_text().splitlines():
            if "ERROR:" in line:
                err_lines.add(line.strip())
    report["cells"][cell] = {
        "reps": len(outs), "out_uniq": len(o_uniq), "err_uniq": len(e_uniq),
        "rc": sorted(rc_set), "pass_uniq": len(passes), "pass_lines": len(passes),
        "err_bytes": [p.stat().st_size for p in errs],
    }
    if len(o_uniq) != 1 or len(e_uniq) != 1 or rc_set != {0}:
        report["unstable"].append(cell)
    if err_lines:
        report["error_lines"][cell] = sorted(err_lines)
    report["pass_lines"][cell] = sorted(passes)

print(json.dumps(report, indent=1)[:200])
(HERE / "runs" / "analyze_r96.json").write_text(json.dumps(report, indent=1))

print(f"{'cell':<12} {'reps':>4} {'out_uniq':>8} {'err_uniq':>8} {'rc':>6} {'pass':>5} {'errB':>6}")
for cell, d in report["cells"].items():
    print(f"{cell:<12} {d['reps']:>4} {d['out_uniq']:>8} {d['err_uniq']:>8} {str(d['rc']):>6} {d['pass_lines']:>5} {d['err_bytes'][0]:>6}")
print("UNSTABLE =", report["unstable"])
print("CRASH_CELLS =", [c for c, d in report["cells"].items() if d["rc"] != [0]])
print()
for cell, lines in report["error_lines"].items():
    print(f"--- {cell} ERROR lines ({len(lines)}) ---")
    for line in lines:
        print("   ", line)
print()
for cell, lines in report["pass_lines"].items():
    print(f"--- {cell} PASS lines ({len(lines)}) ---")
    for line in lines:
        print("   ", line[:400] + (" …" if len(line) > 400 else ""))
