#!/usr/bin/env python3
"""r92 critic seat — static audit of the COMMITTED bytes (5900431).

Everything here is derived from:
  * `git show 5900431:<path>` (the committed tree, never the worktree), and
  * the seat's own fresh receipts under corpus/live/r92-critic/runs/.
No tracked file is written; no commit.
"""
import ast, hashlib, json, pathlib, subprocess, sys

REPO = pathlib.Path("/home/vgpnk/Projects/shokunin/game-dev-2d-shokunin")
SEAT = REPO / "corpus" / "live" / "r92-critic"
FROZEN = SEAT / "frozen" / "corpus" / "fixtures"
COMMIT = "5900431"
out = {}


def sh(*cmd, cwd=REPO):
    return subprocess.run(cmd, cwd=cwd, capture_output=True, text=True).stdout


def committed(path):
    return subprocess.run(["git", "show", f"{COMMIT}:{path}"], cwd=REPO,
                          capture_output=True, text=True).stdout


# ---------------------------------------------------------------- 1. commit shape
numstat = sh("git", "show", "--numstat", "--format=", COMMIT)
files = [l.split("\t") for l in numstat.strip().splitlines() if l.strip()]
add = sum(int(f[0]) for f in files if f[0] != "-")
dele = sum(int(f[1]) for f in files if f[1] != "-")
rb = [f for f in files if f[2] == "corpus/fixtures/run_battery.py"][0]
out["commit"] = {"files": len(files), "insertions": add, "deletions": dele,
                 "run_battery_numstat": [int(rb[0]), int(rb[1])],
                 "run_battery_sha": hashlib.sha256(
                     committed("corpus/fixtures/run_battery.py").encode()).hexdigest(),
                 "fixture_sha": hashlib.sha256(
                     committed("corpus/fixtures/tilemap_lattice.gd").encode()).hexdigest(),
                 "project_godot_sha": hashlib.sha256(
                     committed("corpus/fixtures/project.godot").encode()).hexdigest()}
out["commit"]["parent"] = sh("git", "rev-parse", COMMIT + "^").strip()
out["commit"]["parent_rb_sha"] = hashlib.sha256(
    subprocess.run(["git", "show", f"{COMMIT}^:corpus/fixtures/run_battery.py"],
                   cwd=REPO, capture_output=True, text=True).stdout.encode()).hexdigest()

# prior rows byte-unchanged: diff of CASES tuples between parent and commit
src = committed("corpus/fixtures/run_battery.py")
psrc = subprocess.run(["git", "show", f"{COMMIT}^:corpus/fixtures/run_battery.py"],
                      cwd=REPO, capture_output=True, text=True).stdout


def cases_of(source):
    tree = ast.parse(source)
    for n in ast.walk(tree):
        if isinstance(n, ast.Assign) and getattr(n.targets[0], "id", "") == "CASES":
            return [ast.literal_eval(e) for e in n.value.elts]
    return []


new_cases, old_cases = cases_of(src), cases_of(psrc)
out["cases"] = {"old": len(old_cases), "new": len(new_cases),
                "old_rows_intact": [c for c in new_cases
                                    if not c[0].startswith("r92_")] == old_cases,
                "r92_index": [i for i, c in enumerate(new_cases)
                              if c[0].startswith("r92_")],
                "prev_row": new_cases[[i for i, c in enumerate(new_cases)
                                       if c[0].startswith("r92_")][0] - 1][0],
                "next_row": new_cases[[i for i, c in enumerate(new_cases)
                                       if c[0].startswith("r92_")][-1] + 1][0]}

# ---------------------------------------------------------------- 2. tables
tree = ast.parse(src)
classify_src = None
cases_tbl, exp_err, req_err = {}, {}, {}
for n in ast.walk(tree):
    if isinstance(n, ast.FunctionDef) and n.name == "classify_process":
        classify_src = ast.get_source_segment(src, n)
    if isinstance(n, ast.Dict):
        keys = [k.value for k in n.keys if isinstance(k, ast.Constant)]
        if "r92_tilemap_atlas" in keys:
            exp_err = {k.value: ast.literal_eval(v) for k, v in zip(n.keys, n.values)
                       if isinstance(k, ast.Constant) and k.value.startswith("r92_")}
        if "nav_lattice_teardown_crash" in keys and "geo2d_lattice_lineempty" in keys:
            req_err = {k.value: ast.literal_eval(v) for k, v in zip(n.keys, n.values)
                       if isinstance(k, ast.Constant) and k.value.startswith("r92_")}
out["classify_process_segment_sha256"] = hashlib.sha256(classify_src.encode()).hexdigest()
ns = {}
exec("import re\n" + classify_src, ns)
classify = ns["classify_process"]
rows = {c[0]: {"flags": c[2], "exit": c[3], "sig": c[4]} for c in new_cases
        if c[0].startswith("r92_")}
