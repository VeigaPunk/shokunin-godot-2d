#!/usr/bin/env python3
"""r100-scout author-row builder — 14 verbatim CASES rows for the Viewport/Control
GUI input-routing + pointer-gesture lattice.

Signatures are the canonical `PASS r100_gui <cell> ...` lines from runs/. Every
canonical cell is byte-stable x6 (out_uniq=1 err_uniq=1 rc=[0]) and every loadtest
rep reproduces the identical line, so the full line IS the row.

The one allowlisted cell is `render`: `ViewportTexture.get_image()` under the
headless RendererDummy emits a deterministic
`ERROR: Parameter "t" is null.` line (dummy texture_storage) and returns null —
that ERROR is the measured fact, so the row carries an exact expected_errors
entry instead of avoiding the call.

Output: author-rows.py.txt (ROWS / ROWS_PREFIX / EXPECTED_ERRORS).
"""
import pathlib

HERE = pathlib.Path(__file__).parent
RUNS = HERE / "runs"

CELLS = [
    "census", "routing", "hover", "motion", "localpos", "cursor", "clip",
    "drag", "touch", "subvp", "warp", "focus", "render", "osmeta",
]

EXPECTED_ERRORS = {
    "r100_gui_render": ('ERROR: Parameter "t" is null.',),
}


def pass_line(cell: str) -> str:
    out = (RUNS / f"r100_gui_{cell}.rep1.out").read_text()
    lines = [ln for ln in out.splitlines() if ln.startswith("PASS r100_gui ")]
    assert len(lines) == 1, (cell, lines)
    return lines[0]


rows = []
for cell in CELLS:
    line = pass_line(cell)
    assert line.startswith(f"PASS r100_gui {cell} "), (cell, line[:80])
    rows.append((f"r100_gui_{cell}", "r100_gui.gd", [f"--arm={cell}"], 0, line))

# ROWS_PREFIX == ROWS: every cell is byte-stable at full-line granularity, so no
# load-robust cut is needed (contrast r94's +-1-tick tails / r95's order vectors).
prefix_rows = list(rows)

body = "ROWS = [\n"
for name, script, flags, code, line in rows:
    body += "    (%r, %r, %r, %d,\n     %r),\n" % (name, script, flags, code, line)
body += "]\n\nROWS_PREFIX = [\n"
for name, script, flags, code, line in prefix_rows:
    body += "    (%r, %r, %r, %d,\n     %r),\n" % (name, script, flags, code, line)
body += "]\n\nEXPECTED_ERRORS = {\n"
for case, entries in EXPECTED_ERRORS.items():
    body += "    %r: %r,\n" % (case, entries)
body += "}\n"

(HERE / "author-rows.py.txt").write_text(body)
print(f"wrote {len(rows)} rows -> author-rows.py.txt")
for name, _s, _f, _c, line in rows:
    print(f"  {name}: {line[:100]}")
