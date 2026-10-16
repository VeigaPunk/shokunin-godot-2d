#!/usr/bin/env python3
"""r92-scribe static custody/fold audit — no execution, committed bytes only.

Checks (all recomputed, nothing quoted):
  A. landing-file sha256 (worktree) == git show HEAD:<path>
  B. CASES arithmetic at HEAD + r92 row shape (names, order, payload arity,
     expected_exit, signature text)
  C. r92 expected_errors census (cases + exact lines) and required_stderr pair
  D. r92 floor-gate key present in the meta verdict dict
  E. manifest completeness: manifest entry set == on-disk file set minus self
  F. fresh-reps arithmetic (14 arms x 3 reps x 3 files)
  G. tombstone/encoding law re-decoded from the pinned r92_tilemap_encoding row
Output: audit/static_folds.json (stdout too).
"""
import ast
import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[4]
FIX = REPO / "corpus" / "fixtures"
LIVE = REPO / "corpus" / "live"
OUT = {}


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def head_bytes(path: str) -> bytes:
    return subprocess.run(["git", "show", f"HEAD:{path}"], cwd=REPO,
                          capture_output=True, check=True).stdout


# ---------------------------------------------------------------- A
landing = {}
for rel in ["corpus/fixtures/tilemap_lattice.gd", "corpus/fixtures/run_battery.py",
            "corpus/fixtures/project.godot"]:
    p = REPO / rel
    landing[rel] = {"worktree_sha256": sha(p),
                    "head_sha256": hashlib.sha256(head_bytes(rel)).hexdigest()}
    landing[rel]["same"] = landing[rel]["worktree_sha256"] == landing[rel]["head_sha256"]
OUT["landing_identity"] = landing

# ---------------------------------------------------------------- B/C/D
src = head_bytes("corpus/fixtures/run_battery.py").decode()
tree = ast.parse(src)
cases = None
for node in tree.body:
    if isinstance(node, ast.Assign) and any(
            isinstance(t, ast.Name) and t.id == "CASES" for t in node.targets):
        cases = ast.literal_eval(node.value)
assert cases is not None, "CASES not found"
names = [c[0] for c in cases]
r92 = [(i, c) for i, c in enumerate(cases) if c[0].startswith("r92_")]
prev = names.index("nav_lattice_teardown_clean")
tail = ["crash_spontaneous_sigabrt", "crash_self_sigkill",
        "descendant_pipe_detached_control", "descendant_pipe_forged_signature_release"]
row_shape = []
for i, c in r92:
    sig = c[4]
    row_shape.append({
        "case": c[0], "script": c[1], "flags": c[2], "expected_exit": c[3],
        "signature_kind": "tuple" if isinstance(sig, (tuple, list)) else "str",
        "payloads": len(sig) if isinstance(sig, (tuple, list)) else 1,
        "sig_prefix": (sig[0] if isinstance(sig, (tuple, list)) else sig)[:60],
    })
OUT["cases"] = {
    "total": len(cases),
    "r92_count": len(r92),
    "r92_indices": [i for i, _ in r92],
    "nav_teardown_clean_index": prev,
    "contiguous_after_nav_teardown_clean": [i for i, _ in r92] == list(
        range(prev + 1, prev + 1 + len(r92))),
    "tail_after_r92": names[len(r92) + prev + 1:][:4] == tail,
    "tail_head": names[len(r92) + prev + 1:][:5],
    "row_shape": row_shape,
}

# expected_errors / required_stderr dicts live inside main(); walk the AST for the
# dict literals whose .get(name, ()) feeds expected_errors / required_stderr.
ee = rs = None
gate_key = None
for node in ast.walk(tree):
    if isinstance(node, ast.Assign):
        for t in node.targets:
            if isinstance(t, ast.Name) and t.id == "expected_errors" and ee is None:
                d = node.value
                # ternary: {..}.get(name, ()) -> find the Dict on either branch
                for sub in ast.walk(d):
                    if isinstance(sub, ast.Dict) and any(
                            isinstance(k, ast.Constant) and isinstance(k.value, str)
                            and k.value.startswith("r92_") for k in sub.keys):
                        ee = ast.literal_eval(sub)
            if isinstance(t, ast.Name) and t.id == "required_stderr" and rs is None:
                for sub in ast.walk(node.value):
                    if isinstance(sub, ast.Dict) and any(
                            isinstance(k, ast.Constant) and isinstance(k.value, str)
                            and k.value.startswith("r92_") for k in sub.keys):
                        rs = ast.literal_eval(sub)
