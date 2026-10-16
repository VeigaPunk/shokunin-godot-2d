#!/usr/bin/env python3
"""r93 verifier — is `--fixed-fps` a stabilizer for the mode cells?

The committed harness comment claims `--fixed-fps` collapses each frame-coupled
cell to one byte-stable value.  Measure it: 3 default reps and 3 `--fixed-fps 60`
reps for the 7 mode arms; report unique PASS lines per regime.
"""
import pathlib
import subprocess
import sys

V = pathlib.Path("/home/vgpnk/Projects/shokunin/game-dev-2d-shokunin/corpus/live/r93-verifier")
PROJ = V / "arms" / "proj"
GODOT = "/usr/bin/godot"
ARMS = [("anim_lattice.gd", "tweenproc"), ("anim_lattice.gd", "animproc"),
        ("r93b_anim.gd", "manual_inv"), ("r93b_anim.gd", "deferred"),
        ("r93b_anim.gd", "frame"), ("r93b_anim.gd", "blend"),
        ("r93b_anim.gd", "clock")]

out = []
for script, arm in ARMS:
    for regime, extra in (("default", []), ("ff60", ["--fixed-fps", "60"])):
        lines = []
        for rep in (1, 2, 3):
            try:
                proc = subprocess.run(
                    [GODOT, "--headless", *extra, "--path", str(PROJ),
                     "--script", f"res://{script}", "--", f"--arm={arm}"],
                    capture_output=True, text=True, timeout=8)
                txt = proc.stdout
            except subprocess.TimeoutExpired as exc:
                txt = (exc.stdout or b"").decode(errors="replace") if isinstance(exc.stdout, bytes) else (exc.stdout or "")
            pl = [ln for ln in txt.splitlines() if ln.startswith("PASS ")]
            lines.append(pl[0] if len(pl) == 1 else f"<{len(pl)} PASS lines>")
        uniq = len(set(lines))
        out.append(f"{script[:-3]}.{arm} {regime}: reps=3 unique_pass_lines={uniq}")
out.append("")
out.append("claim: ff60 collapses each mode cell to 1 unique line while default varies")
(V / "probes" / "ff-stabilizer.txt").write_text("\n".join(out) + "\n")
print("\n".join(out))
sys.exit(0)
