#!/usr/bin/env python3
"""r94 scribe fresh single-arm receipts from the COMMITTED bytes.

Runs the landed fixture (`corpus/fixtures/particles_lattice.gd` == HEAD, sha
0701e813…) from a git-archive extract, in an out-of-repo scratch project, in the
battery's launch shape (`godot --headless --path <proj> --script
res://particles_lattice.gd -- --arm=<arm>`), bounded `timeout -s KILL 25`.

  * 19 arms x 3 reps, default 60 tps            -> fresh/
  * cpu_pause / cpu_lifetime / cpu_request x 3  -> fresh-ff30/  (--fixed-fps 30)
  * cpu_pause / cpu_lifetime / cpu_request x 3  -> fresh-ff60/  (--fixed-fps 60)

Receipts: <script>.<arm>.<mode>.rep<N>.{out,err,rc}
"""
import os
import shutil
import subprocess
import sys
from pathlib import Path

EXTRACT = Path("/home/vgpnk/r94-committed-extract")
REPO = Path("/home/vgpnk/Projects/shokunin/game-dev-2d-shokunin")
LANE = REPO / "corpus/live/r94-scribe"
PROJ = Path("/home/vgpnk/r94-scribe-fresh-proj")

ARMS = ["census", "ppm", "convert", "cpu_lifetime", "cpu_expl", "cpu_speed_pre",
        "cpu_stop", "cpu_never", "cpu_contam", "cpu_oneshot_off",
        "cpu_oneshot_flag", "cpu_pause", "cpu_restart", "cpu_retrigger",
        "cpu_lt_mid", "cpu_speed_mid", "cpu_amount_mid", "cpu_request",
        "gpu_headless"]


def prepare():
    if PROJ.exists():
        shutil.rmtree(PROJ)
    PROJ.mkdir(parents=True)
    for f in ("project.godot", "particles_lattice.gd"):
        shutil.copy2(EXTRACT / "corpus/fixtures" / f, PROJ / f)
    (LANE / "fresh").mkdir(parents=True, exist_ok=True)


def run(arm, rep, mode, outdir):
    outdir.mkdir(parents=True, exist_ok=True)
    cmd = ["timeout", "-s", "KILL", "25", "/usr/bin/godot", "--headless",
           "--path", str(PROJ), "--script", "res://particles_lattice.gd", "--",
           f"--arm={arm}"]
    if mode != "default":
        cmd[6:6] = ["--fixed-fps", mode.replace("ff", "")]
    env = os.environ.copy()
    env["XDG_DATA_HOME"] = str(PROJ / "xdg-data")
    p = subprocess.run(cmd, capture_output=True, text=True, env=env)
    stem = outdir / f"particles_lattice.{arm}.{mode}.rep{rep}"
    Path(str(stem) + ".out").write_text(p.stdout)
    Path(str(stem) + ".err").write_text(p.stderr)
    Path(str(stem) + ".rc").write_text(str(p.returncode) + "\n")
    return p.returncode, len(p.stderr)


def main():
    prepare()
    bad = []
    for arm in ARMS:
        for rep in (1, 2, 3):
            rc, err = run(arm, rep, "default", LANE / "fresh")
            if rc != 0 or err:
                bad.append((arm, "default", rep, rc, err))
    for mode in ("ff30", "ff60"):
        for arm in ("cpu_pause", "cpu_lifetime", "cpu_request"):
            for rep in (1, 2, 3):
                rc, err = run(arm, rep, mode, LANE / f"fresh-{mode}")
                if rc != 0 or err:
                    bad.append((arm, mode, rep, rc, err))
    print("bad runs:", bad if bad else "none")
    print("receipts:", len(list((LANE / 'fresh').glob('*.out'))),
          len(list((LANE / 'fresh-ff30').glob('*.out'))),
          len(list((LANE / 'fresh-ff60').glob('*.out'))))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