for node in ast.walk(tree):
    if isinstance(node, ast.Dict):
        for k in node.keys:
            if isinstance(k, ast.Constant) and isinstance(k.value, str) \
                    and k.value.endswith("_expected_errors_all_matched"):
                gate_key = k.value
r92ee = {k: v for k, v in (ee or {}).items() if k.startswith("r92_")}
r92rs = {k: v for k, v in (rs or {}).items() if k.startswith("r92_")}
OUT["r92_expected_errors"] = {
    "cases": len(r92ee),
    "lines": sum(len(v) for v in r92ee.values()),
    "entries": {k: list(v) for k, v in r92ee.items()},
}
OUT["r92_required_stderr"] = {k: list(v) for k, v in r92rs.items()}
OUT["floor_gate_key"] = gate_key

# ---------------------------------------------------------------- E
manifests = {}
for lane in ["r92-scout", "r92-boundary", "r92-author"]:
    d = LIVE / lane
    mf = d / "manifest.sha256"
    entries = {}
    for line in mf.read_text().splitlines():
        if not line.strip():
            continue
        h, p = line.split("  ", 1)
        entries[p.lstrip("./")] = h
    on_disk = set()
    for root, _dirs, files in os.walk(d):
        for f in files:
            rel = os.path.relpath(os.path.join(root, f), d)
            on_disk.add(rel)
    missing = sorted(set(entries) - on_disk)
    unlisted = sorted(on_disk - set(entries) - {"manifest.sha256"})
    manifests[lane] = {"entries": len(entries), "files_on_disk": len(on_disk),
                       "missing_from_disk": missing, "unlisted_files": unlisted}
OUT["manifests"] = manifests

# ---------------------------------------------------------------- F
fr = sorted(p.name for p in (LIVE / "r92-author" / "fresh-reps").iterdir())
arms = sorted({n.split(".")[0] for n in fr})
reps = sorted({n.split(".")[1] for n in fr})
OUT["author_fresh_reps"] = {"files": len(fr), "arms": len(arms), "reps": reps,
                            "arm_names": arms}

# ---------------------------------------------------------------- G
enc = next(c for c in cases if c[0] == "r92_tilemap_encoding")[4]
fields = dict(kv.split("=", 1) for kv in enc.split()[3:])
for k in ["one_bytes", "two_bytes", "tomb_set_bytes", "tomb_erase_bytes",
          "tomb_reset_bytes", "tomb_clear_bytes", "tomb_clear_set_bytes", "alt_bytes"]:
    fields[k] = ast.literal_eval(fields[k])


def records(bs):
    assert bs[0] == 0 and bs[1] == 0, "header"
    body = bs[2:]
    assert len(body) % 12 == 0, f"stride {len(body)}"
    out = []
    for i in range(0, len(body), 12):
        r = body[i:i + 12]
        ints = [int.from_bytes(r[j:j + 2], "little", signed=True) for j in (0, 2, 4, 6, 8, 10)]
        out.append(tuple(ints))
    return out


OUT["encoding_decode"] = {
    "stride_field": fields["stride"],
    "one": records(fields["one_bytes"]),
    "two": records(fields["two_bytes"]),
    "tomb_set": records(fields["tomb_set_bytes"]),
    "tomb_erase": records(fields["tomb_erase_bytes"]),
    "tomb_reset": records(fields["tomb_reset_bytes"]),
    "tomb_clear": records(fields["tomb_clear_bytes"]),
    "tomb_clear_set": records(fields["tomb_clear_set_bytes"]),
    "alt": records(fields["alt_bytes"]),
    "lens": {k: len(fields[k]) for k in
             ["empty_bytes" if False else "one_bytes", "two_bytes", "tomb_erase_bytes",
              "tomb_clear_bytes", "tomb_clear_set_bytes", "alt_bytes"]},
    "pinned_len_fields": {k: fields[k] for k in
                          ["one_bytes_len", "two_bytes_len", "tomb_erase_len",
                           "tomb_reset_len", "tomb_clear_len", "tomb_clear_set_len"]},
}

print(json.dumps(OUT, indent=1, sort_keys=True))
(Path(__file__).parent / "static_folds.json").write_text(
    json.dumps(OUT, indent=1, sort_keys=True))
