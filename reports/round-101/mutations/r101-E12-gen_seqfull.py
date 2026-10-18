#!/usr/bin/env python3
"""r101-E12 generator: corpus/fixtures/r101_seqfull.gd from corpus/fixtures/r100b_seq.gd.

Mechanical transform (auditable: `git diff --no-index r100b_seq.gd r101_seqfull.gd`
shows ONLY the header comment, the receipt assembly in `_run()`, the new
`_emit`/`_transcript` members and the embedded FRESH_PINS table):

  * every cell's `print("PASS r100_gui ...")` becomes `_emit("PASS r100_gui ...")`
    so the line is additionally appended to `_transcript` and printed
    contiguously in run order (the stdout contiguity is what makes a forged
    extra line inside the replay break the multi-line row signature);
  * `_run()` gains `SEQ_BEGIN` before the cell loop and
    `SEQ_CENSUS`/`SEQ_END digest=<sha256>` after it;
  * FRESH_PINS embeds the 14 `r100_gui_*` CASES pins BY VALUE so the fixture
    itself computes the divergence census against the harness's own pins
    (a drift between harness pin and replay output shows up as a changed
    census + changed digest, i.e. as a row failure).

Read-only on run_battery.py (AST extract); writes ONLY the two assigned paths.
"""
import ast
import hashlib
import pathlib
import sys

REPO = pathlib.Path(__file__).resolve().parents[3]
FIXTURES = REPO / "corpus" / "fixtures"
SRC = FIXTURES / "r100b_seq.gd"
HARNESS = FIXTURES / "run_battery.py"
OUT = FIXTURES / "r101_seqfull.gd"

SRC_SHA = "4718a19e0050f4043613a5a93a13cbd812c811605f7a14d33e000544eafa94dd"
CELLS = ["census", "routing", "hover", "motion", "localpos", "cursor", "clip",
         "drag", "touch", "subvp", "warp", "focus", "render", "osmeta"]


def fresh_pins():
    tree = ast.parse(HARNESS.read_text())
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign) and getattr(node.targets[0], "id", "") == "CASES":
            rows = ast.literal_eval(node.value)
            break
    else:
        sys.exit("CASES not found")
    pins = {}
    for name, fixture, flags, rc, sig in rows:
        if name.startswith("r100_gui_"):
            cell = name[len("r100_gui_"):]
            assert fixture == "r100_gui.gd" and flags == ["--arm=" + cell] and rc == 0, name
            assert cell not in pins, cell
            pins[cell] = sig
    assert sorted(pins) == sorted(CELLS), (sorted(pins), sorted(CELLS))
    return pins


def gd_quote(s: str) -> str:
    assert "\n" not in s and "\r" not in s, repr(s)
    return '"' + s.replace("\\", "\\\\").replace('"', '\\"') + '"'


