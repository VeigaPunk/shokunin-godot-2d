#!/usr/bin/env python3
"""r93-scribe static custody audit — committed tree only (HEAD 4b75151).

Re-derives, from `git show HEAD:...` bytes and the frozen dossier receipts:
  * CASES tuple inventory (count, r93 rows, contiguity, neighbours)
  * allowlist dictionaries (expected_errors / required_stderr) and their keys
  * insertion-only shape of the r93 author diff vs HEAD~1
  * fixture byte-identity: worktree == HEAD == frozen probes
  * manifest completeness for r93-scout / r93-boundary / r93-author
  * floor gate presence/scope
Writes JSON only under corpus/live/r93-scribe/audit/.
"""
import ast
import hashlib
import json
import subprocess
import sys
from pathlib import Path

REPO = Path("/home/vgpnk/Projects/shokunin/game-dev-2d-shokunin")
OUT = REPO / "corpus/live/r93-scribe/audit/static_audit.json"


def git(*args, binary=False):
    p = subprocess.run(["git", "-C", str(REPO)] + list(args),
                       capture_output=True)
    if p.returncode != 0:
        raise RuntimeError(f"git {' '.join(args)} failed: {p.stderr.decode()}")
    return p.stdout if binary else p.stdout.decode()


def sha(b):
    return hashlib.sha256(b).hexdigest()


def sha_file(p):
    return sha(Path(p).read_bytes())


def walk_files(root: Path):
    out = set()
    for p in root.rglob("*"):
        if p.is_file():
            out.add(str(p.relative_to(root)))
    return out


report = {}

# ---- 1. CASES inventory from HEAD bytes --------------------------------
head_src = git("show", "HEAD:corpus/fixtures/run_battery.py")
tree = ast.parse(head_src)
cases = None
for node in ast.walk(tree):
    if isinstance(node, ast.Assign):
        for t in node.targets:
            if isinstance(t, ast.Name) and t.id == "CASES":
                cases = ast.literal_eval(node.value)
assert cases is not None, "CASES not found"
report["cases_total"] = len(cases)
names = [c[0] for c in cases]
r93 = [c for c in cases if c[0].startswith("r93_")]
report["r93_rows"] = [
    {"case": c[0], "fixture": c[1], "args": list(c[2]), "exit": c[3],
     "signature_is_envelope": isinstance(c[4], (tuple, list)),
     "signature_len": len(c[4]) if isinstance(c[4], str) else len(c[4])}
    for c in r93]
report["r93_row_count"] = len(r93)
idx = [i for i, n in enumerate(names) if n.startswith("r93_")]
report["r93_index_first"], report["r93_index_last"] = idx[0], idx[-1]
report["r93_contiguous"] = idx == list(range(idx[0], idx[-1] + 1))
report["neighbour_before"] = names[idx[0] - 1]
report["neighbour_after"] = names[idx[-1] + 1]
report["r93_fixtures"] = sorted({c[1] for c in r93})
report["r93_expected_exit_values"] = sorted({c[3] for c in r93})
# every r93 signature must be a non-empty string (no envelopes claimed)
report["r93_all_signatures_plain_strings"] = all(
    isinstance(c[4], str) and c[4] for c in r93)
report["r93_signature_sha_joined"] = sha(
    "\n".join(c[0] + "|" + (c[4] if isinstance(c[4], str) else repr(c[4]))
              for c in r93).encode())

# tail after r93 must still contain the crash/descendant/meta surface
tail = names[idx[-1] + 1:]
report["tail_after_r93"] = tail
report["r93_rows_by_fixture"] = {}
for c in r93:
    report["r93_rows_by_fixture"].setdefault(c[1], []).append(c[0])

# ---- 2. allowlist dictionaries -----------------------------------------
# expected_errors / required_stderr are built inside execute(); extract every
# dict literal assigned to those names, merge keys.
allow = {"expected_errors": {}, "required_stderr": {}}
for node in ast.walk(tree):
    if isinstance(node, ast.Assign):
        for t in node.targets:
            if isinstance(t, ast.Name) and t.id in allow:
                v = node.value
                if isinstance(v, ast.Call) and isinstance(v.func, ast.Attribute) \
                        and v.func.attr == "get" and isinstance(v.func.value, ast.Dict):
                    v = v.func.value  # the dict literal is the .get() receiver
                if isinstance(v, ast.Dict):
                    for k, val in zip(v.keys, v.values):
                        key = ast.literal_eval(k)
                        allow[t.id][key] = ast.literal_eval(val)
report["expected_errors_cases"] = sorted(allow["expected_errors"])
report["expected_errors_entry_lines"] = sum(
    len(v) for v in allow["expected_errors"].values())
report["required_stderr_cases"] = sorted(allow["required_stderr"])
report["required_stderr_entry_lines"] = sum(
    len(v) for v in allow["required_stderr"].values())
report["r93_allowlist_keys"] = sorted(
    [k for k in allow["expected_errors"] if k.startswith("r93_")] +
    [k for k in allow["required_stderr"] if k.startswith("r93_")])
# per-round key census (named-by-round shape)
report["allowlist_keys_by_prefix"] = {}
for name, d in allow.items():
    for k in d:
        pre = k.split("_")[0]
        report["allowlist_keys_by_prefix"].setdefault(name, {}).setdefault(pre, 0)
        report["allowlist_keys_by_prefix"][name][pre] += 1

