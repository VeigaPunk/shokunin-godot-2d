"""r71 simplifier scratch: bisect the piped-stdout withholding edge and
test whether it TRACKS a declared buffer size.

Arm A (`default`): plain child, bulk written via sys.stdout.buffer.write.
Arm B (`explicit:<N>`): child replaces stdout with os.fdopen(1,"wb",buffering=N)
  and writes the same payload -- if the withholding edge moves to N, the
  window is *bounded by buffer size* (mechanism claim proven); if it stays
  put, the edge is something else (pipe capacity, dynamic buffer).
"""
import os
import select
import subprocess
import sys
import time

CHILD_SRC = r"""
import os, sys, time
mode = sys.argv[1]; n = int(sys.argv[2])
if mode.startswith("explicit:"):
    bufsize = int(mode.split(":", 1)[1])
    out = os.fdopen(1, "wb", buffering=bufsize)
else:
    out = sys.stdout.buffer
out.write(b"A1\n")
time.sleep(0.30)
out.write(b"B" * n)
time.sleep(0.30)
out.write(b"A3\n")
"""

SIZES = [65536, 81920, 98304, 114688, 122880, 131072]


def run(mode, n):
    proc = subprocess.Popen([sys.executable, "-c", CHILD_SRC, mode, str(n)],
                            stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
    t0 = time.perf_counter()
    bulk_ms = None
    while True:
        ready, _, _ = select.select([proc.stdout], [], [], 5.0)
        if not ready:
            break
        data = os.read(proc.stdout.fileno(), 1 << 20)
        if not data:
            break
        if bulk_ms is None and b"B" in data:
            bulk_ms = (time.perf_counter() - t0) * 1e3
    proc.wait()
    return bulk_ms


def main():
    probe = subprocess.run(
        [sys.executable, "-c",
         "import io,sys,os;"
         "print('io.DEFAULT_BUFFER_SIZE', io.DEFAULT_BUFFER_SIZE);"
         "print('stdout.encoding', sys.stdout.encoding);"
         "print('stdout.buffer', type(sys.stdout.buffer).__name__);"
         "print('isatty', sys.stdout.isatty())"],
        capture_output=True, text=True)
    print("== interpreter facts ==")
    print(probe.stdout.strip())
    print(f"python={sys.version.split()[0]}")

    for mode in ("default", "explicit:8192", "explicit:65536", "explicit:131072"):
        print(f"== {mode} ==")
        for n in SIZES:
            ms = run(mode, n)
            verdict = "EARLY" if (ms is not None and ms < 450) else "WITHHELD"
            print(f"  bulk={n:>7}  first_b_visible_ms="
                  f"{'-' if ms is None else f'{ms:.1f}':>7}  {verdict}")


if __name__ == "__main__":
    main()
