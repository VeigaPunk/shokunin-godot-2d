"""r71-verifier independent edge scan: first parent-visible ms for a
mid-run unflushed write of size k, sweeping k across the two candidate
bounds (8192 frontier claim vs 131072 = io.DEFAULT_BUFFER_SIZE author
claim). Child: MARK-1, sleep 100ms, write k bytes, sleep 100ms, MARK-2.
Parent: select+os.read, raw fd. Plain python3 child (no pygame) --
language-layer claim tested at language layer.
"""
import io
import os
import select
import subprocess
import sys
import time

SIZES = [4096, 8192, 8193, 9000, 65536, 131071, 131072, 131073, 200000]
ENV = {k: v for k, v in os.environ.items() if k != "PYTHONUNBUFFERED"}


def scan(k):
    src = ("import sys,time;print('MARK-1');time.sleep(0.10);"
           f"sys.stdout.write('B'*{k});time.sleep(0.10);print('MARK-2')")
    t0 = time.perf_counter()
    p = subprocess.Popen([sys.executable, "-c", src],
                         stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
                         env=ENV)
    fd = p.stdout.fileno()
    first = None
    data = 0
    while True:
        r, _, _ = select.select([fd], [], [], 5.0)
        if not r:
            break
        chunk = os.read(fd, 65536)
        if not chunk:
            break
        if first is None:
            first = (time.perf_counter() - t0) * 1e3
        data += len(chunk)
    p.wait()
    eof = (time.perf_counter() - t0) * 1e3
    return first, eof, data


print(f"io.DEFAULT_BUFFER_SIZE={io.DEFAULT_BUFFER_SIZE}")
for k in SIZES:
    f, e, d = scan(k)
    tag = "EXIT-BATCHED" if f is not None and f > e - 25 else "EARLY"
    print(f"k={k:>7} first_vis_ms={f if f is not None else -1:>8.2f} "
          f"eof_ms={e:7.2f} total={d:>7} -> {tag}")
