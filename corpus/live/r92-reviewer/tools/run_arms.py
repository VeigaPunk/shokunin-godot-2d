#!/usr/bin/env python3
"""r92-reviewer fresh arm runner — the battery's exact launch shape:
    godot --headless --path <proj> --script res://tilemap_lattice.gd -- --arm=<a>
(no shell wrapper, subprocess.run, capture stdout/stderr separately, text=True).

Writes <out>/<arm>.rep<N>.{out,err,rc}. Optional --fps <N> inserts
`--fixed-fps N` before --script (opt-in cell, never the battery shape).
Optional --env KEY=VAL for XDG isolation.
"""
import argparse, concurrent.futures as cf, pathlib, subprocess, sys, time

ARMS = ["census", "atlas", "cells", "custom", "terrain", "pattern", "encoding",
        "fixinvalid", "srcids", "physics", "timing", "quadrant", "nav", "nullts"]


def run_one(godot, proj, out, arm, rep, fps=None, env=None, timeout=60):
    cmd = [godot, "--headless", "--path", str(proj)]
    if fps:
        cmd += ["--fixed-fps", str(fps)]
    cmd += ["--script", "res://tilemap_lattice.gd", "--", f"--arm={arm}"]
    t0 = time.time()
    proc = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout, env=env)
    dt = time.time() - t0
    stem = out / f"{arm}.rep{rep}"
    (out / f"{arm}.rep{rep}.out").write_text(proc.stdout)
    (out / f"{arm}.rep{rep}.err").write_text(proc.stderr)
    (out / f"{arm}.rep{rep}.rc").write_text(f"{proc.returncode}\n")
    return {"arm": arm, "rep": rep, "rc": proc.returncode, "seconds": round(dt, 3),
            "cmd": cmd}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--proj", type=pathlib.Path, required=True)
    ap.add_argument("--out", type=pathlib.Path, required=True)
    ap.add_argument("--godot", default="godot")
    ap.add_argument("--reps", type=int, default=5)
    ap.add_argument("--par", type=int, default=4)
    ap.add_argument("--fps", type=int, default=None)
    ap.add_argument("--arms", default=",".join(ARMS))
    ap.add_argument("--timeout", type=float, default=60)
    ap.add_argument("--log", type=pathlib.Path, default=None)
    args = ap.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)
    arms = [a for a in args.arms.split(",") if a]
    jobs = [(a, r) for a in arms for r in range(1, args.reps + 1)]
    log_lines = []
    with cf.ThreadPoolExecutor(max_workers=args.par) as ex:
        futs = {ex.submit(run_one, args.godot, args.proj, args.out, a, r,
                          args.fps, None, args.timeout): (a, r) for a, r in jobs}
        for fut in cf.as_completed(futs):
            rec = fut.result()
            line = (f"{rec['arm']}.rep{rec['rep']} rc={rec['rc']} "
                    f"t={rec['seconds']}s")
            log_lines.append(line)
            print(line, flush=True)
    if args.log:
        args.log.write_text("\n".join(sorted(log_lines)) + "\n")
    print(f"done: {len(jobs)} runs -> {args.out}")


if __name__ == "__main__":
    sys.exit(main())
