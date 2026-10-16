#!/usr/bin/env python3
"""r95-scribe static custody audit — COMMITTED tree only (HEAD bytes).

Read-only: never writes into the repo tree outside corpus/live/r95-scribe/.
"""
import ast
import hashlib
import json
import os
import re
import subprocess
import sys
from pathlib import Path

REPO = Path("/home/vgpnk/Projects/shokunin/game-dev-2d-shokunin")
OUT = REPO / "corpus/live/r95-scribe/audit"
# the audited landing commit (HEAD may advance under concurrent lanes)
AUDITED = "9cd475078dfb8c7df1d394c68d81a1dce14d585b"


def sh(*args):
    return subprocess.run(args, cwd=REPO, capture_output=True, text=True)


def blob(path):
    r = sh("git", "show", f"{AUDITED}:{path}")
    assert r.returncode == 0, (path, r.stderr)
    return r.stdout


def sha(text_or_bytes):
    if isinstance(text_or_bytes, str):
        text_or_bytes = text_or_bytes.encode()
    return hashlib.sha256(text_or_bytes).hexdigest()


def file_sha(p):
    return sha(Path(p).read_bytes())


def worktree_sha(p):
    return sha((REPO / p).read_bytes())


report = {}

# ---------------------------------------------------------------- identity
head = sh("git", "rev-parse", "HEAD").stdout.strip()
parent = sh("git", "rev-parse", f"{AUDITED}~1").stdout.strip()
report_head_now = head
porcelain_uno = sh("git", "status", "--porcelain", "-uno").stdout
report["head"] = head
report["audited_commit"] = AUDITED
report["head_at_audit_start"] = AUDITED
report["parent"] = parent
report["porcelain_uno_empty"] = porcelain_uno == ""
report["porcelain_uno"] = porcelain_uno

numstat = sh("git", "show", "--numstat", "--format=%H", AUDITED).stdout.strip().splitlines()
report["numstat"] = numstat

# insertion-only proof for run_battery.py vs HEAD~1
old = blob("corpus/fixtures/run_battery.py")  # audited commit
new = sh("git", "show", f"{AUDITED}~1:corpus/fixtures/run_battery.py").stdout
import difflib

sm = difflib.SequenceMatcher(None, old.splitlines(), new.splitlines(), autojunk=False)
report["run_battery_vs_parent"] = {
    "head_lines": len(old.splitlines()),
    "parent_lines": len(new.splitlines()),
    "opcodes": [
        {"tag": op[0], "head": [op[1], op[2]], "parent": [op[3], op[4]]}
        for op in sm.get_opcodes() if op[0] != "equal"
    ],
}

# ------------------------------------------------------- landing blobs
landing = [
    "corpus/fixtures/dss_lattice.gd",
    "corpus/fixtures/r95b_order.gd",
    "corpus/fixtures/run_battery.py",
    "reports/round-95/r95-author.md",
    "corpus/fixtures/project.godot",
]
report["landing"] = {}
for p in landing:
    b = blob(p)
    report["landing"][p] = {
        "blob_sha256": sha(b),
        "lines": len(b.splitlines()),
        "worktree_sha256": worktree_sha(p),
        "identical_to_worktree": worktree_sha(p) == sha(b),
        "blob_sha256_at_current_head": sha(sh("git", "show", f"HEAD:{p}").stdout) if sh("git", "cat-file", "-e", f"HEAD:{p}").returncode == 0 else None,
        "tracked": bool(sh("git", "ls-files", "--error-unmatch", p).returncode == 0),
    }

# fixture vs frozen probe byte identity
pairs = [
    ("corpus/fixtures/dss_lattice.gd", "corpus/live/r95-scout/probes/dss_lattice.gd"),
    ("corpus/fixtures/r95b_order.gd", "corpus/live/r95-boundary/probes/r95b_order.gd"),
    ("corpus/live/r95-scout/proj/dss_lattice.gd", "corpus/live/r95-scout/probes/dss_lattice.gd"),
    ("corpus/live/r95-boundary/proj/r95b_order.gd", "corpus/live/r95-boundary/probes/r95b_order.gd"),
    ("corpus/live/r95-scout/proj/project.godot", "corpus/fixtures/project.godot"),
    ("corpus/live/r95-boundary/proj/project.godot", "corpus/fixtures/project.godot"),
]
report["probe_identity"] = []
for a, b in pairs:
    sa, sb = file_sha(REPO / a), file_sha(REPO / b)
    report["probe_identity"].append({"a": a, "b": b, "sha_a": sa, "sha_b": sb, "equal": sa == sb})