out["r92_rows"] = len(rows)
out["r92_allowlisted_rows"] = sorted(exp_err)
out["r92_required_stderr_rows"] = sorted(req_err)
out["expected_errors_total"] = sum(len(v) for v in exp_err.values())

# ---------------------------------------------------------------- 3. envelope shape
envelopes = {}
for name, row in rows.items():
    sig = row["sig"]
    if isinstance(sig, (tuple, list)):
        base = sig[0]
        diffs = []
        for other in sig[1:]:
            a, b = base.split(), other.split()
            diffs.append([f"{x}->{y}" for x, y in zip(a, b) if x != y])
        envelopes[name] = {"payloads": len(sig), "token_counts": [len(base.split()),
                                                                  *[len(o.split()) for o in sig[1:]]],
                           "token_diffs": diffs}
out["envelopes"] = envelopes

# volatile-token scan over every pinned token
VOLATILE = ("settle", "iter", "ladder", "first_reach", "walk_steps", "reached_at",
            "first_reachable", "iter_b=", "link_iter", "gate=", "chg_iter", "dis_same",
            "fwd_disabled_same", "frame", "tick", "usec", "msec", "time", "elapsed")
hits = []
for name, row in rows.items():
    sigs = row["sig"] if isinstance(row["sig"], (tuple, list)) else (row["sig"],)
    for sig in sigs:
        for tok in sig.split():
            if any(v in tok for v in VOLATILE):
                hits.append((name, tok))
out["volatile_token_hits"] = hits

# ---------------------------------------------------------------- 4. census over seat receipts
RUNS = SEAT / "runs"
receipts = {}
for p in sorted(RUNS.glob("fresh.*.rc")):
    stem = p.name[:-3]
    arm = stem.split(".")[1]
    receipts.setdefault(arm, []).append(stem)

def merged(stem):
    return (RUNS / f"{stem}.out").read_text() + (RUNS / f"{stem}.err").read_text()

census = []
for case, entries in sorted(exp_err.items()):
    arm = case.replace("r92_tilemap_", "").replace("_crash", "")
    arm = "nullts" if case.endswith("nullts_crash") else arm
    rec = {"case": case, "entries": [], "any_entry_matched": False}
    for entry in entries:
        matched = []
        for stem in receipts.get(arm, []):
            for line in merged(stem).splitlines():
                s = line.strip()
                ok = (s == entry) or (entry.endswith(",") and s.startswith(entry)
                                      and s.count("ERROR:") == 1)
                if ok:
                    matched.append(stem)
        rec["entries"].append({"entry": entry, "matched_receipts": len(matched),
                               "dead_in_run": not matched})
    rec["any_entry_matched"] = any(not e["dead_in_run"] for e in rec["entries"])
    census.append(rec)
out["census"] = census
out["dead_entries"] = [f"{r['case']}:{e['entry'][:60]}" for r in census
                       for e in r["entries"] if e["dead_in_run"]]
out["r92_expected_errors_all_matched"] = all(
    not e["dead_in_run"] for r in census for e in r["entries"])

# ---------------------------------------------------------------- 5. nullts stream binding
nl = {"fragments": req_err.get("r92_tilemap_nullts_crash", [])}
nl["per_rep"] = []
for stem in receipts.get("nullts", []):
    o, e = (RUNS / f"{stem}.out").read_text(), (RUNS / f"{stem}.err").read_text()
    nl["per_rep"].append({
        "stem": stem,
        "rc": int((RUNS / f"{stem}.rc").read_text().strip()),
        "sig_on_stdout": "R92 nullts about_to_call_tile_data=1" in o,
        "frag_on_stdout": [f in o for f in nl["fragments"]],
        "frag_on_stderr": [f in e for f in nl["fragments"]],
        "pass_line_absent": "PASS tilemap_lattice" not in o})
out["nullts"] = nl

# ---------------------------------------------------------------- 6. gate wiring
gate_src = None
for n in ast.walk(tree):
    if isinstance(n, ast.Dict):
        for k, v in zip(n.keys, n.values):
            if isinstance(k, ast.Constant) and k.value == "r92_expected_errors_all_matched":
                gate_src = ast.unparse(v)
out["gate_expr"] = gate_src
out["gate_in_sf_discriminations"] = gate_src is not None
out["sf_meta_ok_expr"] = "all(sf_discriminations.values())" in src
out["r92_prefix_covers_all_rows"] = all(r.startswith("r92_") for r in rows)

print(json.dumps(out, indent=1))
(SEAT / "audit.json").write_text(json.dumps(out, indent=1))
