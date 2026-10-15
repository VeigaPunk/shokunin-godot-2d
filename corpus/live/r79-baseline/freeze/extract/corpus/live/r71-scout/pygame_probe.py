"""r71 scout — pygame 2.6.1 headless probe (PROTOTYPE for
corpus/fixtures/pygame_probe.py; sibling to love_probe/main.lua + run_battery).

Headless profile is owned by the fixture: SDL_VIDEODRIVER=dummy +
SDL_AUDIODRIVER=dummy + PYGAME_HIDE_SUPPORT_PROMPT=1, forced before
`import pygame` (frontier-pygame: dummy is the only hard requirement;
the support banner writes to stdout unless hidden; the avx2
RuntimeWarning always lands on stderr).

Arms (emit `PYGAME-ARM <arm> | k=v` lines, exact bytes where
deterministic, values space-free for the whitespace kv parser):
  viability    init counts, driver, sdl, surf=WxH, flags
  cadence60    Clock.tick(60) x240 — bound-pinned (~62Hz, never 60.00)
  cadence120   Clock.tick(120) x240 — ~124Hz
  cadence0     Clock.tick() uncapped x1200 — bare-loop MHz spin
  cadencebusy  Clock.tick_busy_loop(60) x120 — tighter tail
  popen        flushing child — writer-bound visibility, byte-exact
  popen_buf    unflushed child — stdio withholding at small scale
  pump         x400 frames, zero event calls; posted event survives
  pump2        x400 frames with pump() — cadence parity
  flip         display.flip() no-op cost headless
  withhold_*   unflushed-write matrix: flush edge = Python stdio buffer
               (single write >= io.DEFAULT_BUFFER_SIZE bypasses the
               buffer; accumulated writes do NOT flush when exactly
               full; overflow flushes the existing buffer first).
               vis_pre_exit_bytes = bytes readable >= 200ms before the
               child's exit, so exit-batched flushes cannot masquerade
               as mid-life visibility.
  --io-child   embedded child writer mode (spec JSON) for withhold_*
"""

import json
import io
import os
import select
import statistics
import subprocess
import sys
import time

os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"
os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "1"

import pygame  # noqa: E402

PRE_EXIT_MARGIN_MS = 200  # bytes counted only if visible this long before exit
SLEEP = 600
SEG_SLEEP1 = 250
SEG_SLEEP2 = 350

WITHHOLD_CASES = [
    # name, ops, interpreter flags before script path
    ("small",      [["w", 100, "x"], ["s", SLEEP]], []),
    ("edge_lo",    [["w", 131071, "x"], ["s", SLEEP]], []),
    ("edge_eq",    [["w", 131072, "x"], ["s", SLEEP]], []),
    ("edge_hi",    [["w", 131073, "x"], ["s", SLEEP]], []),
    ("big",        [["w", 200000, "x"], ["s", SLEEP]], []),
    ("seg_eq",     [["w", 65536, "x"], ["s", SEG_SLEEP1],
                    ["w", 65536, "y"], ["s", SEG_SLEEP2]], []),
    ("seg_over",   [["w", 70000, "x"], ["s", SEG_SLEEP1],
                    ["w", 70000, "y"], ["s", SEG_SLEEP2]], []),
    ("unbuf",      [["w", 100, "x"], ["s", SLEEP]], ["-u"]),
]


def emit(arm, **kv):
    print(f"PYGAME-ARM {arm} | " + " ".join(f"{k}={v}" for k, v in kv.items()),
          flush=True)


def io_child(spec):
    """Embedded child: scripted unflushed stdout writer, exits to flush."""
    for op in json.loads(spec):
        if op[0] == "w":
            sys.stdout.write(op[2] * (op[1] - 1) + "\n")
        elif op[0] == "f":
            sys.stdout.write(op[2] * (op[1] - 1) + "\n")
            sys.stdout.flush()
        elif op[0] == "s":
            time.sleep(op[1] / 1000.0)


def expected_bytes(ops):
    out = b""
    for op in ops:
        if op[0] in ("w", "f"):
            out += (op[2] * (op[1] - 1) + "\n").encode()
    return out


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


