"""r72-scout scratch — crossing-release structure map (order-only).

Same descendant-order observable as boundary_pair.py, but varies the
WRITE STRUCTURE feeding the text layer:
  A  : no prior pending, one write of E        (r71 single-write shape)
  A2 : no prior pending, one write of E-1
  B  : R-HEAD then one write of E-7            (coalesced pending = E)
  C  : R-HEAD then one write of E-6            (coalesced pending = E+1)
  H  : R-HEAD then two writes summing to E-7   (coalesced pending = E)
  H2 : R-HEAD then two writes summing to E-6   (coalesced pending = E+1)
E = io.DEFAULT_BUFFER_SIZE. Observable: does the big write hit the wire
before the descendant's R-INJ (released) or after (withheld)?

Run: python3 boundary_struct.py
"""

import io
import subprocess
import sys

E = io.DEFAULT_BUFFER_SIZE

STRUCTS = {
    "A_no_prior_E":        ["W('B' * %d)" % E],
    "A2_no_prior_E-1":     ["W('B' * %d)" % (E - 1)],
    "B_head_one_E-7":      ["W('R-HEAD\\n')", "W('C' * %d)" % (E - 7)],
    "C_head_one_E-6":      ["W('R-HEAD\\n')", "W('C' * %d)" % (E - 6)],
    "H_head_two_sum_E-7":  ["W('R-HEAD\\n')", "W('C' * 60000)",
                            "W('C' * %d)" % (E - 7 - 60000)],
    "H2_head_two_sum_E-6": ["W('R-HEAD\\n')", "W('C' * 60000)",
                            "W('C' * %d)" % (E - 6 - 60000)],
}

for label, ops in STRUCTS.items():
    body = "\n".join(ops)
    src = (
        "import sys,subprocess\n"
        "W = sys.stdout.write\n"
        f"{body}\n"
        "p = subprocess.Popen(['sh', '-c', 'printf \"R-INJ\\\\n\"'])\n"
        "p.wait()\n"
        "W('R-TAIL\\n')\n"
        "sys.stdout.flush()\n"
    )
    proc = subprocess.run([sys.executable, "-c", src], capture_output=True)
    d = proc.stdout
    inj = d.find(b"R-INJ")
    head = d.find(b"R-HEAD")
    tail = d.find(b"R-TAIL")
    big_first = d[:1] == b"B" or d[:1] == b"C" or d[:1] == b"R"
    if inj < 0:
        topo = "MISSING"
    elif inj == 0:
        topo = "withheld"
    elif head == 0 and inj > head:
        topo = "released(head-first)"
    elif inj > 0 and d[:1] in (b"B", b"C"):
        topo = "released(big-first)"
    else:
        topo = "other"
    print(f"STRUCT {label:22s} edge={E} verdict={topo} "
          f"head_idx={head} inj_idx={inj} tail_idx={tail} "
          f"total_bytes={len(d)} rc={proc.returncode}")
