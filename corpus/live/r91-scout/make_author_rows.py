#!/usr/bin/env python3
"""r91-scout author-row builder — 9 verbatim CASES rows for the Navigation2D lattice.

Signatures are the canonical `PASS nav_lattice <arm> ...` lines from runs/r91_*.
For nav_avoid (a mode cell: the RVO numeric tail varies per process) the signature
is the stable PREFIX of the line through `warm_n_a=16`; the varying tail is offered
as a mode envelope in the report.

Output: author-rows.py.txt (rows as Python 5-tuples + expected_errors dict).
"""
import pathlib
import re

RUNS = pathlib.Path(__file__).parent / "runs"

# (case, arm, reps, prefix_or_None)
ROWS = [
    ("nav_lattice_census", "census", 3, None),
    ("nav_lattice_path", "path", 3, None),
    ("nav_lattice_query", "query", 3, None),
    ("nav_lattice_sync", "sync", 6, None),
    ("nav_lattice_region", "region", 6, None),
    ("nav_lattice_agent", "agent", 6, None),
    ("nav_lattice_avoid", "avoid", 6, "PASS nav_lattice avoid pa=(150.0000,150.0000) pb=(190.0000,150.0000) warm_n_a=16"),
    ("nav_lattice_bake", "bake", 6, None),
    ("nav_lattice_link", "link", 6, None),
]

EXPECTED_ERRORS = {
    "nav_lattice_sync": (
        "ERROR: NavigationServer navigation map query failed because it was made before first map synchronization.",
    ),
    "nav_lattice_bake": (
        "ERROR: The root node needs to be inside the SceneTree.",
    ),
}


def pass_line(case):
    f = sorted(RUNS.glob(f"r91_{case.replace('nav_lattice_', 'nav_')}.rep*.out"))[0]
    m = re.search(r"^PASS nav_lattice .*$", f.read_text(), re.M)
    assert m, f"no PASS line in {f}"
    return m.group(0)


# Stable-prefix cut points: everything before these tokens is load-independent
# (settle= / iter= / ladder= / first_reach* are async-sync counters that vary
# under concurrent-lane load — measured: full-line rows fail 1/3..2/3 under load).
PREFIX_CUT = {
    "nav_lattice_path": " settle=",
    "nav_lattice_query": " settle=",
    "nav_lattice_sync": " ladder=",
    "nav_lattice_region": " settle=",
    "nav_lattice_agent": " first_reachable=",
    "nav_lattice_bake": " settle_a=",
    "nav_lattice_link": " settle=",
}


def main():
    out = []
    pref = []
    for case, arm, reps, prefix in ROWS:
        full = pass_line(case)
        sig = prefix if prefix else full
        out.append((case, "nav_lattice.gd", [f"--arm={arm}"], 0, sig))
        cut = PREFIX_CUT.get(case)
        if prefix:
            pref.append((case, "nav_lattice.gd", [f"--arm={arm}"], 0, prefix))
        elif cut and cut in full:
            pref.append((case, "nav_lattice.gd", [f"--arm={arm}"], 0, full.split(cut)[0]))
        else:
            pref.append((case, "nav_lattice.gd", [f"--arm={arm}"], 0, full))
    text = ["# r91-scout author rows — Navigation2D lattice (verbatim-ready)", ""]
    text.append("# 5-tuples: (case, script, flags, expected_exit, signature)")
    text.append("# ROWS: full-line signatures, verified on the 45 canonical reps (byte-stable")
    text.append("#       8/9 cells).  Load-sensitive: see ROWS_PREFIX.")
    text.append("ROWS = [")
    for r in out:
        text.append("    (" + ", ".join(repr(x) for x in r) + "),")
    text.append("]")
    text.append("")
    text.append("# ROWS_PREFIX: RECOMMENDED robust form — signature ends before the async-sync")
    text.append("# counters (settle/iter/ladder/first_reach) that vary under concurrent-lane load.")
    text.append("# Verified against canonical + loadtest receipts (load avg 20+).")
    text.append("ROWS_PREFIX = [")
    for r in pref:
        text.append("    (" + ", ".join(repr(x) for x in r) + "),")
    text.append("]")
    text.append("")
    text.append("# expected_errors additions for corpus/fixtures/run_battery.py (keyed by case name)")
    text.append("EXPECTED_ERRORS = {")
    for k, v in EXPECTED_ERRORS.items():
        text.append(f"    {k!r}: (")
        for e in v:
            text.append(f"        {e!r},")
        text.append("    ),")
    text.append("}")
    pathlib.Path(__file__).with_name("author-rows.py.txt").write_text("\n".join(text) + "\n")
    print("\n".join(text))


if __name__ == "__main__":
    main()
