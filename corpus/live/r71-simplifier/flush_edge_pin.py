"""r71 simplifier scratch: exact edge pin + 3 reps.

default      : sys.stdout.buffer (buffer size = io.DEFAULT_BUFFER_SIZE)
explicit:8192: os.fdopen(1,"wb",buffering=8192)

Rule under test (CPython BufferedWriter): a single write from an empty
buffer with len(data) >= buffer_size flushes and writes directly (parent
sees it at write time); len(data) < buffer_size is buffered (parent sees
it only when a later >=buffer_size write displaces it, or at exit).
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
    out = os.fdopen(1, "wb", buffering=int(mode.split(":", 1)[1]))
else:
    out = sys.stdout.buffer
out.write(b"A1\n")
time.sleep(0.30)
out.write(b"B" * n)
time.sleep(0.30)
out.write(b"A3\n")
"""

CELLS = [("default", 131071), ("default", 131072), ("default", 131073),
         ("explicit:8192", 8191), ("explicit:8192", 8192)]
REPS = 3


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
    print(f"python={sys.version.split()[0]}  reps={REPS}")
    for mode, n in CELLS:
        reps = []
        for _ in range(REPS):
            ms = run(mode, n)
            reps.append(round(ms, 1) if ms is not None else None)
        verdicts = ["EARLY" if (m is not None and m < 450) else "WITHHELD"
                    for m in reps]
        print(f"{mode:>14} bulk={n:>7}  reps_ms={reps}  verdicts={verdicts}")


if __name__ == "__main__":
    main()
