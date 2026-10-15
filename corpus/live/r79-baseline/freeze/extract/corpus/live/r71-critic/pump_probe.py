"""r71-critic pump/QUIT cell: does the headless dummy queue behave as the
frontier claims (no spontaneous QUIT; posted event survives 400 pump-free
frames; event.get() pumps implicitly)?

Usage: SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy \
       PYGAME_HIDE_SUPPORT_PROMPT=1 python3 pump_probe.py <tag>
"""
import json
import sys
import time
from pathlib import Path

import pygame

HERE = Path(__file__).resolve().parent


def main():
    tag = sys.argv[1] if len(sys.argv) > 1 else "idle"
    init = pygame.init()
    pygame.display.set_mode((320, 240))
    MY = pygame.USEREVENT + 1
    pygame.event.clear()
    pygame.event.post(pygame.event.Event(MY, marker="posted"))
    clock = pygame.time.Clock()
    prev = time.perf_counter()
    for _ in range(400):
        clock.tick(120)                 # no pump(), no get()
    nopump_ms = (time.perf_counter() - prev) * 1e3
    evs = pygame.event.get()            # implicit pump here
    survived = sum(1 for e in evs if e.type == MY)

    # QUIT poll: pump via get() for 0.5s — anything spontaneous?
    t0 = time.perf_counter()
    types = []
    while time.perf_counter() - t0 < 0.5:
        for e in pygame.event.get():
            types.append(int(e.type))
        time.sleep(0.005)

    prev = time.perf_counter()
    for _ in range(200):
        pygame.display.flip()
    flip_ms = (time.perf_counter() - prev) * 1e3 / 200

    out = {"tag": tag, "init": list(init), "nopump_total_ms":
           round(nopump_ms, 1), "queued_after_nopump": len(evs),
           "posted_survived": survived, "events_0p5s": types,
           "quit_seen": 256 in types, "flip_mean_ms": round(flip_ms, 3)}
    pygame.quit()
    print(json.dumps(out))
    (HERE / ("pump.%s.json" % tag)).write_text(json.dumps(out, indent=2) + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
