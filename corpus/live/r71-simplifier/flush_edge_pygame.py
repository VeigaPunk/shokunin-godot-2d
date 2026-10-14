"""r71 simplifier scratch: does the withholding edge change under a
pygame-importing child?

The frontier report's window was measured on a pygame child (`--io-child
buf`), and the scout's pygame-parity control (`--import-pygame`) returned
rc=2 with no output on 3/3 reps -- so the pygame-child edge was never
pinned. This probe pins it.

Child: optionally `import pygame` (env pinned dummy), then unflushed
  A1\n at t0, B*n at t0+300ms, A3\n at t0+600ms via sys.stdout (text layer,
  the layer a `print()` fixture actually uses).
Parent: select+os.read timestamps for the first chunk carrying 'B'.
"""
import os
import select
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
CHILD = os.path.join(HERE, "flush_child_pg.py")

ENV = dict(os.environ,
           SDL_VIDEODRIVER="dummy",
           SDL_AUDIODRIVER="dummy",
           PYGAME_HIDE_SUPPORT_PROMPT="1")

SIZES = [8192, 131071, 131072, 131073]
REPS = 3


def run(import_pg, n):
    argv = [sys.executable, CHILD, str(n)] + (["--import-pygame"] if import_pg else [])
    proc = subprocess.Popen(argv, stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE, text=False, env=ENV)
    t0 = time.perf_counter()
    bulk_ms = None
    while True:
        ready, _, _ = select.select([proc.stdout], [], [], 5.0)
        if not ready:
            break
        data = os.read(proc.stdout.fileno(), 1 << 20)
        if not data:
            break
        if bulk_ms is None and b"B" in data:
            bulk_ms = (time.perf_counter() - t0) * 1e3
    err = proc.stderr.read()
    proc.wait()
    return bulk_ms, proc.returncode, err[:120]


def main():
    print(f"python={sys.version.split()[0]} reps={REPS} "
          f"SDL_VIDEODRIVER=dummy PYGAME_HIDE_SUPPORT_PROMPT=1")
    for import_pg in (False, True):
        label = "pygame-child" if import_pg else "plain-child "
        for n in SIZES:
            reps, rcs, errs = [], set(), []
            for _ in range(REPS):
                ms, rc, err = run(import_pg, n)
                reps.append(round(ms, 1) if ms is not None else None)
                rcs.add(rc)
                if err:
                    errs.append(err.decode(errors="replace").strip())
            verdicts = ["EARLY" if (m is not None and m < 450) else "WITHHELD"
                        for m in reps]
            print(f"{label} bulk={n:>7} reps_ms={reps} {verdicts} rc={sorted(rcs)}")
            for e in errs[:1]:
                print(f"    stderr: {e}")


if __name__ == "__main__":
    main()
