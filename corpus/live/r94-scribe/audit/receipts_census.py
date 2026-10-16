#!/usr/bin/env python3
"""r94 scribe receipts census — signature binding / collisions / clause constancy.

Reads the 19 landed r94 CASES tuples from `git show HEAD:corpus/fixtures/run_battery.py`
(AST, production bytes), then checks every r94 receipt on disk (scout canonical+loadtest,
boundary matrix+reprobe, author battery runs, scribe fresh receipts+battery runs) for the
pinned signature substring. Emits JSON + a human table.

Writes only corpus/live/r94-scribe/audit/receipts_census.json.
"""
import ast
import json
import re
import subprocess
from collections import Counter, defaultdict
from pathlib import Path

REPO = Path("/home/vgpnk/Projects/shokunin/game-dev-2d-shokunin")
OUT = REPO / "corpus/live/r94-scribe/audit"

src = subprocess.run(["git", "show", "HEAD:corpus/fixtures/run_battery.py"],
                     cwd=REPO, capture_output=True).stdout.decode()
tree = ast.parse(src)
cases = None
for node in ast.walk(tree):
    if isinstance(node, ast.Assign) and getattr(node.targets[0], "id", "") == "CASES":
        cases = node.value
rows = {}
for el in cases.elts:
    t = ast.literal_eval(el)
    if t[0].startswith("r94_"):
        rows[t[0]] = {"script": t[1], "flags": t[2], "exit": t[3], "signature": t[4],
                      "arm": t[2][0].split("=", 1)[1] if t[2] and t[2][0].startswith("--arm=") else None}
case_to_arm = {k: v["arm"] for k, v in rows.items()}
assert len(case_to_arm) == 19

# ---- receipt collection ----------------------------------------------------
receipts = []  # dict(path, source, arm, text, condition)


def add_file(path, source, condition=""):
    try:
        text = path.read_text(errors="replace")
    except OSError:
        return
    m = re.search(r"PASS particles_lattice (\w+)", text)
    arm = m.group(1) if m else None
    receipts.append({"path": str(path.relative_to(REPO)), "source": source,
                     "arm": arm, "condition": condition, "text": text})


scout = REPO / "corpus/live/r94-scout"
for f in sorted((scout / "runs").glob("r94_particles_*.rep*.out")):
    add_file(f, "scout-canonical", "quiet-60tps")
for f in sorted((scout / "runs/loadtest").glob("r94_particles_*.rep*.out")):
    add_file(f, "scout-loadtest", "load-8hogs")

bnd = REPO / "corpus/live/r94-boundary"
for batch in ("quiet", "load", "ff30", "ff60", "ff120", "ff120load", "ab", "reprobe"):
    for f in sorted((bnd / "runs" / batch).glob("*")):
        if f.suffix in (".out",):
            add_file(f, f"boundary-{batch}", batch)

# author battery runs (per-row output in verdicts.json)
author_runs = []
for stamp in ("20261016T055703426158Z", "20261016T060430025246Z"):
    p = REPO / f"corpus/live/runs/{stamp}/verdicts.json"
    if not p.is_file():
        continue
    d = json.loads(p.read_text())
    for r in d["results"]:
        if r["case"].startswith("r94_"):
            receipts.append({"path": f"{p.parent.name}/{r['case']}",
                             "source": "author-battery", "condition": stamp,
                             "arm": case_to_arm.get(r["case"]), "text": "\n".join(r.get("output") or []),
                             "case": r["case"], "verdict": r["verdict"]})
            author_runs.append((stamp, r["case"], r["verdict"]))

# scribe fresh receipts + scribe battery runs
for mode in ("fresh", "fresh-ff30", "fresh-ff60"):
    d = REPO / f"corpus/live/r94-scribe/{mode}"
    for f in sorted(d.glob("*.out")) if d.is_dir() else []:
        add_file(f, f"scribe-{mode}", mode)
for d in sorted((REPO / "corpus/live/r94-scribe").glob("battery-*/*/verdicts.json")):
    dd = json.loads(d.read_text())
    for r in dd["results"]:
        if r["case"].startswith("r94_"):
            receipts.append({"path": str(d.parent.relative_to(REPO)) + f"/{r['case']}",
                             "source": "scribe-battery", "condition": d.parent.name,
                             "arm": case_to_arm.get(r["case"]), "text": "\n".join(r.get("output") or []),
                             "case": r["case"], "verdict": r["verdict"]})

