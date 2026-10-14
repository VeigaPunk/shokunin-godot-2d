"""r71 pygame_probe — headless pygame 2.6.1 battery probe.

Claim under test (r71 declared move): "stdout withholding is a
language-layer window bounded by buffer size" — Python block-buffers
piped stdout (~8KB), so an unflushed line is parent-invisible until the
buffer fills or the process exits. Falsifiable via a >8KB mid-run write
surfacing early, and via the flush edge NOT tracking the byte bound.

Emits `PYGAME-ARM <arm> | k=v` lines (flush=True); timings are measured
inside the process (perf_counter) so parent-side delivery order never
distorts them — same convention as love_probe/main.lua.

Battery modes (selected by argv, BEFORE pygame is imported):
  --io-child buf|flush        two-line timed writer for parent capture
  --wh-child N [--wh-init]    withholding-window child: line1 @~0ms,
                              N-byte payload @~200ms, line3 @~400ms,
                              exit @~600ms — all unflushed, single writes
  --wh-drip CHUNK,NCH,MS [--wh-init]
                              drip-feed child: line1, then NCH chunks of
                              CHUNK bytes spaced MS apart — finds the
                              exact byte count at which the stdio block
                              buffer tips (parent-visible flush point)
  --wh-init                   with either wh mode: pygame.init() +
                              set_mode first, so the edge is measured
                              with SDL fully loaded (vs pure-python)

Env the battery always sets: SDL_VIDEODRIVER=dummy
SDL_AUDIODRIVER=dummy PYGAME_HIDE_SUPPORT_PROMPT=1.
"""

import os
import statistics
import subprocess
import sys
import time

os.environ.setdefault("PYGAME_HIDE_SUPPORT_PROMPT", "1")

HERE = os.path.dirname(os.path.abspath(__file__))
WH_LINE1 = "PYGAME-WH-1\n"   # 12 bytes
WH_LINE3 = "PYGAME-WH-3\n"   # 12 bytes


def wh_init_pygame():
    import pygame
    pygame.init()
    pygame.display.set_mode((64, 64))


def wh_child(nbytes, init):
    """line1 (12B) @0 -> sleep 0.2 -> payload N B @~200 -> sleep 0.2 ->
    line3 (12B) @~400 -> sleep 0.2 -> exit @~600. All writes unflushed;
    parent-visible first-byte time identifies the flush edge:
    ~200ms = payload write flushed early, ~400ms = line3 tipped the
    buffer, ~600ms = withheld until exit."""
    if init:
        wh_init_pygame()
    w = sys.stdout.write
    w(WH_LINE1)
    time.sleep(0.2)
    if nbytes > 0:
        w("x" * nbytes)
    time.sleep(0.2)
    w(WH_LINE3)
    time.sleep(0.2)
    sys.exit(0)


def wh_drip(chunk, nchunks, ms, init):
    """line1 (12B) @0 -> sleep 0.15 -> NCH chunks of CHUNK bytes spaced
    MS apart -> line3 -> exit. The chunk index at which bytes first
    surface parent-side pins the block-buffer capacity exactly."""
    if init:
        wh_init_pygame()
    w = sys.stdout.write
    w(WH_LINE1)
    time.sleep(0.15)
    for _ in range(nchunks):
        w("y" * chunk)
        time.sleep(ms / 1000.0)
    w(WH_LINE3)
    time.sleep(0.3)   # wide tail: tip-vs-exit gap stays classifiable
    sys.exit(0)


def iochild(mode):
    """Two-line timed writer for parent-side capture. mode=buf|flush."""
    flush = mode == "flush"
    print("PYGAME-IOCHILD-1", flush=flush)
    time.sleep(0.20)
    print("PYGAME-IOCHILD-2", flush=flush)
    sys.exit(0)


