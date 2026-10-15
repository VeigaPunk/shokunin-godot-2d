#!/usr/bin/env python3
"""r95-scout author-row builder — 17 verbatim CASES rows for the
PhysicsDirectSpaceState2D query lattice + ordering probe.

Signatures are the canonical `PASS dss_lattice <arm> ...` lines from runs/r95_*.
Every canonical cell is byte-stable (analyze_r95.py: out_uniq=1 err_uniq=1 rc=[0]
pass_uniq=1 for all 17), so the full line IS the row.

ROWS_PREFIX is the load-robust form: for the three cells whose PASS line carries
multi-hit ORDER VECTORS (point_cap / point_cap_rev / order_core / order_core_rev)
the signature is cut immediately before the first order vector, keeping the
order-free prefix (arm name, add_order, cap0=[] for point_cap; add_order for
order_core).  The order vectors themselves are a broadphase artifact — see
reports/round-95/r95-scout.md §3.7 / §6.2.

Output: author-rows.py.txt (rows as Python 5-tuples + expected_errors dict).
"""
import pathlib
import re

HERE = pathlib.Path(__file__).parent
RUNS = HERE / "runs"

# (case, arm, extra_flags, reps)
CELLS = [
    ("dss_lattice_census", "census", [], 3),
    ("dss_lattice_ray_flags", "ray_flags", [], 6),
    ("dss_lattice_ray_geom", "ray_geom", [], 6),
    ("dss_lattice_ray_order", "ray_order", [], 6),
    ("dss_lattice_ray_order_rev", "ray_order", ["--rev"], 6),
    ("dss_lattice_point_cap", "point_cap", [], 6),
    ("dss_lattice_point_cap_rev", "point_cap", ["--rev"], 6),
    ("dss_lattice_point_edge", "point_edge", [], 6),
    ("dss_lattice_point_canvas", "point_canvas", [], 6),
    ("dss_lattice_shape", "shape_lattice", [], 6),
    ("dss_lattice_shape_rev", "shape_lattice", ["--rev"], 6),
    ("dss_lattice_order_core", "order_core", [], 6),
    ("dss_lattice_order_core_rev", "order_core", ["--rev"], 6),
    ("dss_lattice_layer_forms", "layer_forms", [], 6),
    ("dss_lattice_cast_rest", "cast_rest", [], 6),
    ("dss_lattice_excl_space", "excl_space", [], 6),
    ("dss_lattice_fresh", "fresh", [], 6),
]

# Stable-prefix cut points for the order-vector cells (everything before the
# token is order-free; the vector tail is a broadphase artifact).
PREFIX_CUT = {
    "dss_lattice_point_cap": " cap1=",
    "dss_lattice_point_cap_rev": " cap1=",
    "dss_lattice_order_core": " rep1=",
    "dss_lattice_order_core_rev": " rep1=",
}

EXPECTED_ERRORS = {}


RUN_PREFIX = {
    "dss_lattice_shape": "dss_shape_lattice",
    "dss_lattice_shape_rev": "dss_shape_lattice_rev",
}


def run_prefix(case):
    if case in RUN_PREFIX:
        return RUN_PREFIX[case]
    return "dss_" + case[len("dss_lattice_"):]


def pass_line(case):
    f = sorted(RUNS.glob(f"r95_{run_prefix(case)}.rep*.out"))[0]
    m = re.search(r"^PASS dss_lattice .*$", f.read_text(), re.M)
    assert m, f"no PASS line in {f}"
    return m.group(0)


def main():
    full_rows = []
    prefix_rows = []
    for case, arm, extra, reps in CELLS:
        full = pass_line(case)
        flags = [f"--arm={arm}"] + list(extra)
        full_rows.append((case, "dss_lattice.gd", flags, 0, full))
        cut = PREFIX_CUT.get(case)
        sig = full.split(cut)[0] if cut and cut in full else full
        prefix_rows.append((case, "dss_lattice.gd", flags, 0, sig))

    text = ["# r95-scout author rows — PhysicsDirectSpaceState2D query lattice (verbatim-ready)", ""]
    text.append("# 5-tuples: (case, script, flags, expected_exit, signature)")
    text.append("# ROWS: full-line signatures, verified on all 93 canonical reps")
    text.append("#       (17 cells byte-stable: out_uniq=1 err_uniq=1 rc=[0], stderr 0 B).")
    text.append("ROWS = [")
    for r in full_rows:
        text.append("    (" + ", ".join(repr(x) for x in r) + "),")
    text.append("]")
    text.append("")
    text.append("# ROWS_PREFIX: RECOMMENDED robust form — for the cells whose PASS line carries")
    text.append("# multi-hit ORDER VECTORS (a broadphase artifact, see report §3.7) the signature")
    text.append("# is cut before the first vector; every other cell keeps its full line.")
    text.append("ROWS_PREFIX = [")
    for r in prefix_rows:
        text.append("    (" + ", ".join(repr(x) for x in r) + "),")
    text.append("]")
    text.append("")
    text.append("# expected_errors additions for corpus/fixtures/run_battery.py (keyed by case name):")
    text.append("# every r95 cell is ERROR:-clean with 0 B stderr — the dict is empty by design.")
    text.append("EXPECTED_ERRORS = {}")
    (HERE / "author-rows.py.txt").write_text("\n".join(text) + "\n")
    print("\n".join(text))


if __name__ == "__main__":
    main()
