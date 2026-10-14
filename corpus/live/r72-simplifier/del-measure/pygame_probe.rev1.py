"""r71 pygame 2.6.1 headless battery probe (third runtime first contact).

Claim under test (round-71 declared coverage move): a pygame process runs
a deterministic user-loop cadence headless (SDL_VIDEODRIVER=dummy), its
child-process stdout surface (subprocess.Popen) is writer-bound and
byte-exact like LOVE's, and its OWN stdout withholding is "a
language-layer window bounded by buffer size" -- falsifiable via a >8KB
mid-run write surfacing early (frontier scout left the upper edge open).

Emits exact-stdout lines:  PYGAME-ARM <arm> | <key>=<val> ...
All ARM lines are print(flush=True) -- the withholding window measured
here applies to piped readers of THIS process too; flush pins keep the
harness's timing view honest (frontier fa-pygame correctness pin).
Run: `python3 pygame_probe.py` (runner: pygame_battery.py).

Headless contract is carried in-fixture (conf.lua-analogous): the env is
pinned before `import pygame` so the probe is headless on compositor and
compositorless hosts alike; the viability arm then verifies driver=dummy.

Arms:
  viability      pygame.init()/set_mode result, SDL driver + version
  cadence60      Clock.tick(60) capped loop -- dt stats bound-pinned
                 (~62Hz: SDL_Delay ms-granularity undershoots 16.67ms)
  cadence0       Clock.tick() uncapped -- bare-Python MHz spin
  popen          flushing Popen child: write->readable latency tracks the
                 writer (l2_wait ~= child's own 120ms sleep), byte-exact
  popen_buf      same child WITHOUT flush: l1 withheld to child exit
  withhold_*     parent-side flush-edge measurement of a buffered child's
                 stdout: three payloads straddling the measured buffer
                 bound (io.DEFAULT_BUFFER_SIZE on this build):
                   small  = 9000   (< bound -> held to exit)
                   big    = 200000 (> bound -> mid-run flush)
                   fill   = 200x1000 cumulative crossing (-> fills flush)
                 the withhold children are plain python3, deliberately --
                 the claim is language-layer (Python stdio), so the
                 subject must NOT import pygame.
  pump           400 frames, zero event calls: cadence unaffected and a
                 pre-posted USEREVENT survives -- pump-free headless.
  reorder_*      r72 composition arm: fd1-inheritance x stdio-withholding.
                 A spawned descendant writes into the child's inherited
                 fd1 while the child's own earlier HEAD bytes sit in its
                 userspace buffer. Per-child stdout-mode cells:
                   buf   buffered        -> prefix_reorder (INJECTED first)
                   unbuf python -u       -> midline_splice (Godot/LOVE shape)
                   flush flush=True head -> midline_splice
                   env   PYTHONUNBUFFERED=1 -> midline_splice
                   late  descendant lands after window close -> append
                 The reorder children are plain python3, deliberately --
                 the fabricated byte ORDER is a language-layer property
                 (buffering mode); the seam is spawn-layer (fd1
                 inheritance). Same 19 bytes on every wire, order moves.
  reorder_self   the same composition on the probe's OWN fd1: raw
                 REORDER-HEAD/CHILD/TAIL markers ride this wire; under the
                 battery's pipe capture the child marker precedes HEAD --
                 the hazard a streaming parser of ARM lines would see.
"""

import io
import os
import select
import statistics
import subprocess
import sys
import time

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
os.environ.setdefault("PYGAME_HIDE_SUPPORT_PROMPT", "1")

import pygame

BUFSIZE = io.DEFAULT_BUFFER_SIZE
CHILD_TIMEOUT_S = 10.0
# buffered stdout is the measured surface: the withhold children must not
# inherit PYTHONUNBUFFERED from an operator environment.
CHILD_ENV = {k: v for k, v in os.environ.items() if k != "PYTHONUNBUFFERED"}


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


