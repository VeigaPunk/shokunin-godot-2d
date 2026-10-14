"""r72-scout scratch — self-contained reorder arm shape (probe-as-reader).

Parent mode (default): spawns writer copies of THIS file under three
writer modes with stdout=PIPE, reads each to EOF incrementally, computes
the marker topology, emits one `ORDER ...` line per mode. This is the
shape a battery can pin without a second probe invocation.

Writer mode (--writer): pygame-importing process (unless --plain);
PHASE0 flushed; R-HEAD unflushed; descendant (sh printf / python)
inherits the writer's fd1; writer waits; holds; R-TAIL flush.

Run: python3 reorder_selfcontained.py [--writer-plain]
"""

import os
import select
import subprocess
import sys
import time

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
os.environ.setdefault("PYGAME_HIDE_SUPPORT_PROMPT", "1")

HERE = os.path.dirname(os.path.abspath(__file__))
SELF = os.path.abspath(__file__)


def writer_main():
    plain = "--plain" in sys.argv
    if not plain:
        import pygame
        pygame.init()
        pygame.display.set_mode((320, 240))
    sys.stdout.write(
        f"PHASE0-WRITER plain={int(plain)} "
        f"isatty={int(sys.stdout.isatty())}\n")
    sys.stdout.flush()
    sys.stdout.write("R-HEAD\n")            # withheld (buffered mode)
    proc = subprocess.Popen(["sh", "-c", "printf 'R-INJ\\n'"],
                            stdout=None, stderr=None)
    proc.wait()
    time.sleep(0.25)                        # hold window open
    sys.stdout.write("R-TAIL\n")
    sys.stdout.flush()
    time.sleep(0.05)


def run_writer(label, py_flags, writer_flags, env_extra=None):
    env = dict(os.environ)
    env.update(env_extra or {})
    cmd = [sys.executable] + py_flags + [SELF, "--writer"] + writer_flags
    t0 = time.perf_counter()
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE,
                            stderr=subprocess.DEVNULL, env=env)
    fd = proc.stdout.fileno()
    data = b""
    first_ms, alive_at_first, inj_ms = -1.0, None, -1.0
    while True:
        ready, _, _ = select.select([fd], [], [], 10.0)
        if not ready:
            break
        chunk = os.read(fd, 65536)
        if not chunk:
            break
        if first_ms < 0:
            first_ms = (time.perf_counter() - t0) * 1e3
            alive_at_first = proc.poll() is None
        if inj_ms < 0 and b"R-INJ" in chunk:
            inj_ms = (time.perf_counter() - t0) * 1e3
        data += chunk
    proc.wait()
    eof_ms = (time.perf_counter() - t0) * 1e3

    def pos(n):
        return data.find(n.encode())

    p_head, p_inj, p_tail = pos("R-HEAD"), pos("R-INJ"), pos("R-TAIL")
    if -1 in (p_head, p_inj, p_tail):
        topo = "MISSING"
    elif p_inj < p_head < p_tail:
        topo = "reorder"
    elif p_head < p_inj < p_tail:
        topo = "splice"
    elif p_head < p_tail < p_inj:
        topo = "suffix"
    else:
        topo = "mixed"
    print(f"ORDER writer={label} topology={topo} head_idx={p_head} "
          f"inj_idx={p_inj} tail_idx={p_tail} total_bytes={len(data)} "
          f"first_read_ms={round(first_ms, 2)} "
          f"inj_read_ms={round(inj_ms, 2)} eof_ms={round(eof_ms, 2)} "
          f"alive_at_first={alive_at_first} rc={proc.returncode}")


def parent_main():
    plain = ["--plain"] if "--writer-plain" in sys.argv else []
    run_writer("buffered", [], plain)
    run_writer("unbuffered_u", ["-u"], plain)
    run_writer("env_unbuffered", [], plain,
               env_extra={"PYTHONUNBUFFERED": "1"})
    print("SELFCONTAINED_DONE")


if __name__ == "__main__":
    if "--writer" in sys.argv:
        writer_main()
    else:
        parent_main()
