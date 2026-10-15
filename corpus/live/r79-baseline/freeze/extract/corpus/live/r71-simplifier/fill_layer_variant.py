"""r71 simplifier scratch: the fill arm's flush size, text layer vs raw buffer.

Both children: print MARK-1; sleep 100ms; 200 x 1000-byte writes; sleep 100ms;
print MARK-2. One writes via sys.stdout.write (text layer, the landed
fixture's form), the other via sys.stdout.buffer.write (bytes, no text layer).

Prints the burst structure so the 126007-byte early flush can be attributed
and the landed `early_bytes` accounting rule (chunks strictly before the read
that *completes* MARK-2) can be checked against the real burst boundary.
"""
import os
import select
import subprocess
import sys
import time

CHILDREN = {
    "text": ("import sys,time;"
             "print('MARK-1');"
             "time.sleep(0.10);"
             "[sys.stdout.write('C'*1000) for _ in range(200)];"
             "time.sleep(0.10);"
             "print('MARK-2')"),
    "buffer": ("import sys,time;"
               "print('MARK-1');"
               "time.sleep(0.10);"
               "[sys.stdout.buffer.write(b'C'*1000) for _ in range(200)];"
               "time.sleep(0.10);"
               "print('MARK-2')"),
}

ENV = {k: v for k, v in os.environ.items() if k != "PYTHONUNBUFFERED"}


def run(child):
    proc = subprocess.Popen([sys.executable, "-c", child],
                            stdout=subprocess.PIPE,
                            stderr=subprocess.DEVNULL, env=ENV)
    fd = proc.stdout.fileno()
    t0 = time.perf_counter()
    chunks = []
    while True:
        ready, _, _ = select.select([fd], [], [], 10.0)
        if not ready:
            chunks.append((-1.0, 0))
            break
        c = os.read(fd, 65536)
        if not c:
            break
        chunks.append((round((time.perf_counter() - t0) * 1e3, 2), len(c)))
    proc.wait()
    return chunks


def landed_rule(chunks):
    """bytes counted early by the landed rule (needs MARK-2 position)."""
    return chunks


def main():
    for name, child in CHILDREN.items():
        for rep in range(2):
            chunks = run(child)
            bursts = []
            for i, (ms, n) in enumerate(chunks):
                if not bursts or ms - bursts[-1][-1][0] > 20:
                    bursts.append([])
                bursts[-1].append((ms, n))
            print(f"{name} rep{rep} chunks={chunks}")
            print(f"   bursts={[ (b[0][0], sum(n for _, n in b)) for b in bursts ]}")


if __name__ == "__main__":
    main()
