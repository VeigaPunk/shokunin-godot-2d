"""r72-critic cell: one reorder/midline/append measurement on the host.

Role: the parent process writes HEAD (unflushed), spawns a descendant
that writes CHILD into the inherited fd1, writes TAIL, then optionally
flushes and/or sleeps. The harness capture sees the wire order.

Parent stdio mode is chosen by the runner (python3 vs python3 -u vs
PYTHONUNBUFFERED=1); child mode by --child.
"""
import argparse
import os
import subprocess
import sys
import time

ap = argparse.ArgumentParser()
ap.add_argument("--child", choices=["printf", "pybuf", "pyu", "pyslow", "bg"],
                default="printf")
ap.add_argument("--flush-after-tail", type=int, default=1)
ap.add_argument("--sleep", type=float, default=0.0)
ap.add_argument("--marker-style", choices=["line", "inline"], default="line")
a = ap.parse_args()

if a.marker_style == "line":
    HEAD, TAIL, CHILD = "HEAD\n", "TAIL\n", "CHILD\n"
else:
    HEAD, TAIL, CHILD = "HEAD ", " TAIL", "CHILD"     # xconnector demo shape


def spawn_sync():
    if a.child == "printf":
        # write-through shell descendant (the xconnector demo's vehicle)
        return os.system("printf '%s'" % CHILD)
    if a.child == "pybuf":
        return subprocess.run(
            [sys.executable, "-c",
             "import sys; sys.stdout.write(%r)" % CHILD]).returncode
    if a.child == "pyu":
        return subprocess.run(
            [sys.executable, "-u", "-c",
             "import sys; sys.stdout.write(%r)" % CHILD]).returncode
    if a.child == "pyslow":
        return subprocess.run(
            [sys.executable, "-c",
             "import time,sys; time.sleep(0.3); sys.stdout.write(%r)" % CHILD]).returncode
    raise SystemExit("bg is spawned separately")


sys.stdout.write(HEAD)
if a.child == "bg":
    # backgrounded, slow: writes at ~0.3s while the parent may already
    # have flushed (closed window -> append) or still withhold (reorder)
    subprocess.Popen(
        [sys.executable, "-c",
         "import time,sys; time.sleep(0.3); sys.stdout.write(%r)" % CHILD])
else:
    spawn_sync()
sys.stdout.write(TAIL)
if a.flush_after_tail:
    sys.stdout.flush()
if a.sleep:
    time.sleep(a.sleep)
