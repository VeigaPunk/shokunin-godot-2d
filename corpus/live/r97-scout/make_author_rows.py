#!/usr/bin/env python3
"""r97-scout author rows — SceneTree groups / signal flags / call_deferred ladder.

Reads the canonical PASS lines from `runs/r97_<cell>.rep1.out` and emits the
verbatim-ready 5-tuples (case, script, flags, expected_exit, signature) plus a
recommended ROWS_PREFIX form that stops before the multi-element order vectors.
"""
import pathlib

HERE = pathlib.Path(__file__).parent
RUNS = HERE / "runs"
SCRIPT = "stree_lattice.gd"

# (case, arm, extra flags, prefix-cut-key)  — prefix cut keeps everything BEFORE
# the named key (that key and everything after it are dropped in ROWS_PREFIX).
CELLS = [
    ("stree_lattice_census", "census", [], None),
    ("stree_lattice_group_order", "group_order", [], "tree_order="),
    ("stree_lattice_group_order_rev", "group_order", ["--rev"], "tree_order="),
    ("stree_lattice_group_flags", "group_flags", [], "fifo="),
    ("stree_lattice_group_lifecycle", "group_lifecycle", [], None),
    ("stree_lattice_group_setters", "group_setters", [], None),
    ("stree_lattice_signal_order", "signal_order", [], None),
    ("stree_lattice_signal_flags", "signal_flags", [], "cross_t0="),
    ("stree_lattice_defer_ladder", "defer_ladder", [], None),
    ("stree_lattice_defer_slots", "defer_slots", [], None),
    ("stree_lattice_defer_order", "defer_order", [], None),
    ("stree_lattice_scene_probe", "scene_probe", [], "packed_loaded="),
]

RUN_NAME = {
    ("group_order", "--rev"): "group_order_rev",
}


def cell_run_name(case, arm, extra):
    key = (arm, extra[0] if extra else "")
    return RUN_NAME.get(key, arm)


def pass_line(case, arm, extra):
    name = cell_run_name(case, arm, extra)
    text = (RUNS / f"r97_{name}.rep1.out").read_text()
    lines = [l for l in text.splitlines() if l.startswith("PASS stree_lattice ")]
    assert len(lines) == 1, (case, lines)
    return lines[0]


def cut(line, key):
    if key is None:
        return line
    idx = line.index(key)
    return line[:idx].rstrip()


rows = []
prefix = []
for case, arm, extra, cut_key in CELLS:
    full = pass_line(case, arm, extra)
    rows.append((case, SCRIPT, list(extra), 0, full))
    prefix.append((case, SCRIPT, list(extra), 0, cut(full, cut_key)))

out = []
out.append("# r97-scout author rows — SceneTree groups / signal connect flags / call_deferred")
out.append("# timing lattice (verbatim-ready)")
out.append("")
out.append("# 5-tuples: (case, script, flags, expected_exit, signature)")
out.append("# ROWS: full-line signatures, verified on all 48 canonical reps")
out.append("#       (12 cells byte-stable: out_uniq=1 err_uniq=1 rc=[0], stderr 0 B)")
out.append("#       plus 36 loadtest reps at host load avg 113-138.")
out.append("ROWS = [")
for case, script, extra, code, sig in rows:
    out.append("    (%r, %r, %r, %d, %r)," % (case, script, extra, code, sig))
out.append("]")
out.append("")
out.append("# ROWS_PREFIX: RECOMMENDED robust form — for the cells whose PASS line carries")
out.append("# multi-element ORDER VECTORS the signature is cut before the first vector.")
out.append("ROWS_PREFIX = [")
for case, script, extra, code, sig in prefix:
    out.append("    (%r, %r, %r, %d, %r)," % (case, script, extra, code, sig))
out.append("]")
out.append("")
out.append("# expected_errors additions for corpus/fixtures/run_battery.py (keyed by case name):")
out.append("# every r97 cell is ERROR:-clean with 0 B stderr — the dict is empty by design.")
out.append("EXPECTED_ERRORS = {}")
out.append("")

(HERE / "author-rows.py.txt").write_text("\n".join(out))
print("\n".join(out[:8]))
print(f"... {len(rows)} rows, {len(prefix)} prefix rows")
