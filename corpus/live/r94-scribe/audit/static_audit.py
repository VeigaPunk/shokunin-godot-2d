#!/usr/bin/env python3
"""r94 scribe static custody audit — committed tree only (HEAD c7228893).

Recomputes, from `git show HEAD:` bytes and on-disk lane files:
  1. landing identity: worktree sha256 == HEAD blob sha256 for every landing file
  2. commit shape: numstat of c7228893 (expect 3 files, 0 deletions)
  3. run_battery.py HEAD vs HEAD~1: insertion-only proof (no deleted lines)
  4. CASES / row arithmetic via AST (counts, r94 contiguity, tail adjacency)
  5. expected_errors / required_stderr key census (no r94_ keys)
  6. floor gate presence + prefix scope
  7. fixture vs frozen scout probe: non-comment code-line diff (expect exactly 4)
  8. lane manifest completeness (scout, boundary) + git tracking inventory
  9. scout evidence-integrity recompute (RECEIPTS.md hash contradiction, mtimes)
 10. author battery runs: verdict/rows/gate/scratch-fixture identity

Writes only JSON/text under corpus/live/r94-scribe/audit/.
"""
import ast
import difflib
import hashlib
import json
import os
import re
import subprocess
import sys
from pathlib import Path

REPO = Path("/home/vgpnk/Projects/shokunin/game-dev-2d-shokunin")
OUT = REPO / "corpus/live/r94-scribe/audit"
OUT.mkdir(parents=True, exist_ok=True)

LANDING = [
    "corpus/fixtures/particles_lattice.gd",
    "corpus/fixtures/run_battery.py",
    "corpus/fixtures/project.godot",
    "reports/round-94/r94-author.md",
    "reports/round-94/r94-scout.md",
    "reports/round-94/r94-boundary.md",
]


def sh(*args):
    return subprocess.run(args, cwd=REPO, capture_output=True, text=True)


def git_show(path):
    r = subprocess.run(["git", "show", f"HEAD:{path}"], cwd=REPO,
                       capture_output=True)
    assert r.returncode == 0, path
    return r.stdout


def sha_bytes(b):
    return hashlib.sha256(b).hexdigest()


report = {}

# ---- 1. landing identity ---------------------------------------------------
ident = {}
for p in LANDING:
    wt = (REPO / p).read_bytes()
    hb = git_show(p)
    ident[p] = {
        "worktree_sha256": sha_bytes(wt),
        "head_sha256": sha_bytes(hb),
        "identical": wt == hb,
        "bytes": len(wt),
        "lines": wt.count(b"\n"),
    }
report["landing_identity"] = ident
report["landing_all_identical"] = all(v["identical"] for v in ident.values())

# ---- 2. commit shape -------------------------------------------------------
num = sh("git", "show", "--numstat", "--format=%H%n%P%n%s", "HEAD").stdout
report["head"] = sh("git", "rev-parse", "HEAD").stdout.strip()
report["head_subject"] = sh("git", "log", "-1", "--format=%s").stdout.strip()
report["head_parent"] = sh("git", "log", "-1", "--format=%P").stdout.strip()
report["numstat_head"] = [l for l in num.splitlines() if l.strip()]

# ---- 3. insertion-only vs HEAD~1 ------------------------------------------
old = subprocess.run(["git", "show", "HEAD~1:corpus/fixtures/run_battery.py"],
                     cwd=REPO, capture_output=True).stdout.decode()
new = git_show("corpus/fixtures/run_battery.py").decode()
sm = difflib.SequenceMatcher(a=old.splitlines(), b=new.splitlines(), autojunk=False)
inserted = deleted = 0
insert_blocks = []
for tag, i1, i2, j1, j2 in sm.get_opcodes():
    if tag == "insert":
        inserted += j2 - j1
        insert_blocks.append({"at_old_line": i1 + 1, "lines": j2 - j1})
    elif tag == "delete":
        deleted += i2 - i1
    elif tag == "replace":
        deleted += i2 - i1
        inserted += j2 - j1
