#!/usr/bin/env python3
"""r91 reviewer — fresh arm runs in the battery's exact launch shape.

  run_arms.py --proj <godot project dir> --out <receipt dir> --reps N [--fps F]
              [--par K] [--arms a,b,c]

Launch shape is the committed harness's:
  timeout -s KILL 25 godot --headless --path <proj> --script res://<script> -- <flags>
(+ optional `--fixed-fps F` inserted the way the r91-boundary seat ran it: as a
Godot CLI flag before `--path`).
Writes <out>/<arm>.rep<i>.{out,err,rc} plus a wall-clock file.
"""
import argparse
import pathlib
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor

ARMS = ["census", "path", "query", "sync", "region", "agent", "avoid", "bake", "link",
        "teardown_crash", "teardown_clean"]


def run_one(godot, proj, arm, fps, timeout=25):
    cmd = [godot, "--headless"]
    if fps:
        cmd += ["--fixed-fps", str(fps)]
    cmd += ["--path", str(proj), "--script", "res://nav_lattice.gd", "--", f"--arm={arm}"]
    t0 = time.time()
    try:
        p = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        out, err, rc, terr = p.stdout, p.stderr, p.returncode, None
    except subprocess.TimeoutExpired as exc:
        out = (exc.stdout or b"").decode(errors="replace") if isinstance(exc.stdout, bytes) else (exc.stdout or "")
        err = (exc.stderr or b"").decode(errors="replace") if isinstance(exc.stderr, bytes) else (exc.stderr or "")
        rc, terr = None, "TIMEOUT"
    return arm, out, err, rc, time.time() - t0, terr


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--proj", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--godot", default="godot")
    ap.add_argument("--reps", type=int, default=1)
    ap.add_argument("--fps", type=int, default=0)
    ap.add_argument("--par", type=int, default=1)
    ap.add_argument("--arms", default=",".join(ARMS))
    args = ap.parse_args()
    outdir = pathlib.Path(args.out)
    outdir.mkdir(parents=True, exist_ok=True)
    arms = args.arms.split(",")
    jobs = [(arm, i) for i in range(args.reps) for arm in arms]
    wall = []
    with ThreadPoolExecutor(max_workers=args.par) as ex:
        futs = {ex.submit(run_one, args.godot, args.proj, arm, args.fps): (arm, i) for arm, i in jobs}
        for fut in futs:
            arm, i = futs[fut]
            a, out, err, rc, dt, terr = fut.result()
            tag = f"{a}.rep{i}"
            (outdir / f"{tag}.out").write_text(out)
            (outdir / f"{tag}.err").write_text(err)
            (outdir / f"{tag}.rc").write_text(("" if rc is None else str(rc)) + "\n")
            (outdir / f"{tag}.wall").write_text(f"{dt:.3f}\n")
            wall.append((tag, dt, terr))
            print(f"{tag}: rc={rc} {terr or ''} wall={dt:.2f}s stale={'STALE' in out}", flush=True)
    print(f"total runs: {len(wall)}  slowest: {max(w for _, w, _ in wall):.2f}s")
    return 0


if __name__ == "__main__":
    sys.exit(main())
