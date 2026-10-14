"""r71 scout — withholding-edge child.

Writes controlled byte amounts to stdout WITHOUT flushing (unless asked),
on a pipe created by the parent probe. Exits after the scripted ops; the
interpreter's implicit stdout flush at exit is the second visibility edge.

argv: withhold_child.py <spec-json> [--import-pygame]
spec: JSON list of ops:
    ["w", n, ch]  write ch*(n-1) + "\n"   (no flush)
    ["f", n, ch]  write ch*(n-1) + "\n"   (immediate flush)
    ["s", ms]     sleep
"""

import json
import sys
import time


def main():
    spec = json.loads(sys.argv[1])
    if "--import-pygame" in sys.argv:
        import pygame  # noqa: F401  (import-cost + banner parity control)
    for op in spec:
        if op[0] == "w":
            sys.stdout.write(op[2] * (op[1] - 1) + "\n")
        elif op[0] == "f":
            sys.stdout.write(op[2] * (op[1] - 1) + "\n")
            sys.stdout.flush()
        elif op[0] == "s":
            time.sleep(op[1] / 1000.0)


if __name__ == "__main__":
    main()
