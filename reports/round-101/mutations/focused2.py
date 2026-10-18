#!/usr/bin/env python3
"""r101 SIMP-1 null-control for the audio residuals: 6 reps, serial, base vs f_audio."""
import hashlib, json, sys, time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
import simp1

WORK = simp1.WORK
CASES = {
    "r99_audio_advance": (["--arm=advance"], "f_audio"),
    "r99_audio_finish": (["--arm=finish"], "f_audio"),
    "r99_audio_loop_pts": (["--arm=loop_pts"], "f_audio"),
    "r99_audio_gen": (["--arm=gen"], "f_audio"),
    "r99_audio_poly": (["--arm=poly"], "f_audio"),
}
out = {}
t0 = time.time()
for name, (flags, cand) in CASES.items():
    out[name] = {}
    for rep in range(1, 7):
        for side in ("base", cand):
            so, se, rc, err = simp1.run_row(WORK / "trees" / side, "audio_lattice.gd", flags)
            stem = "focused2/%s.%s.rep%d" % (name, side, rep)
            p = WORK / "receipts" / (stem + ".stdout")
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(so or "")
            (WORK / "receipts" / (stem + ".stderr")).write_text(se or "")
            out[name].setdefault(side, []).append(
                {"rep": rep, "rc": rc, "sha": hashlib.sha256((so or "").encode()).hexdigest()[:16]})
    print("done", name, "%.0fs" % (time.time() - t0), flush=True)
(WORK / "focused2.json").write_text(json.dumps(out, indent=1))
print("elapsed %.0fs" % (time.time() - t0))
