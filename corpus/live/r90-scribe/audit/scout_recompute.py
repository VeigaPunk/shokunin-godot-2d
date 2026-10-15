import json, hashlib, pathlib, re
root = pathlib.Path("/home/vgpnk/Projects/shokunin/game-dev-2d-shokunin/corpus/live/r90-scout")
runs = root / "runs"
cells = {}
for out in sorted(runs.glob("*.rep*.out")):
    cell = out.name.split(".rep")[0]
    stem = out.name[:-4]
    err = runs / (stem + ".err"); rc = runs / (stem + ".rc")
    cells.setdefault(cell, []).append((out, err, rc))
report = []
mismatch = 0
for cell, reps in sorted(cells.items()):
    outs = [p.read_bytes() for p, _, _ in reps]
    errs = [p.read_bytes() for p, _, _ in reps]
    rcs  = [p.read_text().strip() for _, _, p in reps]
    out_uniq = len(set(outs)); err_uniq = len(set(errs)); rc_uniq = len(set(rcs))
    sig = outs[0].decode(errors="replace").splitlines()
    sigline = [l for l in sig if l.startswith("PASS ")]
    report.append((cell, len(reps), out_uniq, err_uniq, sorted(set(rcs)), len(sigline)))
    if out_uniq != 1 or err_uniq != 1 or rc_uniq != 1 or len(sigline) != 1:
        mismatch += 1
print("cell                          reps out_uniq err_uniq rc        PASS_lines")
for r in report: print(f"{r[0]:29s} {r[1]:4d} {r[2]:8d} {r[3]:8d} {','.join(r[4]):9s} {r[5]}")
print("cells=", len(report), "cells_with_any_instability=", mismatch)
aj = json.loads((root / "analyze_r90.json").read_text())
print("json keys:", list(aj.keys())[:12])
