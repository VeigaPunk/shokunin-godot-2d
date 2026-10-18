#!/usr/bin/env python3
"""r101 SIMP-2 fold builder — stree_lattice.gd (r97-simplifier F1..F5, unlanded).

Reads committed bytes, applies exact-string edits, writes folded copy + asserts
each edit matched exactly the expected number of times.  Emits a `diff -u` patch.
"""
import pathlib
import re
import subprocess
import sys

BASE = pathlib.Path("/var/tmp/r101-simp2")
SRC = BASE / "corpus" / "fixtures" / "stree_lattice.gd"
DST = BASE / "folded" / "stree_lattice.gd"


def strip_def(text, head, count=1):
    """Delete a func/const definition block, keeping the 2-blank-line rhythm."""
    needle = head + "\n\n\n"
    assert text.count(needle) == count, (head, text.count(needle))
    return text.replace(needle, "")


def balanced_args(text, opener, replace):
    """Rewrite every `opener(arg1, arg2)` call via a callback on the arg list."""
    out = []
    i = 0
    n = 0
    while True:
        j = text.find(opener, i)
        if j < 0:
            out.append(text[i:])
            break
        out.append(text[i:j])
        k = j + len(opener)
        depth = 1
        instr = None
        while depth:
            ch = text[k]
            if instr:
                if ch == instr and text[k - 1] != "\\":
                    instr = None
            elif ch in "\"'":
                instr = ch
            elif ch == "(":
                depth += 1
            elif ch == ")":
                depth -= 1
            k += 1
        inner = text[j + len(opener):k - 1]
        # split top-level commas
        parts, buf, d = [], [], 0
        instr = None
        for ch in inner:
            if instr:
                buf.append(ch)
                if ch == instr:
                    instr = None
                continue
            if ch in "\"'":
                instr = ch
                buf.append(ch)
            elif ch in "([{":
                d += 1
                buf.append(ch)
            elif ch in ")]}":
                d -= 1
                buf.append(ch)
            elif ch == "," and d == 0:
                parts.append("".join(buf).strip())
                buf = []
            else:
                buf.append(ch)
        parts.append("".join(buf).strip())
        out.append(replace(parts))
        n += 1
        i = k
    return "".join(out), n


def main():
    src_bytes = SRC.read_bytes()
    text = src_bytes.decode()

    # F2 — it_valid() alias folded to _it (51 call sites) + def deleted.
    assert text.count("it_valid(") == 52, text.count("it_valid(")
    text = strip_def(text, "func it_valid(key: String, value: String) -> void:\n\t_it(key, value)")
    text = text.replace("it_valid(", "_it(")

    # F3 — it_connected() folded to _it(key, _v(v)) + def deleted.
    assert text.count("it_connected(") == 7, text.count("it_connected(")
    text = strip_def(text, "func it_connected(key: String, v: bool) -> void:\n\t_it(key, _v(v))")
    text, n3 = balanced_args(text, "it_connected(", lambda p: '_it(%s, _v(%s))' % (p[0], p[1]))
    assert n3 == 6, n3

    # F4 — it_paused() folded to _it("paused_seen", str(n)) + def deleted.
    assert text.count("it_paused(") == 4, text.count("it_paused(")
    text = strip_def(text, 'func it_paused(n: int) -> void:\n\t_it("paused_seen", str(n))')
    text, n4 = balanced_args(text, "it_paused(", lambda p: '_it("paused_seen", str(%s))' % p[0])
    assert n4 == 3, n4

    # F1 — dead helper _tree_names() deleted.
    text = strip_def(
        text,
        "func _tree_names() -> String:\n\treturn _ord(root.get_children().map(func(n): return str(n.name)))",
    )

    # F5 — _arm_defer_ladder comment: drop the restated general law, point at header laws block.
    old5 = (
        "\t# L10 \u2014 the timing ladder. `await process_frame` resumes AT the signal.\n"
        "\t# r97-boundary corrected the frozen universal: a deferred call queued from\n"
        "\t# _process/_physics_process flushes BEFORE that frame's process_frame\n"
        "\t# signal; one queued from this coroutine body (`cd`) lands within the same\n"
        "\t# idle frame \u2014 this arm's separate df_log does not pin its position inside\n"
        "\t# the signal window (boundary \u00a72.3).\n"
    )
    new5 = (
        "\t# L10 \u2014 the timing ladder. `await process_frame` resumes AT the signal.\n"
        "\t# (general flush-position law: header laws block; boundary \u00a72.3) \u2014 one\n"
        "\t# queued from this coroutine body (`cd`) lands within the same idle frame;\n"
        "\t# this arm's separate df_log does not pin its position inside the signal\n"
        "\t# window.\n"
    )
    assert text.count(old5) == 1, text.count(old5)
    text = text.replace(old5, new5)

    for tok in ("it_valid", "it_connected", "it_paused", "_tree_names"):
        assert tok not in text, tok

    DST.parent.mkdir(parents=True, exist_ok=True)
    DST.write_text(text)
    old_n = src_bytes.decode().count("\n")
    new_n = text.count("\n")
    print(f"stree_lattice.gd: {len(src_bytes)} -> {len(text.encode())} bytes, "
          f"{old_n} -> {new_n} lines (delta {new_n - old_n})")
    patch = subprocess.run(
        ["diff", "-u", "--label", "a/corpus/fixtures/stree_lattice.gd",
         "--label", "b/corpus/fixtures/stree_lattice.gd", str(SRC), str(DST)],
        capture_output=True, text=True)
    (BASE / "patches").mkdir(exist_ok=True)
    (BASE / "patches" / "stree_lattice.gd.diff").write_text(patch.stdout)
    print(patch.stdout[:400], "...patch lines:", patch.stdout.count("\n"))
    return 0 if new_n - old_n < 0 else 1


if __name__ == "__main__":
    sys.exit(main())
