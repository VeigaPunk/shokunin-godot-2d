"""r72-scout scratch — streaming observer for reorder_mini.py.

Spawns `python3 [-u] reorder_mini.py <variants>` with stdout=PIPE, reads
the pipe incrementally with raw os.read + select (no reader-side stdio
buffering), timestamps every read, records whether the writer was still
alive at the first read, and reports:
  - the observed marker order (reorder | splice | suffix | mixed)
  - the read timeline
  - alive_at_first (streaming hazard: INJ visible while writer alive)

Usage: python3 reorder_harness.py [--unbuf] [-- <mini variants...>]
Exit 0 always; receipt on stdout (key=value lines + raw data).
"""

import os
import select
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
MINI = os.path.join(HERE, "reorder_mini.py")

argv = sys.argv[1:]
unbuf = "--unbuf" in argv
if unbuf:
    argv.remove("--unbuf")
if argv[:1] == ["--"]:
    argv = argv[1:]

cmd = [sys.executable] + (["-u"] if unbuf else []) + [MINI] + argv
env = dict(os.environ)
env.setdefault("SDL_VIDEODRIVER", "dummy")
env.setdefault("SDL_AUDIODRIVER", "dummy")
env.setdefault("PYGAME_HIDE_SUPPORT_PROMPT", "1")

t0 = time.perf_counter()
proc = subprocess.Popen(cmd, stdout=subprocess.PIPE,
                        stderr=subprocess.DEVNULL, env=env)
fd = proc.stdout.fileno()
chunks = []
data = b""
alive_at_first = None
while True:
    ready, _, _ = select.select([fd], [], [], 10.0)
    if not ready:
        chunks.append((-1.0, 0))
        break
    chunk = os.read(fd, 65536)
    if not chunk:
        break
    ms = (time.perf_counter() - t0) * 1e3
    if alive_at_first is None:
        alive_at_first = proc.poll() is None
    chunks.append((ms, len(chunk)))
    data += chunk
proc.wait()
eof_ms = (time.perf_counter() - t0) * 1e3


def pos(needle):
    return data.find(needle.encode())


p_head, p_inj, p_tail = pos("R-HEAD"), pos("R-INJ"), pos("R-TAIL")
if -1 in (p_head, p_inj, p_tail):
    topology = "MISSING"
elif p_inj < p_head < p_tail:
    topology = "reorder"
elif p_head < p_inj < p_tail:
    topology = "splice"
elif p_head < p_tail < p_inj:
    topology = "suffix"
else:
    topology = "mixed"

inj_first_read_ms = -1.0
seen = 0
for ms, n in chunks:
    if p_inj >= 0 and seen + n > p_inj:
        inj_first_read_ms = ms
        break
    seen += n

print(f"HARNESS mode={'unbuffered' if unbuf else 'buffered'} "
      f"variants={' '.join(argv) or '(none)'}")
print(f"HARNESS topology={topology} head_idx={p_head} inj_idx={p_inj} "
      f"tail_idx={p_tail} total_bytes={len(data)} "
      f"alive_at_first={alive_at_first} "
      f"inj_first_read_ms={round(inj_first_read_ms, 2)} "
      f"eof_ms={round(eof_ms, 2)} rc={proc.returncode}")
print(f"HARNESS timeline={[(round(ms, 2), n) for ms, n in chunks]}")
print("HARNESS raw_b64=" + __import__("base64").b64encode(data).decode())
