#!/usr/bin/env python3
"""r72-scribe independent harness — probe-process side of the reorder cells.

Usage: reorder_parent.py MODE [--pygame]

The process writes `HEAD ` (unflushed unless MODE flushes), optionally
sleeps / fills the buffer, spawns a descendant that writes `INJECTED`
into the inherited fd1, then writes ` TAIL\\n` and exits. The reader
(reorder_driver.py) owns the pipe and records the raw byte order.

The reader -> this process -> descendant chain mirrors the battery ->
pygame_probe -> spawned-descendant chain of round 72. `--pygame` runs the
same sequence inside an initialized pygame/SDL-dummy process.
"""
import os
import subprocess
import sys
import time

MODE = sys.argv[1]
USE_PYGAME = "--pygame" in sys.argv

if USE_PYGAME:
    os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
    os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
    os.environ.setdefault("PYGAME_HIDE_SUPPORT_PROMPT", "1")
    import pygame  # noqa: E402

    pygame.init()
    pygame.display.set_mode((64, 64))


def head():
    sys.stdout.write("HEAD ")


def tail():
    sys.stdout.write(" TAIL\n")


def descendant_os():
    os.system("printf INJECTED")


def descendant_popen():
    subprocess.Popen(["printf", "INJECTED"])


def descendant_ownpipe():
    p = subprocess.Popen(["printf", "INJECTED"], stdout=subprocess.PIPE)
    p.wait()


def descendant_popen_wait():
    p = subprocess.Popen(["printf", "INJECTED"])
    p.wait()


def descendant_delayed():
    # async, inherits fd1, writes at +50ms (mid crossing-flush window)
    subprocess.Popen(["sh", "-c", "sleep 0.05; printf INJECTED"])


if MODE == "buffered":
    head()
    descendant_os()
    tail()
elif MODE == "flushed":
    head()
    sys.stdout.flush()
    descendant_os()
    tail()
elif MODE == "sleep_before_spawn":
    head()
    time.sleep(0.30)
    descendant_os()
    tail()
elif MODE == "fill_before_spawn":
    head()
    sys.stdout.write("H" * 140000)
    descendant_os()
    tail()
elif MODE == "popen_child":
    head()
    descendant_popen()
    tail()
elif MODE == "popen_wait":
    head()
    descendant_popen_wait()
    tail()
elif MODE == "hybrid_flush":
    # descendant writes at +50ms while the parent's 400000-byte write is
    # crossing the pipe; the driver stalls reads 150ms after chunk 1 so
    # the parent's flush blocks and the descendant's bytes can interleave.
    head()
    descendant_delayed()
    sys.stdout.write("H" * 400000)
    sys.stdout.flush()
    tail()
elif MODE == "ownpipe_control":
    head()
    descendant_ownpipe()
    tail()
elif MODE == "arm_lines":
    # battery-grammar cell: the parent's ARM lines are withheld; the
    # descendant emits its own ARM line into the inherited fd1 first.
    sys.stdout.write("PYGAME-ARM order | seq=1 marker=parent_head\n")
    os.system("printf 'PYGAME-ARM order | seq=2 marker=descendant\\n'")
    sys.stdout.write("PYGAME-ARM order | seq=3 marker=parent_tail\n")
elif MODE == "arm_prefix":
    # descendant bytes (no newline) land BEFORE the parent's withheld ARM
    # line -> the line is prefixed and no longer regex-parseable
    sys.stdout.write("PYGAME-ARM order | seq=1 marker=parent_head\n")
    os.system("printf INJECTED")
    sys.stdout.write("PYGAME-ARM order | seq=2 marker=parent_tail\n")
elif MODE == "arm_midline":
    # flushed parent: the ARM line is split across the spawn; the
    # descendant's bytes land INSIDE the line body
    sys.stdout.write("PYGAME-ARM order | seq=1")
    sys.stdout.flush()
    os.system("printf INJECTED")
    sys.stdout.write(" marker=parent_head\n")
else:
    raise SystemExit("unknown mode: " + MODE)

if USE_PYGAME:
    pygame.quit()
