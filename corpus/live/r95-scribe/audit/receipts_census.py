#!/usr/bin/env python3
"""r95-scribe receipts census — signature binding + collision + ERROR: census.

Sources (all on-disk receipts / recorded run outputs):
  boundary   corpus/live/r95-boundary/runs/**/*.out        (fresh process)
  scout      corpus/live/r95-scout/runs/**/*.out           (fresh process)
  author     corpus/live/runs/<stamp>/verdicts.json        (battery rows)
  scribe     corpus/live/r95-scribe/battery-*/<stamp>/verdicts.json
  fresh      corpus/live/r95-scribe/fresh/*.out            (fresh process)
Read-only.
"""
import ast
import json
import re
import subprocess
from pathlib import Path

REPO = Path("/home/vgpnk/Projects/shokunin/game-dev-2d-shokunin")
LANE = REPO / "corpus/live/r95-scribe"


def r95_cases():
    src = subprocess.run(["git", "show", "HEAD:corpus/fixtures/run_battery.py"],
                         cwd=REPO, capture_output=True, text=True).stdout
    tree = ast.parse(src)
    for node in tree.body:
        if isinstance(node, ast.Assign):
            for t in node.targets:
                if isinstance(t, ast.Name) and t.id == "CASES":
                    vals = [tuple(ast.literal_eval(e) for e in c.elts) for c in node.value.elts]
                    return [v for v in vals
                            if str(v[0]).startswith(("dss_lattice_", "r95b_order_"))]
    raise SystemExit("no CASES")


CASES = {c[0]: c for c in r95_cases()}

receipts = []  # {source, path, case, text}


def add(source, path, case, text):
    receipts.append({"source": source, "path": path, "case": case, "text": text})


for p in sorted((REPO / "corpus/live/r95-boundary/runs").glob("*/*.out")):
    add("boundary", str(p.relative_to(REPO)), p.name.split(".rep")[0], p.read_text(errors="replace"))
for p in sorted((REPO / "corpus/live/r95-scout/runs").glob("**/*.out")):
    add("scout", str(p.relative_to(REPO)), p.name.split(".rep")[0], p.read_text(errors="replace"))
for stamp_dir in sorted((REPO / "corpus/live/runs").glob("2026*")):
    vf = stamp_dir / "verdicts.json"
    if not vf.exists():
        continue
    v = json.loads(vf.read_text())
    if len(v.get("results", [])) < 360:
        continue
    for r in v["results"]:
        if str(r.get("case", "")).startswith(("dss_lattice_", "r95b_order_")):
            add("author", str(vf.relative_to(REPO)), r["case"],
                "\n".join(r.get("output") or []))
for lane_dir in ("battery-runs", "battery-committed"):
    for vf in sorted((LANE / lane_dir).glob("*/verdicts.json")):
        v = json.loads(vf.read_text())
        for r in v["results"]:
            if str(r.get("case", "")).startswith(("dss_lattice_", "r95b_order_")):
                add("scribe-battery", str(vf.relative_to(REPO)), r["case"],
                    "\n".join(r.get("output") or []))
for p in sorted((LANE / "fresh").glob("*.out")):
    add("scribe-fresh", str(p.relative_to(REPO)), p.name.split(".")[0], p.read_text(errors="replace"))

# ---- binding -----------------------------------------------------------------
own_hits, own_misses, collisions, error_lines = 0, [], [], []
unmapped = 0
for r in receipts:
    case = r["case"]
    c = CASES.get(case)
    if not c:
        unmapped += 1
        continue
    sig = c[4]
    if sig in r["text"]:
        own_hits += 1
    else:
        own_misses.append({"source": r["source"], "path": r["path"], "case": case})
    # collisions: some OTHER r95 signature inside this receipt
    for other, oc in CASES.items():
        if other == case:
            continue
        if oc[4] in r["text"] and len(oc[4]) > 40:
            collisions.append({"source": r["source"], "path": r["path"],
                               "case": case, "foreign_sig_case": other})
    for line in r["text"].splitlines():
        if "ERROR:" in line:
            error_lines.append({"source": r["source"], "path": r["path"], "case": case,
                                "line": line[:200]})

# ---- per-source counts -------------------------------------------------------
by_source = {}
for r in receipts:
    by_source.setdefault(r["source"], {"receipts": 0, "cases": set()})
    by_source[r["source"]]["receipts"] += 1
    by_source[r["source"]]["cases"].add(r["case"])
by_source = {k: {"receipts": v["receipts"], "distinct_cases": len(v["cases"])}
             for k, v in sorted(by_source.items())}

# ---- per-case receipt counts -------------------------------------------------
per_case = {}
for r in receipts:
    per_case.setdefault(r["case"], {}).setdefault(r["source"], 0)
    per_case[r["case"]][r["source"]] += 1

out = {
    "sources": by_source,
    "total_receipts": len(receipts),
    "receipts_named_by_landed_case": len(receipts) - unmapped,
    "receipts_unmapped_probe_names": unmapped,
    "own_arm_checks": len(receipts) - unmapped,
    "own_arm_hits": own_hits,
    "own_arm_misses": own_misses,
    "cross_arm_collisions": collisions[:20],
    "cross_arm_collision_count": len(collisions),
    "error_line_receipts": error_lines[:20],
    "error_line_count": len(error_lines),
    "per_case_receipts": {k: v for k, v in sorted(per_case.items())},
}
(LANE / "audit/receipts_census.json").write_text(json.dumps(out, indent=2, sort_keys=True))
print(json.dumps({k: v for k, v in out.items() if k != "per_case_receipts"}, indent=2)[:5000])