def emit(arm, **kv):
    print(f"PYGAME-ARM {arm} | " + " ".join(f"{k}={v}" for k, v in kv.items()),
          flush=True)


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
    argv = sys.argv
    if "--wh-child" in argv:
        wh_child(int(argv[argv.index("--wh-child") + 1]),
                 "--wh-init" in argv)
        return
    if "--wh-drip" in argv:
        chunk, nch, ms = (int(x) for x in
                          argv[argv.index("--wh-drip") + 1].split(","))
        wh_drip(chunk, nch, ms, "--wh-init" in argv)
        return
    if "--io-child" in argv:
        iochild(argv[argv.index("--io-child") + 1])
        return

    import pygame

    n = pygame.init()
    pygame.display.set_mode((320, 240))
    emit("viability", init_pass=n[0], init_fail=n[1],
         driver=pygame.display.get_driver(),
         pygame_ver=pygame.version.ver,
         sdl=".".join(str(x) for x in pygame.get_sdl_version()),
         surf="x".join(str(v) for v in
                       pygame.display.get_surface().get_size()),
         flags=hex(pygame.display.get_surface().get_flags()))

    clock = pygame.time.Clock()

    # --- cadence60: tick(60) — bound-pinned, never 60.00 --------------
    N = 240
    deltas = []
    prev = time.perf_counter()
    t0 = prev
    for _ in range(N):
        ret = clock.tick(60)
        now = time.perf_counter()
        deltas.append((now - prev) * 1e3)
        prev = now
    emit("cadence60", n=N,
         dt_mean_ms=round(statistics.fmean(deltas), 3),
         dt_min_ms=round(min(deltas), 3),
         dt_max_ms=round(max(deltas), 3),
         eff_hz=round(N / (prev - t0), 2),
         fps=round(clock.get_fps(), 2), last_tick_ret=ret)

    # --- cadence0: tick() uncapped — MHz-scale bare loop --------------
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

    # --- cadencebusy: tick_busy_loop(60) -------------------------------
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

    # --- popen: flushing child (python -u) — writer-bound pipe --------
    popen_arm("popen",
              [sys.executable, "-u", "-c",
               "import time; print('CHILD-MARK-1',flush=True);"
               " time.sleep(0.12); print('CHILD-MARK-2',flush=True)"])

    # --- popen_buf: same child, no flush — withholding window in
    #     direction 1: both lines land in one burst at child exit ------
    popen_arm("popen_buf",
              [sys.executable, "-c",
               "import time; print('CHILD-MARK-1');"
               " time.sleep(0.12); print('CHILD-MARK-2')"])

    # --- pump: 400 frames, zero event calls — pump-free headless ------
    MYEVENT = pygame.USEREVENT + 1
    pygame.event.post(pygame.event.Event(MYEVENT, marker="posted"))
    prev = time.perf_counter()
    for _ in range(400):
        clock.tick(120)
    nopump_ms = (time.perf_counter() - prev) * 1e3
    queued = pygame.event.get()
    mine = sum(1 for e in queued if e.type == MYEVENT)
    emit("pump", frames_nopump=400, nopump_total_ms=round(nopump_ms, 1),
         queued_after_nopump=len(queued), posted_survived=mine,
         posted_found_at_end=str(mine > 0).lower())

    pygame.event.clear()
    prev = time.perf_counter()
    for _ in range(400):
        pygame.event.pump()
        clock.tick(120)
    withpump_ms = (time.perf_counter() - prev) * 1e3
    emit("pump2", frames_withpump=400,
         withpump_total_ms=round(withpump_ms, 1),
         queued_after_pump=len(pygame.event.get()))

    # --- quitpoll: no spontaneous QUIT headless (~0.6s) ---------------
    pygame.event.clear()
    quits = 0
    deadline = time.perf_counter() + 0.6
    while time.perf_counter() < deadline:
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                quits += 1
        time.sleep(0.01)
    emit("quitpoll", window_ms=600, quits_seen=quits)

    # --- flip cost headless -------------------------------------------
    prev = time.perf_counter()
    for _ in range(200):
        pygame.display.flip()
    emit("flip", n=200,
         flip_mean_ms=round((time.perf_counter() - prev) * 1e3 / 200, 3))

    pygame.quit()
    print("PYGAME_PROBE_DONE", flush=True)


if __name__ == "__main__":
    main()
