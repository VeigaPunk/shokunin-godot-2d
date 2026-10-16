#!/usr/bin/env python3
"""r93 verifier — provenance of the committed r93 artefacts (4b75151).

  * committed fixture sha256 vs the frozen scout/boundary probe copies
    (byte-copy chain, no fold)
  * the 15 scout gating rows carried verbatim into the committed CASES;
    the 2 informational load-fragile rows excluded
  * commit scope (paths by top-level area)
"""
import ast
import hashlib
import pathlib
import subprocess
import sys

REPO = pathlib.Path("/home/vgpnk/Projects/shokunin/game-dev-2d-shokunin")
FIX = REPO / "corpus/live/r93-verifier/freeze/x/corpus/fixtures"
out = []


def sha(p):
    return hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()


pairs = [
    ("anim_lattice.gd", "corpus/live/r93-scout/probes/anim_lattice.gd"),
    ("anim_lattice.gd", "corpus/live/r93-scout/proj/anim_lattice.gd"),
    ("anim_lattice.gd", "corpus/live/r93-boundary/probes/scout_anim_lattice.gd"),
    ("r93b_anim.gd", "corpus/live/r93-boundary/probes/r93b_anim.gd"),
    ("r93b_anim.gd", "corpus/live/r93-boundary/proj/r93b_anim.gd"),
]
for fixture, copy in pairs:
    a, b = sha(FIX / fixture), sha(REPO / copy)
    out.append(f"{'OK ' if a == b else 'MISMATCH '}{fixture} == {copy}  {a[:16]}")

committed = ast.parse((FIX / "run_battery.py").read_text())
for node in ast.walk(committed):
    if isinstance(node, ast.Assign) and getattr(node.targets[0], "id", "") == "CASES":
        cases = [ast.literal_eval(e) for e in node.value.elts]
c93 = {c[0]: c for c in cases if c[0].startswith("r93_")}
txt = (REPO / "corpus/live/r93-scout/author-rows.py.txt").read_text()
start = txt.index("ROWS = [")
end = txt.index("]\n\nROWS_FULL")
rows = ast.literal_eval(txt[start + len("ROWS = "):end + 1])
same = sum(1 for r in rows if r[0] in c93 and tuple(r) == tuple(c93[r[0]]))
out.append(f"scout ROWS carried verbatim: {same}/{len(rows)}")
out.append(f"informational ROWS_FULL excluded: "
           f"{[n for n in ('r93_tween_process_full', 'r93_anim_process_full') if n not in c93]}")

scope = subprocess.run(["git", "-C", str(REPO), "show", "--name-only", "--format=", "HEAD"],
                       capture_output=True, text=True).stdout.split()
areas = {}
for p in scope:
    if p.startswith("corpus/live/r93-author/"):
        key = "corpus/live/r93-author/**"
    elif p.startswith("corpus/live/r93-verifier/"):
        key = "corpus/live/r93-verifier/** (this seat, must be absent)"
    else:
        key = p
    areas[key] = areas.get(key, 0) + 1
out.append(f"commit paths total={len(scope)}")
for k, v in sorted(areas.items()):
    out.append(f"  {k}: {v}")
(REPO / "corpus/live/r93-verifier/probes/provenance.txt").write_text("\n".join(out) + "\n")
print("\n".join(out))
sys.exit(0)
