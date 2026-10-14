"""r71-critic child: stdout withholding patterns for the flush-edge bisect.

Never flushes unless the mode says so. Each mode writes a deterministic
byte stream so the parent can timestamp *when* bytes become visible on the
pipe and *how many* bytes the window held at release.

Modes (argv[1]):
  exit          one small line, sleep 0.40, exit          (exit-batch cell)
  exit_pygame   same, but import pygame first             (spawn-floor cell)
  bigwrite      small line; 0.25s; 16001-byte write; 0.50s; exit
                (the scout's open cell: does a >8KB mid-run write
                 release the withheld line early?)
  single4000    one 4001-byte write; sleep 0.50            (sub-buffer cell)
  single8192    one 8192-byte write, no newline; sleep 0.50 (== nominal buffer)
  single8193    one 8193-byte write, no newline; sleep 0.50 (> nominal buffer)
  single16000   one 16001-byte write; sleep 0.50           (oversized cell)
  incr64        400 lines of exactly 64 bytes; sleep 0.40  (granular fill)
  incr8000      3 writes of exactly 8000 bytes; sleep 0.40 (coarse fill)
  flushsmall    small line + explicit flush; sleep 0.40    (harness sanity)
  single130k    one 130000-byte write (under 128KiB buffer)
  single132k    one 132000-byte write (over 128KiB buffer)
  single200k    one 200000-byte write (oversized)
  incr65_260k   4000 lines of 65 bytes = 260000 bytes, no flush
  bin_incr64    binary layer: 2200 x 64 bytes = 140800 bytes, no flush
  bin_single200k binary layer: one 200000-byte write
  mixed_invert  unflushed text line, then binary-layer raw write > buffer

stderr always gets one CHILD-STDIO line first (line-buffered) with the
child's own stdio provenance, so the parent can assert the precondition
(block-buffered stdout, not a tty) instead of assuming it.
"""
import sys
import time


def w(s):
    sys.stdout.write(s)


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else "exit"
    sys.stderr.write(
        "CHILD-STDIO mode=%s isatty=%s line_buffering=%s write_through=%s "
        "unbuffered=%s\n" % (
            mode, sys.stdout.isatty(), sys.stdout.line_buffering,
            sys.stdout.write_through,
            bool(getattr(sys.flags, "unbuffered", False))))
    sys.stderr.flush()

    if mode == "exit_pygame":
        import pygame  # noqa: F401  (spawn floor only)

    if mode == "exit" or mode == "exit_pygame":
        w("LINE-1\n")
        time.sleep(0.40)
    elif mode == "bigwrite":
        w("LINE-1\n")
        time.sleep(0.25)
        w("B" * 16000 + "\n")          # single >8KB write
        time.sleep(0.50)
        w("LINE-2\n")
    elif mode == "single4000":
        w("A" * 4000 + "\n")
        time.sleep(0.50)
    elif mode == "single8192":
        w("A" * 8192)
        time.sleep(0.50)
    elif mode == "single8193":
        w("A" * 8193)
        time.sleep(0.50)
    elif mode == "single16000":
        w("A" * 16000 + "\n")
        time.sleep(0.50)
    elif mode == "incr64":
        for i in range(400):
            w("%04dx%s\n" % (i, "x" * 59))     # 64 bytes/line
        time.sleep(0.40)
    elif mode == "incr8000":
        for _ in range(3):
            w("Y" * 7999 + "\n")               # 8000 bytes/write
        time.sleep(0.40)
    elif mode == "flushsmall":
        w("LINE-1\n")
        sys.stdout.flush()
        time.sleep(0.40)
    elif mode == "single130k":
        w("A" * 130000)
        time.sleep(0.40)
    elif mode == "single131072":
        w("A" * 131072)
        time.sleep(0.40)
    elif mode == "single131073":
        w("A" * 131073)
        time.sleep(0.40)
    elif mode == "single132k":
        w("A" * 132000)
        time.sleep(0.40)
    elif mode == "single200k":
        w("A" * 200000)
        time.sleep(0.40)
    elif mode == "incr65_260k":
        for i in range(4000):
            w("%04dx%s\n" % (i, "x" * 59))     # 65 bytes/line
        time.sleep(0.40)
    elif mode == "bin_incr64":
        for _ in range(2200):
            sys.stdout.buffer.write(b"z" * 64)  # binary layer only
        time.sleep(0.40)
    elif mode == "bin_single200k":
        sys.stdout.buffer.write(b"z" * 200000)
        time.sleep(0.40)
    elif mode == "bigwrite128k":
        w("LINE-1\n")
        time.sleep(0.25)
        w("B" * 132000)                # > 128KiB: releases the withheld line
        time.sleep(0.50)
        w("LINE-2\n")
    elif mode == "mixed_invert":
        w("T1\n")                               # stuck in text pending
        sys.stdout.buffer.write(b"B" * 140000)  # > 128KiB: raw write now
        time.sleep(0.40)
    else:
        sys.stderr.write("unknown mode %r\n" % mode)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