# ---- 3. floor gate text ------------------------------------------------
gate_ok = '"r93_expected_errors_all_matched"' in head_src
report["r93_gate_present"] = gate_ok
# extract the gate expression body
start = head_src.find('"r93_expected_errors_all_matched"')
report["r93_gate_snippet"] = head_src[start:start + 220]

# ---- 4. insertion-only diff vs HEAD~1 ----------------------------------
diff = git("diff", "--numstat", "HEAD~1", "HEAD", "--", "corpus/fixtures/")
report["fixture_numstat"] = [l.split("\t") for l in diff.strip().splitlines()]
prev_src = git("show", "HEAD~1:corpus/fixtures/run_battery.py")
prev_lines = prev_src.splitlines()
head_lines = head_src.splitlines()
import difflib
sm = difflib.SequenceMatcher(a=prev_lines, b=head_lines, autojunk=False)
ops = sm.get_opcodes()
report["diff_opcodes"] = [
    {"op": op, "a": [i1, i2], "b": [j1, j2],
     "n_a": i2 - i1, "n_b": j2 - j1}
    for op, i1, i2, j1, j2 in ops if op != "equal"]
report["diff_deletions"] = sum(i2 - i1 for op, i1, i2, j1, j2 in ops
                               if op != "equal")
report["diff_insertions"] = sum(j2 - j1 for op, i1, i2, j1, j2 in ops
                                if op != "equal")
# inserted block must be exactly the r93 comment+rows region
ins = [o for o in report["diff_opcodes"] if o["op"] == "insert"]
report["insert_blocks"] = ins
if ins:
    blk = head_lines[ins[0]["b"][0]:ins[0]["b"][1]]
    report["insert_block_first_line"] = blk[0]
    report["insert_block_last_line"] = blk[-1]
    report["insert_block_r93_row_lines"] = sum(
        1 for l in blk if l.strip().startswith("('r93_"))
report["r93_rows_present_in_prev"] = sum(
    1 for n in names if n.startswith("r93_")
    and n in "\n".join(prev_lines))

# ---- 5. fixture byte-identity ------------------------------------------
pairs = [
    ("worktree", REPO / "corpus/fixtures/anim_lattice.gd",
     "HEAD:corpus/fixtures/anim_lattice.gd"),
    ("worktree", REPO / "corpus/fixtures/r93b_anim.gd",
     "HEAD:corpus/fixtures/r93b_anim.gd"),
    ("worktree", REPO / "corpus/fixtures/run_battery.py",
     "HEAD:corpus/fixtures/run_battery.py"),
    ("worktree", REPO / "corpus/fixtures/project.godot",
     "HEAD:corpus/fixtures/project.godot"),
]
report["identity"] = {}
for _, wt, spec in pairs:
    a = sha_file(wt)
    b = sha(git("show", spec, binary=True))
    report["identity"][str(wt.name)] = {"worktree": a, "head": b,
                                        "equal": a == b}
# frozen probes
probes = {
    "r93-scout/probes/anim_lattice.gd": "corpus/live/r93-scout/probes/anim_lattice.gd",
    "r93-boundary/probes/r93b_anim.gd": "corpus/live/r93-boundary/probes/r93b_anim.gd",
    "r93-boundary/probes/scout_anim_lattice.gd": "corpus/live/r93-boundary/probes/scout_anim_lattice.gd",
}
report["probes"] = {}
for label, rel in probes.items():
    h = sha_file(REPO / rel)
    report["probes"][label] = {"sha256": h}
report["probe_vs_landed"] = {
    "anim_lattice.gd": {
        "landed": sha_file(REPO / "corpus/fixtures/anim_lattice.gd"),
        "scout_probe": sha_file(REPO / "corpus/live/r93-scout/probes/anim_lattice.gd"),
        "boundary_copy": sha_file(REPO / "corpus/live/r93-boundary/probes/scout_anim_lattice.gd"),
    },
    "r93b_anim.gd": {
        "landed": sha_file(REPO / "corpus/fixtures/r93b_anim.gd"),
        "boundary_probe": sha_file(REPO / "corpus/live/r93-boundary/probes/r93b_anim.gd"),
    },
}
report["commit_files"] = [
    l for l in git("show", "--name-only", "--format=", "HEAD").splitlines() if l]
report["project_godot_touched_by_commit"] = any(
    l == "corpus/fixtures/project.godot" for l in report["commit_files"])

# ---- 6. manifest completeness ------------------------------------------
report["manifests"] = {}
for dossier in ("r93-scout", "r93-boundary", "r93-author"):
    d = REPO / "corpus/live" / dossier
    man = d / "manifest.sha256"
    listed = set()
    bad = 0
    total = 0
    for line in man.read_text().splitlines():
        if not line.strip():
            continue
        h, path = line.split("  ", 1)
        if path.startswith("./"):
            path = path[2:]
        listed.add(path)
        total += 1
        p = d / path
        if not p.is_file() or sha_file(p) != h:
            bad += 1
    on_disk = walk_files(d)
    on_disk.discard("manifest.sha256")
    report["manifests"][dossier] = {
        "entries": total, "bad": bad,
        "listed_not_on_disk": sorted(listed - on_disk)[:10],
        "on_disk_not_listed": sorted(on_disk - listed)[:10],
        "n_on_disk": len(on_disk),
    }

# ---- 7. write ----------------------------------------------------------
OUT.write_text(json.dumps(report, indent=1, sort_keys=True))
print(json.dumps({k: v for k, v in report.items()
                  if k not in ("r93_rows", "tail_after_r93",
                               "r93_gate_snippet")},
                 indent=1, sort_keys=True))
