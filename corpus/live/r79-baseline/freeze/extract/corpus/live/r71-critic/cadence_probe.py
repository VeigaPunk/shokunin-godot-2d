"""r71-critic cadence probe: tick(60) / uncapped / tick_busy_loop stats.

Run once idle and once under full-core load; the point is whether the
round-71 proposed cadence bounds (~62Hz capped, MHz uncapped) survive
host load, and whether a spontaneous SDL QUIT ever arrives headless.

Usage: SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy \
       PYGAME_HIDE_SUPPORT_PROMPT=1 python3 cadence_probe.py <tag>
"""
import json
import statistics
import sys
import time
from pathlib import Path

import pygame

HERE = Path(__file__).resolve().parent


def loop(n, fps=None, busy=False):
    clock = pygame.time.Clock()
    deltas = []
    prev = time.perf_counter()
    t0 = prev
    for _ in range(n):
        if busy:
            ret = clock.tick_busy_loop(fps)
        elif fps is None:
            ret = clock.tick()
        else:
            ret = clock.tick(fps)
        now = time.perf_counter()
        deltas.append((now - prev) * 1e3)
        prev = now
    return {"n": n, "total_ms": round((prev - t0) * 1e3, 1),
            "hz": round(n / (prev - t0), 1),
            "mean": round(statistics.fmean(deltas), 3),
            "min": round(min(deltas), 3), "max": round(max(deltas), 3),
            "p50": round(statistics.median(deltas), 3),
            "last_ret": ret}


def main():
    tag = sys.argv[1] if len(sys.argv) > 1 else "idle"
    init = pygame.init()
    surf = pygame.display.set_mode((320, 240))
    out = {"tag": tag, "init": list(init),
           "driver": pygame.display.get_driver(),
           "pygame": pygame.version.ver,
           "sdl": list(pygame.get_sdl_version()),
           "surf": surf.get_size(), "flags": hex(surf.get_flags())}
    out["tick60"] = loop(240, 60, False)
    out["uncapped"] = loop(1200, None, False)
    out["busy60"] = loop(120, 60, True)

    # spontaneous QUIT poll: does anything arrive in 0.5s of idle frames?
    t0 = time.perf_counter()
    seen = []
    while time.perf_counter() - t0 < 0.5:
        for e in pygame.event.get():
            seen.append(int(e.type))
        time.sleep(0.005)
    out["events_0p5s_idle"] = seen

    pygame.quit()
    print(json.dumps(out))
    (HERE / ("cadence.%s.json" % tag)).write_text(json.dumps(out, indent=2) + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