# ------------------------------------------------- AST of committed battery
src = old
tree = ast.parse(src)
cases = None
for node in tree.body:
    if isinstance(node, ast.Assign):
        for t in node.targets:
            if isinstance(t, ast.Name) and t.id == "CASES":
                cases = node.value.elts
assert cases is not None
report["cases_count"] = len(cases)
report["cases"] = []
for c in cases:
    vals = tuple(ast.literal_eval(e) for e in c.elts)
    report["cases"].append(vals)

r95_cases = [(i, v) for i, v in enumerate(report["cases"])
             if str(v[0]).startswith(("dss_lattice_", "r95b_order_"))]
r95_vals = [v for _, v in r95_cases]
idx = [i for i, _ in r95_cases]
report["r95_index_range"] = [min(idx), max(idx)] if idx else None
report["r95_contiguous"] = idx == list(range(min(idx), max(idx) + 1)) if idx else None
report["r95_prev_case"] = report["cases"][min(idx) - 1][0] if idx else None
report["r95_next_case"] = report["cases"][max(idx) + 1][0] if idx else None
report["r95_split"] = {
    "dss_lattice": sum(1 for _, v in r95_cases if str(v[0]).startswith("dss_lattice_")),
    "r95b_order": sum(1 for _, v in r95_cases if str(v[0]).startswith("r95b_order_")),
}
report["tail_cases"] = [v[0] for v in report["cases"][max(idx) + 1:]]

# allowlists
allow = {}
for node in ast.walk(tree):
    if isinstance(node, ast.Assign):
        for t in node.targets:
            if isinstance(t, ast.Name) and t.id in ("expected_errors", "required_stderr"):
                v = node.value
                inner = None
                if isinstance(v, ast.Dict):
                    inner = v
                elif (isinstance(v, ast.Call) and isinstance(v.func, ast.Attribute)
                      and isinstance(v.func.value, ast.Dict)):
                    inner = v.func.value
                if inner is not None:
                    allow[t.id] = (node.lineno, inner)
report["allowlists"] = {}
for name, (lineno, node) in allow.items():
    keys = [ast.literal_eval(k) for k in node.keys]
    report["allowlists"][name] = {
        "line": lineno,
        "count": len(keys),
        "r95_keys": [k for k in keys if str(k).startswith(("dss_lattice_", "r95b_order_"))],
        "nonempty": sum(1 for k, v in zip(node.keys, node.values)
                        if not (isinstance(v, ast.Tuple) and not v.elts)),
        "keys": keys,
    }

# gate expression
gate = None
for node in ast.walk(tree):
    if isinstance(node, ast.Assign):
        for t in node.targets:
            if isinstance(t, ast.Name) and t.id == "sf_discriminations":
                for k, v in zip(node.value.keys, node.value.values):
                    if ast.literal_eval(k) == "r95_expected_errors_all_matched":
                        gate = ast.unparse(v)
report["r95_gate_expr"] = gate
report["r95_gate_lines"] = [i + 1 for i, l in enumerate(src.splitlines())
                            if "r95_expected_errors_all_matched" in l]

# ------------------------------------------------- scout ROWS / ROWS_PREFIX
scout_rows_src = (REPO / "corpus/live/r95-scout/author-rows.py.txt").read_text()
stree = ast.parse(scout_rows_src)
srows, sprefix = None, None
for node in stree.body:
    if isinstance(node, ast.Assign):
        for t in node.targets:
            if isinstance(t, ast.Name) and t.id == "ROWS":
                srows = [ast.literal_eval(e) for e in node.value.elts]
            if isinstance(t, ast.Name) and t.id == "ROWS_PREFIX":
                sprefix = [ast.literal_eval(e) for e in node.value.elts]
report["scout_rows"] = {"ROWS": len(srows), "ROWS_PREFIX": len(sprefix)}

committed_by_case = {v[0]: v for v in report["cases"]}
match_rows, match_prefix, mismatch = [], [], []
for row in srows:
    c = committed_by_case.get(row[0])
    if c == row:
        match_rows.append(row[0])
    else:
        mismatch.append({"case": row[0], "equal": False})
for row in sprefix:
    c = committed_by_case.get(row[0])
    if c == row:
        match_prefix.append(row[0])
report["scout_match"] = {
    "rows_equal": len(match_rows), "prefix_equal": len(match_prefix),
    "rows_total": len(srows), "prefix_total": len(sprefix),
    "committed_equals_prefix_set": sorted(
        [v[0] for v in r95_vals if str(v[0]).startswith("dss_lattice_")]) == sorted(r[0] for r in sprefix),
    "prefix_shorter_than_full": [
        r[0] for r in srows
        if len(next(p for p in sprefix if p[0] == r[0])[4]) < len(r[4])],
}

