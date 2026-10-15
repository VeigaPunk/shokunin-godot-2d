#!/usr/bin/env python3
"""r88-critic seat runner: fresh arm executions in the battery's launch shape.

Seat-owned scratch only. Every godot launch is bounded by `timeout -s KILL`.
Usage:
  python3 run_arms.py --tag T --arms mp_loopback,audio_pos --reps 6 [--load N]
  python3 run_arms.py --tag T --arms mp_loopback --concurrent 3
"""
import argparse
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
PROJ = HERE / "proj"
GODOT = "/usr/bin/godot"


def launch(arm, out_prefix, hog_note, script="r88_surfaces.gd"):
    out = Path(f"{out_prefix}.out")
    err = Path(f"{out_prefix}.err")
    rc = Path(f"{out_prefix}.rc")
    wall = Path(f"{out_prefix}.wall")
    cmd = ["timeout", "-s", "KILL", "20", GODOT, "--headless",
           "--path", str(PROJ), "--script", f"res://{script}",
           "--", f"--arm={arm}"]
    t0 = time.monotonic()
    with out.open("w") as fo, err.open("w") as fe:
        p = subprocess.run(cmd, stdout=fo, stderr=fe)
    dt = time.monotonic() - t0
    rc.write_text(f"{p.returncode}\n")
    wall.write_text(f"{dt:.2f}\n")
    return p.returncode, dt


def start_hogs(n):
    procs = []
    for _ in range(n):
        procs.append(subprocess.Popen(["yes"], stdout=subprocess.DEVNULL,
                                      stderr=subprocess.DEVNULL))
    return procs


def stop_hogs(procs):
    for p in procs:
        p.kill()
    for p in procs:
        p.wait()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tag", required=True)
    ap.add_argument("--arms", required=True)
    ap.add_argument("--reps", type=int, default=1)
    ap.add_argument("--load", type=int, default=0, help="number of `yes` hogs")
    ap.add_argument("--concurrent", type=int, default=0)
    ap.add_argument("--script", default="r88_surfaces.gd")
    args = ap.parse_args()
    arms = [a for a in args.arms.split(",") if a]
    base = HERE / "runs" / args.tag
    base.mkdir(parents=True, exist_ok=True)
    hogs = start_hogs(args.load) if args.load else []
    if hogs:
        print(f"hogs={len(hogs)}", flush=True)
    try:
        for arm in arms:
            if args.concurrent:
                procs = []
                for k in range(args.concurrent):
                    pre = base / f"conc_{arm}.{k}"
                    cmd = ["timeout", "-s", "KILL", "20", GODOT, "--headless",
                           "--path", str(PROJ), "--script", f"res://{args.script}",
                           "--", f"--arm={arm}"]
                    fo = open(f"{pre}.out", "w")
                    fe = open(f"{pre}.err", "w")
                    procs.append((k, subprocess.Popen(cmd, stdout=fo, stderr=fe), fo, fe, pre))
                for k, p, fo, fe, pre in procs:
                    p.wait()
                    fo.close(); fe.close()
                    (pre.with_suffix(".rc")).write_text(f"{p.returncode}\n")
                    print(f"{args.tag} {arm} conc{k} rc={p.returncode}", flush=True)
            else:
                for r in range(args.reps):
                    pre = base / f"{arm}.{r}"
                    rc, dt = launch(arm, pre, args.load, args.script)
                    print(f"{args.tag} {arm} rep{r} rc={rc} wall={dt:.2f}", flush=True)
    finally:
        stop_hogs(hogs)


if __name__ == "__main__":
    sys.exit(main())
