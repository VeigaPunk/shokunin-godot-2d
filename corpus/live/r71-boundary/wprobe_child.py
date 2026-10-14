"""r71-boundary scratch child: stdout/stderr withholding cells.

Run under the parent driver (wprobe_parent.py) with stdout/stderr piped.
The child emits TRACE lines on fd2 via os.write (raw, never buffered by
Python) so the parent can timestamp exactly when each stdout write was
issued, without perturbing the stdout buffer under test.

No flush of stdout is ever performed by the child except in the explicit
control modes; the interpreter's shutdown flush is the only guaranteed
flush. That is the phenomenon under measurement.
"""

import argparse
import os
import sys
import time


def trace(label):
    os.write(2, f"TRACE {label} t_ns={time.time_ns()}\n".encode())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", required=True,
                    choices=["single", "singleb", "multi", "flush",
                             "stderr", "stderr_multi", "none"])
    ap.add_argument("--size", type=int, default=100)
    ap.add_argument("--sizes", default="")     # multi: comma list
    ap.add_argument("--newline", type=int, default=0)
    ap.add_argument("--nl-last", type=int, default=0)
    ap.add_argument("--sleep", type=float, default=0.35)
    ap.add_argument("--gap", type=float, default=0.06)
    ap.add_argument("--pygame", type=int, default=0)
    a = ap.parse_args()

    if a.pygame:
        import pygame
        pygame.init()
        pygame.display.set_mode((64, 64))

    trace("start")

    if a.mode == "single":
        payload = "x" * a.size + ("\n" if a.newline else "")
        trace("pre-write")
        sys.stdout.write(payload)
        trace("post-write")
    elif a.mode == "singleb":
        payload = b"x" * a.size + (b"\n" if a.newline else b"")
        trace("pre-write")
        sys.stdout.buffer.write(payload)
        trace("post-write")
    elif a.mode == "multi":
        sizes = [int(s) for s in a.sizes.split(",") if s]
        for i, s in enumerate(sizes):
            trace(f"pre-write-{i}")
            if a.nl_last and i == len(sizes) - 1:
                sys.stdout.write("x" * s + "\n")
            else:
                sys.stdout.write("x" * s)
            trace(f"post-write-{i}")
            if i < len(sizes) - 1:
                time.sleep(a.gap)
    elif a.mode == "stderr_multi":
        sizes = [int(s) for s in a.sizes.split(",") if s]
        for i, s in enumerate(sizes):
            trace(f"pre-write-{i}")
            if a.nl_last and i == len(sizes) - 1:
                sys.stderr.write("y" * s + "\n")
            else:
                sys.stderr.write("y" * s)
            trace(f"post-write-{i}")
            if i < len(sizes) - 1:
                time.sleep(a.gap)
    elif a.mode == "flush":
        trace("pre-write")
        sys.stdout.write("x" * a.size)
        sys.stdout.flush()
        trace("post-write")
    elif a.mode == "stderr":
        trace("pre-write")
        sys.stderr.write("y" * a.size + ("\n" if a.newline else ""))
        trace("post-write")

    time.sleep(a.sleep)
    trace("pre-exit")
    # no explicit flush: shutdown flush is the only one


if __name__ == "__main__":
    main()
