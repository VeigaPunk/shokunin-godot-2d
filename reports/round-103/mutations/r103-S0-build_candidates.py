#!/usr/bin/env python3
"""r103 S0 — build folded candidates for the 3 queued simplifier gaps.

Reads committed bytes via `git show HEAD:<path>` (no tree writes), applies
count-asserted exact-string deletions, writes candidates + unified diffs into
/var/tmp/r103-S0/ and patch files into reports/round-103/mutations/.
All deletions are exactly the queue notes: r97 F6, r99 F2, r100 SP2+SP3.
"""
import hashlib
import pathlib
import subprocess

REPO = pathlib.Path("/home/vgpnk/Projects/shokunin/game-dev-2d-shokunin")
SCRATCH = pathlib.Path("/var/tmp/r103-S0")
MUT = REPO / "reports/round-103/mutations"
(SCRATCH / "committed").mkdir(parents=True, exist_ok=True)
(SCRATCH / "candidates").mkdir(parents=True, exist_ok=True)
(SCRATCH / "applytest/corpus/fixtures").mkdir(parents=True, exist_ok=True)
MUT.mkdir(parents=True, exist_ok=True)


def commit_bytes(path: str) -> bytes:
    return subprocess.run(
        ["git", "-C", str(REPO), "show", f"HEAD:{path}"],
        capture_output=True, check=True).stdout


def sha(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def one_replace(data: bytes, old: bytes, new: bytes) -> bytes:
    n = data.count(old)
    assert n == 1, f"expected 1 occurrence, found {n}: {old[:60]!r}"
    return data.replace(old, new)


def build(name: str, edits, post_asserts, label: str) -> dict:
    path = f"corpus/fixtures/{name}"
    src = commit_bytes(path)
    (SCRATCH / "committed" / name).write_bytes(src)
    out = src
    for old, new in edits:
        out = one_replace(out, old, new)
    for check in post_asserts:
        assert check(out), f"post-assert failed for {name}"
    (SCRATCH / "candidates" / name).write_bytes(out)
    (SCRATCH / "applytest/corpus/fixtures" / name).write_bytes(src)
    # unified diff with git-apply -p1 compatible labels
    diff = subprocess.run(
        ["diff", "-u", "--label", f"a/{path}", "--label", f"b/{path}",
         str(SCRATCH / "committed" / name), str(SCRATCH / "candidates" / name)],
        capture_output=True).stdout
    (MUT / label).write_bytes(diff)
    return {
        "name": name, "before": sha(src), "after": sha(out),
        "lines_before": src.count(b"\n"), "lines_after": out.count(b"\n"),
        "diff": diff.decode(), "patch": label,
    }


results = []

# E1 — r97 F6: delete `ready_ticks` field + the `_ready()` that only increments it.
results.append(build(
    "r97_scene_marker.gd",
    [(b'var ready_ticks := 0\n\nfunc _ready() -> void:\n\tready_ticks += 1\n', b'')],
    [lambda b: b'ready_ticks' not in b,
     lambda b: b'func _ready' not in b,
     lambda b: b.startswith(b'extends Node2D\n# r97 scout scene marker'),
     lambda b: b.endswith(b'@export var tag := "?"\n')],
    "r103-S0-E1-r97-F6-scene_marker.patch"))

# E2 — r99 F2: delete the declared-never-used `pairs` dictionary in _arm_splitcycle.
results.append(build(
    "r99b_modes.gd",
    [(b'\tvar pairs: Dictionary = {}\n', b'')],
    [lambda b: b'pairs' not in b],
    "r103-S0-E2-r99-F2-r99b_modes.patch"))

# E3 — r100 SP2+SP3: delete the never-observed `--arm=` parse in _initialize
# and the `arm` carrier (decl + loop assignment); `match arm:` -> `match a:`.
results.append(build(
    "r100b_seq.gd",
    [(b'\tfor a in OS.get_cmdline_user_args():\n'
      b'\t\tif a.begins_with("--arm="):\n'
      b'\t\t\tarm = a.substr(6)\n', b''),
     (b'var arm := ""\n', b''),
     (b'\t\tarm = a\n', b''),
     (b'\t\tmatch arm:', b'\t\tmatch a:')],
    [lambda b: b'var arm' not in b,
     lambda b: b'arm = a' not in b,
     lambda b: b'match arm' not in b,
     lambda b: b'\t\tmatch a:' in b,
     lambda b: b'OS.get_cmdline_user_args' in b,
     lambda b: b.count(b'OS.get_cmdline_user_args') == 1],
    "r103-S0-E3-r100-SP2SP3-r100b_seq.patch"))

for r in results:
    print(f"{r['name']}: before={r['before']} ({r['lines_before']}L)  "
          f"after={r['after']} ({r['lines_after']}L)  patch={r['patch']}")
    print(r["diff"])
