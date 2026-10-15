"""r71 reviewer scratch: independent pygame reference probe (arms a/c/d).

Not the author's fixture — reviewer-side cross-check of the r71 claims:
  cadence   : tick(60), tick(120), busy_loop(60), uncapped tick()
  popen     : Popen writer-bound + byte-exact (LOVE-shape confirmation)
  pump      : 400-frame tick(120) loop with zero event calls
Emits ARM lines in the corpus convention for easy diffing.
Env: SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy PYGAME_HIDE_SUPPORT_PROMPT=1
"""
import os
import subprocess
import sys
import time

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame  # noqa: E402

OUT = []


def emit(arm, kv):
    OUT.append("PYGAME-ARM %s | %s" % (
        arm, " ".join("%s=%s" % (k, v) for k, v in sorted(kv.items()))))


def stats(dts):
    return {"n": len(dts),
            "dt_mean_ms": "%.3f" % (sum(dts) / len(dts) * 1000),
            "dt_min_ms": "%.3f" % (min(dts) * 1000),
            "dt_max_ms": "%.3f" % (max(dts) * 1000)}


def cadence():
    pygame.init()
    scr = pygame.display.set_mode((320, 240))
    emit("init", {"driver": pygame.display.get_driver(),
                  "flags": hex(scr.get_flags())})
    clock = pygame.time.Clock()

    for fps, n in ((60, 240), (120, 240)):
        dts = []
        for _ in range(n):
            t0 = time.perf_counter()
            clock.tick(fps)
            dts.append(time.perf_counter() - t0)
        emit("tick%d" % fps, stats(dts))

    dts = []
    for _ in range(120):
        t0 = time.perf_counter()
        clock.tick_busy_loop(60)
        dts.append(time.perf_counter() - t0)
    emit("busy60", stats(dts))

    n = 200000
    t0 = time.perf_counter()
    for _ in range(n):
        clock.tick()
    wall = time.perf_counter() - t0
    emit("uncapped", {"n": n, "wall_ms": "%.1f" % (wall * 1000),
                      "hz": "%.0f" % (n / wall),
                      "tick_ret": clock.tick()})


def popen():
    cmd = ["sh", "-c", "echo CHILD-MARK-1; sleep 0.12; echo CHILD-MARK-2"]
    t0 = time.perf_counter()
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, text=True)
    t_open = time.perf_counter() - t0
    r1 = time.perf_counter()
    l1 = p.stdout.readline().strip()
    l1_wait = time.perf_counter() - r1
    r2 = time.perf_counter()
    l2 = p.stdout.readline().strip()
    l2_wait = time.perf_counter() - r2
    r3 = time.perf_counter()
    rest = p.stdout.read()
    close_wait = time.perf_counter() - r3
    p.wait()
    total = time.perf_counter() - t0
    emit("popen", {"l1": l1, "l2": l2, "rest_len": len(rest),
                   "open_ms": "%.2f" % (t_open * 1000),
                   "l1_wait_ms": "%.2f" % (l1_wait * 1000),
                   "l2_wait_ms": "%.2f" % (l2_wait * 1000),
                   "close_wait_ms": "%.2f" % (close_wait * 1000),
                   "total_ms": "%.2f" % (total * 1000)})


def pump_free():
    clock = pygame.time.Clock()
    n = 400
    t0 = time.perf_counter()
    for _ in range(n):
        clock.tick(120)
        # zero event calls: no pump/get/post
    wall = time.perf_counter() - t0
    ev = pygame.event.get()
    emit("pump", {"frames": n, "wall_ms": "%.1f" % (wall * 1000),
                  "pump_calls": 0, "events_after": len(ev),
                  "pump_needed": "false"})


def main():
    cadence()
    popen()
    pump_free()
    pygame.quit()
    for line in OUT:
        print(line, flush=True)
    print("PYGAME_REF_DONE", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