report["run_battery_diff_vs_HEAD1"] = {
    "inserted": inserted, "deleted": deleted, "insert_blocks": insert_blocks,
    "insertion_only": deleted == 0,
}

# ---- 4/5. AST: CASES, allowlists, gate ------------------------------------
src = new
tree = ast.parse(src)
cases = None
for node in ast.walk(tree):
    if isinstance(node, ast.Assign) and getattr(node.targets[0], "id", "") == "CASES":
        cases = node.value
assert isinstance(cases, ast.List), "CASES not a list literal"
case_names = [ast.literal_eval(el.elts[0]) for el in cases.elts]
r94_idx = [i for i, n in enumerate(case_names) if n.startswith("r94_")]
r93_idx = [i for i, n in enumerate(case_names) if n.startswith("r93_")]
tail = [i for i, n in enumerate(case_names)
        if n in ("crash_spontaneous_sigabrt", "crash_self_sigkill",
                 "descendant_pipe_detached_control",
                 "descendant_pipe_forged_signature_release")]
report["cases"] = {
    "total": len(case_names),
    "r94_count": len(r94_idx),
    "r94_indices": [r94_idx[0], r94_idx[-1]] if r94_idx else None,
    "r94_contiguous": r94_idx == list(range(r94_idx[0], r94_idx[-1] + 1)) if r94_idx else None,
    "r94_names": [case_names[i] for i in r94_idx],
    "r93_last_index": r93_idx[-1] if r93_idx else None,
    "tail_indices": tail,
    "tail_after_r94": all(i > r94_idx[-1] for i in tail),
    "r94_tuples_parse": len(cases.elts) == len(case_names),
}

# expected_errors / required_stderr dict literals (assigned conditionally)
allow = {"expected_errors": None, "required_stderr": None}
def _dict_from(node):
    """Unwrap `{...}.get(name, ())` / bare dict literals."""
    if isinstance(node, ast.Dict):
        return node
    if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) \
            and isinstance(node.func.value, ast.Dict):
        return node.func.value
    return None


for node in ast.walk(tree):
    if isinstance(node, ast.Assign) and len(node.targets) == 1 \
            and isinstance(node.targets[0], ast.Name) \
            and node.targets[0].id in allow:
        d = _dict_from(node.value)
        if d is not None:
            allow[node.targets[0].id] = [ast.literal_eval(k) for k in d.keys]
report["allowlists"] = {
    "expected_errors_keys": len(allow["expected_errors"] or []),
    "expected_errors_r94_keys": [k for k in (allow["expected_errors"] or []) if k.startswith("r94_")],
    "required_stderr_keys": allow["required_stderr"],
    "required_stderr_r94_keys": [k for k in (allow["required_stderr"] or []) if k.startswith("r94_")],
}

gate_src = src
report["floor_gate"] = {
    "present": "r94_expected_errors_all_matched" in gate_src,
    "prefix_scoped": 'r["case"].startswith("r94_")' in gate_src,
    "all_round_gates": sorted(set(re.findall(r'"(r\d+_expected_errors_all_matched|phys2d_expected_errors_all_matched)"', gate_src))),
}

# ---- 7. fixture vs frozen probe: code-line diff ---------------------------
probe = (REPO / "corpus/live/r94-scout/probes/particles_lattice.gd").read_text().splitlines()
fixture = (REPO / "corpus/fixtures/particles_lattice.gd").read_text().splitlines()


def code_lines(lines):
    out = []
    for i, l in enumerate(lines):
        s = l.strip()
        if s.startswith("#") or not s:
            continue
        out.append((i + 1, l))
    return out


cl_p, cl_f = code_lines(probe), code_lines(fixture)
pcode = [l for _, l in cl_p]
fcode = [l for _, l in cl_f]
smat = difflib.SequenceMatcher(a=pcode, b=fcode, autojunk=False)
code_diff = []
for tag, i1, i2, j1, j2 in smat.get_opcodes():
    if tag == "equal":
        continue
    code_diff.append({"tag": tag,
                      "probe_lines": [cl_p[i][0] for i in range(i1, i2)],
                      "fixture_lines": [cl_f[j][0] for j in range(j1, j2)],
                      "probe": pcode[i1:i2], "fixture": fcode[j1:j2]})
