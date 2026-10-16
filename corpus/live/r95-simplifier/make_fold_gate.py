#!/usr/bin/env python3
"""r95-simplifier floor-gate fold: inject ONE stale r95 allowlist entry and run
the full battery on the folded harness.

The committed `r95_expected_errors_all_matched` gate covers
`case.startswith(("dss_lattice_", "r95b_order_"))` with zero entries today. The
fold adds a never-emitted entry for `r95b_order_canon`; the row must still PASS
(its signature is intact), the gate must flip False, `dead_entry_count` must
name the entry, and `probe_error_clause_surface` must FAIL => battery FAIL.

Usage: python3 make_fold_gate.py            (builds fold-gate/)
       bash run_fold_gate.sh                (runs the battery on it)
"""
import shutil
from pathlib import Path

HERE = Path(__file__).resolve().parent
CF = HERE / "committed-fixtures"
REPO = HERE.parents[2]
FIXTURES = REPO / "corpus" / "fixtures"
GATE = HERE / "fold-gate"

ANCHOR = "        expected_errors = {\n"
INJECT = ('        expected_errors = {\n'
          '            # r95-simplifier dead-entry fold probe (never emitted):\n'
          '            "r95b_order_canon": ("ERROR: r95-simplifier dead-entry fold probe (never emitted)",),\n')


def main():
    if GATE.exists():
        shutil.rmtree(GATE)
    shutil.copytree(FIXTURES, GATE)
    harness = GATE / "run_battery.py"
    text = harness.read_text()
    assert text.count(ANCHOR) == 1, "anchor not unique: %d" % text.count(ANCHOR)
    folded = text.replace(ANCHOR, INJECT, 1)
    harness.write_text(folded)
    (HERE / "fold-gate.diff").write_text(
        "--- a/corpus/fixtures/run_battery.py\n"
        "+++ b/fold-gate/run_battery.py\n"
        "@@ +1 stale r95 allowlist entry for r95b_order_canon @@\n"
        "+            # r95-simplifier dead-entry fold probe (never emitted):\n"
        '+            "r95b_order_canon": ("ERROR: r95-simplifier dead-entry fold probe (never emitted)",),\n')
    print("fold-gate harness: %s" % harness)
    print("committed harness sha256: %s" % __import__("hashlib").sha256(
        (CF / "run_battery.py").read_bytes()).hexdigest())
    print("folded harness sha256:    %s" % __import__("hashlib").sha256(
        harness.read_bytes()).hexdigest())


if __name__ == "__main__":
    main()
