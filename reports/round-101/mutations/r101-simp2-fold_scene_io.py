#!/usr/bin/env python3
"""r101 SIMP-2 fold builder — scene_io_lattice.gd (r96-simplifier fold, unlanded).

14 edit sites, net -12 lines: 2 binding->bare-call rewrites (0-line) and 12
terminal `= null` stores after last read.  Every edit is exact-string and
count-asserted.
"""
import pathlib
import subprocess
import sys

BASE = pathlib.Path("/var/tmp/r101-simp2")
SRC = BASE / "corpus" / "fixtures" / "scene_io_lattice.gd"
DST = BASE / "folded" / "scene_io_lattice.gd"

# (kind, needle) — "sub" rewrites in place, "del" removes the whole line.
EDITS = [
    ("sub", '\tvar child := _mk_child(root, "Child", Vector2(3, 4))\n',
            '\t_mk_child(root, "Child", Vector2(3, 4))\n', 1),
    ("sub", "\tvar e2 := ResourceSaver.save(b, p2)\n",
            "\tResourceSaver.save(b, p2)\n", 1),
    ("del", "\tl1 = null\n", 1),
    ("del", "\tcached = null\n", 1),
    ("del", "\tstale = null\n", 1),
    ("del", "\trepl = null\n", 1),
    ("del", "\tign = null\n", 1),
    ("del", "\tign2 = null\n", 1),
    ("del", "\tign3 = null\n", 1),
    ("del", "\tspr.texture = null\n", 1),
    ("del", "\tgt = null\n", 1),
    ("del", "\tloaded = null\n", 2),
    ("del", "\tback = null\n", 1),
]


def main():
    src_bytes = SRC.read_bytes()
    text = src_bytes.decode()
    for kind, needle, *rest in EDITS:
        if kind == "sub":
            repl, count = rest
            assert text.count(needle) == count, (needle, text.count(needle))
            text = text.replace(needle, repl)
        else:
            (count,) = rest
            assert text.count(needle) == count, (needle, text.count(needle))
            text = text.replace(needle, "")
    DST.parent.mkdir(parents=True, exist_ok=True)
    DST.write_text(text)
    old_n = src_bytes.decode().count("\n")
    new_n = text.count("\n")
    print(f"scene_io_lattice.gd: {len(src_bytes)} -> {len(text.encode())} bytes, "
          f"{old_n} -> {new_n} lines (delta {new_n - old_n})")
    patch = subprocess.run(
        ["diff", "-u", "--label", "a/corpus/fixtures/scene_io_lattice.gd",
         "--label", "b/corpus/fixtures/scene_io_lattice.gd", str(SRC), str(DST)],
        capture_output=True, text=True)
    (BASE / "patches").mkdir(exist_ok=True)
    (BASE / "patches" / "scene_io_lattice.gd.diff").write_text(patch.stdout)
    print("patch lines:", patch.stdout.count("\n"))
    return 0 if new_n - old_n == -12 else 1


if __name__ == "__main__":
    sys.exit(main())
