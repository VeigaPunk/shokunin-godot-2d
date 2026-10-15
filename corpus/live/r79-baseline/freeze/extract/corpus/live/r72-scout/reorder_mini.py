"""r72-scout scratch — reorder-fabrication mechanism probe (own-fd1 variant).

Claim under pre-measurement (wave-11 xconnector X1): a descendant that
inherits fd1 and writes mid-window lands BEFORE the writer's earlier
buffered bytes when the writer block-buffers stdout (CPython piped
default); the order collapses to the midline splice (LOVE/Godot shape)
when the writer flushes through (-u / flush=True).

This scratch probe runs the writer side inside a pygame process
(import + init + dummy set_mode) and emits ordered markers:
  PHASE0 (flushed) -> R-HEAD (unflushed) -> descendant R-INJ (inherited
  fd1) -> hold -> R-TAIL (flushed).
The observable is the captured byte order (reader = reorder_harness.py or
a shell pipe). Variants: --child=sh|pyu|pyb, --flush-head, --crossing,
--byte-level, --no-wait, --hold=S.

Run: python3 reorder_mini.py [variants]   (buffered) | python3 -u ...
"""

import os
import subprocess
import sys
import time

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
os.environ.setdefault("PYGAME_HIDE_SUPPORT_PROMPT", "1")

import pygame  # noqa: E402

opts = {}
for a in sys.argv[1:]:
    if a.startswith("--"):
        if "=" in a:
            k, v = a[2:].split("=", 1)
            opts[k] = v
        else:
            opts[a[2:]] = "1"

CHILD = opts.get("child", "sh")
FLUSH_HEAD = "flush-head" in opts
CROSSING = "crossing" in opts
BYTE_LEVEL = "byte-level" in opts
NO_WAIT = "no-wait" in opts
HOLD = float(opts.get("hold", "0.3"))

if BYTE_LEVEL:
    HEAD, INJ, TAIL = "R-HEAD ", "R-INJ", " R-TAIL\n"
else:
    HEAD, INJ, TAIL = "R-HEAD\n", "R-INJ\n", "R-TAIL\n"


def w(s, flush=False):
    sys.stdout.write(s)
    if flush:
        sys.stdout.flush()


def main():
    pygame.init()
    pygame.display.set_mode((320, 240))

    w(f"PHASE0-FLUSHED isatty={int(sys.stdout.isatty())} "
      f"bufsize={__import__('io').DEFAULT_BUFFER_SIZE}\n", flush=True)

    # --- window opens: earlier bytes go into the userspace buffer ---------
    w(HEAD)
    if FLUSH_HEAD:
        sys.stdout.flush()          # control: window collapsed by flush
    if CROSSING:
        w("C" * 140000)             # >= io.DEFAULT_BUFFER_SIZE crossing

    # --- descendant writes into inherited fd1 (mid-window) ----------------
    if CHILD == "sh":
        child_argv = ["sh", "-c", f"printf '%s' '{INJ}'"]
    elif CHILD == "pyu":
        child_argv = [sys.executable, "-u", "-c",
                      f"import sys; sys.stdout.write({INJ!r})"]
    elif CHILD == "pyb":
        child_argv = [sys.executable, "-c",
                      f"import sys; sys.stdout.write({INJ!r})"]
    else:
        raise SystemExit(f"unknown --child={CHILD}")
    if NO_WAIT:
        child_argv = ["sh", "-c", f"sleep 0.35; printf '%s' '{INJ}'"]
    proc = subprocess.Popen(child_argv, stdout=None, stderr=None)
    if not NO_WAIT:
        proc.wait()
        time.sleep(HOLD)            # keep window open: streaming observable
    w(TAIL, flush=True)             # window closes: HEAD released, then TAIL
    if NO_WAIT:
        proc.wait()                 # let the late child land before exit
    time.sleep(0.05)


if __name__ == "__main__":
    main()
