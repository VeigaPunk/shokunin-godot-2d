"""r72-scout scratch — reorder-window boundary, text-layer-coalesced form.

Writer: R-HEAD (7 B) unflushed, then N crossing bytes ('C'*N) in ONE
sys.stdout.write, then descendant (sh printf R-INJ) into inherited fd1,
then R-TAIL + flush. CPython's text layer coalesces the pending batch
(7 + N) into one binary-layer write; the reorder window is expected to
stay open while 7+N < io.DEFAULT_BUFFER_SIZE and to close at >= it
(HEAD released with the crossing, before the descendant write).

Run: python3 boundary_pair.py
"""

import io
import subprocess
import sys

EDGE = io.DEFAULT_BUFFER_SIZE
HEAD_BYTES = len(b"R-HEAD\n")
for n in (0, EDGE - HEAD_BYTES - 1, EDGE - HEAD_BYTES,
          EDGE - HEAD_BYTES + 1, EDGE - 1, EDGE):
    total_pending = n + HEAD_BYTES
    src = (
        "import sys,subprocess\n"
        "sys.stdout.write('R-HEAD\\n')\n"
        f"sys.stdout.write('C' * {n})\n"
        "p = subprocess.Popen(['sh', '-c', 'printf \"R-INJ\\\\n\"'])\n"
        "p.wait()\n"
        "sys.stdout.write('R-TAIL\\n')\n"
        "sys.stdout.flush()\n"
    )
    proc = subprocess.run([sys.executable, "-c", src],
                          capture_output=True)
    d = proc.stdout
    head, inj, tail = (d.find(b"R-HEAD"), d.find(b"R-INJ"),
                       d.find(b"R-TAIL"))
    if -1 in (head, inj, tail):
        topo = "MISSING"
    elif inj < head < tail:
        topo = "reorder"
    elif head < inj < tail:
        topo = "splice"
    else:
        topo = "mixed"
    print(f"BOUNDARY n={n} pending_total={total_pending} edge={EDGE} "
          f"topology={topo} head_idx={head} inj_idx={inj} tail_idx={tail} "
          f"total_bytes={len(d)} rc={proc.returncode}")
