"""r71 simplifier scratch: parent-side flush-edge probe for piped CPython stdout.

Question (open in reports/frontier/fa-pygame.md "Remaining unknowns"):
  the withholding window is "unflushed line parent-invisible until ~8KB or
  exit" -- but is a mid-run >buffer write surfacing EARLY (partial visibility
  mid-life)? If yes, the window is bounded by buffer size, not by exit.

Method: spawn flush_child.py with stdout=PIPE (no -u), os.read with select
timestamps, attribute each line's first-parent-visible time to its slot
(t0=0ms / +300ms / +600ms). Bulk payload swept over sizes around the
CPython block-buffer boundary.

Receipt: flush-edge.txt (stdout is echoed by the caller).
"""
import os
import select
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
CHILD = os.path.join(HERE, "flush_child.py")

SIZES = [0, 1000, 4096, 8000, 8185, 8192, 8200, 9000, 16384, 65536]


def run(n):
    """Return (t_start, [(bytes, t_ms), ...], exit_ms, returncode)."""
    proc = subprocess.Popen([sys.executable, CHILD, str(n)],
                            stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
    t0 = time.perf_counter()
    chunks = []
    fd = proc.stdout
    while True:
        ready, _, _ = select.select([fd], [], [], 5.0)
        if not ready:
            break
        data = os.read(fd.fileno(), 65536)
        if not data:
            break
        chunks.append((data, (time.perf_counter() - t0) * 1e3))
    proc.wait()
    exit_ms = (time.perf_counter() - t0) * 1e3
    return chunks, exit_ms, proc.returncode


def attribute(chunks):
    """Map each complete line to the ms of the chunk that first carried it."""
    out = []
    for data, ms in chunks:
        for line in data.decode(errors="replace").splitlines():
            if line.startswith("CH-HEAD"):
                out.append(("HEAD", ms))
            elif line.startswith("CH-BULK"):
                out.append(("BULK", ms))
            elif line.startswith("CH-TAIL"):
                out.append(("TAIL", ms))
    return out


def main():
    print(f"python={sys.version.split()[0]} child={CHILD}")
    print(f"{'bulk_bytes':>10} {'n_chunks':>8} "
          f"{'HEAD_ms':>9} {'BULK_ms':>9} {'TAIL_ms':>9} {'exit_ms':>9} rc")
    for n in SIZES:
        chunks, exit_ms, rc = run(n)
        att = dict(attribute(chunks))
        print(f"{n:>10} {len(chunks):>8} "
              f"{att.get('HEAD', float('nan')):>9.1f} "
              f"{att.get('BULK', float('nan')):>9.1f} "
              f"{att.get('TAIL', float('nan')):>9.1f} "
              f"{exit_ms:>9.1f} {rc}")


if __name__ == "__main__":
    main()
