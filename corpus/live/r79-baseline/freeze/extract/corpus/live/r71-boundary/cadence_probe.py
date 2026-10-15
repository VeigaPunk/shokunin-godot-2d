"""r71-boundary scratch: pygame Clock cadence knife-edges.

Pins the measured pacing lattice for the battery's bound-pins:
  - tick(fps) sleeps int(1000/fps) ms -> every fps is really a *bound*
  - the pacing cutoff: fps > 1000 -> delay 0 -> bare-loop spin
  - tick()/tick(0)/tick(-1) uncapped spin vs tick_busy_loop tails

Run: SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy PYGAME_HIDE_SUPPORT_PROMPT=1 \
     python3 cadence_probe.py
"""

import os
import time

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
os.environ.setdefault("PYGAME_HIDE_SUPPORT_PROMPT", "1")

import pygame  # noqa: E402

pygame.init()
pygame.display.set_mode((64, 64))
clock = pygame.time.Clock()


def run(label, fps, n, busy=False):
    dts = []
    rets = {}
    for _ in range(n):
        t0 = time.perf_counter()
        if busy:
            ret = clock.tick_busy_loop(fps)
        elif fps is None:
            ret = clock.tick()
        else:
            ret = clock.tick(fps)
        dt = (time.perf_counter() - t0) * 1e3
        dts.append(dt)
        rets[ret] = rets.get(ret, 0) + 1
    mean = sum(dts) / len(dts)
    print(f"PYGAME-ARM cadence | cell={label} fps={fps} n={n} "
          f"dt_mean_ms={mean:.4f} dt_min_ms={min(dts):.4f} "
          f"dt_max_ms={max(dts):.4f} hz={1000.0/mean:.2f} "
          f"get_fps={clock.get_fps():.2f} tick_rets={sorted(rets.items())[:6]}")


def main():
    print(f"PYGAME-ARM cadence_env | python={os.sys.version.split()[0]} "
          f"pygame={pygame.version.ver} sdl={'.'.join(map(str, pygame.get_sdl_version()))}")

    # nominal-fps lattice: each fps -> observed period
    run("tick60_a", 60, 150)
    run("tick60_b", 60, 150)
    run("tick60_c", 60, 150)
    run("tick30", 30, 60)
    run("tick59p94", 59.94, 150)
    run("tick100", 100, 300)
    run("tick120", 120, 300)
    run("tick144", 144, 300)
    run("tick240", 240, 300)

    # truncation edge: int(1000/fps) == 1 for fps in (500, 1000], 0 above
    run("tick500", 500, 300)
    run("tick999", 999, 300)
    run("tick1000", 1000, 300)
    run("tick1001", 1001, 300)
    run("tick2000", 2000, 300)

    # zero / negative / no-arg
    run("tick0", 0, 5000)
    run("tickneg", -1, 5000)
    run("ticknone", None, 5000)

    # busy-loop tails
    run("busy60", 60, 150, busy=True)
    run("busy1000", 1000, 300, busy=True)

    # timer granularity floor
    t0 = time.perf_counter()
    t_prev = pygame.time.get_ticks()
    distinct = []
    while time.perf_counter() - t0 < 0.05:
        t = pygame.time.get_ticks()
        if t != t_prev:
            distinct.append(t)
            t_prev = t
    print(f"PYGAME-ARM timer | get_ticks_type={type(pygame.time.get_ticks()).__name__} "
          f"distinct_values_in_50ms={len(distinct)}")

    print("CADENCE_PROBE_DONE")


if __name__ == "__main__":
    main()
