#!/usr/bin/env python3
"""r101 SIMP-1 null-control: re-run the 3 residual-diff rows, 6 reps, serial, base vs folded."""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import simp1  # noqa: E402

WORK = simp1.WORK
CASES = {
    "nav_lattice_sync": ("nav_lattice.gd", ["--arm=sync"], "f_nav"),
    "r98b_qflush_same_frame": ("r98b_attack.gd", ["--arm=qflush"], "f_attack"),
    "r98b_qorder_tree": ("r98b_attack.gd", ["--arm=qorder"], "f_attack"),
}


def main():
    reps = 6
    out = {}
    t0 = time.time()
    for name, (script, flags, cand) in CASES.items():
        out[name] = {}
        for rep in range(1, reps + 1):
            for side in ("base", cand):
                so, se, rc, err = simp1.run_row(WORK / "trees" / side, script, flags)
                stem = "focused/%s.%s.rep%d" % (name, side, rep)
                p = WORK / "receipts" / (stem + ".stdout")
                p.parent.mkdir(parents=True, exist_ok=True)
                p.write_text(so if so is not None else "")
                (WORK / "receipts" / (stem + ".stderr")).write_text(se if se is not None else "")
                out[name].setdefault(side, []).append({"rep": rep, "rc": rc,
                    "sha": __import__("hashlib").sha256((so or "").encode()).hexdigest()[:16]})
        print("done", name, "%.0fs" % (time.time() - t0), flush=True)
    (WORK / "focused.json").write_text(json.dumps(out, indent=1))
    print("elapsed %.0fs" % (time.time() - t0))


if __name__ == "__main__":
    main()