# --------------------------------------------- boundary receipts census
runs_root = REPO / "corpus/live/r95-boundary/runs"
receipts = []
for batch in sorted(p for p in runs_root.iterdir() if p.is_dir()):
    for out in sorted(batch.glob("*.out")):
        cell = out.name.rsplit(".rep", 1)[0]
        rep = out.name.split(".rep")[1].split(".")[0]
        err = out.with_suffix(".err")
        rc = out.with_suffix(".rc")
        receipts.append({
            "batch": batch.name, "cell": cell, "rep": rep,
            "out": str(out.relative_to(REPO)),
            "rc": int(rc.read_text().strip()) if rc.exists() else None,
            "err_bytes": err.stat().st_size if err.exists() else None,
            "text": out.read_text(errors="replace"),
        })
report["boundary_receipts"] = {
    "runs": len(receipts),
    "batches": sorted({r["batch"] for r in receipts}),
    "rc_nonzero": [r["out"] for r in receipts if r["rc"] != 0],
    "err_nonempty": [r["out"] for r in receipts if r["err_bytes"]],
    "timeouts_137": [r["out"] for r in receipts if r["rc"] == 137],
}

# per-cell PASS-line uniqueness (whole lines that start with 'PASS r95b_order')
cell_sigs = {}
for r in receipts:
    for line in r["text"].splitlines():
        if line.startswith("PASS r95b_order"):
            cell_sigs.setdefault(r["cell"], set()).add(line)
report["boundary_cell_sig_uniq"] = {c: len(s) for c, s in sorted(cell_sigs.items())}
report["boundary_unstable_cells"] = {c: sorted(s) for c, s in cell_sigs.items() if len(s) > 1}

# the 35 authored r95b signatures must be whole PASS lines of their cell receipts
sig_binding = []
for v in r95_vals:
    case, script, flags, exit_code, sig = v
    if not str(case).startswith("r95b_order_"):
        continue
    cell = None
    m = re.search(r"--arm=([a-z0-9_]+)", " ".join(flags))
    arm = m.group(1) if m else None
    # cell naming in the boundary runs: arm-derived; find receipts whose PASS line matches
    hits = [r["out"] for r in receipts if sig in r["text"].splitlines()]
    prefix_hits = [r["out"] for r in receipts if sig in r["text"]]
    sig_binding.append({
        "case": case, "arm": arm, "whole_line_hits": len(hits),
        "substring_only_hits": len(prefix_hits) - len(hits),
        "sample": hits[0] if hits else None,
    })
report["boundary_sig_binding"] = {
    "bound": sum(1 for s in sig_binding if s["whole_line_hits"]),
    "total": len(sig_binding),
    "unbound": [s for s in sig_binding if not s["whole_line_hits"]],
}

# dss_lattice signatures: bound to scout receipts?
scout_receipts = []
for sub in ["runs", "runs/loadtest", "runs/alt"]:
    d = REPO / "corpus/live/r95-scout" / sub
    if d.is_dir():
        for out in sorted(d.glob("*.out")):
            scout_receipts.append({"out": str(out.relative_to(REPO)),
                                   "text": out.read_text(errors="replace")})
report["scout_receipts"] = {"runs": len(scout_receipts)}
scout_binding = []
for v in r95_vals:
    case, script, flags, exit_code, sig = v
    if not str(case).startswith("dss_lattice_"):
        continue
    hits = [r["out"] for r in scout_receipts if sig in r["text"]]
    scout_binding.append({"case": case, "hits": len(hits), "sample": hits[0] if hits else None})
report["scout_sig_binding"] = {
    "bound": sum(1 for s in scout_binding if s["hits"]),
    "total": len(scout_binding),
    "unbound": [s for s in scout_binding if not s["hits"]],
}

# ------------------------------------------------------------ manifests
def verify_manifest(lane):
    lane_dir = REPO / "corpus/live" / lane
    man = lane_dir / "manifest.sha256"
    lines = [l for l in man.read_text().splitlines() if l.strip()]
    listed = {}
    raw = []
    for l in lines:
        h, p = l.split(None, 1)
        raw.append(p.strip())
        p = p.strip()
        if p.startswith("*"):
            p = p[1:]
        if p.startswith("./"):
            p = p[2:]
        pref = f"corpus/live/{lane}/"
        if p.startswith(pref):
            p = p[len(pref):]
        listed[p] = h
    missing, mismatched = [], []
    for p, h in listed.items():
        f = lane_dir / p
        if not f.exists():
            missing.append(p)
            continue
        if file_sha(f) != h:
            mismatched.append(p)
    on_disk = set()
    for root, dirs, files in os.walk(lane_dir):
        for f in files:
            fp = Path(root) / f
            rel = str(fp.relative_to(lane_dir))
            on_disk.add(rel)
    unlisted = sorted(p for p in on_disk if p not in listed and p != "manifest.sha256")
    tracked = sh("git", "ls-files", f"corpus/live/{lane}").stdout.splitlines()
    return {
        "path_style": ("repo-relative" if raw and raw[0].startswith("corpus/")
                       else "lane-relative"),
        "entries": len(listed), "missing": missing, "mismatched": mismatched,
        "files_on_disk": len(on_disk), "unlisted": unlisted[:20], "unlisted_count": len(unlisted),
        "self_excluded": "manifest.sha256" not in listed,
        "tracked_files": len(tracked),
        "tracked_missing_on_disk": [p for p in tracked if not (REPO / p).exists()],
    }


