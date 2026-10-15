"""r72-critic: same parent role as reorder_demo.py, but the parent is a
pygame 2.6.1 headless process (the actual fixture runtime).

Checks whether the reorder composition transfers from bare CPython to the
pygame process the round-72 arm would instrument. Headless contract pinned
before import, same as the tracked fixture.
"""
import argparse
import os
import subprocess
import sys
import time

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
os.environ.setdefault("PYGAME_HIDE_SUPPORT_PROMPT", "1")

import pygame  # noqa: E402

ap = argparse.ArgumentParser()
ap.add_argument("--child", choices=["printf", "pybuf", "pyu", "pyslow", "bg"],
                default="printf")
ap.add_argument("--flush-after-tail", type=int, default=1)
ap.add_argument("--sleep", type=float, default=0.0)
ap.add_argument("--marker-style", choices=["line", "inline"], default="line")
a = ap.parse_args()

pygame.init()
pygame.display.set_mode((320, 240))

if a.marker_style == "line":
    HEAD, TAIL, CHILD = "HEAD\n", "TAIL\n", "CHILD\n"
else:
    HEAD, TAIL, CHILD = "HEAD ", " TAIL", "CHILD"

sys.stdout.write(HEAD)
if a.child == "bg":
    subprocess.Popen(
        [sys.executable, "-c",
         "import time,sys; time.sleep(0.3); sys.stdout.write(%r)" % CHILD])
elif a.child == "printf":
    os.system("printf '%s'" % CHILD)
elif a.child == "pybuf":
    subprocess.run([sys.executable, "-c",
                    "import sys; sys.stdout.write(%r)" % CHILD])
elif a.child == "pyu":
    subprocess.run([sys.executable, "-u", "-c",
                    "import sys; sys.stdout.write(%r)" % CHILD])
elif a.child == "pyslow":
    subprocess.run([sys.executable, "-c",
                    "import time,sys; time.sleep(0.3); sys.stdout.write(%r)" % CHILD])
sys.stdout.write(TAIL)
if a.flush_after_tail:
    sys.stdout.flush()
if a.sleep:
    time.sleep(a.sleep)
pygame.quit()
