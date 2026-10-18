#!/usr/bin/env python3
"""r101 SIMP-1 long null-control: 10 interleaved reps on the 3 audio rows whose
folded side varied where the 6-rep base did not."""
import hashlib, json, sys, time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
import simp1
WORK = simp1.WORK
CASES = {"r99_audio_advance": ["--arm=advance"], "r99_audio_gen": ["--arm=gen"], "r99_audio_loop_pts": ["--arm=loop_pts"]}
out = {}
t0 = time.time()
for name, flags in CASES.items():
    out[name] = {}
    for rep in range(1, 11):
        for side in ("base", "f_audio"):
            so, se, rc, err = simp1.run_row(WORK / "trees" / side, "audio_lattice.gd", flags)
            stem = "focused3/%s.%s.rep%d" % (name, side, rep)
            p = WORK / "receipts" / (stem + ".stdout")
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(so or "")
            (WORK / "receipts" / (stem + ".stderr")).write_text(se or "")
            out[name].setdefault(side, []).append(
                {"rep": rep, "rc": rc, "sha": hashlib.sha256((so or "").encode()).hexdigest()[:16]})
    print("done", name, "%.0fs" % (time.time() - t0), flush=True)
(WORK / "focused3.json").write_text(json.dumps(out, indent=1))
print("elapsed %.0fs" % (time.time() - t0))