report["manifests"] = {
    "r95-scout": verify_manifest("r95-scout"),
    "r95-boundary": verify_manifest("r95-boundary"),
}

# ------------------------------------------------------- author runs check
author_runs = []
for ts in ["20261016T055703426158Z", "20261016T060430025246Z",
           "20261016T064148780406Z", "20261016T064742446822Z",
           "20261016T065335715243Z", "20261016T065922894811Z"]:
    p = REPO / "corpus/live/runs" / ts / "verdicts.json"
    if not p.exists():
        author_runs.append({"ts": ts, "present": False})
        continue
    v = json.loads(p.read_text())
    res = v.get("results", [])
    fails = [r for r in res if r.get("verdict") != "PASS"]
    r95 = [r for r in res if str(r.get("case", "")).startswith(("dss_lattice_", "r95b_order_"))]
    meta = next((r for r in res if r.get("case") == "probe_error_clause_surface"), {})
    disc = meta.get("discriminations", {})
    census = meta.get("census", {})
    author_runs.append({
        "ts": ts, "present": True, "rows": len(res), "verdict": v.get("verdict"),
        "pass": sum(1 for r in res if r.get("verdict") == "PASS"),
        "fail_cases": [r.get("case") for r in fails],
        "r95_rows": len(r95), "r95_pass": sum(1 for r in r95 if r.get("verdict") == "PASS"),
        "gate": disc.get("r95_expected_errors_all_matched"),
        "gate_keys_span": [k for k in disc if k.endswith("_expected_errors_all_matched")],
        "dead_entry_count": census.get("dead_entry_count"),
        "rows_with_expected_errors": census.get("rows_with_expected_errors"),
        "meta_row_verdict": meta.get("verdict"),
        "scratch": v.get("scratch"),
        "godot": v.get("godot"),
    })
report["author_runs"] = author_runs

# author-claimed fixture sha in verdicts (scratch copy)
report["author_scratch_fixture_shas"] = {}
for r in author_runs:
    if r.get("present") and r.get("scratch"):
        for name in ("dss_lattice.gd", "r95b_order.gd"):
            fp = Path(r["scratch"]) / name
            report["author_scratch_fixture_shas"].setdefault(r["ts"], {})[name] = (
                file_sha(fp) if fp.exists() else None)

# --------------------------------------------- scout/boundary report claims
report["scout_report_claims"] = {
    "report_lines": len((REPO / "reports/round-95/r95-scout.md").read_text().splitlines()),
    "report_blob_sha": sha(blob("reports/round-95/r95-scout.md")),
    "report_tracked": bool(sh("git", "ls-files", "--error-unmatch",
                              "reports/round-95/r95-scout.md").returncode == 0),
}
report["boundary_report_claims"] = {
    "report_lines": len((REPO / "reports/round-95/r95-boundary.md").read_text().splitlines()),
    "report_blob_sha": sha(blob("reports/round-95/r95-boundary.md")),
    "report_tracked": bool(sh("git", "ls-files", "--error-unmatch",
                              "reports/round-95/r95-boundary.md").returncode == 0),
}

report["late_window"] = {
    "head_now": head,
    "head_now_equals_audited": head == AUDITED,
    "diff_name_status_audited_to_now": sh("git", "diff", "--name-status", AUDITED, head).stdout.splitlines()[:400],
    "r95_artefacts_unchanged": {
        p: sha(sh("git", "show", f"{AUDITED}:{p}").stdout) == sha(sh("git", "show", f"{head}:{p}").stdout)
        for p in landing + ["reports/round-95/r95-scout.md", "reports/round-95/r95-boundary.md"]
    },
}
OUT.mkdir(parents=True, exist_ok=True)
(OUT / "static_audit.json").write_text(json.dumps(report, indent=2, sort_keys=True))
print(json.dumps({k: v for k, v in report.items()
                  if k not in ("cases", "allowlists")}, indent=2, sort_keys=True)[:12000])
