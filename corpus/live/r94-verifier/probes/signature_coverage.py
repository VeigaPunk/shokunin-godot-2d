#!/usr/bin/env python3
"""r94 verifier — signature coverage over every committed/collected receipt corpus.

For every r94 CASES row, re-classify every receipt of its own arm with the
PRODUCTION classify_process (AST-extracted from the frozen committed harness)
and require the signature byte-exactly present. Also:
  - classify each matching PASS line as EXACT (signature == full line) or TAIL
  - fallback forgery: no signature may be a substring of the unknown-arm
    fallback text; count fallback lines seen
  - stream hygiene: stderr byte counts for .err corpora
Writes only stdout.
"""
import ast
import hashlib
import json
import pathlib
import re
import sys

ROOT = pathlib.Path("/home/vgpnk/Projects/shokunin/game-dev-2d-shokunin")
FREEZE = ROOT / "corpus/live/r94-verifier/freeze/corpus/fixtures"
OUTDIR = ROOT / "corpus/live/r94-verifier"

src = (FREEZE / "run_battery.py").read_text()
tree = ast.parse(src)
fn_src = None
for node in ast.walk(tree):
    if isinstance(node, ast.FunctionDef) and node.name == "classify_process":
        fn_src = ast.get_source_segment(src, node)
        break
assert fn_src
seg_sha = hashlib.sha256(fn_src.encode()).hexdigest()
ns = {}
exec("import re\n" + fn_src, ns)
classify_process = ns["classify_process"]

import importlib.util
spec = importlib.util.spec_from_file_location("frozen_harness", FREEZE / "run_battery.py")
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
r94 = [(i, c) for i, c in enumerate(mod.CASES) if c[0].startswith("r94_")]
FALLBACK = "PASS particles_lattice unknown arm="


def arm_of(c):
    return c[2][0].removeprefix("--arm=")


def receipts():
    """yield (label, merged_output, rc, stderr_bytes, source_kind)"""
    # scout canonical + loadtest
    for base in [ROOT / "corpus/live/r94-scout/runs",
                 ROOT / "corpus/live/r94-scout/runs/loadtest"]:
        for out in sorted(base.glob("r94_particles_*.rep*.out")):
            err = out.with_suffix(".err")
            rc = out.with_suffix(".rc")
            if not rc.exists():
                continue
            e = err.read_bytes() if err.exists() else b""
            yield (str(out.relative_to(ROOT)), out.read_text() + e.decode(errors="replace"),
                   int(rc.read_text().strip()), len(e), "scout")
    # boundary batches
    for batch in ["quiet", "load", "ff30", "ff60", "ff120", "ff120load", "ab", "reprobe", "smoke"]:
        base = ROOT / "corpus/live/r94-boundary/runs" / batch
        for out in sorted(base.glob("r94_particles_*.rep*.out")):
            err = out.with_suffix(".err")
            rc = out.with_suffix(".rc")
            if not rc.exists():
                continue
            e = err.read_bytes() if err.exists() else b""
            yield (str(out.relative_to(ROOT)), out.read_text() + e.decode(errors="replace"),
                   int(rc.read_text().strip()), len(e), "boundary")
    # author battery runs + verifier battery runs (canonical five; foreign-seat
    # runs are counted separately below so the headline number is not diluted)
    for vj in [ROOT / "corpus/live/runs/20261016T055703426158Z/verdicts.json",
               ROOT / "corpus/live/runs/20261016T060430025246Z/verdicts.json",
               OUTDIR / "runs/20261016T063334001914Z/verdicts.json",
               OUTDIR / "runs/20261016T064310819140Z/verdicts.json",
               OUTDIR / "runs/20261016T065158572001Z/verdicts.json"]:
        try:
            j = json.loads(vj.read_text())
        except Exception:
            continue
        for r in j.get("results", []):
            if not r["case"].startswith("r94_"):
                continue
            yield (f"{vj.parent.name}:{r['case']}", "\n".join(r.get("output", [])) + "\n",
                   r.get("actual_exit"), None, "battery")
    # fresh arms
    for out in sorted((OUTDIR / "arms").glob("*.out")):
        err = out.with_suffix(".err")
        rc = out.with_suffix(".rc")
        if not rc.exists():
            continue
        e = err.read_bytes() if err.exists() else b""
        yield (str(out.relative_to(ROOT)), out.read_text() + e.decode(errors="replace"),
               int(rc.read_text().strip()), len(e), "fresh")