def main() -> None:
    src = SRC.read_text()
    have = hashlib.sha256(src.encode()).hexdigest()
    assert have == SRC_SHA, f"r100b_seq.gd sha256 drift: {have} != {SRC_SHA}"
    pins = fresh_pins()

    out = src

    # 1. header comment (lines 2..6 of the source)
    old_head = (
        "# r100-scout scratch probe — Viewport/Control GUI input-routing + pointer-gesture lattice.\n"
        "# One cell per process, exactly the battery's launch shape:\n"
        "#   godot --headless --path <scratch> --script res://r100_gui.gd -- --arm=<cell>\n"
        "# Prints one final `PASS r100_gui <cell> ...` line. No object ids / RIDs / timestamps.\n"
        "# Cells: census routing hover motion localpos cursor drag touch subvp warp focus render osmeta\n"
    )
    new_head = (
        "# r101-E12 scratch probe — FULL-REPLAY receipt for the 14-cell sequence\n"
        "# (closes reports/round-100/r100-critic.md F2: the r100b_seq rows pinned one\n"
        "#  line of a 14-cell replay, so a forged extra output line inside the replay\n"
        "#  left both rows PASS and 3 of the 4 divergences were unconstrained).\n"
        "#\n"
        "#   godot --headless --path <scratch> --script res://r101_seqfull.gd -- --clean=<0|1>\n"
        "#\n"
        "# Cell bodies are the r100b_seq.gd bodies unchanged (byte-diff shows only the\n"
        "# `print(` -> `_emit(` rename plus the receipt assembly). Each cell's\n"
        "# `PASS r100_gui <cell> ...` line is printed in run order and appended to the\n"
        "# transcript, so the whole stdout span\n"
        "#\n"
        "#   SEQ_BEGIN ... <14 cell lines, contiguous> SEQ_CENSUS ... SEQ_END digest=<sha256>\n"
        "#\n"
        "# is one contiguous multi-line unit: a forged extra stdout line anywhere inside\n"
        "# the replay breaks the adjacency the row signature pins. SEQ_CENSUS recomputes\n"
        "# the divergence census against FRESH_PINS (the 14 `r100_gui_*` harness pins\n"
        "# embedded BY VALUE), SEQ_END digest binds the 14 cell lines by content.\n"
        "# No object ids / RIDs / timestamps.\n"
    )
    assert old_head in out
    out = out.replace(old_head, new_head, 1)

    # 2. per-cell print -> _emit
    n = out.count('print("PASS r100_gui ')
    assert n == 14, f"expected 14 cell prints, saw {n}"
    out = out.replace('print("PASS r100_gui ', '_emit("PASS r100_gui ')

    # 3. transcript member + FRESH_PINS table after `var _nodes: Array = []`
    anchor_members = "var arm := \"\"\nvar _nodes: Array = []\n"
    assert out.count(anchor_members) == 1
    table = "".join("    %s: %s,\n" % (gd_quote(c), gd_quote(pins[c])) for c in CELLS)
    out = out.replace(anchor_members, anchor_members + "\nvar _transcript: Array = []\n\n# The 14 fresh-process `r100_gui_*` CASES pins, by value.\nconst FRESH_PINS := {\n" + table + "}\n", 1)

    # 4. SEQ_BEGIN before the cell loop
    anchor_loop = "\tfor a in seq_arms:\n\t\tarm = a\n"
    assert out.count(anchor_loop) == 1
    out = out.replace(anchor_loop,
                      "\tprint(\"SEQ_BEGIN cells=%d clean=%d pins=%d\" % [seq_arms.size(), do_clean, FRESH_PINS.size()])\n"
                      "\tfor a in seq_arms:\n\t\tarm = a\n", 1)

    # 5. SEQ_CENSUS / SEQ_END replacing SEQ_DONE
    anchor_done = "\tprint(\"SEQ_DONE clean=%d\" % do_clean)\n"
    assert out.count(anchor_done) == 1
    census = (
        "\tvar divergent: Array = []\n"
        "\tfor i in range(seq_arms.size()):\n"
        "\t\tif _transcript[i] != FRESH_PINS[seq_arms[i]]:\n"
        "\t\t\tdivergent.append(seq_arms[i])\n"
        "\tprint(\"SEQ_CENSUS identical=%d divergent_n=%d divergent=[%s]\" % [\n"
        "\t\tseq_arms.size() - divergent.size(), divergent.size(), \"|\".join(divergent)])\n"
        "\tprint(\"SEQ_END digest=%s\" % \"\\n\".join(_transcript).sha256_text())\n"
    )
    out = out.replace(anchor_done, census, 1)

    # 6. _emit helper before _cleanup
    anchor_cleanup = "func _cleanup() -> void:\n"
    assert out.count(anchor_cleanup) == 1
    out = out.replace(anchor_cleanup,
                      "func _emit(line: String) -> void:\n"
                      "\t_transcript.append(line)\n"
                      "\tprint(line)\n\n\n"
                      "func _cleanup() -> void:\n", 1)

    # sanity: the cell bodies' dispatch + order unchanged
    assert out.count("'census', 'routing', 'hover', 'motion', 'localpos', 'cursor', 'clip', 'drag', 'touch', 'subvp', 'warp', 'focus', 'render', 'osmeta'") == 1

    OUT.write_text(out)
    digest = hashlib.sha256(out.encode()).hexdigest()
    print(f"wrote {OUT.relative_to(REPO)} bytes={len(out.encode())} sha256={digest}")
    print(f"pins: {len(pins)} total_pin_bytes={sum(len(v) for v in pins.values())}")


if __name__ == "__main__":
    main()
