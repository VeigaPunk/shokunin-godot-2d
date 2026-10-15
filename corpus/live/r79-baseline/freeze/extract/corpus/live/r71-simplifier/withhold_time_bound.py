"""r71 simplifier scratch: is the withholding window time-bounded?

Child: writes A1\n unflushed at t0, sleeps 5s, writes A2\n, exits.
If the window were time-bounded (a timer/absorption window), A1 would
surface mid-sleep; if it is buffer/exit-bounded, A1 stays parent-invisible
for the whole 5s and lands with A2 at exit.

2 reps. Prints first-visible ms per line.
"""
import os
import select
import subprocess
import sys
import time

CHILD = ("import time;"
         "import sys;"
         "sys.stdout.write('A1\\n');"
         "time.sleep(5.0);"
         "sys.stdout.write('A2\\n')")


def run():
    proc = subprocess.Popen([sys.executable, "-c", CHILD],
                            stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
    t0 = time.perf_counter()
    seen = {}
    while True:
        ready, _, _ = select.select([proc.stdout], [], [], 8.0)
        if not ready:
            break
        data = os.read(proc.stdout.fileno(), 4096)
        if not data:
            break
        now = (time.perf_counter() - t0) * 1e3
        for line in data.decode(errors="replace").splitlines():
            seen.setdefault(line, round(now, 1))
    proc.wait()
    return seen, round((time.perf_counter() - t0) * 1e3, 1)


def main():
    print(f"python={sys.version.split()[0]} child sleeps 5000ms between writes")
    for rep in range(2):
        seen, exit_ms = run()
        print(f"rep{rep}: first_visible_ms={seen} exit_ms={exit_ms}")


if __name__ == "__main__":
    main()
