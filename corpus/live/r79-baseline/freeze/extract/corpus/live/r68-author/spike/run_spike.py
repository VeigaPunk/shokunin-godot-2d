#!/usr/bin/env python3
"""r68-author spike: measure the midlineforge fabrication window.

Runs the instrumented descendant_pipe_probe copy at several nominal offsets,
captures stdout/stderr separately, and reports per-rep:
  - head_ms / tail_ms (child stderr timestamps, CLOCK_REALTIME)
  - desc write_ms (descendant's own date+%s%3N)
  - splice_landed: descendant stdout bytes physically interposed between the
    signature head and tail bytes in the stdout stream
  - signature intact/destroyed
"""
import json
import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
PROJ = HERE / "proj"
GODOT = "/usr/bin/godot"
OFFSETS = [0, 40, 80, 120, 160, 200, 220, 240, 260, 300, 400]
REPS = 3
HEAD = "DESCENDANT_PIPE_PROBE: expected "
TAIL = "signature"


def one(offset_ms, rep):
    cmd = [GODOT, "--headless", "--path", str(PROJ), "--script",
           "res://midline_timing_probe.gd", "--",
           "--spawn-midlineforge", f"--midline-offset-ms={offset_ms}"]
    p = subprocess.run(cmd, capture_output=True, text=True, timeout=8)
    so, se = p.stdout or "", p.stderr or ""

    def ms(name, src):
        m = re.search(name + r"=(\d+)", src)
        return int(m.group(1)) if m else None

    head = ms("head", se)
    tail = ms("tail", se)
    write = ms("DESC_WRITE_MS", so)
    # Byte-order analysis on stdout.
    p_head = so.find(HEAD)
    spliced = False
    desc_before_head = False
    desc_after_tail = False
    sig_intact = False
    if p_head >= 0:
        head_end = p_head + len(HEAD)
        intact_prefix = HEAD + TAIL
        sig_intact = so[p_head:p_head + len(intact_prefix)] == intact_prefix
        p_tail = (so.find(TAIL, head_end) if not sig_intact
                  else p_head + len(intact_prefix))
        # Descendant payload markers in stdout.
        p_desc = so.find("DESC_WRITE_MS=")
        if p_desc is None:
            p_desc = so.find("ERROR: DESCENDANT_PIPE_MIDLINE")
        if p_desc is not None:
            if p_desc < p_head:
                desc_before_head = True
            elif p_desc > p_tail:
                desc_after_tail = True
            else:
                spliced = True
    return {"off": offset_ms, "rep": rep, "exit": p.returncode,
            "head_ms": head, "tail_ms": tail, "write_ms": write,
            "write_rel_head": (write - head) if None not in (write, head) else None,
            "write_rel_tail": (write - tail) if None not in (write, tail) else None,
            "gap_ms": (tail - head) if None not in (tail, head) else None,
            "spliced": spliced, "sig_intact": sig_intact,
            "desc_before_head": desc_before_head,
            "desc_after_tail": desc_after_tail}


def main():
    rows = []
    for off in OFFSETS:
        for rep in range(REPS):
            rows.append(one(off, rep))
            r = rows[-1]
            print(f"off={r['off']:>4} rep={r['rep']} exit={r['exit']} "
                  f"rel_head={r['write_rel_head']} rel_tail={r['write_rel_tail']} "
                  f"gap={r['gap_ms']} spliced={r['spliced']} "
                  f"sig_intact={r['sig_intact']} "
                  f"before={r['desc_before_head']} after={r['desc_after_tail']}",
                  flush=True)
    (HERE / "spike-results.json").write_text(json.dumps(rows, indent=1) + "\n")


if __name__ == "__main__":
    sys.exit(main())
