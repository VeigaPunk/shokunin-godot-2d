"""r71-boundary scratch parent: withholding-window flush-edge driver.

Spawns wprobe_child.py with piped stdout/stderr and timestamps every byte
chunk that becomes parent-visible (select + os.read), while the child
timestamps each write via raw fd2 TRACE lines (os.write, never buffered).

The measured question: when does an unflushed stdout write become
parent-visible -- at buffer fill, or only at process exit? Where is the
flush edge (byte granularity)? Does a >buffer write surface early, and
if so, how much of it?

Usage:
  python3 wprobe_parent.py --reader raw  --json withhold-raw.json
  python3 wprobe_parent.py --reader lines --json withhold-lines.json
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
CHILD = HERE / "wprobe_child.py"

BASE_ENV = dict(os.environ,
                SDL_VIDEODRIVER="dummy",
                SDL_AUDIODRIVER="dummy",
                PYGAME_HIDE_SUPPORT_PROMPT="1")

TIMEOUT_S = 12.0

# (name, child argv, env overrides, python args, reps)
CELLS_RAW = [
    # --- single unflushed text write, size sweep ---
    ("w_1k",        ["--mode", "single", "--size", "1000"], {}, [], 1),
    ("w_8k_lo",     ["--mode", "single", "--size", "8191"], {}, [], 2),
    ("w_8k_eq",     ["--mode", "single", "--size", "8192"], {}, [], 2),
    ("w_8k_hi",     ["--mode", "single", "--size", "8193"], {}, [], 2),
    ("w_64k",       ["--mode", "single", "--size", "65536"], {}, [], 1),
    ("w_128k_lo",   ["--mode", "single", "--size", "131071"], {}, [], 3),
    ("w_128k_eq",   ["--mode", "single", "--size", "131072"], {}, [], 3),
    ("w_128k_hi",   ["--mode", "single", "--size", "131073"], {}, [], 3),
    ("w_192k",      ["--mode", "single", "--size", "196608"], {}, [], 1),
    ("w_256k",      ["--mode", "single", "--size", "262144"], {}, [], 1),
    ("w_256k_hi",   ["--mode", "single", "--size", "262145"], {}, [], 1),
    # --- binary-layer write (sys.stdout.buffer) ---
    ("b_8k_hi",     ["--mode", "singleb", "--size", "8193"], {}, [], 1),
    ("b_128k_eq",   ["--mode", "singleb", "--size", "131072"], {}, [], 2),
    ("b_128k_hi",   ["--mode", "singleb", "--size", "131073"], {}, [], 2),
    # --- multi-write accumulation (60ms gaps) ---
    ("m_2x4k",      ["--mode", "multi", "--sizes", "4096,4096"], {}, [], 1),
    ("m_2x4k_plus", ["--mode", "multi", "--sizes", "4096,4097"], {}, [], 1),
    ("m_64k_x2",    ["--mode", "multi", "--sizes", "65536,65536"], {}, [], 1),
    ("m_64k_x2_pl", ["--mode", "multi", "--sizes", "65536,65537"], {}, [], 1),
    ("m_8k_x16",    ["--mode", "multi", "--sizes",
                     ",".join(["8192"] * 16)], {}, [], 1),
    ("m_8k_x16_pl", ["--mode", "multi", "--sizes",
                     ",".join(["8192"] * 16) + ",1"], {}, [], 1),
    # --- controls ---
    ("c_flush",     ["--mode", "flush", "--size", "100"], {}, [], 1),
    ("c_plain_nl",  ["--mode", "single", "--size", "100", "--newline", "1"],
     {}, [], 1),
    ("c_u_nl",      ["--mode", "single", "--size", "100", "--newline", "1"],
     {}, ["-u"], 1),
    ("c_u_nonl",    ["--mode", "single", "--size", "100", "--newline", "0"],
     {}, ["-u"], 1),
    ("c_env_nl",    ["--mode", "single", "--size", "100", "--newline", "1"],
     {"PYTHONUNBUFFERED": "1"}, [], 1),
    ("c_env_nonl",  ["--mode", "single", "--size", "100", "--newline", "0"],
     {"PYTHONUNBUFFERED": "1"}, [], 1),
    ("c_none",      ["--mode", "none"], {}, [], 1),
    ("c_stderr_nl", ["--mode", "stderr", "--size", "100", "--newline", "1"],
     {}, [], 2),
    ("c_stderr_nn", ["--mode", "stderr", "--size", "100", "--newline", "0"],
     {}, [], 2),
    ("c_stderr_9k", ["--mode", "stderr", "--size", "9000", "--newline", "0"],
     {}, [], 1),
    # --- pygame process cells ---
    ("p_plain",     ["--mode", "single", "--size", "100", "--pygame", "1"],
     {}, [], 2),
    ("p_banner",    ["--mode", "single", "--size", "100", "--pygame", "1"],
     {"PYGAME_HIDE_SUPPORT_PROMPT": None}, [], 1),
    ("p_128k_hi",   ["--mode", "single", "--size", "131073", "--pygame", "1"],
     {}, [], 2),
]

CELLS_LINES = [
    ("l_plain_nl",  ["--mode", "single", "--size", "100", "--newline", "1"],
     {}, [], 2),
    ("l_plain_nn",  ["--mode", "single", "--size", "100", "--newline", "0"],
     {}, [], 1),
    ("l_128k_hi_nl", ["--mode", "single", "--size", "131073", "--newline", "1"],
     {}, [], 2),
    ("l_flush_nl",  ["--mode", "flush", "--size", "100"], {}, [], 1),
    ("l_16x8k_nl",  ["--mode", "multi", "--sizes",
                     ",".join(["8192"] * 16) + ",0", "--nl-last", "1"],
     {}, [], 2),
    ("l_17x8k_pl_nl", ["--mode", "multi", "--sizes",
                       ",".join(["8192"] * 17) + ",1", "--nl-last", "1"],
     {}, [], 1),
    ("l_2x4k_nl",   ["--mode", "multi", "--sizes", "4096,4096",
                     "--nl-last", "1"], {}, [], 1),
]

CELLS_EDGE3 = [
    # compound capacity: BufferedWriter 131072 + textio pending 8191 = 139263
    ("e_16x8k_then_8191",
     ["--mode", "multi", "--gap", "0.02", "--sizes",
      ",".join(["8192"] * 16) + ",8191"], {}, [], 2),
    ("e_16x8k_then_8191_then_1",
     ["--mode", "multi", "--gap", "0.02", "--sizes",
      ",".join(["8192"] * 16) + ",8191,1"], {}, [], 2),
    ("e_single_139263", ["--mode", "single", "--size", "139263"], {}, [], 1),
    ("e_single_139264", ["--mode", "single", "--size", "139264"], {}, [], 1),
    ("e_100_then_131072", ["--mode", "multi", "--sizes", "100,131072"], {}, [], 2),
    ("e_131071_then_131072", ["--mode", "multi", "--sizes", "131071,131072"],
     {}, [], 1),
    ("e_131072_then_131071", ["--mode", "multi", "--sizes", "131072,131071"],
     {}, [], 1),
]

# disambiguation / threshold cells: textio pending layer vs BufferedWriter layer
CELLS_EDGE2 = [
    ("d_8k_then_122881",  ["--mode", "multi", "--sizes", "8192,122881"], {}, [], 2),
    ("d_8193_then_122880", ["--mode", "multi", "--sizes", "8193,122880"], {}, [], 2),
    ("d_8k_then_123000",  ["--mode", "multi", "--sizes", "8192,123000"], {}, [], 1),
    ("d_17x8k",           ["--mode", "multi", "--sizes", ",".join(["8192"] * 17)],
     {}, [], 2),
    ("d_17x8k_pl",        ["--mode", "multi", "--sizes",
                           ",".join(["8192"] * 17) + ",1"], {}, [], 2),
    ("d_18x8k",           ["--mode", "multi", "--sizes", ",".join(["8192"] * 18)],
     {}, [], 1),
    ("d_131071_then_1",   ["--mode", "multi", "--sizes", "131071,1"], {}, [], 2),
    ("d_131072_then_1",   ["--mode", "multi", "--sizes", "131072,1"], {}, [], 2),
    ("w_139264",          ["--mode", "single", "--size", "139264"], {}, [], 1),
    ("w_139265",          ["--mode", "single", "--size", "139265"], {}, [], 1),
    ("st_128k_eq",        ["--mode", "stderr", "--size", "131072", "--newline", "0"],
     {}, [], 2),
    ("st_128k_hi",        ["--mode", "stderr", "--size", "131073", "--newline", "0"],
     {}, [], 1),
    ("st_8k_then_1_nl",   ["--mode", "stderr_multi", "--sizes", "8192,1",
                           "--nl-last", "1"], {}, [], 2),
    ("st_131071_then_nl", ["--mode", "stderr_multi", "--sizes", "131071,1",
                           "--nl-last", "1"], {}, [], 2),
]


def read_raw(proc, t0):
    """select/os.read both pipes; return chunk lists."""
    fds = {proc.stdout.fileno(): "out", proc.stderr.fileno(): "err"}
    chunks = {"out": [], "err": []}
    open_fds = set(fds)
    deadline = time.monotonic() + TIMEOUT_S
    while open_fds and time.monotonic() < deadline:
        ready, _, _ = select.select(list(open_fds), [], [], 0.5)
        for fd in ready:
            data = os.read(fd, 1 << 20)
            t_ms = round((time.time_ns() - t0) / 1e6, 3)
            if data:
                chunks[fds[fd]].append([t_ms, data.decode("utf-8", "replace")])
            else:
                open_fds.discard(fd)
    return chunks


def read_lines(proc, t0):
    """Timestamp each line the text layer yields (readline semantics)."""
    import threading
    lines = []
    err_chunks = []

    def rd_out():
        for line in proc.stdout:
            lines.append([round((time.time_ns() - t0) / 1e6, 3),
                          line.rstrip(b"\n").decode("utf-8", "replace")])

    def rd_err():
        for line in proc.stderr:
            err_chunks.append([round((time.time_ns() - t0) / 1e6, 3),
                               line.rstrip(b"\n").decode("utf-8", "replace")])

    t1 = threading.Thread(target=rd_out, daemon=True)
    t2 = threading.Thread(target=rd_err, daemon=True)
    t1.start(); t2.start()
    return lines, err_chunks


def analyze_raw(mode, chunks, rc, exit_ms, child_ms):
    """early/withheld split on the channel under test."""
    channel = "err" if mode.startswith("stderr") else "out"
    marker = "y" if channel == "err" else "x"
    # parent-arrival of the post-write trace (channel-independent: fd2)
    t_post = None
    for t_ms, text in chunks["err"]:
        if "post-write" in text and "pre-write-0" not in text:
            t_post = t_ms
    t_pre = None
    for t_ms, text in chunks["err"]:
        if "TRACE pre-write " in text:
            t_pre = t_ms
    early = 0
    withheld = 0
    first_out = None
    for t_ms, text in chunks[channel]:
        has = marker in text
        if has and first_out is None:
            first_out = t_ms
        if not has:
            continue
        if t_post is not None and t_ms <= t_post + 50.0:
            early += len(text)
        else:
            withheld += len(text)
    total = sum(len(text) for t_ms, text in chunks[channel] if marker in text)
    return {
        "channel": channel,
        "t_pre_ms": t_pre,
        "t_post_ms": t_post,
        "first_out_ms": first_out,
        "early_bytes": early,
        "withheld_bytes": withheld,
        "total_bytes": total,
        "out_chunks": [[t, len(text)] for t, text in chunks["out"]],
        "err_chunks": [[t, len(text)] for t, text in chunks["err"]],
        "trace_timeline": [
            [t_ms, lbl, int(tail[5:])]
            for t_ms, text in chunks["err"]
            for line in text.splitlines()
            if line.startswith("TRACE ")
            for lbl, _, tail in [line[len("TRACE "):].partition(" ")]
            if tail.startswith("t_ns=")
        ],
        "rc": rc,
        "exit_ms": exit_ms,
        "child_pre_ns": child_ms.get("pre-write"),
        "child_post_ns": child_ms.get("post-write"),
    }


def parse_child_traces(chunks):
    out = {}
    for t_ms, text in chunks["err"]:
        for line in text.splitlines():
            if line.startswith("TRACE "):
                body = line[len("TRACE "):]
                label, _, tail = body.partition(" ")
                if tail.startswith("t_ns="):
                    out[label] = int(tail[5:])
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--reader", choices=["raw", "lines"], default="raw")
    ap.add_argument("--suite", choices=["raw", "lines", "edge2", "edge3", "lines2"],
                    default="raw")
    ap.add_argument("--json", required=True)
    args = ap.parse_args()

    cells = {"raw": CELLS_RAW, "lines": CELLS_LINES,
             "edge2": CELLS_EDGE2, "edge3": CELLS_EDGE3,
             "lines2": CELLS_LINES}[args.suite]
    results = []
    for name, argv, env_over, pyargs, reps in cells:
        for rep in range(reps):
            env = dict(BASE_ENV)
            for k, v in env_over.items():
                if v is None:
                    env.pop(k, None)
                else:
                    env[k] = v
            t0 = time.time_ns()
            cmd = [sys.executable] + pyargs + [str(CHILD)] + argv
            proc = subprocess.Popen(cmd, stdout=subprocess.PIPE,
                                    stderr=subprocess.PIPE, env=env)
            if args.reader == "raw":
                chunks = read_raw(proc, t0)
                rc = proc.wait()
                exit_ms = round((time.time_ns() - t0) / 1e6, 3)
                child_ms = parse_child_traces(chunks)
                res = analyze_raw(argv[1] if argv[0] == "--mode" else "",
                                  chunks, rc, exit_ms, child_ms)
                res.update({"cell": name, "rep": rep, "argv": argv})
            else:
                lines, err_chunks = read_lines(proc, t0)
                rc = proc.wait()
                exit_ms = round((time.time_ns() - t0) / 1e6, 3)
                res = {"cell": name, "rep": rep, "argv": argv,
                       "rc": rc, "exit_ms": exit_ms,
                       "lines": lines, "err_chunks": err_chunks}
            results.append(res)
            if args.reader == "raw":
                print(f"{name:14} rep{rep} rc={res['rc']} "
                      f"first_out_ms={res['first_out_ms']} "
                      f"early={res['early_bytes']} "
                      f"withheld={res['withheld_bytes']} "
                      f"total={res['total_bytes']} "
                      f"exit_ms={res['exit_ms']}")
            else:
                got = [(t, l[:24]) for t, l in res["lines"]]
                print(f"{name:14} rep{rep} rc={res['rc']} "
                      f"exit_ms={res['exit_ms']} lines={got}")

    Path(args.json).write_text(json.dumps(results, indent=2) + "\n")
    print(f"json: {args.json}")


if __name__ == "__main__":
    main()
