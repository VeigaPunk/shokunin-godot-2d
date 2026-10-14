"""frontier-pygame probe: headless pygame 2.6.1 surface measurement.

Arms (emit `PYGAME-ARM <arm> | k=v` lines, exact bytes where deterministic):
  cadence60   Clock.tick(60) capped loop — dt stats + get_fps
  cadence0    Clock.tick() uncapped — the LOVE-dtcadence analogue
  cadencebusy Clock.tick_busy_loop(60) — busy-wait variant
  popen       subprocess.Popen child stdout read latency, flushing child
  popen_buf   same child WITHOUT flush — stdio absorption window
  pump        N frames with zero event calls vs with pump() — queue retention
  iochild     (--io-child mode) two-line timed writer for parent-side capture
"""

import statistics
import subprocess
import sys
import time

import pygame


def emit(arm, **kv):
    print(f"PYGAME-ARM {arm} | " + " ".join(f"{k}={v}" for k, v in kv.items()),
          flush=True)


def iochild(mode):
    """Child for the parent-side capture probe. mode=buf|flush."""
    flush = mode == "flush"
    print("PYGAME-IOCHILD-1", flush=flush)
    time.sleep(0.20)
    print("PYGAME-IOCHILD-2", flush=flush)
    sys.exit(0)


def readline_timed(stream):
    t0 = time.perf_counter()
    line = stream.readline()
    return (time.perf_counter() - t0) * 1e3, line


def popen_arm(emit_name, child_argv):
    proc = subprocess.Popen(child_argv, stdout=subprocess.PIPE,
                            stderr=subprocess.DEVNULL, text=True)
    t_start = time.perf_counter()
    w1, l1 = readline_timed(proc.stdout)
    w2, l2 = readline_timed(proc.stdout)
    w_eof, rest = readline_timed(proc.stdout)
    proc.wait()
    total = (time.perf_counter() - t_start) * 1e3
    emit(emit_name,
         l1=l1.strip() or "EMPTY", l2=l2.strip() or "EMPTY",
         l1_wait_ms=round(w1, 2), l2_wait_ms=round(w2, 2),
         close_wait_ms=round(w_eof, 2), total_ms=round(total, 2),
         rest_len=len(rest), ret=proc.returncode)


def main():
    if "--io-child" in sys.argv:
        iochild(sys.argv[sys.argv.index("--io-child") + 1])
        return

    n = pygame.init()
    screen = pygame.display.set_mode((320, 240))
    emit("viability", init_pass=n[0], init_fail=n[1],
         driver=pygame.display.get_driver(),
         sdl=".".join(str(x) for x in pygame.get_sdl_version()),
         surf=pygame.display.get_surface().get_size(),
         flags=hex(pygame.display.get_surface().get_flags()))

    clock = pygame.time.Clock()

    # --- cadence60: tick(60) -------------------------------------------
    N = 240
    deltas = []
    prev = time.perf_counter()
    for _ in range(N):
        ret = clock.tick(60)
        now = time.perf_counter()
        deltas.append((now - prev) * 1e3)
        prev = now
    emit("cadence60", n=N,
         dt_mean_ms=round(statistics.fmean(deltas), 3),
         dt_min_ms=round(min(deltas), 3),
         dt_max_ms=round(max(deltas), 3),
         fps=round(clock.get_fps(), 2), last_tick_ret=ret)

    # --- cadence0: tick() uncapped --------------------------------------
    N = 1200
    deltas = []
    prev = time.perf_counter()
    t0 = prev
    for _ in range(N):
        ret = clock.tick()
        now = time.perf_counter()
        deltas.append((now - prev) * 1e3)
        prev = now
    emit("cadence0", n=N,
         dt_mean_ms=round(statistics.fmean(deltas), 3),
         dt_min_ms=round(min(deltas), 3),
         dt_max_ms=round(max(deltas), 3),
         hz=round(N / (prev - t0), 1), fps=round(clock.get_fps(), 1),
         last_tick_ret=ret)

    # --- cadencebusy: tick_busy_loop(60) --------------------------------
    N = 120
    deltas = []
    prev = time.perf_counter()
    for _ in range(N):
        ret = clock.tick_busy_loop(60)
        now = time.perf_counter()
        deltas.append((now - prev) * 1e3)
        prev = now
    emit("cadencebusy", n=N,
         dt_mean_ms=round(statistics.fmean(deltas), 3),
         dt_min_ms=round(min(deltas), 3),
         dt_max_ms=round(max(deltas), 3),
         fps=round(clock.get_fps(), 2), last_tick_ret=ret)

    # --- popen: flushing child ------------------------------------------
    popen_arm("popen",
              [sys.executable, "-u", "-c",
               "import time; print('CHILD-MARK-1',flush=True);"
               " time.sleep(0.12); print('CHILD-MARK-2',flush=True)"])

    # --- popen_buf: child that never flushes (block-buffered pipe) ------
    popen_arm("popen_buf",
              [sys.executable, "-c",
               "import time; print('CHILD-MARK-1');"
               " time.sleep(0.12); print('CHILD-MARK-2')"])

    # --- pump: frames without any event call, then with ------------------
    MYEVENT = pygame.USEREVENT + 1
    pygame.event.post(pygame.event.Event(MYEVENT, marker="posted"))
    prev = time.perf_counter()
    for _ in range(400):
        clock.tick(120)          # no pump(), no get() — pure cadence
    nopump_ms = (time.perf_counter() - prev) * 1e3
    queued = pygame.event.get()  # single drain at end
    mine = sum(1 for e in queued if e.type == MYEVENT)
    emit("pump", frames_nopump=400, nopump_total_ms=round(nopump_ms, 1),
         queued_after_nopump=len(queued), posted_survived=mine,
         posted_found_at_end=mine > 0)

    pygame.event.clear()
    prev = time.perf_counter()
    for _ in range(400):
        pygame.event.pump()
        clock.tick(120)
    withpump_ms = (time.perf_counter() - prev) * 1e3
    emit("pump2", frames_withpump=400,
         withpump_total_ms=round(withpump_ms, 1),
         queued_after_pump=len(pygame.event.get()))

    # --- flip cost headless ----------------------------------------------
    prev = time.perf_counter()
    for _ in range(200):
        pygame.display.flip()
    emit("flip", n=200,
         flip_mean_ms=round((time.perf_counter() - prev) * 1e3 / 200, 3))

    pygame.quit()
    print("PYGAME_PROBE_DONE", flush=True)


if __name__ == "__main__":
    main()
