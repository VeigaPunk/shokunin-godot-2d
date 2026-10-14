"""r71 scout — parent-side withholding-edge probe (the open falsifier).

Claim under test (from frontier-pygame remaining unknowns):
  "stdout withholding is a language-layer window bounded by buffer size"
  falsifiable via a >8KB mid-run unflushed write surfacing early.

For each case: spawn withhold_child.py with stdout=PIPE (binary, no text
layer), poll readability, record
  first_vis_ms   — parent-visible latency of the first byte
  vis_mid_bytes  — cumulative bytes parent-visible at t = MID_MS after spawn
  exit_ms        — child exit time
  total_bytes    — bytes drained across the whole life
  integrity      — drained bytes == expected payload bytes
plus the full read-event timeline for partial-visibility cases.

3 reps per case. Emits WITHHOLD-REP lines on stdout + JSON receipt.
"""

import json
import os
import select
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
CHILD = HERE / "withhold_child.py"
MID_MS = 300.0
REPS = 3
SLEEP = 600          # single-write cases: exit well after MID_MS
SEG_SLEEP1 = 250     # segmented: second write lands ~270ms (before MID)
SEG_SLEEP2 = 350

CASES = [
    # name, ops, interpreter flags (before script), child flags (after)
    ("small",          [["w", 100, "x"], ["s", SLEEP]], [], []),
    ("small_pg",       [["w", 100, "x"], ["s", SLEEP]], [], ["--import-pygame"]),
    ("edge_8192",      [["w", 8192, "x"], ["s", SLEEP]], [], []),
    ("edge_65536",     [["w", 65536, "x"], ["s", SLEEP]], [], []),
    ("edge_128k_lo",   [["w", 131071, "x"], ["s", SLEEP]], [], []),
    ("edge_128k_eq",   [["w", 131072, "x"], ["s", SLEEP]], [], []),
    ("edge_128k_hi",   [["w", 131073, "x"], ["s", SLEEP]], [], []),
    ("big_200k",       [["w", 200000, "x"], ["s", SLEEP]], [], []),
    ("big_200k_pg",    [["w", 200000, "x"], ["s", SLEEP]], [],
     ["--import-pygame"]),
    ("seg_64k_64k",    [["w", 65536, "x"], ["s", SEG_SLEEP1],
                        ["w", 65536, "y"], ["s", SEG_SLEEP2]], [], []),
    ("seg_70k_70k",    [["w", 70000, "x"], ["s", SEG_SLEEP1],
                        ["w", 70000, "y"], ["s", SEG_SLEEP2]], [], []),
    ("seg_131072_100", [["w", 131072, "x"], ["s", SEG_SLEEP1],
                        ["w", 100, "y"], ["s", SEG_SLEEP2]], [], []),
    ("flush_control",  [["w", 100, "x"], ["s", 200], ["f", 100, "z"],
                        ["s", 300]], [], []),
    ("unbuf_control",  [["w", 100, "x"], ["s", SLEEP]], ["-u"], []),
]


def expected_bytes(ops):
    out = b""
    for op in ops:
        if op[0] in ("w", "f"):
            out += (op[2] * (op[1] - 1) + "\n").encode()
    return out


def run_case(ops, before, after):
    env = {k: v for k, v in os.environ.items() if k != "PYTHONUNBUFFERED"}
    env["PYGAME_HIDE_SUPPORT_PROMPT"] = "1"
    argv = [sys.executable, *before, str(CHILD), json.dumps(ops), *after]
    t0 = time.perf_counter()
    proc = subprocess.Popen(argv, stdout=subprocess.PIPE,
                            stderr=subprocess.DEVNULL, env=env, bufsize=0)
    fd = proc.stdout.fileno()
    os.set_blocking(fd, False)
    first_vis = None
    vis_mid = None
    chunks = []
    while True:
        r, _, _ = select.select([proc.stdout], [], [], 0.005)
        if r:
            try:
                data = os.read(fd, 1 << 20)
            except (BlockingIOError, OSError):
                data = b""
            if data:
                now = time.perf_counter()
                if first_vis is None:
                    first_vis = now - t0
                chunks.append((round((now - t0) * 1e3, 1), data))
        cum = sum(len(c[1]) for c in chunks)
        if vis_mid is None and (time.perf_counter() - t0) * 1e3 >= MID_MS:
            vis_mid = cum
        if proc.poll() is not None:
            break
        if (time.perf_counter() - t0) > 5.0:
            proc.kill()
            break
    exit_ms = (time.perf_counter() - t0) * 1e3
    while True:
        try:
            d = os.read(fd, 1 << 20)
        except (BlockingIOError, OSError):
            break
        if not d:
            break
        chunks.append((round((time.perf_counter() - t0) * 1e3, 1), d))
    proc.wait()
    if vis_mid is None:
        vis_mid = sum(len(c[1]) for c in chunks)
    got = b"".join(c[1] for c in chunks)
    return {
        "first_vis_ms": None if first_vis is None else round(first_vis * 1e3, 1),
        "vis_mid_bytes": vis_mid,
        "exit_ms": round(exit_ms, 1),
        "total_bytes": len(got),
        "integrity": int(got == expected_bytes(ops)),
        "timeline": [[t, len(d)] for t, d in chunks],
        "rc": proc.returncode,
    }


def main():
    receipt = {"python": sys.version, "mid_ms": MID_MS, "reps": REPS,
               "cases": {}}
    for name, ops, before, after in CASES:
        reps = []
        for i in range(REPS):
            r = run_case(ops, before, after)
            reps.append(r)
            print(f"WITHHOLD-REP {name} | rep={i} "
                  f"first_vis_ms={r['first_vis_ms']} "
                  f"vis_mid_ms={MID_MS:.0f} vis_mid_bytes={r['vis_mid_bytes']} "
                  f"exit_ms={r['exit_ms']} total_bytes={r['total_bytes']} "
                  f"integrity={r['integrity']} rc={r['rc']}", flush=True)
        receipt["cases"][name] = {"ops": ops, "before": before,
                                  "after": after, "reps": reps}
    out = HERE / "withhold_receipt.json"
    out.write_text(json.dumps(receipt, indent=2) + "\n")
    print(f"WITHHOLD_RECEIPT {out}", flush=True)


if __name__ == "__main__":
    main()
