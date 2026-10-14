"""r71 reviewer scratch: flush-edge size matrix.

For each shape, spawn a child with piped stdout:
  W1 (flushed), then N bytes of 'F' via either one write or K equal
  writes, then sleep 300ms, then W2 unflushed, exit.
Record visible bytes at each chunk arrival time.

Usage: python3 flush_edge_matrix.py  -> flush_edge_matrix.json/.txt
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
import sys, time
mode, k, reps = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])
out = sys.stdout
t0 = time.monotonic()
out.write("W1\n"); out.flush()
payload = "F" * k
if mode == "one":
    out.write(payload)
else:
    per = max(1, k // reps)
    left = k
    while left > 0:
        n = min(per, left)
        out.write("F" * n)
        left -= n
time.sleep(0.300)
out.write("\nW2 t=%.3f\n" % ((time.monotonic() - t0) * 1000))
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
            events.append((round(t, 3), len(c), cum))
        if time.perf_counter() > t0 + timeout:
            p.kill()
            break
    p.wait()
    return events


def run(shape, k, reps):
    m = monitor([sys.executable, "-c", CHILD, shape, str(k), str(reps)])
    early = 0
    early_t = None
    for t, n, cum in m:
        if t < 250.0:  # before the child's 300ms sleep ends
            early = cum
            early_t = t
    return {"shape": shape, "k": k, "reps": reps,
            "events": m, "early_bytes": early, "early_t_ms": early_t,
            "total_bytes": m[-1][2] if m else 0,
            "last_t_ms": m[-1][0] if m else None}


def main():
    rows = []
    # single-write matrix around the 8KiB edge
    for k in [4096, 8191, 8192, 8193, 9000, 10240, 16384, 32768, 65536]:
        rows.append(run("one", k, 1))
    # multi-write accumulation (each write 1000 bytes)
    for k in [8192, 8193, 10000, 16384]:
        rows.append(run("many", k, max(1, k // 1000)))
    (HERE / "flush_edge_matrix.json").write_text(json.dumps(rows, indent=2) + "\n")
    lines = []
    for r in rows:
        lines.append(f"{r['shape']:5} k={r['k']:6d} reps={r['reps']:3d} "
                     f"early={r['early_bytes']:6d} early_t={r['early_t_ms']}ms "
                     f"total={r['total_bytes']:6d} last_t={r['last_t_ms']}ms "
                     f"events={[(t, n) for t, n, c in r['events']]}")
    (HERE / "flush_edge_matrix.txt").write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    return 0


if __name__ == "__main__":
    sys.exit(main())
