"""r71 simplifier scratch: replicate the landed `withhold_fill` child exactly
and print the byte timeline, to explain the whf_early_bytes FAIL.

Child (from corpus/fixtures/pygame_probe.py:220-221):
  print('MARK-1'); sleep(0.10); [sys.stdout.write('C'*1000) for _ in range(200)];
  sleep(0.10); print('MARK-2')
"""
import os
import select
import subprocess
import sys
import time

CHILD = ("import sys,time;"
         "print('MARK-1');"
         "time.sleep(0.10);"
         "[sys.stdout.write('C'*1000) for _ in range(200)];"
         "time.sleep(0.10);"
         "print('MARK-2')")

ENV = {k: v for k, v in os.environ.items() if k != "PYTHONUNBUFFERED"}
REPS = 3


def run():
    proc = subprocess.Popen([sys.executable, "-c", CHILD],
                            stdout=subprocess.PIPE,
                            stderr=subprocess.DEVNULL, env=ENV)
    fd = proc.stdout.fileno()
    t0 = time.perf_counter()
    chunks = []
    data = b""
    while True:
        ready, _, _ = select.select([fd], [], [], 10.0)
        if not ready:
            chunks.append((-1.0, 0))
            break
        c = os.read(fd, 65536)
        if not c:
            break
        ms = (time.perf_counter() - t0) * 1e3
        chunks.append((round(ms, 2), len(c)))
        data += c
    proc.wait()
    return chunks, data


def main():
    for rep in range(REPS):
        chunks, data = run()
        mark2_off = data.find(b"MARK-2")
        early = sum(n for ms, n in chunks if 0 <= ms < chunks[-1][0]) if chunks else 0
        # replicate the landed early_bytes rule exactly: chunks strictly
        # before the read whose cumulative count reaches MARK-2's end
        seen = 0
        mark2_ms = None
        for ms, n in chunks:
            seen += n
            if mark2_off >= 0 and seen >= mark2_off + len(b"MARK-2"):
                mark2_ms = ms
                break
        early_landed_rule = sum(n for ms, n in chunks if 0 <= ms < (mark2_ms or 0))
        print(f"rep{rep} total={len(data)} mark2_ms={mark2_ms} "
              f"early_bytes={early_landed_rule} chunks={chunks}")


if __name__ == "__main__":
    main()