def withhold_arm(emit_name, mid_src, write_bytes):
    """Spawn a buffered child that emits MARK-1, sleeps 100ms, runs the
    `mid_src` statement (the mid-run write) raw, sleeps 100ms, prints
    MARK-2, exits. Parent times readability with raw os.read + select
    (no parent-side stdio buffering): the window edge is wherever bytes
    first surface relative to the child's ~200ms+ exit.
    """
    child = ("import sys,time;"
             "print('MARK-1');"
             "time.sleep(0.10);"
             f"{mid_src};"
             "time.sleep(0.10);"
             "print('MARK-2')")
    t0 = time.perf_counter()
    proc = subprocess.Popen([sys.executable, "-c", child],
                            stdout=subprocess.PIPE,
                            stderr=subprocess.DEVNULL, env=CHILD_ENV)
    fd = proc.stdout.fileno()
    chunks = []
    data = b""
    alive_at_first = None
    while True:
        ready, _, _ = select.select([fd], [], [], CHILD_TIMEOUT_S)
        if not ready:
            chunks.append((-1.0, 0))
            break
        chunk = os.read(fd, 65536)
        if not chunk:
            break
        ms = (time.perf_counter() - t0) * 1e3
        if alive_at_first is None:
            alive_at_first = proc.poll() is None
        chunks.append((ms, len(chunk)))
        data += chunk
    proc.wait()
    eof_ms = (time.perf_counter() - t0) * 1e3

    def find_ms(needle):
        """ms at which the read containing `needle` completed, else -1."""
        off = data.find(needle)
        seen = 0
        for ms, n in chunks:
            seen += n
            if off >= 0 and seen >= off + len(needle):
                return ms
        return -1.0

    mark2_ms = find_ms(b"MARK-2")
    # early = bytes delivered before the exit burst. The exit burst can
    # span several 64KiB pipe reads all landing within ~1ms of EOF, so
    # key off eof_ms (the bursts are ~100ms apart by construction: the
    # child sleeps 100ms after the mid-run write). 25ms margin.
    early_bytes = sum(n for ms, n in chunks if 0 <= ms < eof_ms - 25)
    emit(emit_name,
         bufsize=BUFSIZE, write_bytes=write_bytes,
         first_read_ms=round(chunks[0][0], 2) if chunks else -1,
         mark1_ms=round(find_ms(b"MARK-1"), 2),
         mark2_ms=round(mark2_ms, 2),
         eof_ms=round(eof_ms, 2),
         early_bytes=early_bytes,
         exit_bytes=len(data) - early_bytes,
         total_bytes=len(data),
         alive_at_first=alive_at_first)


# reorder_* child programs (r72): HEAD -> descendant write into inherited
# fd1 -> TAIL -> exit.  Plain python3, same rule as the withhold children.
REORDER_SYNC = ("import os,sys;"
                "sys.stdout.write('HEAD ');"
                "os.system('printf INJECTED >&1');"
                "sys.stdout.write(' TAIL\\n')")
REORDER_FLUSH = ("import os,sys;"
                 "sys.stdout.write('HEAD ');sys.stdout.flush();"
                 "os.system('printf INJECTED >&1');"
                 "sys.stdout.write(' TAIL\\n')")
# descendant inside vs after the window: the HEAD+TAIL flush closes the
# window at ~t=0 while a backgrounded descendant lands at ~t=300ms, the
# parent held alive to t=600ms so the pipe stays open for the late write.
REORDER_LATE = ("import os,sys,time;"
                "sys.stdout.write('HEAD ');"
                "os.system('(sleep 0.30;printf INJECTED >&1) &');"
                "sys.stdout.write(' TAIL\\n');"
                "sys.stdout.flush();"
                "time.sleep(0.60)")


def reorder_arm(emit_name, child_argv, env=None):
    """Spawn a child on a piped stdout; inside it the child writes HEAD,
    runs a descendant that writes INJECTED straight into the inherited
    fd1, writes TAIL, exits.  The probe reads the delivered stream to EOF
    and classifies byte ORDER: a block-buffered child withholds HEAD
    until exit, so the descendant's bytes surface FIRST
    (prefix_reorder); any collapse of the withholding window (-u /
    flush=True / PYTHONUNBUFFERED=1) splices midline (the Godot/LOVE
    topology); a descendant landing after window close appends.
    """
    proc = subprocess.Popen(child_argv, stdout=subprocess.PIPE,
                            stderr=subprocess.DEVNULL,
                            env=env if env is not None else CHILD_ENV)
    try:
        data, _ = proc.communicate(timeout=CHILD_TIMEOUT_S)
    except subprocess.TimeoutExpired:
        proc.kill()
        data, _ = proc.communicate()
    head = data.find(b"HEAD")
    inj = data.find(b"INJECTED")
    tail = data.find(b"TAIL")
    if -1 in (head, inj, tail):
        topo = "markers_missing"
    elif inj < head:
        topo = "prefix_reorder"
    elif head < inj < tail:
        topo = "midline_splice"
    elif tail < inj:
        topo = "append"
    else:
        topo = "degenerate"
    emit(emit_name, bufsize=BUFSIZE, topology=topo,
         head_at=head, injected_at=inj, tail_at=tail,
         wire_bytes=len(data), ret=proc.returncode)


