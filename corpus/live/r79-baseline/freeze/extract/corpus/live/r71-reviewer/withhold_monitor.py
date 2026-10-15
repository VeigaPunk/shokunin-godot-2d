"""r71 reviewer scratch: parent-side stdout-visibility monitor.

Spawns child_withhold.py <mode> with a piped stdout and records, for every
chunk that becomes parent-visible, the wall time (perf_counter) and the
cumulative byte offset. This is the independent measurement of the
"withholding window" the r71 author must pin.

Usage: python3 withhold_monitor.py [--reps N] [--child PATH]
Writes withhold_receipts.json + withhold_receipts.txt next to itself.
"""
import argparse
import json
import os
import select
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent


def monitor(cmd, timeout=15.0):
    t0 = time.perf_counter()
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE)
    fd = proc.stdout.fileno()
    os.set_blocking(fd, False)
    events = []
    cum = 0
    deadline = t0 + timeout
    eof_at = None
    while True:
        now = time.perf_counter()
        if now > deadline:
            proc.kill()
            return {"error": "TIMEOUT", "events": events}
        r, _, _ = select.select([fd], [], [], 0.002)
        if r:
            chunk = os.read(fd, 1 << 20)
            t = (time.perf_counter() - t0) * 1000.0
            if chunk == b"":
                eof_at = t
                break
            cum += len(chunk)
            events.append({"t_ms": round(t, 3), "n": len(chunk),
                           "cum": cum,
                           "head": chunk[:48].decode("utf-8", "replace")})
        if proc.poll() is not None:
            # drain remaining then EOF
            while True:
                r2, _, _ = select.select([fd], [], [], 0.05)
                if not r2:
                    break
                chunk = os.read(fd, 1 << 20)
                t = (time.perf_counter() - t0) * 1000.0
                if chunk == b"":
                    eof_at = t
                    break
                cum += len(chunk)
                events.append({"t_ms": round(t, 3), "n": len(chunk),
                               "cum": cum,
                               "head": chunk[:48].decode("utf-8", "replace")})
            if eof_at is None:
                eof_at = (time.perf_counter() - t0) * 1000.0
            break
    stderr = proc.stderr.read()
    proc.wait()
    return {"events": events, "eof_ms": round(eof_at, 3) if eof_at else None,
            "exit": proc.returncode,
            "stderr_len": len(stderr),
            "total_bytes": cum}


def summarize(mode, rep, m):
    ev = m["events"]
    first = ev[0]["t_ms"] if ev else None
    last = ev[-1]["t_ms"] if ev else None
    first_full = None
    for e in ev:
        if "\nW2" in e["head"] or e["head"].startswith("W2"):
            first_full = e["t_ms"]
            break
    return {"mode": mode, "rep": rep, "n_chunks": len(ev),
            "first_visible_ms": first, "last_visible_ms": last,
            "eof_ms": m["eof_ms"], "total_bytes": m["total_bytes"],
            "exit": m["exit"], "first_head": ev[0]["head"] if ev else None,
            "last_head": ev[-1]["head"] if ev else None,
            "events": ev}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--reps", type=int, default=3)
    ap.add_argument("--child", default=str(HERE / "child_withhold.py"))
    args = ap.parse_args()

    modes = ["flush", "buf", "big", "edge"]
    rows = []
    for mode in modes:
        for rep in range(args.reps):
            m = monitor([sys.executable, args.child, mode])
            rows.append(summarize(mode, rep, m))
    (HERE / "withhold_receipts.json").write_text(
        json.dumps(rows, indent=2) + "\n")
    lines = []
    for r in rows:
        lines.append(
            f"{r['mode']:6} rep{r['rep']} chunks={r['n_chunks']:2d} "
            f"first={r['first_visible_ms']}ms last={r['last_visible_ms']}ms "
            f"eof={r['eof_ms']}ms bytes={r['total_bytes']} "
            f"first_head={r['first_head']!r}")
    (HERE / "withhold_receipts.txt").write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    return 0


if __name__ == "__main__":
    sys.exit(main())
