#!/usr/bin/env python3
"""r98-scout author-row builder — emits author-rows.py.txt from the canonical
receipts (byte-exact PASS lines; never hand-typed).

ROWS        full-line signatures (informational where a measured tail can move)
ROWS_PREFIX gating prefixes (byte-stable over canonical + loadtest)
EXPECTED_ERRORS  exact allowed ERROR lines for the two refusal cells
"""
import pathlib
import re

HERE = pathlib.Path(__file__).parent
RUNS = HERE / "runs"

ARMS = ["census", "modulate", "queue", "draw_surface", "draw_refusal", "vis_chain",
        "clip", "zorder", "xform_skew", "xform_mirror", "xform_global", "notify",
        "draw_state", "redraw_triggers", "redraw_context"]

# cells whose measured tail may move (frame numbers): gating prefix cut marker
PREFIX_CUT = {
    "queue": " events_tail=",
}

EXPECTED_ERRORS = {
    "r98_canvas_draw_refusal": (
        "ERROR: Drawing is only allowed inside this node's `_draw()`, functions connected to its "
        "`draw` signal, or when it receives NOTIFICATION_DRAW.",
    ),
    "r98_canvas_clip": (
        'ERROR: Condition "p_clip_mode >= CLIP_CHILDREN_MAX" is true.',
    ),
}


def pass_line(arm):
    out = RUNS / f"r98_canvas_{arm}.rep1.out"
    text = out.read_text()
    for line in reversed(text.splitlines()):
        if line.startswith("PASS canvas_lattice "):
            return line
    raise SystemExit(f"no PASS line for arm {arm} in {out}")


def main():
    rows, prefixes = [], []
    for arm in ARMS:
        line = pass_line(arm)
        case = f"r98_canvas_{arm}"
        flags = [f"--arm={arm}"]
        rows.append((case, "canvas_lattice.gd", flags, 0, line))
        cut = PREFIX_CUT.get(arm)
        prefix = line.split(cut)[0] if cut and cut in line else line
        prefixes.append((case, "canvas_lattice.gd", flags, 0, prefix))
    body = []
    body.append("# r98-scout author rows — CanvasItem draw/transform lattice (verbatim-ready)")
    body.append("")
    body.append("# 5-tuples: (case, script, flags, expected_exit, signature)")
    body.append("# ROWS: full-line signatures (informational where a measured tail can move).")
    body.append("# ROWS_PREFIX: gating prefixes (byte-stable over canonical + loadtest receipts).")
    body.append("# EXPECTED_ERRORS: exact engine ERROR lines expected by the two refusal cells.")
    body.append("ROWS = [")
    for r in rows:
        body.append("    (%r, %r, %r, %r,\n     %r)," % (r[0], r[1], r[2], r[3], r[4]))
    body.append("]")
    body.append("")
    body.append("ROWS_PREFIX = [")
    for r in prefixes:
        body.append("    (%r, %r, %r, %r,\n     %r)," % (r[0], r[1], r[2], r[3], r[4]))
    body.append("]")
    body.append("")
    body.append("EXPECTED_ERRORS = {")
    for case in sorted(EXPECTED_ERRORS):
        body.append("    %r: %r," % (case, EXPECTED_ERRORS[case]))
    body.append("}")
    body.append("")
    (HERE / "author-rows.py.txt").write_text("\n".join(body))
    print(f"wrote author-rows.py.txt: {len(rows)} rows, {len(prefixes)} prefixes, "
          f"{len(EXPECTED_ERRORS)} expected_errors")


if __name__ == "__main__":
    main()
