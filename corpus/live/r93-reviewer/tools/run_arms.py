#!/usr/bin/env python3
"""r93-reviewer fresh arm runner — the battery's exact launch shape:

    godot --headless --path <proj> --script res://<script> -- --arm=<a>

(no shell wrapper, subprocess.run, stdout/stderr captured separately, text=True)
Writes <out>/<arm>.rep<N>.{out,err,rc}. Optional --fps N inserts `--fixed-fps N`
before --script (opt-in cell, never the battery shape).
"""
import argparse
import concurrent.futures as cf
import pathlib
import subprocess
import sys
import time

A = "anim_lattice.gd"
B = "r93b_anim.gd"
ARMS = [(A, a) for a in ["census", "tweenval", "tweenval_grid", "tweenstep",
                         "tweenchain", "tweenproc", "animseek", "animmethod",
                         "animtrack", "animblend", "animproc"]] + \
       [(B, a) for a in ["clock", "manual_inv", "frame", "deferred", "purity", "blend"]]


def run_one(godot, proj, out, script, arm, rep, fps=None, timeout=60):
    cmd = [godot, "--headless", "--path", str(proj)]
    if fps:
        cmd += ["--fixed-fps", str(fps)]
    cmd += ["--script", f"res://{script}", "--", f"--arm={arm}"]
    t0 = time.time()
    proc = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
    dt = time.time() - t0
    (out / f"{arm}.rep{rep}.out").write_text(proc.stdout)
    (out / f"{arm}.rep{rep}.err").write_text(proc.stderr)
    (out / f"{arm}.rep{rep}.rc").write_text(f"{proc.returncode}\n")
    return {"arm": arm, "script": script, "rep": rep, "rc": proc.returncode,
            "seconds": round(dt, 3), "cmd": cmd}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--proj", type=pathlib.Path, required=True)
    ap.add_argument("--out", type=pathlib.Path, required=True)
    ap.add_argument("--godot", default="godot")
    ap.add_argument("--reps", type=int, default=5)
    ap.add_argument("--par", type=int, default=4)
    ap.add_argument("--fps", type=int, default=None)
    ap.add_argument("--only", default=None, help="comma list of arm names")
    ap.add_argument("--timeout", type=float, default=60)
    ap.add_argument("--log", type=pathlib.Path, default=None)
    args = ap.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)
    jobs = [(s, a) for (s, a) in ARMS if not args.only or a in args.only.split(",")]
    jobs = [(s, a, r) for (s, a) in jobs for r in range(1, args.reps + 1)]
    lines = []
    with cf.ThreadPoolExecutor(max_workers=args.par) as ex:
        futs = {ex.submit(run_one, args.godot, args.proj, args.out, s, a, r,
                          args.fps, args.timeout): (s, a, r) for s, a, r in jobs}
        for fut in cf.as_completed(futs):
            rec = fut.result()
            line = f"{rec['script']}:{rec['arm']}.rep{rec['rep']} rc={rec['rc']} t={rec['seconds']}s"
            lines.append(line)
            print(line, flush=True)
    if args.log:
        args.log.write_text("\n".join(sorted(lines)) + "\n")
    print(f"done: {len(jobs)} runs -> {args.out}")


if __name__ == "__main__":
    sys.exit(main())
