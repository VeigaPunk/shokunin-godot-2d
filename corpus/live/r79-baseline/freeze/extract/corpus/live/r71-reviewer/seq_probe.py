"""r71 reviewer scratch: stdout step-sequencer + visibility timeline.

Child spec = JSON list of steps:
  ["w", n]        write n 'F' bytes (unflushed)
  ["wm", text]    write literal text
  ["flush"]       flush stdout
  ["sleep", ms]   sleep ms
Parent records every chunk arrival (t_ms, n, cumulative).

Usage: python3 child_seq.py '<json>'        (child, run directly)
       python3 seq_probe.py '<json>'        (parent, prints timeline)
"""
import json
import os
import select
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent

CHILD = r"""
import json, sys, time
steps = json.loads(sys.argv[1])
out = sys.stdout
for st in steps:
    op = st[0]
    if op == "w":
        out.write("F" * int(st[1]))
    elif op == "wm":
        out.write(st[1])
    elif op == "flush":
        out.flush()
    elif op == "sleep":
        time.sleep(float(st[1]) / 1000.0)
sys.exit(0)
"""


def monitor(cmd, timeout=10.0):
    t0 = time.perf_counter()
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    fd = p.stdout.fileno()
    os.set_blocking(fd, False)
    events, cum = [], 0
    while True:
        r, _, _ = select.select([fd], [], [], 0.002)
        if r:
            c = os.read(fd, 1 << 20)
            t = (time.perf_counter() - t0) * 1000.0
            if c == b"":
                break
            cum += len(c)
            events.append([round(t, 3), len(c), cum])
        if time.perf_counter() > t0 + timeout:
            p.kill()
            break
    p.wait()
    return events


def main():
    steps = sys.argv[1]
    events = monitor([sys.executable, "-c", CHILD, steps])
    print("steps:", steps)
    for t, n, cum in events:
        print(f"  t={t:8.3f}ms n={n:7d} cum={cum:7d}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
