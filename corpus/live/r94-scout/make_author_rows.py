#!/usr/bin/env python3
"""r94-scout author-row builder — 19 verbatim CASES rows for the Particles2D
emission lattice (prefix r94_).

Row shape matches corpus/fixtures/run_battery.py CASES:
    (case, script, flags, expected_exit, signature)

- ROWS:        full PASS lines (informational: several cells carry a +-1-tick
               measured tail; use in a quiet window or as mode envelopes).
- ROWS_PREFIX: stable gating prefixes.  For cells whose payload separates the
               boolean block from the measured tail with " | ", the prefix ends
               before " | "; for byte-stable cells the full line is the prefix.
- EXPECTED_ERRORS: empty — every cell produced 0 B stderr (measured, 105
               canonical + loadtest runs).

Output: author-rows.py.txt
"""
import pathlib
import re

HERE = pathlib.Path(__file__).parent
RUNS = HERE / "runs"

CELLS = [
    ("r94_particles_census", "census", 3),
    ("r94_particles_ppm", "ppm", 3),
    ("r94_particles_convert", "convert", 3),
    ("r94_particles_cpu_lifetime", "cpu_lifetime", 6),
    ("r94_particles_cpu_expl", "cpu_expl", 6),
    ("r94_particles_cpu_speed_pre", "cpu_speed_pre", 6),
    ("r94_particles_cpu_stop", "cpu_stop", 6),
    ("r94_particles_cpu_never", "cpu_never", 6),
    ("r94_particles_cpu_contam", "cpu_contam", 6),
    ("r94_particles_cpu_oneshot_off", "cpu_oneshot_off", 6),
    ("r94_particles_cpu_oneshot_flag", "cpu_oneshot_flag", 6),
    ("r94_particles_cpu_pause", "cpu_pause", 6),
    ("r94_particles_cpu_restart", "cpu_restart", 6),
    ("r94_particles_cpu_retrigger", "cpu_retrigger", 6),
    ("r94_particles_cpu_lt_mid", "cpu_lt_mid", 6),
    ("r94_particles_cpu_speed_mid", "cpu_speed_mid", 6),
    ("r94_particles_cpu_amount_mid", "cpu_amount_mid", 6),
    ("r94_particles_cpu_request", "cpu_request", 6),
    ("r94_particles_gpu_headless", "gpu_headless", 6),
]


def pass_line(arm):
    f = sorted(RUNS.glob(f"r94_particles_{arm}.rep*.out"))[0]
    m = re.search(r"^PASS particles_lattice .*$", f.read_text(), re.M)
    assert m, f"no PASS line in {f}"
    return m.group(0)


def main():
    rows, prefixes = [], []
    for case, arm, reps in CELLS:
        full = pass_line(arm)
        cut = full.split(" | ")[0] if " | " in full else full
        rows.append((case, "particles_lattice.gd", [f"--arm={arm}"], 0, full))
        prefixes.append((case, "particles_lattice.gd", [f"--arm={arm}"], 0, cut))

    text = ["# r94-scout author rows — Particles2D emission lattice (verbatim-ready)", ""]
    text.append("# 5-tuples: (case, script, flags, expected_exit, signature)")
    text.append("# ROWS: full-line signatures (informational; +-1-tick tails on the ladder cells).")
    text.append("# ROWS_PREFIX: gating prefixes — for ' | '-separated cells the prefix is the")
    text.append("#   boolean block before the measured tail; byte-stable cells keep the full line.")
    text.append("# EXPECTED_ERRORS: empty (0 B stderr on every measured run).")
    text.append("ROWS = [")
    for r in rows:
        text.append("    (" + ", ".join(repr(x) for x in r) + "),")
    text.append("]")
    text.append("")
    text.append("ROWS_PREFIX = [")
    for r in prefixes:
        text.append("    (" + ", ".join(repr(x) for x in r) + "),")
    text.append("]")
    text.append("")
    text.append("EXPECTED_ERRORS = {}")
    text.append("")
    (HERE / "author-rows.py.txt").write_text("\n".join(text))
    print(f"wrote author-rows.py.txt: {len(rows)} ROWS, {len(prefixes)} ROWS_PREFIX")


if __name__ == "__main__":
    main()
