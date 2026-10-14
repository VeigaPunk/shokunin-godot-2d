"""r71-boundary scratch: pygame-process -> grandchild pipe surface.

Mirrors the LOVE r70 popen arm keys (l1/l2/close/total/rest_len, byte-exact)
and adds the withholding edge on the *grandchild* writer:
  - io_flush   : grandchild `python3 -u`  -> writer-bound latency (LOVE shape)
  - io_buf     : grandchild plain python3 -> its stdio withholds until exit
  - io_big_9k  : grandchild plain, one 9000-byte write -> still withheld
                 (9000 < its 131072 BufferedWriter buffer)
  - io_big_128k: grandchild plain, one 131073-byte write -> surfaces early
                 (>= buffer_size -> raw write-through)

Run under dummy env (env set inside).
"""

import os
import select
import subprocess
import sys
import time

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
os.environ.setdefault("PYGAME_HIDE_SUPPORT_PROMPT", "1")

import pygame  # noqa: E402

pygame.init()
pygame.display.set_mode((64, 64))

CHILD = sys.executable


def child_cmd(mode):
    if mode == "io_flush":
        return [CHILD, "-u", "-c",
                "import sys,time;print('CHILD-MARK-1',flush=True);"
                "time.sleep(0.12);print('CHILD-MARK-2',flush=True)"]
    if mode == "io_buf":
        return [CHILD, "-c",
                "import sys,time;print('CHILD-MARK-1');"
                "time.sleep(0.12);print('CHILD-MARK-2')"]
    if mode == "io_big_9k":
        return [CHILD, "-c",
                "import sys,time;sys.stdout.write('x'*9000);"
                "time.sleep(0.30);sys.stdout.write('\\n')"]
    if mode == "io_big_128k":
        return [CHILD, "-c",
                "import sys,time;sys.stdout.write('x'*131073);"
                "time.sleep(0.30)"]
    raise ValueError(mode)


def run(mode):
    t0 = time.time()
    proc = subprocess.Popen(child_cmd(mode), stdout=subprocess.PIPE,
                            stderr=subprocess.DEVNULL)
    fd = proc.stdout.fileno()
    chunks = []
    eof_ms = None
    deadline = time.monotonic() + 6.0
    while time.monotonic() < deadline:
        ready, _, _ = select.select([fd], [], [], 0.5)
        if not ready:
            continue
        data = os.read(fd, 1 << 20)
        t_ms = round((time.time() - t0) * 1e3, 2)
        if data:
            chunks.append((t_ms, len(data)))
        else:
            eof_ms = t_ms
            break
    proc.wait()
    total_ms = round((time.time() - t0) * 1e3, 2)
    return chunks, eof_ms, total_ms, proc.returncode


def main():
    for mode in ("io_flush", "io_buf", "io_big_9k", "io_big_128k"):
        chunks, eof_ms, total_ms, rc = run(mode)
        print(f"PYGAME-ARM {mode} | rc={rc} total_ms={total_ms} "
              f"eof_ms={eof_ms} chunks={chunks[:6]}")

    # readline-level shape for the writer-bound arm (LOVE keys)
    for mode in ("io_flush", "io_buf"):
        t0 = time.time()
        proc = subprocess.Popen(child_cmd(mode), stdout=subprocess.PIPE,
                                stderr=subprocess.DEVNULL)
        waits = []
        for want in ("CHILD-MARK-1", "CHILD-MARK-2"):
            ready, _, _ = select.select([proc.stdout], [], [], 5.0)
            if not ready:
                waits.append((want, None, "TIMEOUT>5s"))
                continue
            line = proc.stdout.readline().decode().strip()
            waits.append((want, round((time.time() - t0) * 1e3, 2), line))
        proc.wait()
        eof = round((time.time() - t0) * 1e3, 2)
        print(f"PYGAME-ARM {mode}_readline | waits={waits} eof_ms={eof} "
              f"rc={proc.returncode}")

    print("IO_PROBE_DONE")


if __name__ == "__main__":
    main()
