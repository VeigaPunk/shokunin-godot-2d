"""frontier-pygame parent-side capture probe.

Spawns pygame_probe.py --io-child <buf|flush> as a subprocess with
stdout=PIPE and measures when each child line becomes readable at the
parent — the parent-visible write->readable surface for a pygame battery.

Verdict shape mirrors r70's writer-bound pipe question:
  flush child: line-1 wait ~= spawn/import cost, line-2 wait ~= 200ms
               (parent-visible latency IS the writer's own clock)
  buf child:   line-1 wait ~= 200ms too — the bytes sit in the child's
               stdio block buffer until exit; an absorption window owned
               by Python stdio, not by SDL/pygame.
"""

import os
import select
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ENV = dict(os.environ,
           SDL_VIDEODRIVER="dummy",
           SDL_AUDIODRIVER="dummy",
           PYGAME_HIDE_SUPPORT_PROMPT="1")


def run(mode):
    t0 = time.perf_counter()
    proc = subprocess.Popen(
        [sys.executable, os.path.join(HERE, "pygame_probe.py"),
         "--io-child", mode],
        stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
        text=True, env=ENV)
    waits = []
    for want in ("PYGAME-IOCHILD-1", "PYGAME-IOCHILD-2"):
        ready, _, _ = select.select([proc.stdout], [], [], 5.0)
        if not ready:
            waits.append((want, None, "TIMEOUT>5s"))
            continue
        line = proc.stdout.readline()
        waits.append((want, round((time.perf_counter() - t0) * 1e3, 2),
                      line.strip()))
    proc.wait()
    eof_ms = round((time.perf_counter() - t0) * 1e3, 2)
    return waits, eof_ms, proc.returncode


def main():
    for mode in ("flush", "buf"):
        waits, eof_ms, ret = run(mode)
        print(f"mode={mode} exit={ret} eof_ms={eof_ms}")
        for want, ms, got in waits:
            print(f"  {want}: wait_ms={ms} got={got!r}")


if __name__ == "__main__":
    main()