def withhold_arm(name, ops, before):
    """Spawn the embedded child and classify its stdout visibility.

    vis_pre_exit_bytes counts only bytes readable at least
    PRE_EXIT_MARGIN_MS before the child's exit, so exit-batched flushes
    cannot masquerade as mid-life visibility (a fixed mid-run sample is
    jitter-fragile: child startup under load can push the first overflow
    flush past the sample point).
    """
    env = {k: v for k, v in os.environ.items() if k != "PYTHONUNBUFFERED"}
    env["PYGAME_HIDE_SUPPORT_PROMPT"] = "1"
    argv = [sys.executable, *before, os.path.abspath(__file__),
            "--io-child", json.dumps(ops)]
    t0 = time.perf_counter()
    proc = subprocess.Popen(argv, stdout=subprocess.PIPE,
                            stderr=subprocess.DEVNULL, env=env, bufsize=0)
    fd = proc.stdout.fileno()
    os.set_blocking(fd, False)
    first_vis = None
    events = []
    while True:
        r, _, _ = select.select([proc.stdout], [], [], 0.005)
        if r:
            try:
                data = os.read(fd, 1 << 20)
            except (BlockingIOError, OSError):
                data = b""
            if data:
                now = time.perf_counter()
                if first_vis is None:
                    first_vis = now - t0
                events.append(((now - t0) * 1e3, data))
        if proc.poll() is not None:
            break
        if (time.perf_counter() - t0) > 5.0:
            proc.kill()
            break
    exit_ms = (time.perf_counter() - t0) * 1e3
    while True:
        try:
            d = os.read(fd, 1 << 20)
        except (BlockingIOError, OSError):
            break
        if not d:
            break
        events.append(((time.perf_counter() - t0) * 1e3, d))
    proc.wait()
    got = b"".join(d for _, d in events)
    vis_pre_exit = sum(len(d) for t, d in events
                       if t <= exit_ms - PRE_EXIT_MARGIN_MS)
    emit(f"withhold_{name}",
         n=sum(op[1] for op in ops if op[0] in ("w", "f")),
         first_vis_ms=(None if first_vis is None else round(first_vis * 1e3, 1)),
         vis_pre_exit_ms=PRE_EXIT_MARGIN_MS, vis_pre_exit_bytes=vis_pre_exit,
         exit_ms=round(exit_ms, 1), total_bytes=len(got),
         integrity=int(got == expected_bytes(ops)), rc=proc.returncode)


def main():
    if "--io-child" in sys.argv:
        io_child(sys.argv[sys.argv.index("--io-child") + 1])
        return

    n = pygame.init()
    screen = pygame.display.set_mode((320, 240))
    emit("viability", init_pass=n[0], init_fail=n[1],
         driver=pygame.display.get_driver(),
         sdl=".".join(str(x) for x in pygame.get_sdl_version()),
         surf="320x240",
         flags=hex(pygame.display.get_surface().get_flags()))
    # parent-side stdio constant; the embedded child runs the same
    # interpreter, so this is the withhold matrix's referent buffer size
    emit("stdio", default_buffer_size=io.DEFAULT_BUFFER_SIZE)

    clock = pygame.time.Clock()

    for arm, fps, N in (("cadence60", 60, 240), ("cadence120", 120, 240)):
        deltas = []
        prev = time.perf_counter()
        for _ in range(N):
            ret = clock.tick(fps)
            now = time.perf_counter()
            deltas.append((now - prev) * 1e3)
            prev = now
        emit(arm, n=N,
             dt_mean_ms=round(statistics.fmean(deltas), 3),
             dt_min_ms=round(min(deltas), 3),
             dt_max_ms=round(max(deltas), 3),
             fps=round(clock.get_fps(), 2), last_tick_ret=ret)

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

    popen_arm("popen",
              [sys.executable, "-u", "-c",
               "import time; print('CHILD-MARK-1',flush=True);"
               " time.sleep(0.12); print('CHILD-MARK-2',flush=True)"])
    popen_arm("popen_buf",
              [sys.executable, "-c",
               "import time; print('CHILD-MARK-1');"
               " time.sleep(0.12); print('CHILD-MARK-2')"])

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

    prev = time.perf_counter()
    for _ in range(200):
        pygame.display.flip()
    emit("flip", n=200,
         flip_mean_ms=round((time.perf_counter() - prev) * 1e3 / 200, 3))

    for name, ops, before in WITHHOLD_CASES:
        withhold_arm(name, ops, before)

    pygame.quit()
    print("PYGAME_PROBE_DONE", flush=True)


if __name__ == "__main__":
    main()