def main():
    if "--version" in sys.argv:
        print(f"{pygame.version.ver} "
              f"SDL={'.'.join(str(x) for x in pygame.get_sdl_version())} "
              f"python={sys.version.split()[0]}")
        return

    n = pygame.init()
    pygame.display.set_mode((320, 240))
    emit("viability", init_pass=n[0], init_fail=n[1],
         driver=pygame.display.get_driver(),
         sdl=".".join(str(x) for x in pygame.get_sdl_version()),
         surf="x".join(str(s) for s in pygame.display.get_surface().get_size()),
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
         hz=round(N / (prev - t0), 1), last_tick_ret=ret)

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

    # --- withhold_*: parent-side flush-edge of a buffered child ---------
    # small (9000 < bufsize): claimed ~8KB bound falsifier -- held to exit
    withhold_arm("withhold_small", "sys.stdout.write('B'*9000)", 9000)
    # big (200000 > bufsize): a >buffer mid-run write surfaces early
    withhold_arm("withhold_big", "sys.stdout.write('B'*200000)", 200000)
    # fill (200x1000 cumulative crossing): edge is buffer-FILL, not a
    # large-write bypass -- granularity-independent bound
    withhold_arm("withhold_fill",
                 "[sys.stdout.write('C'*1000) for _ in range(200)]", 200000)

    # --- pump: 400 frames, zero event calls ----------------------------
    MYEVENT = pygame.USEREVENT + 1
    pygame.event.post(pygame.event.Event(MYEVENT, marker="posted"))
    prev = time.perf_counter()
    for _ in range(400):
        clock.tick(120)          # no pump(), no get() -- pure cadence
    nopump_ms = (time.perf_counter() - prev) * 1e3
    queued = pygame.event.get()  # single drain at end
    mine = sum(1 for e in queued if e.type == MYEVENT)
    emit("pump", frames_nopump=400, nopump_total_ms=round(nopump_ms, 1),
         queued_after_nopump=len(queued), posted_survived=mine,
         pump_needed="false")

    # --- reorder_*: descendant into inherited fd1 mid-window (r72) ------
    # buffered child: HEAD withheld to exit, so INJECTED lands first
    reorder_arm("reorder_buf", [sys.executable, "-c", REORDER_SYNC])
    # -u child: no withholding window -> midline splice (Godot/LOVE)
    reorder_arm("reorder_unbuf", [sys.executable, "-u", "-c", REORDER_SYNC])
    # flush=True child: HEAD on the wire before the spawn -> midline
    reorder_arm("reorder_flush", [sys.executable, "-c", REORDER_FLUSH])
    # PYTHONUNBUFFERED=1 collapses the window from the env side
    reorder_arm("reorder_env", [sys.executable, "-c", REORDER_SYNC],
                env={**CHILD_ENV, "PYTHONUNBUFFERED": "1"})
    # late descendant: writes after the parent's flush closed the window
    reorder_arm("reorder_late", [sys.executable, "-c", REORDER_LATE])

    # --- reorder_self: the composition on the probe's OWN fd1 (r72) -----
    # Raw markers ride THIS wire: HEAD/TAIL are withheld whenever fd1 is a
    # block-buffered pipe (the battery's capture), so the descendant's
    # REORDER-CHILD surfaces first -- the fabricated order a streaming
    # parser would see.  The battery pins the captured byte order; this
    # ARM line carries metadata only.  fd1_isatty records which regime
    # ran (pipe -> buffered -> reorder; tty -> line-buffered -> splice).
    sys.stdout.write("REORDER-HEAD\n")
    os.system("printf 'REORDER-CHILD\\n' >&1")
    sys.stdout.write("REORDER-TAIL\n")
    emit("reorder_self", bufsize=BUFSIZE, fd1_isatty=sys.stdout.isatty(),
         descendant="printf")

    pygame.quit()
    print("PYGAME_PROBE_DONE", flush=True)


if __name__ == "__main__":
    main()
