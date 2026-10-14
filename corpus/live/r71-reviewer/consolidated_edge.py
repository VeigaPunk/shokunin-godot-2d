"""r71 reviewer scratch: consolidated withholding-edge receipt.

Runs the full independent matrix once (3 reps for edge cells) and writes
consolidated-edge.json / consolidated-edge.txt. Layers:
  T = sys.stdout (TextIOWrapper -> BufferedWriter(131072) -> FileIO)
  B = sys.stdout.buffer (BufferedWriter only)
Child steps are emitted inline; parent timestamps chunk arrivals.
"""
import json
import os
import select
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent

TEXT_CHILD = r'''
import json, sys, time
steps = json.loads(sys.argv[1])
out = sys.stdout
for st in steps:
    op = st[0]
    if op == "w": out.write("F" * int(st[1]))
    elif op == "wm": out.write(st[1])
    elif op == "flush": out.flush()
    elif op == "sleep": time.sleep(float(st[1]) / 1000.0)
'''

BUF_CHILD = r'''
import json, sys, time
steps = json.loads(sys.argv[1])
out = sys.stdout.buffer
for st in steps:
    op = st[0]
    if op == "w": out.write(b"F" * int(st[1]))
    elif op == "wm": out.write(st[1].encode())
    elif op == "flush": out.flush()
    elif op == "sleep": time.sleep(float(st[1]) / 1000.0)
'''


def run(child_src, steps, timeout=8.0):
    t0 = time.perf_counter()
    p = subprocess.Popen([sys.executable, "-c", child_src, json.dumps(steps)],
                         stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    fd = p.stdout.fileno()
    os.set_blocking(fd, False)
    ev, cum = [], 0
    while True:
        r, _, _ = select.select([fd], [], [], 0.002)
        if r:
            c = os.read(fd, 1 << 20)
            t = (time.perf_counter() - t0) * 1000.0
            if c == b"":
                break
            cum += len(c)
            ev.append([round(t, 3), len(c), cum])
        if time.perf_counter() - t0 > timeout:
            p.kill()
            break
    p.wait()
    return ev, cum


def cell(layer, name, steps, nreps=1):
    src = TEXT_CHILD if layer == "T" else BUF_CHILD
    rows = []
    for _ in range(nreps):
        ev, total = run(src, steps)
        early = max((c for t, n, c in ev if t < 250.0), default=0)
        first = ev[0][0] if ev else None
        rows.append({"first_ms": first, "early_bytes": early, "total": total,
                     "events": ev})
    return {"layer": layer, "cell": name, "steps": steps, "reps": rows}


def main():
    rows = []
    # exact edge, text layer, 3 reps
    for name, n in [("T single 131071", 131071), ("T single 131072", 131072),
                    ("T single 131073", 131073)]:
        rows.append(cell("T", name, [["wm", "H\n"], ["flush"], ["w", n],
                                     ["sleep", 300]], 3))
    # below-edge cells
    for name, n in [("T single 8192", 8192), ("T single 65536", 65536)]:
        rows.append(cell("T", name, [["wm", "H\n"], ["flush"], ["w", n],
                                     ["sleep", 300]], 2))
    # accumulation cells
    rows.append(cell("T", "T 132x1000", [["wm", "H\n"], ["flush"]] +
                     [["w", 1000]] * 132 + [["sleep", 300]], 2))
    rows.append(cell("T", "T 135x1000", [["wm", "H\n"], ["flush"]] +
                     [["w", 1000]] * 135 + [["sleep", 300]], 2))
    rows.append(cell("T", "T 16x8192", [["wm", "H\n"], ["flush"]] +
                     [["w", 8192]] * 16 + [["sleep", 300]], 2))
    rows.append(cell("T", "T 17x8192", [["wm", "H\n"], ["flush"]] +
                     [["w", 8192]] * 17 + [["sleep", 300]], 2))
    # buffered layer
    rows.append(cell("B", "B single 131071", [["wm", "H\n"], ["flush"],
                                              ["w", 131071], ["sleep", 300]], 2))
    rows.append(cell("B", "B single 131072", [["wm", "H\n"], ["flush"],
                                              ["w", 131072], ["sleep", 300]], 2))
    rows.append(cell("B", "B 132x1000", [["wm", "H\n"], ["flush"]] +
                     [["w", 1000]] * 132 + [["sleep", 300]], 2))
    # controls
    rows.append(cell("T", "T flush control", [["wm", "A\n"], ["flush"],
                                              ["sleep", 300], ["wm", "B\n"],
                                              ["flush"]], 2))

    (HERE / "consolidated-edge.json").write_text(
        json.dumps(rows, indent=2) + "\n")
    lines = []
    for r in rows:
        for i, rep in enumerate(r["reps"]):
            lines.append(f"{r['cell']:16s} rep{i} first={rep['first_ms']}ms "
                         f"early={rep['early_bytes']} total={rep['total']}")
    (HERE / "consolidated-edge.txt").write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    return 0


if __name__ == "__main__":
    sys.exit(main())
