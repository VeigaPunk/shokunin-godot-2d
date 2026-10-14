"""r71 simplifier scratch: layer isolation + edge bisection for the
piped-stdout withholding window.

Three write layers, each preceded by a small unflushed head line at t0 and
followed by a small unflushed tail line at t0+600ms, with the bulk payload
issued at t0+300ms:

  os     -> os.write(1, b...)            raw fd (no userspace buffering)
  buffer -> sys.stdout.buffer.write(b..) io.BufferedWriter (block buffer)
  text   -> sys.stdout.write(str)        TextIOWrapper -> BufferedWriter

Reported per (layer, size): the parent-visible ms of the BULK bytes.
  early  (~305ms) => that layer flushes at/below this size
  exit   (~605ms) => still withheld at process exit
"""
import os
import select
import subprocess
import sys
import time

CHILD_SRC = r"""
import sys, time
layer, n = sys.argv[1], int(sys.argv[2])
def w(b):
    if layer == "os":
        os.write(1, b)
    elif layer == "buffer":
        sys.stdout.buffer.write(b)
    else:
        sys.stdout.write(b.decode())
if layer == "os":
    import os
w(b"A1\n")
time.sleep(0.30)
w(b"B" * n)
time.sleep(0.30)
w(b"A3\n")
"""

SIZES = [8192, 9216, 16384, 32768, 65536, 131072, 262144, 1048576]


def run(layer, n):
    proc = subprocess.Popen([sys.executable, "-c", CHILD_SRC, layer, str(n)],
                            stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
    t0 = time.perf_counter()
    bulk_ms = None
    tail_ms = None
    while True:
        ready, _, _ = select.select([proc.stdout], [], [], 5.0)
        if not ready:
            break
        data = os.read(proc.stdout.fileno(), 1 << 20)
        if not data:
            break
        now = (time.perf_counter() - t0) * 1e3
        if bulk_ms is None and b"B" in data:
            bulk_ms = now
        if tail_ms is None and b"A3" in data:
            tail_ms = now
    proc.wait()
    exit_ms = (time.perf_counter() - t0) * 1e3
    return bulk_ms, tail_ms, exit_ms


def main():
    print(f"{'layer':>7} {'bytes':>9} {'bulk_ms':>9} {'tail_ms':>9} "
          f"{'exit_ms':>9}  verdict")
    for layer in ("os", "buffer", "text"):
        for n in SIZES:
            bulk, tail, exit_ms = run(layer, n)
            if bulk is None:
                verdict = "MISSING"
            elif bulk < 450:
                verdict = "EARLY (write-time flush)"
            else:
                verdict = "WITHHELD (exit flush)"
            b = f"{bulk:.1f}" if bulk is not None else "-"
            t = f"{tail:.1f}" if tail is not None else "-"
            print(f"{layer:>7} {n:>9} {b:>9} {t:>9} {exit_ms:>9.1f}  {verdict}")


if __name__ == "__main__":
    main()
