#!/usr/bin/env python3
"""r93 verifier — custody of the author's tracked r93 evidence.

  * the 51 tracked fresh-rep receipts (153 files) re-classified with the
    AST-extracted production classify_process against every committed r93 row
    pinned on that arm
  * the tracked proj/ copies byte-identical to the committed fixtures
  * the three tracked battery logs: r93 verdict lines
  * the tracked manifest.sha256: sha256sum -c result
"""
import ast
import hashlib
import pathlib
import re
import subprocess
import sys

REPO = pathlib.Path("/home/vgpnk/Projects/shokunin/game-dev-2d-shokunin")
V = REPO / "corpus/live/r93-verifier"
FIX = V / "freeze" / "x" / "corpus" / "fixtures"
A = REPO / "corpus/live/r93-author"

src = (FIX / "run_battery.py").read_text()
tree = ast.parse(src)
for node in ast.walk(tree):
    if isinstance(node, ast.FunctionDef) and node.name == "classify_process":
        seg = ast.get_source_segment(src, node)
        break
ns = {"re": re}
exec("import re\n" + seg, ns)  # noqa: S102 - frozen committed source
classify = ns["classify_process"]
for node in ast.walk(tree):
    if isinstance(node, ast.Assign) and getattr(node.targets[0], "id", "") == "CASES":
        cases = [ast.literal_eval(e) for e in node.value.elts]
        break
rows = [c for c in cases if c[0].startswith("r93_")]

out = []
ok = bad = 0
for r in rows:
    stem, arm = r[1][:-3], r[2][0].split("=", 1)[1]
    for rep in (1, 2, 3):
        o = (A / "fresh-reps" / f"{stem}.{arm}.rep{rep}.out").read_text()
        e = (A / "fresh-reps" / f"{stem}.{arm}.rep{rep}.err").read_text()
        rc = int((A / "fresh-reps" / f"{stem}.{arm}.rep{rep}.rc").read_text().strip())
        v = classify(rc, None, o + e, r[3], r[4], ())
        ok += bool(v)
        bad += (not v)
        if not v:
            out.append(f"BAD {stem}.{arm}.rep{rep} {r[0]}")
out.insert(0, f"author fresh-reps re-classified with production classify_process: OK={ok} BAD={bad} (of {len(rows) * 3})")

for name in ("anim_lattice.gd", "r93b_anim.gd"):
    a = hashlib.sha256((A / "proj" / name).read_bytes()).hexdigest()
    b = hashlib.sha256((FIX / name).read_bytes()).hexdigest()
    out.append(f"author proj/{name} == committed fixture: {a == b} {a[:16]}")

for i in (1, 2, 3):
    log = (A / f"battery{i}.log").read_text()
    lines = [l for l in log.splitlines() if l.startswith(("PASS r93_", "FAIL r93_"))]
    fails = [l for l in lines if l.startswith("FAIL")]
    out.append(f"author battery{i}.log: r93 lines={len(lines)} fails={len(fails)}")

res = subprocess.run(["sha256sum", "-c", "manifest.sha256"], cwd=A, capture_output=True, text=True)
bad_lines = [l for l in res.stdout.splitlines() if "OK" not in l]
out.append(f"author manifest.sha256: entries={len((A / 'manifest.sha256').read_text().splitlines())} "
           f"sha256sum -c rc={res.returncode} non-OK lines={len(bad_lines)}")

(V / "probes" / "author-custody.txt").write_text("\n".join(out) + "\n")
print("\n".join(out))
sys.exit(0)
