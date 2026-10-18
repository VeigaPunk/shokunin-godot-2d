#!/usr/bin/env python3
"""r102-ver9 focused counterfactual: 6 interleaved reps per side for the
three audio rows whose raw stdout differed in the main matrix. If the diffs
are fold-caused, values split cleanly per side; if wall-clock noise, the
value sets interleave on both sides.
"""
import ast, subprocess, time
from pathlib import Path

REPO = Path("/home/vgpnk/Projects/shokunin/game-dev-2d-shokunin")
WORK = Path("/var/tmp/r102-ver9")
GODOT = "/usr/bin/godot"
TARGETS = ["r99_audio_finish", "r99_audio_gen", "r99_audio_pause"]

src = (REPO / "corpus/fixtures/run_battery.py").read_text()
tree = ast.parse(src)
cases = None
for node in tree.body:
    if isinstance(node, ast.Assign) and any(getattr(t, "id", None) == "CASES" for t in node.targets):
        cases = ast.literal_eval(node.value)
        break
rows = {c[0]: (c[1], list(c[2])) for c in cases if c[0] in TARGETS}
assert set(rows) == set(TARGETS), rows.keys()

KEYS = {"r99_audio_finish": ["fin_us", "frames"],
        "r99_audio_gen": ["skips_dry"],
        "r99_audio_pause": ["a", "b", "c", "d"]}


def run(proj, script, flags):
    cmd = [GODOT, "--headless", "--path", str(proj),
           "--script", "res://" + script, "--", *flags]
    p = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
    assert p.returncode == 0, (p.returncode, p.stderr[-400:])
    return p.stdout


def pick(out, keys):
    vals = {}
    for token in out.replace("|", " ").split():
        if "=" in token:
            k, v = token.split("=", 1)
            if k in keys:
                vals.setdefault(k, []).append(v)
    return vals


for name in TARGETS:
    script, flags = rows[name]
    print("==", name, flags)
    for rep in range(1, 7):
        for side, proj in (("base", WORK / "proj_base"), ("fold", WORK / "proj_folded")):
            t0 = time.time()
            out = run(proj, script, flags)
            vals = pick(out, KEYS[name])
            print(f"  rep{rep} {side:4s} {vals}  ({time.time()-t0:.1f}s)")