receipt_list = list(receipts())
print(f"receipts total: {len(receipt_list)}")
by_kind = {}
for r in receipt_list:
    by_kind[r[4]] = by_kind.get(r[4], 0) + 1
print("by kind:", by_kind)

counts = {"EXACT": 0, "TAIL": 0, "MISS": 0, "REJECT": 0, "CHECKED": 0}
per_row = {}
fallback_hits = 0
for r in receipt_list:
    if FALLBACK in r[1]:
        fallback_hits += 1

bad = []
for idx, c in r94:
    case, script, flags, expected_exit, sig = c
    arm = arm_of(c)
    st = {"EXACT": 0, "TAIL": 0, "MISS": 0, "REJECT": 0, "CHECKED": 0}
    for label, output, rc, errb, kind in receipt_list:
        # battery receipts are keyed by case; file receipts by arm prefix
        if kind == "battery":
            if not label.endswith(":" + case):
                continue
        else:
            base = pathlib.Path(label).name
            if not base.startswith(f"r94_particles_{arm}."):
                continue
        st["CHECKED"] += 1
        counts["CHECKED"] += 1
        ok = classify_process(rc, None, output, expected_exit, sig, ())
        if not ok:
            st["REJECT"] += 1
            counts["REJECT"] += 1
            bad.append((case, label))
            continue
        # find the matching PASS line
        hit_exact = False
        for line in output.splitlines():
            if sig in line:
                if line.strip() == sig:
                    hit_exact = True
                break
        if hit_exact:
            st["EXACT"] += 1
            counts["EXACT"] += 1
        else:
            st["TAIL"] += 1
            counts["TAIL"] += 1
    if st["MISS"] == 0 and st["REJECT"] == 0 and st["CHECKED"] == 0:
        st["MISS"] += 1
        counts["MISS"] += 1
    per_row[case] = st
    print(f"{case:36s} checked={st['CHECKED']:4d} exact={st['EXACT']:4d} tail={st['TAIL']:4d} reject={st['REJECT']}")

print("TOTALS", counts)
print("fallback lines in corpora:", fallback_hits)
print("signature is substring of fallback text:",
      [c[0] for _, c in r94 if c[4] in FALLBACK])
print("rejections:", bad[:20], "count", len(bad))
print("classify_process segment sha256 =", seg_sha[:16])

# stream hygiene for file receipts
err_total = sum(r[3] for r in receipt_list if r[3] is not None)
n_err = sum(1 for r in receipt_list if r[3] is not None)
print(f"file receipts with .err: {n_err}, total stderr bytes: {err_total}")

# foreign-seat battery runs (other seats' control/mutant harness copies): the
# r94 rows are still classified here, reported separately from the headline.
foreign = []
for vj in sorted((ROOT / "corpus/live/runs").glob("20261016T*/verdicts.json")):
    if vj.parent.name in ("20261016T055703426158Z", "20261016T060430025246Z"):
        continue
    try:
        j = json.loads(vj.read_text())
    except Exception:
        continue
    rows = [r for r in j.get("results", []) if r["case"].startswith("r94_")]
    if not rows:
        continue
    fails = []
    for r in rows:
        case = r["case"]
        sig = dict((c[0], c[4]) for _, c in r94)[case]
        if not classify_process(r.get("actual_exit"), r.get("error"),
                                "\n".join(r.get("output", [])) + "\n", 0, sig, ()):
            fails.append(case)
    foreign.append((vj.parent.name, len(rows), fails))
for name, n, fails in foreign:
    print(f"foreign battery run {name}: r94 rows={n} fails={fails}")
print("foreign battery runs:", len(foreign))

sys.exit(1 if (counts["REJECT"] or counts["MISS"] or fallback_hits) else 0)
