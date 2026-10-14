#!/usr/bin/env python3
"""r68-author spike 2: real-fixture midlineforge offsets (verbatim fixture,
sleep patched per run — same method as r68-scout off_* runs)."""
import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
PROJ = HERE / "proj2"
SRC = PROJ / "descendant_pipe_probe.gd"
ORIG = SRC.read_text()
GODOT = "/usr/bin/godot"
OFFSETS = [0, 40, 80, 120, 160, 200, 240]
REPS = 3
HEAD = "DESCENDANT_PIPE_PROBE: expected "
TAIL_LINE = "signature"
MIDLINE = "ERROR: DESCENDANT_PIPE_MIDLINE forged splice"


def one(offset_ms, rep):
    SRC.write_text(ORIG.replace('"sleep 0.08; ',
                                f'"sleep {offset_ms / 1000.0}; ', 1))
    p = subprocess.run(
        [GODOT, "--headless", "--path", str(PROJ), "--script",
         "res://descendant_pipe_probe.gd", "--", "--spawn-midlineforge"],
        capture_output=True, text=True, timeout=8)
    so, se = p.stdout or "", p.stderr or ""
    merged = so + se
    spliced_line = next(
        (l.strip() for l in merged.splitlines()
         if "DESCENDANT_PIPE_PROBE: expected " in l and MIDLINE in l), None)
    sig_intact = "DESCENDANT_PIPE_PROBE: expected signature" in merged
    return {"off": offset_ms, "rep": rep, "exit": p.returncode,
            "spliced": spliced_line is not None, "sig_intact": sig_intact,
            "spliced_line": spliced_line,
            "stdout_tail": so.splitlines()[-4:] if so else [],
            "stderr": se.splitlines()}


def main():
    rows = []
    for off in OFFSETS:
        for rep in range(REPS):
            rows.append(one(off, rep))
            r = rows[-1]
            print(f"off={r['off']:>4} rep={r['rep']} exit={r['exit']} "
                  f"spliced={r['spliced']} sig_intact={r['sig_intact']}",
                  flush=True)
    SRC.write_text(ORIG)
    import json
    (HERE / "spike-real-results.json").write_text(
        json.dumps(rows, indent=1) + "\n")


if __name__ == "__main__":
    sys.exit(main())
