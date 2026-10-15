#!/usr/bin/env python3
"""r92-boundary independent row verification.

Gates the r92 scout's 13 author rows against EVERY r92-boundary receipt (all
conditions: quiet / load / fixed-fps 10,20,30,60,120,600 / load+ff / 120-tps
project / repeat window) using the PRODUCTION `classify_process` extracted
verbatim (AST) from corpus/fixtures/run_battery.py — the same segment the scout
pinned (sha256 749fa060…). Also re-gates the scout's own canonical+loadtest
receipts as a control, and the scout's ROWS_PREFIX form.

Usage: python3 verify_r92b.py [repo_root]
Exit 0 iff every gated receipt is accepted under both row forms.
"""
import ast
import hashlib
import pathlib
import re
import sys

HERE = pathlib.Path(__file__).parent
ROOT = pathlib.Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else HERE.parent.parent.parent
FIXTURE = ROOT / "corpus" / "fixtures" / "run_battery.py"
SCOUT = ROOT / "corpus" / "live" / "r92-scout"

src = FIXTURE.read_text()
tree = ast.parse(src)
fn_src = None
for node in ast.walk(tree):
    if isinstance(node, ast.FunctionDef) and node.name == "classify_process":
        fn_src = ast.get_source_segment(src, node)
        break
assert fn_src, "classify_process not found"
seg_sha = hashlib.sha256(fn_src.encode()).hexdigest()
ns = {}
exec("import re\n" + fn_src, ns)
classify_process = ns["classify_process"]

rows_ns = {}
exec((SCOUT / "author-rows.py.txt").read_text(), rows_ns)
ROWS = rows_ns["ROWS"]
ROWS_PREFIX = rows_ns["ROWS_PREFIX"]
EXPECTED = rows_ns["EXPECTED_ERRORS"]

CASE_TO_CELL = {
    "r92_tilemap_census": "tm_census",
    "r92_tilemap_atlas": "tm_atlas",
    "r92_tilemap_cells": "tm_cells",
    "r92_tilemap_custom": "tm_custom",
    "r92_tilemap_terrain": "tm_terrain",
    "r92_tilemap_pattern": "tm_pattern",
    "r92_tilemap_encoding": "tm_encoding",
    "r92_tilemap_fixinvalid": "tm_fixinvalid",
    "r92_tilemap_srcids": "tm_srcids",
    "r92_tilemap_physics": "tm_physics",
    "r92_tilemap_timing": "tm_timing",
    "r92_tilemap_quadrant": "tm_quadrant",
    "r92_tilemap_nav": "tm_nav",
}

# boundary receipt name -> arm cell
def cell_of(name):
    if name.startswith("o"):
        return None  # own poller arms (oq_/ol_/of30_/...) are not scout author rows
    m = re.match(r"(?:[a-z0-9]+)_(census|atlas|cells|custom|terrain|pattern|encoding|fixinvalid|srcids|physics|timing|quadrant|nav)\.rep\d+\.out$", name)
    return ("tm_" + m.group(1)) if m else None


def boundary_receipts():
    for out in sorted((HERE / "runs").glob("*.out")):
        cell = cell_of(out.name)
        if cell is None:
            continue  # own probe arms (r92b_*) are not author rows
        err = out.with_suffix(".err")
        rc = out.with_suffix(".rc")
        batch = out.name.split("_")[0]
        yield batch, out.name, out.read_text() + (err.read_text() if err.exists() else ""), int(rc.read_text().strip()), cell


def scout_receipts():
    for out in sorted((SCOUT / "runs").glob("r92_tm_*.rep*.out")):
        err = out.with_suffix(".err")
        rc = out.with_suffix(".rc")
        cell = "tm_" + out.name.split("_tm_")[1].split(".")[0]
        yield "scout_canonical", out.name, out.read_text() + (err.read_text() if err.exists() else ""), int(rc.read_text().strip()), cell
    for out in sorted((SCOUT / "runs" / "loadtest").glob("r92_tm_*.rep*.out")):
        err = out.with_suffix(".err")
        rc = out.with_suffix(".rc")
        cell = "tm_" + out.name.split("_tm_")[1].split(".")[0]
        yield "scout_loadtest", out.name, out.read_text() + (err.read_text() if err.exists() else ""), int(rc.read_text().strip()), cell


def check(rows, label, receipts):
    rejected = []
    checked = 0
    per_batch = {}
    for case, script, flags, expected_exit, sig in rows:
        cell = CASE_TO_CELL[case]
        allowed = EXPECTED.get(case, ())
        for batch, name, output, code, rc_cell in receipts:
            if rc_cell != cell:
                continue
            ok = classify_process(code, None, output, expected_exit, sig, allowed)
            checked += 1
            per_batch.setdefault(batch, [0, 0])
            per_batch[batch][0] += 1
            if not ok:
                per_batch[batch][1] += 1
                rejected.append((case, batch, name))
    print("[%s] rows=%d receipts_checked=%d rejected=%d" % (label, len(rows), checked, len(rejected)))
    for b in sorted(per_batch):
        n, r = per_batch[b]
        print("    %-16s checked=%-4d rejected=%d" % (b, n, r))
    for r in rejected[:20]:
        print("    REJECTED %s" % (r,))
    return rejected


boundary = list(boundary_receipts())
scout = list(scout_receipts())
print("classify_process segment sha256=%s" % seg_sha[:16])
print("boundary receipts=%d  scout control receipts=%d" % (len(boundary), len(scout)))

rej = []
rej += check(ROWS, "BOUNDARY/ROWS(full-line)", boundary)
rej += check(ROWS_PREFIX, "BOUNDARY/ROWS_PREFIX(census-tail-cut)", boundary)
rej += check(ROWS, "SCOUT-CONTROL/ROWS", scout)
print("TOTAL rejected=%d" % len(rej))
sys.exit(1 if rej else 0)
