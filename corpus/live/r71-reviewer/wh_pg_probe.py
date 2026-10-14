"""r71 reviewer scratch: pygame-initialized withholding child + monitor.

Child modes (argv):
  wh N          : L1 unflushed @~0ms; N-byte payload unflushed @~200ms;
                  L3 unflushed @~400ms; exit ~600ms
  wh N --init   : pygame.init()+set_mode first (SDL fully loaded)
  drip C K MS   : L1 unflushed; K chunks of C bytes spaced MS ms; exit
Parent: monitor stdout visibility with perf_counter timeline.

Usage: python3 wh_pg_probe.py [--reps N]
"""
import argparse
import json
import os
import select
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent

CHILD = r'''
import os, sys, time
args = sys.argv[1:]
mode = args[0]
init = "--init" in args
if init:
    os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
    os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
    os.environ.setdefault("PYGAME_HIDE_SUPPORT_PROMPT", "1")
    import pygame
    pygame.init()
    pygame.display.set_mode((320, 240))
out = sys.stdout
t0 = time.monotonic()
if mode == "wh":
    n = int(args[1])
    out.write("WH-L1\n")
    time.sleep(0.200)
    if n > 0:
        out.write("P" * n)
    time.sleep(0.200)
    out.write("\nWH-L3\n")
elif mode == "drip":
    c, k, ms = int(args[1]), int(args[2]), float(args[3])
    out.write("WH-L1\n")
    for _ in range(k):
        time.sleep(ms / 1000.0)
        out.write("P" * c)
sys.exit(0)
'''


def monitor(env_extra, cmd, timeout=15.0):
    env = dict(os.environ)
    env.update(env_extra)
    t0 = time.perf_counter()
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                         env=env)
    fd = p.stdout.fileno()
    os.set_blocking(fd, False)
    ev, cum = [], 0
    while True:
        r, _, _ = select.select([fd], [], [], 0.002)
        if r:
            c = os.read(fd, 1 << 20)
            t = (time.perf_counter() - t0) * 1000.0
            if c == b"":
                break
            cum += len(c)
            ev.append([round(t, 3), len(c), cum])
        if time.perf_counter() - t0 > timeout:
            p.kill()
            break
    p.wait()
    return {"events": ev, "total": cum}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--reps", type=int, default=2)
    args = ap.parse_args()
    child = [sys.executable, "-c", CHILD]
    envx = {}
    rows = []
    for rep in range(args.reps):
        for label, spec, env_extra in [
                ("wh0", ["wh", "0"], {}),
                ("wh0_init", ["wh", "0", "--init"], {}),
                ("wh8k", ["wh", "8192"], {}),
                ("wh8k_init", ["wh", "8192", "--init"], {}),
                ("wh128k", ["wh", "131072"], {}),
                ("wh128k_init", ["wh", "131072", "--init"], {}),
                ("drip1000x135", ["drip", "1000", "135", "5"], {}),
        ]:
            m = monitor(env_extra, child + spec)
            ev = m["events"]
            first = ev[0][0] if ev else None
            n_early = sum(n for t, n, c in ev if t < 550.0)
            rows.append({"label": label, "rep": rep,
                         "first_ms": first,
                         "early_bytes": n_early,
                         "total": m["total"],
                         "events": ev})
    (HERE / "wh_pg_receipts.json").write_text(json.dumps(rows, indent=2) + "\n")
    for r in rows:
        print(f"{r['label']:14s} rep{r['rep']} first={r['first_ms']}ms "
              f"early(<550ms)={r['early_bytes']} total={r['total']} "
              f"events={[(t, n) for t, n, c in r['events']]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
