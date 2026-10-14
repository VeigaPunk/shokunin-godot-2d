"""r72-reviewer independent reorder-topology probe (scratch; not a fixture).

Ground truth for the round-72 claim surface: a spawned descendant writes
into inherited fd1 while the parent's earlier bytes are still withheld in
userspace. Parent here reads the child's raw fd with select+os.read and
prints the delivered byte order.

Cells: child default (block-buffered) / child -u / child flushed-before-spawn.
Descendant is a grandchild of this probe (os.system -> sh -> printf), i.e.
exactly the spawn-layer seam: inherited fd1, no fd plumbing by the child.
"""
import os
import select
import subprocess
import sys
import time

CHILD = (
    "import sys,time,os;"
    "sys.stdout.write('HEAD-');"
    "{flush}"
    "os.system(\"printf 'INJ>INJ'\");"
    "time.sleep(0.05);"
    "sys.stdout.write('-TAIL');"
    "time.sleep(0.05);"
    "print('', flush=True)"
)


def run_cell(name, argv_extra, flush_stmt):
    src = CHILD.format(flush=flush_stmt)
    env = {k: v for k, v in os.environ.items() if k != "PYTHONUNBUFFERED"}
    proc = subprocess.Popen([sys.executable] + argv_extra + ["-c", src],
                            stdout=subprocess.PIPE,
                            stderr=subprocess.DEVNULL, env=env)
    fd = proc.stdout.fileno()
    chunks = []
    t0 = time.perf_counter()
    data = b""
    while True:
        ready, _, _ = select.select([fd], [], [], 10.0)
        if not ready:
            chunks.append((-1.0, 0))
            break
        chunk = os.read(fd, 65536)
        if not chunk:
            break
        ms = (time.perf_counter() - t0) * 1e3
        chunks.append((round(ms, 2), len(chunk)))
        data += chunk
    proc.wait()
    text = data.decode(errors="replace")
    # find the first occurrence positions of the tokens
    head_at = text.find("HEAD-")
    inj_at = text.find("INJ>INJ")
    tail_at = text.find("-TAIL")
    print(f"REORDER-CELL {name} | bytes={text!r} chunks={chunks} "
          f"head_pos={head_at} inj_pos={inj_at} tail_pos={tail_at} "
          f"topology={'reorder' if (inj_at >= 0 and head_at >= 0 and inj_at < head_at) else ('splice' if inj_at > head_at else 'other')} "
          f"ret={proc.returncode}")


if __name__ == "__main__":
    run_cell("buffered", [], "")
    run_cell("unbuffered_u", ["-u"], "")
    run_cell("flushed", [], "sys.stdout.flush();")