report["fixture_vs_probe"] = {
    "probe_lines": len(probe), "fixture_lines": len(fixture),
    "probe_code_lines": len(pcode), "fixture_code_lines": len(fcode),
    "code_diff_blocks": code_diff,
    "code_diff_line_count": sum(len(d["probe"]) + len(d["fixture"]) for d in code_diff),
}

# ---- 8. manifests + tracking ---------------------------------------------
def manifest_audit(lane):
    mf = REPO / f"corpus/live/{lane}/manifest.sha256"
    entries = []
    for line in mf.read_text().splitlines():
        if not line.strip():
            continue
        h, p = line.split(None, 1)
        entries.append((h, p.lstrip("./")))
    root = REPO / f"corpus/live/{lane}"
    on_disk = sorted(
        str(p.relative_to(root)) for p in root.rglob("*") if p.is_file())
    listed = sorted(p for _, p in entries)
    missing_files = [p for p in listed if not (REPO / f"corpus/live/{lane}" / p).is_file()]
    unlisted = [p for p in on_disk if p not in set(listed) and p != "manifest.sha256"]
    bad_hash = []
    for h, p in entries:
        fp = REPO / f"corpus/live/{lane}" / p
        if fp.is_file() and sha_bytes(fp.read_bytes()) != h:
            bad_hash.append(p)
    tracked = subprocess.run(["git", "ls-files", f"corpus/live/{lane}"],
                             cwd=REPO, capture_output=True, text=True).stdout.split()
    return {"entries": len(entries), "on_disk_files": len(on_disk),
            "missing_listed": missing_files, "unlisted_files": unlisted,
            "hash_mismatches": bad_hash, "tracked_files": len(tracked),
            "untracked_on_disk": len(on_disk) - len(tracked)}


report["manifests"] = {lane: manifest_audit(lane) for lane in ("r94-scout", "r94-boundary")}

# ---- 9. scout evidence integrity ------------------------------------------
scout = REPO / "corpus/live/r94-scout"
probe_mtime = (scout / "probes/particles_lattice.gd").stat().st_mtime
canon = sorted((scout / "runs").glob("r94_particles_*.rep*.out"))
load = sorted((scout / "runs/loadtest").glob("r94_particles_*.rep*.out"))
pre = [f for f in canon + load if f.stat().st_mtime < probe_mtime]
receipts_md = (scout / "RECEIPTS.md").read_text()
hash_in_receipts = re.search(r"`sha256 (09dd7723[0-9a-f]*…)`", receipts_md)
manifest_probe = re.search(r"^([0-9a-f]{64})  \./probes/particles_lattice\.gd$",
                           (scout / "manifest.sha256").read_text(), re.M)
report["scout_evidence"] = {
    "receipts_canonical": len(canon), "receipts_loadtest": len(load),
    "probe_mtime": probe_mtime,
    "predate_freeze": len(pre),
    "post_freeze": [f.name for f in canon + load if f.stat().st_mtime >= probe_mtime],
    "receipts_md_hash_mention": hash_in_receipts.group(1) if hash_in_receipts else None,
    "manifest_probe_hash": manifest_probe.group(1) if manifest_probe else None,
    "actual_probe_hash": sha_bytes((scout / "probes/particles_lattice.gd").read_bytes()),
}