# ---- binding census --------------------------------------------------------
bind = {}
for name, row in rows.items():
    arm = row["arm"]
    own = [r for r in receipts if r["arm"] == arm]
    hits, misses = [], []
    for r in own:
        (hits if row["signature"] in r["text"] else misses).append(r)
    miss_detail = []
    for r in misses:
        line = next((l for l in r["text"].splitlines()
                     if l.startswith("PASS particles_lattice " + arm)), None)
        miss_detail.append({"path": r["path"], "source": r["source"],
                            "condition": r["condition"], "line": line})
    # collisions: the same pin seen in a different arm's receipts
    coll = [{"path": r["path"], "source": r["source"], "arm": r["arm"]}
            for r in receipts if r["arm"] not in (arm, None) and row["signature"] in r["text"]]
    prefixes = Counter()
    for r in own:
        line = next((l for l in r["text"].splitlines()
                     if l.startswith("PASS particles_lattice " + arm)), None)
        if line:
            prefixes[line.split(" | ")[0]] += 1
    bind[name] = {
        "arm": arm, "receipts_own_arm": len(own), "hits": len(hits),
        "misses": len(misses), "miss_detail": miss_detail,
        "collisions": coll, "distinct_gating_prefixes": len(prefixes),
        "prefix_counts": dict(prefixes.most_common(6)),
    }

# ---- stderr / rc sidecar census (scout + boundary) ------------------------
side = {"rc_nonzero": [], "stderr_nonempty": [], "files": 0}
for root, pat in ((scout / "runs", "r94_particles_*"), (bnd / "runs", "r94_particles_*")):
    for f in sorted(root.rglob("*")):
        if f.suffix == ".rc":
            side["files"] += 1
            if f.read_text().strip() not in ("0",):
                side["rc_nonzero"].append(str(f.relative_to(REPO)))
        if f.suffix == ".err":
            side["files"] += 1
            if f.read_bytes():
                side["stderr_nonempty"].append(str(f.relative_to(REPO)))

# ---- battery row verdicts --------------------------------------------------
bat = defaultdict(Counter)
for r in receipts:
    if "verdict" in r:
        bat[r["source"]][(r["condition"], r["verdict"])] += 1

# ---- boundary condition matrix (frozen probe) ------------------------------
matrix = {}
for cond in ("quiet", "load", "ff30", "ff60", "ff120", "ff120load"):
    checks = rejected = 0
    which = []
    for name, row in rows.items():
        arm = row["arm"]
        for r in receipts:
            if r["source"] == f"boundary-{cond}" and r["arm"] == arm:
                checks += 1
                if row["signature"] not in r["text"]:
                    rejected += 1
                    which.append(name)
    matrix[cond] = {"checks": checks, "rejected": rejected, "which": sorted(set(which))}
matrix["total"] = {"checks": sum(v["checks"] for v in matrix.values()),
                   "rejected": sum(v["rejected"] for v in matrix.values())}

# ---- landed-fixture-only census -------------------------------------------
landed = {"checks": 0, "rejected": []}
for name, row in rows.items():
    arm = row["arm"]
    for r in receipts:
        if r["source"] in ("author-battery", "scribe-battery", "scribe-fresh",
                           "scribe-fresh-ff30", "scribe-fresh-ff60") and r["arm"] == arm:
            landed["checks"] += 1
            if row["signature"] not in r["text"]:
                landed["rejected"].append({"case": name, "path": r["path"]})

payload = {"rows": {k: {"arm": v["arm"], "signature": v["signature"]} for k, v in rows.items()},
           "receipt_totals": Counter(r["source"] for r in receipts),
           "binding": bind, "sidecars": side, "boundary_matrix": matrix,
           "landed_fixture_census": landed,
           "battery_rows": {k: {f"{c}|{v}": n for (c, v), n in cnt.items()}
                            for k, cnt in bat.items()},
           "author_runs": [{"stamp": s, "case": c, "verdict": v} for s, c, v in author_runs]}
(OUT / "receipts_census.json").write_text(json.dumps(payload, indent=2, default=str) + "\n")

print("receipts by source:", dict(payload["receipt_totals"]))
tot_hit = tot_miss = 0
for name, b in bind.items():
    tot_hit += b["hits"]
    tot_miss += b["misses"]
    print(f"{name:34s} own={b['receipts_own_arm']:3d} hit={b['hits']:3d} miss={b['misses']:2d} "
          f"coll={len(b['collisions']):2d} prefixes={b['distinct_gating_prefixes']}")
print("TOTAL hits", tot_hit, "misses", tot_miss)
print("rc_nonzero", side["rc_nonzero"][:5], "stderr_nonempty", side["stderr_nonempty"][:5], "files", side["files"])
