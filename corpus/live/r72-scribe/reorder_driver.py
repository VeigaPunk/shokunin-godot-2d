#!/usr/bin/env python3
"""r72-scribe independent driver — raw-pipe byte-order capture.

Spawns corpus/live/r72-scribe/reorder_parent.py per cell with stdout as a
pipe read raw (os.read + select, chunk-timestamped), stderr captured, and
records the byte layout + topology per cell. Optional per-cell reader stall
forces a crossing write to block so a mid-flush descendant write can
interleave (xconnector prediction iii). Writes
corpus/live/r72-scribe/reorder-results.json and prints a table.

No tracked fixture is modified; no fixture code is imported (own harness).
"""
import argparse
import hashlib
import json
import os
import select
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
PARENT = HERE / "reorder_parent.py"

# name, parent argv, env extra, pygame flag, reader_stall_ms
CELLS = [
    ("buffered",        ["buffered"], {}, False, 0),
    ("unbuffered_u",    ["buffered"], {}, False, 0),      # -u added below
    ("flush_inside",    ["flushed"], {}, False, 0),
    ("env_unbuffered",  ["buffered"], {"PYTHONUNBUFFERED": "1"}, False, 0),
    ("sleep_before",    ["sleep_before_spawn"], {}, False, 0),
    ("fill_before",     ["fill_before_spawn"], {}, False, 0),
    ("popen_child",     ["popen_child"], {}, False, 0),
    ("popen_wait",      ["popen_wait"], {}, False, 0),
    ("ownpipe_control", ["ownpipe_control"], {}, False, 0),
    ("hybrid_flush",    ["hybrid_flush"], {}, False, 150),
    ("pg_buffered",     ["buffered"], {}, True, 0),
    ("pg_unbuffered",   ["buffered"], {}, True, 0),       # -u added below
    ("pg_flush",        ["flushed"], {}, True, 0),
    ("pg_sleep_before", ["sleep_before_spawn"], {}, True, 0),
    ("pg_popen_wait",   ["popen_wait"], {}, True, 0),
]

UNBUFFERED = {"unbuffered_u", "pg_unbuffered"}


def run_cell(name, parent_argv, env_extra, pygame_flag, reader_stall_ms):
    argv = [sys.executable]
    if name in UNBUFFERED:
        argv.append("-u")
    argv += [str(PARENT)] + parent_argv
    if pygame_flag:
        argv.append("--pygame")
    env = {k: v for k, v in os.environ.items() if k != "PYTHONUNBUFFERED"}
    env.update(env_extra)

    t0 = time.perf_counter()
    proc = subprocess.Popen(argv, stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE, env=env)
    fd = proc.stdout.fileno()
    chunks = []
    data = b""
    timeout = False
    stalled = False
    while True:
        ready, _, _ = select.select([fd], [], [], 15.0)
        if not ready:
            timeout = True
            break
        b = os.read(fd, 65536)
        if not b:
            break
        ms = (time.perf_counter() - t0) * 1e3
        chunks.append({"ms": round(ms, 2), "len": len(b)})
        data += b
        if reader_stall_ms and not stalled:
            stalled = True
            time.sleep(reader_stall_ms / 1000.0)
    proc.wait()
    exit_ms = (time.perf_counter() - t0) * 1e3
    stderr = proc.stderr.read().decode(errors="replace")
    text = data.decode(errors="replace")

    i_inj = text.find("INJECTED")
    i_hd = text.find("HEAD")
    i_tl = text.find(" TAIL")
    if i_inj < 0:
        topo = "no-injection"
    elif i_hd < 0:
        topo = "inject-only"
    elif i_inj < i_hd:
        topo = "prefix_reorder"
    elif i_tl >= 0 and i_hd < i_inj < i_tl:
        topo = "midline_splice"
    elif i_tl >= 0 and i_inj > i_tl:
        topo = "post_tail"
    else:
        topo = "other"
    # fill-run position of INJECTED: how many bytes precede it and whether
    # the preceding bytes are HEAD + an unbroken fill run (crossing write)
    prefix = text[:i_inj] if i_inj > 0 else ""
    hybrid_fill = (prefix.startswith("HEAD ")
                   and len(prefix) > 5 and set(prefix[5:]) <= {"H"})
    fill_after = text[i_inj + len("INJECTED"):].count("H")

    first_chunk = text[:chunks[0]["len"]] if chunks else ""
    return {
        "cell": name,
        "argv": argv,
        "env_extra": env_extra,
        "topology": topo,
        "exit": proc.returncode,
        "stderr_len": len(stderr),
        "stderr_head": stderr[:200],
        "timeout": timeout,
        "exit_ms": round(exit_ms, 2),
        "first_chunk_ms": chunks[0]["ms"] if chunks else -1,
        "n_chunks": len(chunks),
        "chunks": chunks,
        "first_chunk_has_head": "HEAD" in first_chunk,
        "first_chunk_has_injected": "INJECTED" in first_chunk,
        "bytes_total": len(data),
        "i_injected": i_inj,
        "i_head": i_hd,
        "i_tail": i_tl,
        "bytes_before_injected": i_inj,
        "fill_h_after_injected": fill_after,
        "around_injected": text[max(0, i_inj - 24):i_inj + 32] if i_inj >= 0 else "",
        "tail_repr": repr(text[-24:]),
        "hybrid_fill": hybrid_fill,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--reps", type=int, default=1)
    ap.add_argument("--only", default="")
    ap.add_argument("--out", default="reorder-results.json")
    args = ap.parse_args()
    only = set(args.only.split(",")) if args.only else None

    results = []
    for name, parent_argv, env_extra, pygame_flag, stall in CELLS:
        if only and name not in only:
            continue
        for rep in range(args.reps):
            r = run_cell(name, parent_argv, env_extra, pygame_flag, stall)
            r["rep"] = rep
            results.append(r)
            print(f"{name:16} r{rep} topo={r['topology']:15} exit={r['exit']} "
                  f"first={r['first_chunk_ms']:>8}ms head1st={r['first_chunk_has_head']} "
                  f"inj1st={r['first_chunk_has_injected']} bytes={r['bytes_total']} "
                  f"before_inj={r['bytes_before_injected']}")

    payload = {
        "harness": "r72-scribe reorder_driver.py",
        "python": sys.version.split()[0],
        "started_utc": datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ"),
        "parent_sha256": hashlib.sha256(PARENT.read_bytes()).hexdigest(),
        "driver_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "cells": results,
    }
    out = HERE / args.out
    out.write_text(json.dumps(payload, indent=2) + "\n")
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