# ---- 10. author battery runs ----------------------------------------------
runs = {}
for stamp in ("20261016T055703426158Z", "20261016T060430025246Z"):
    p = REPO / f"corpus/live/runs/{stamp}/verdicts.json"
    if not p.is_file():
        runs[stamp] = {"present": False}
        continue
    d = json.loads(p.read_text())
    rows = {r["case"]: r["verdict"] for r in d["results"]}
    meta = next(r for r in d["results"] if r["case"] == "probe_error_clause_surface")
    scratch_fixture = p.parent / "scratch" / "particles_lattice.gd"
    runs[stamp] = {
        "present": True, "verdict": d["verdict"], "n_results": len(d["results"]),
        "r94_pass": sum(1 for k, v in rows.items() if k.startswith("r94_") and v == "PASS"),
        "r94_total": sum(1 for k in rows if k.startswith("r94_")),
        "fails": [k for k, v in rows.items() if v != "PASS"],
        "gate_r94": meta["discriminations"].get("r94_expected_errors_all_matched"),
        "gate_r93": meta["discriminations"].get("r93_expected_errors_all_matched"),
        "dead_entry_count": meta["census"]["dead_entry_count"],
        "rows_with_expected_errors": meta["census"]["rows_with_expected_errors"],
        "scratch_fixture_sha": sha_bytes(scratch_fixture.read_bytes()) if scratch_fixture.is_file() else None,
    }
report["author_runs"] = runs

# ---- 11. foreign worktree modifications (concurrent lanes) -----------------
# A late-window r95-author lane inserted its block into the *worktree*
# run_battery.py; the committed r94 content must be provably untouched.
wt_src = (REPO / "corpus/fixtures/run_battery.py").read_text()
gate_pat = re.compile(r'"r94_expected_errors_all_matched":\s*(all\(.*?\))', re.S)
head_src = git_show("corpus/fixtures/run_battery.py").decode()


def r94_tuples(src):
    t = ast.parse(src)
    c = next(n.value for n in ast.walk(t)
             if isinstance(n, ast.Assign) and getattr(n.targets[0], "id", "") == "CASES")
    return {ast.literal_eval(e)[0]: ast.literal_eval(e) for e in c.elts
            if ast.literal_eval(e)[0].startswith("r94_")}


wt_cases = ast.parse(wt_src)
wt_names = [ast.literal_eval(e)[0] for e in
            next(n.value for n in ast.walk(wt_cases)
                 if isinstance(n, ast.Assign) and getattr(n.targets[0], "id", "") == "CASES").elts]
head_names = [ast.literal_eval(e)[0] for e in
              next(n.value for n in ast.walk(ast.parse(head_src))
                   if isinstance(n, ast.Assign) and getattr(n.targets[0], "id", "") == "CASES").elts]
new_rows = [x for x in wt_names if x not in set(head_names)]
report["foreign_worktree_modification"] = {
    "git_status_uno": sh("git", "status", "--porcelain", "-uno").stdout.strip().splitlines(),
    "run_battery_mtime": (REPO / "corpus/fixtures/run_battery.py").stat().st_mtime,
    "run_battery_numstat_vs_head": sh("git", "diff", "--numstat",
                                      "corpus/fixtures/run_battery.py").stdout.strip(),
    "worktree_cases_total": len(wt_names),
    "head_cases_total": len(head_names),
    "new_rows_in_worktree": len(new_rows),
    "new_row_prefixes": sorted({x.split("_", 1)[0] for x in new_rows}),
    "r94_tuples_identical": r94_tuples(head_src) == r94_tuples(wt_src),
    "r94_gate_comprehension_identical": gate_pat.search(head_src).group(1) == gate_pat.search(wt_src).group(1),
    "r94_prefix_scope_present": 'r["case"].startswith("r94_")' in wt_src,
    "crash_tail_last": wt_names[-4:],
    "only_nonidentical_landing_file": [k for k, v in ident.items() if not v["identical"]],
}
report["foreign_worktree_modification"]["is_foreign"] = True

(OUT / "static_audit.json").write_text(json.dumps(report, indent=2) + "\n")

# human summary
print(json.dumps({k: v for k, v in report.items() if k != "landing_identity"}, indent=2)[:6000])
print("\nlanding_identity:")
for k, v in report["landing_identity"].items():
    print(f"  {v['identical']!s:5} {v['worktree_sha256'][:16]} {k}")
