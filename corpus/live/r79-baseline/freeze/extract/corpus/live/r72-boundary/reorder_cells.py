#!/usr/bin/env python3
"""r72-boundary scratch: reorder-fabrication EDGE CELLS (author-arm boundaries).

Round 72 author arm (briefed): a spawned descendant writes into inherited
fd1 mid-window; pin buffered parent -> prefix/reorder topology, flushed/-u
parent -> midline splice.  This driver measures the cells that arm as
briefed does NOT cover:

  grid_*     2x2+ parent-mode x descendant-mode (descendant's own buffer)
  win_*      window edges in write-time (child before head / inside / after
             parent flush / after parent exit)
  cross_*    buffer-lifetime edges (single >=131072 write; exact-full buffer
             flushed by a crossing write AFTER the child wrote)
  edge_head* the 1-byte edge: 131071 B buffered + 1 B after child -> no flush
  paced2     child write between two flush epochs (infix/hybrid topology)
  fd2mrg     fd2 write vs fd1 buffer, no spawn (merged capture)
  multi      two descendants
  kill/oex   abnormal exit: no flush -> loss edge
  receipt_*  probe's own flush=True ARM receipt line vs the window
  pygame_*   same cells inside a real pygame process
  sh_sys     os.system / sh -c seam (xconnector demo shape)
  nlchild    descendant marker terminated with newline (line-merge control)

Design: the parent program emits TRACE lines on fd2 via os.write (never
buffered) at every write/flush/spawn event; the driver timestamps every
fd1 chunk with select+os.read and every fd2 line arrival, so the byte
stream can be checked against the WRITE-TIME order (fabrication vs
honest order).  Child programs are plain python3 / sh -- the claim is
language-layer, the children must not import pygame.

Receipts: cells.json (raw reader), lines.json (line reader), capture.json
(battery-mode subprocess.run capture_output).  Scratch only.
"""

import argparse
import json
import os
import re
import select
import subprocess
import sys
import time

PY = sys.executable
BUFSIZE = 131072
ARM_LINE = re.compile(r"^PYGAME-ARM (\S+) \| (.*)$")

# child programs ------------------------------------------------------------
CHILD_WT = ("import os,time;"
            "time.sleep({s});"
            "os.write(2,b'TRACE C-WRITE\\n');"
            "os.write(1,b'INJ');"
            "os.write(2,b'TRACE C-WROTE\\n')")
CHILD_NL = ("import os,time;"
            "time.sleep({s});"
            "os.write(2,b'TRACE C-WRITE\\n');"
            "os.write(1,b'INJ\\n');"
            "os.write(2,b'TRACE C-WROTE\\n')")
CHILD_BUF = ("import os,sys,time;"
             "time.sleep({s});"
             "os.write(2,b'TRACE C-WRITE\\n');"
             "sys.stdout.write('INJ');"
             "time.sleep({s2});"
             "os.write(2,b'TRACE C-EXIT\\n')")
CHILD_U = ("import os,time;"
           "time.sleep({s});"
           "os.write(2,b'TRACE C-WRITE\\n');"
           "print('INJ',end='')")

PRELUDE = """\
import os, sys, subprocess, time
def T(tag):
    os.write(2, b"TRACE " + tag.encode() + b"\\n")
def spawn(src, extra=()):
    env = {k: v for k, v in os.environ.items() if k != "PYTHONUNBUFFERED"}
    return subprocess.Popen([sys.executable, *extra, "-c", src], env=env)
"""


def parent_src(body):
    return PRELUDE + body


def child_src(kind, s=0.02, s2=0.02):
    return {"wt": CHILD_WT, "nl": CHILD_NL, "buf": CHILD_BUF,
            "u": CHILD_U}[kind].format(s=s, s2=s2)


def spawn_args(kind):
    return '("-u",)' if kind == "u" else "()"


# parent cell programs ------------------------------------------------------
def src_grid(kind, head_mode):
    c = child_src(kind)
    head = 'T("P-HEAD"); sys.stdout.write("HEAD ")'
    if head_mode == "flush_before":
        head += '; sys.stdout.flush(); T("P-FLUSH")'
    return parent_src(f"""
T("P-START")
{head}
p = spawn({c!r}, {spawn_args(kind)})
T("P-SPAWN")
p.wait()
T("P-CHILD-DONE")
sys.stdout.write(" TAIL\\n")
T("P-TAIL")
""")


def src_win_before():
    c = child_src("wt")
    return parent_src(f"""
T("P-START")
p = spawn({c!r})
T("P-SPAWN")
time.sleep(0.08)
T("P-HEAD")
sys.stdout.write("HEAD ")
p.wait()
T("P-CHILD-DONE")
sys.stdout.write(" TAIL\\n")
T("P-TAIL")
""")


def src_win_flush_after_child():
    c = child_src("wt", s=0.05)
    return parent_src(f"""
T("P-START")
T("P-HEAD")
sys.stdout.write("HEAD ")
p = spawn({c!r})
T("P-SPAWN")
time.sleep(0.08)
sys.stdout.flush()
T("P-FLUSH")
p.wait()
T("P-CHILD-DONE")
sys.stdout.write(" TAIL\\n")
T("P-TAIL")
""")


def src_win_after_exit():
    c = child_src("wt", s=0.30)
    return parent_src(f"""
T("P-START")
T("P-HEAD")
sys.stdout.write("HEAD ")
p = spawn({c!r})
T("P-SPAWN")
sys.stdout.write(" TAIL\\n")
T("P-TAIL")
""")


def src_cross_hi():
    c = child_src("wt")
    return parent_src(f"""
T("P-START")
T("P-HEAD")
sys.stdout.write("HEAD " + "H" * (131072 - 5))
T("P-HEAD-WROTE")
p = spawn({c!r})
T("P-SPAWN")
p.wait()
T("P-CHILD-DONE")
sys.stdout.write(" TAIL\\n")
T("P-TAIL")
""")


def src_cross_after_child():
    c = child_src("wt", s=0.05)
    return parent_src(f"""
T("P-START")
T("P-HEAD")
sys.stdout.write("HEAD ")
for _ in range(131):
    sys.stdout.write("A" * 1000)
sys.stdout.write("A" * 67)      # 5 + 131000 + 67 = 131072 buffered, exact-full
T("P-HEAD-FULL")
p = spawn({c!r})
T("P-SPAWN")
p.wait()
T("P-CHILD-DONE")
sys.stdout.write("B")           # len 1 > avail 0 -> flush of the 131072 B
T("P-CROSS")
sys.stdout.write(" TAIL\\n")
T("P-TAIL")
""")


def src_edge_head131071():
    c = child_src("wt", s=0.05)
    return parent_src(f"""
T("P-START")
T("P-HEAD")
sys.stdout.write("HEAD ")
for _ in range(130):
    sys.stdout.write("A" * 1000)
sys.stdout.write("A" * 66)      # 5 + 130000 + 66 = 131071 buffered
T("P-HEAD-131071")
p = spawn({c!r})
T("P-SPAWN")
p.wait()
T("P-CHILD-DONE")
sys.stdout.write("B")           # len 1 <= avail 1 -> buffered (R3, no flush)
T("P-PLUS-ONE")
sys.stdout.write(" TAIL\\n")
T("P-TAIL")
""")


def src_paced2():
    c = child_src("wt", s=0.15)
    return parent_src(f"""
T("P-START")
T("P-HEAD")
sys.stdout.write("HEAD ")
p = spawn({c!r})
T("P-SPAWN")
for i in range(300):
    sys.stdout.write("C" * 1000)
    if i in (100, 120, 130, 140, 150, 160, 200, 260):
        T("P-CHUNK-%d" % i)
    time.sleep(0.001)
T("P-CHUNKS-DONE")
p.wait()
T("P-CHILD-DONE")
sys.stdout.write(" TAIL\\n")
T("P-TAIL")
""")


def src_fd2mrg():
    # no TRACE: fd2 is merged into the captured stream
    return parent_src("""
sys.stdout.write("HEAD ")
os.write(2, b"ERR\\n")
sys.stdout.write(" TAIL\\n")
""")


def src_multi():
    c = child_src("wt")
    return parent_src(f"""
T("P-START")
T("P-HEAD")
sys.stdout.write("HEAD ")
p1 = spawn({c!r}); T("P-SPAWN1"); p1.wait(); T("P-DONE1")
p2 = spawn({c!r}); T("P-SPAWN2"); p2.wait(); T("P-DONE2")
sys.stdout.write(" TAIL\\n")
T("P-TAIL")
""")


def src_kill():
    c = child_src("wt")
    return parent_src(f"""
T("P-START")
T("P-HEAD")
sys.stdout.write("HEAD ")
p = spawn({c!r})
T("P-SPAWN")
time.sleep(0.08)
T("P-KILL")
os.kill(os.getpid(), signal.SIGKILL)
""").replace("import os, sys, subprocess, time",
             "import os, signal, sys, subprocess, time")


def src_oexit():
    c = child_src("wt")
    return parent_src(f"""
T("P-START")
T("P-HEAD")
sys.stdout.write("HEAD ")
p = spawn({c!r})
T("P-SPAWN")
time.sleep(0.08)
T("P-OEXIT")
os._exit(0)
""")


def src_receipt(head_nl, receipt_before_spawn, child_kind="wt"):
    c = child_src(child_kind)
    head = 'sys.stdout.write("HEAD\\n")' if head_nl else \
           'sys.stdout.write("HEAD ")'
    if receipt_before_spawn:
        body = f"""
T("P-START")
T("P-HEAD")
{head}
print("PYGAME-ARM reorder | x=1", flush=True)
T("P-RECEIPT")
p = spawn({c!r})
T("P-SPAWN")
p.wait()
T("P-CHILD-DONE")
sys.stdout.write("TAIL\\n")
T("P-TAIL")
"""
    else:
        body = f"""
T("P-START")
T("P-HEAD")
{head}
p = spawn({c!r})
T("P-SPAWN")
p.wait()
T("P-CHILD-DONE")
print("PYGAME-ARM reorder | x=1", flush=True)
T("P-RECEIPT")
sys.stdout.write("TAIL\\n")
T("P-TAIL")
"""
    return parent_src(body)


def src_pygame(kind):
    c = child_src(kind)
    return parent_src(f"""
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
os.environ.setdefault("PYGAME_HIDE_SUPPORT_PROMPT", "1")
import pygame
pygame.init()
pygame.display.set_mode((64, 64))
T("P-PYGAME-READY")
T("P-HEAD")
sys.stdout.write("HEAD ")
p = spawn({c!r})
T("P-SPAWN")
p.wait()
T("P-CHILD-DONE")
sys.stdout.write(" TAIL\\n")
T("P-TAIL")
pygame.quit()
""")


def src_parent_oswrite_head():
    c = child_src("wt")
    return parent_src(f"""
T("P-START")
T("P-HEAD")
os.write(1, b"HEAD ")           # write path bypasses the userspace buffer
T("P-HEAD-WROTE")
p = spawn({c!r})
T("P-SPAWN")
p.wait()
T("P-CHILD-DONE")
sys.stdout.write(" TAIL\\n")
T("P-TAIL")
""")


def src_sh_sys():
    return parent_src("""
T("P-START")
T("P-HEAD")
sys.stdout.write("HEAD ")
os.system("printf INJ; echo TRACE C-WRITE >&2")
T("P-SH-DONE")
sys.stdout.write(" TAIL\\n")
T("P-TAIL")
""")


# cell table ----------------------------------------------------------------
CELLS = [
    # name, src, argv_extra, env_extra, reps, merge_stderr
    ("grid_pp_bufchild", src_grid("buf", "buffered"), (), {}, 3, False),
    ("grid_pw_wtchild", src_grid("wt", "buffered"), (), {}, 3, False),
    ("grid_pn_nlchild", src_grid("nl", "buffered"), (), {}, 2, False),
    ("grid_pu_uchild", src_grid("u", "buffered"), (), {}, 2, False),
    ("grid_up_unbufparent", src_grid("buf", "buffered"), ("-u",), {}, 2, False),
    ("grid_uw_unbufparent", src_grid("wt", "buffered"), ("-u",), {}, 2, False),
    ("grid_fp_flushparent", src_grid("buf", "flush_before"), (), {}, 2, False),
    ("grid_fw_flushparent", src_grid("wt", "flush_before"), (), {}, 2, False),
    ("grid_ew_envparent", src_grid("wt", "buffered"), (),
     {"PYTHONUNBUFFERED": "1"}, 2, False),
    ("win_before", src_win_before(), (), {}, 2, False),
    ("win_flush_after_child", src_win_flush_after_child(), (), {}, 2, False),
    ("win_after_exit", src_win_after_exit(), (), {}, 2, False),
    ("win_after_exit_u", src_win_after_exit(), ("-u",), {}, 2, False),
    ("cross_hi", src_cross_hi(), (), {}, 2, False),
    ("cross_after_child", src_cross_after_child(), (), {}, 2, False),
    ("edge_head131071", src_edge_head131071(), (), {}, 2, False),
    ("paced2", src_paced2(), (), {}, 1, False),
    ("fd2mrg", src_fd2mrg(), (), {}, 2, True),
    ("multi", src_multi(), (), {}, 2, False),
    ("kill", src_kill(), (), {}, 2, False),
    ("os_exit", src_oexit(), (), {}, 2, False),
    ("receipt_before", src_receipt(False, True), (), {}, 2, False),
    ("receipt_after", src_receipt(False, False), (), {}, 2, False),
    ("receipt_head_nl", src_receipt(True, False), (), {}, 2, False),
    ("pygame_pw", src_pygame("wt"), (), {}, 2, False),
    ("sh_os_system", src_sh_sys(), (), {}, 2, False),
    ("parent_oswrite_head", src_parent_oswrite_head(), (), {}, 2, False),
]

LINE_CELLS = ["grid_pw_wtchild", "grid_pp_bufchild", "grid_pn_nlchild",
              "grid_up_unbufparent", "win_after_exit", "receipt_after"]

CAPTURE_CELLS = [  # battery-mode: subprocess.run(capture_output=True)
    ("capture_buffered", src_receipt(False, False), ()),
    ("capture_unbuf", src_receipt(False, False), ("-u",)),
    ("capture_head_nl", src_receipt(True, False), ()),
    ("capture_unbuf_nlchild", src_receipt(False, False, "nl"), ("-u",)),
]


def run_cell(name, src, argv_extra, env_extra, merge_stderr=False,
             timeout=20.0):
    env = {k: v for k, v in os.environ.items() if k != "PYTHONUNBUFFERED"}
    env.update(env_extra)
    err = subprocess.STDOUT if merge_stderr else subprocess.PIPE
    proc = subprocess.Popen([PY, *argv_extra, "-c", src],
                            stdout=subprocess.PIPE, stderr=err, env=env)
    fd1 = proc.stdout.fileno()
    fd2 = None if merge_stderr else proc.stderr.fileno()
    t0 = time.perf_counter()
    chunks1 = []
    data1 = b""
    trace = []
    buf2 = b""
    open_fds = {fd1} | ({fd2} if fd2 is not None else set())
    while open_fds:
        ready, _, _ = select.select(list(open_fds), [], [], timeout)
        if not ready:
            break
        for fd in ready:
            b = os.read(fd, 65536)
            ms = (time.perf_counter() - t0) * 1e3
            if not b:
                open_fds.discard(fd)
                continue
            if fd == fd1:
                chunks1.append((ms, len(b), b))
                data1 += b
            else:
                buf2 += b
                while b"\n" in buf2:
                    line, buf2 = buf2.split(b"\n", 1)
                    trace.append((round(ms, 2), line.decode(errors="replace")))
    try:
        proc.wait(timeout=timeout)
    except subprocess.TimeoutExpired:
        proc.kill()
        proc.wait()
    eof_ms = (time.perf_counter() - t0) * 1e3

    def vis_ms(token):
        off = data1.find(token)
        if off < 0:
            return None
        seen = 0
        for ms, n, _ in chunks1:
            if seen + n > off:
                return round(ms, 2)
            seen += n
        return None

    def tok_ms(tag):
        for ms, line in trace:
            if line.strip() == "TRACE " + tag:
                return ms
        return None

    def idx(token):
        i = data1.find(token)
        return i if i >= 0 else None

    def vis_at(off):
        seen = 0
        for ms, n, _ in chunks1:
            if seen + n > off:
                return round(ms, 2)
            seen += n
        return None

    analysis = {
        "stream_repr": repr(data1 if len(data1) <= 400 else
                            data1[:200] + b"..." + data1[-120:]),
        "stream_len": len(data1),
        "order": {t.decode(): idx(t) for t in (b"HEAD", b"INJ", b"TAIL")},
        "vis_ms": {t.decode(): vis_ms(t) for t in (b"HEAD", b"INJ", b"TAIL")},
        "trace_ms": {tag: tok_ms(tag) for tag in
                     ("P-HEAD", "P-FLUSH", "P-SPAWN", "C-WRITE", "C-WROTE",
                      "C-EXIT", "P-TAIL", "P-KILL", "P-OEXIT", "P-RECEIPT",
                      "P-CHILD-DONE", "P-SH-DONE", "P-PYGAME-READY",
                      "P-HEAD-FULL", "P-CROSS", "P-HEAD-131071",
                      "P-PLUS-ONE") + tuple("P-CHUNK-%d" % i for i in
                                            (100, 120, 130, 140, 150, 160,
                                             200, 260))},
        "chunk_timeline": [[round(ms, 2), n] for ms, n, _ in chunks1[:14]],
        "first_chunk_ms": round(chunks1[0][0], 2) if chunks1 else None,
        "eof_ms": round(eof_ms, 2),
        "exit": proc.returncode,
        "n_chunks": len(chunks1),
    }
    # tokens first visible before the exit burst (streaming-consumer view)
    analysis["early_prefix_repr"] = repr(
        b"".join(raw for ms, n, raw in chunks1 if 0 <= ms < eof_ms - 25))
    t_head = analysis["trace_ms"]["P-HEAD"]
    t_cw = analysis["trace_ms"]["C-WRITE"]
    # paced-chunk infix analysis (only cells with P-CHUNK-* markers):
    # how many parent chunk bytes were WRITTEN before the child's write but
    # DELIVERED after it (interpolated from the marker times; +/- one chunk).
    marks = [(i, analysis["trace_ms"]["P-CHUNK-%d" % i])
             for i in (100, 120, 130, 140, 150, 160, 200, 260)]
    marks = [(i, t) for i, t in marks if t is not None]
    if len(marks) >= 2 and t_cw is not None and idx(b"INJ") is not None:
        n_written = None
        for (i0, t0), (i1, t1) in zip(marks, marks[1:]):
            if t0 <= t_cw <= t1 and t1 > t0:
                n_written = i0 + (i1 - i0) * (t_cw - t0) / (t1 - t0)
                break
        if n_written is None and t_cw > marks[-1][1]:
            n_written = marks[-1][0] + (t_cw - marks[-1][1])  # 1 ms pacing
        n_delivered = (idx(b"INJ") - 5) / 1000.0
        if n_written is not None:
            analysis["paced_infix"] = {
                "chunks_written_before_child": round(n_written, 1),
                "chunks_delivered_before_inj": round(n_delivered, 1),
                "chunk_bytes_written_before_child_delivered_after_inj":
                    round(max(0.0, n_written - n_delivered) * 1000, 0),
                "marker_ms": marks,
            }
    # topology verdict: does the byte order match the write-time order?
    if idx(b"INJ") is None:
        if analysis["exit"] is not None and analysis["exit"] < 0:
            analysis["verdict"] = "loss (signal, no flush)"
        elif analysis["trace_ms"]["P-OEXIT"] is not None:
            analysis["verdict"] = "loss (os._exit, no flush)"
        elif analysis["trace_ms"]["P-SPAWN"] is None:
            analysis["verdict"] = "no-descendant cell"
        else:
            analysis["verdict"] = "INJ missing"
    elif idx(b"HEAD") is None:
        analysis["verdict"] = "loss (HEAD absent, no flush)"
    else:
        inj_first = idx(b"INJ") < idx(b"HEAD")
        if t_cw is not None and t_head is not None:
            if inj_first and t_cw > t_head:
                analysis["verdict"] = "INVERTED (fabricated reorder)"
            elif inj_first and t_cw < t_head:
                analysis["verdict"] = "child-first (honest order)"
            elif not inj_first and t_cw > t_head:
                analysis["verdict"] = "splice (honest order)"
            else:
                analysis["verdict"] = "anomaly"
        else:
            analysis["verdict"] = "inverted(byte-order only)" if inj_first \
                else "splice(byte-order only)"
    return analysis


def run_lines_cell(name, src, argv_extra, env_extra, timeout=20.0):
    env = {k: v for k, v in os.environ.items() if k != "PYTHONUNBUFFERED"}
    env.update(env_extra)
    proc = subprocess.Popen([PY, *argv_extra, "-c", src],
                            stdout=subprocess.PIPE,
                            stderr=subprocess.DEVNULL, env=env)
    fd1 = proc.stdout.fileno()
    t0 = time.perf_counter()
    lines = []
    buf = b""
    while True:
        ready, _, _ = select.select([fd1], [], [], timeout)
        if not ready:
            break
        b = os.read(fd1, 65536)
        ms = (time.perf_counter() - t0) * 1e3
        if not b:
            break
        buf += b
        while b"\n" in buf:
            line, buf = buf.split(b"\n", 1)
            lines.append((round(ms, 2), line.decode(errors="replace")))
    proc.wait()
    return {"lines": lines, "trailing": repr(buf)}


def run_capture_cell(name, src, argv_extra):
    env = {k: v for k, v in os.environ.items() if k != "PYTHONUNBUFFERED"}
    proc = subprocess.run([PY, *argv_extra, "-c", src],
                          capture_output=True, text=True, timeout=20, env=env)
    lines = proc.stdout.splitlines()
    parsed = [l for l in lines if ARM_LINE.match(l.strip())]
    return {"stdout_repr": repr(proc.stdout), "exit": proc.returncode,
            "parsed_arm_lines": parsed,
            "arm_line_parseable": bool(parsed)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", default="cells.json")
    ap.add_argument("--lines-json", default="lines.json")
    ap.add_argument("--capture-json", default="capture.json")
    ap.add_argument("--only", default=None)
    args = ap.parse_args()

    out = {"host": {"python": sys.version.split()[0],
                    "default_buffer_size": BUFSIZE},
           "cells": {}}
    for name, src, argv_extra, env_extra, reps, merge in CELLS:
        if args.only and name not in args.only.split(","):
            continue
        runs = [run_cell(name, src, argv_extra, env_extra, merge)
                for _ in range(reps)]
        out["cells"][name] = {
            "reps": runs,
            "stable": all(r["verdict"] == runs[0]["verdict"] and
                          r["order"] == runs[0]["order"] for r in runs),
        }
        r0 = runs[0]
        print(f"{name:24} {r0['verdict']:32} order={r0['order']} "
              f"vis={r0['vis_ms']} stream={r0['stream_repr'][:80]}")
    with open(args.json, "w") as fh:
        json.dump(out, fh, indent=2)
        fh.write("\n")

    lines_out = {}
    for name, src, argv_extra, env_extra, reps, merge in CELLS:
        if name in LINE_CELLS:
            lines_out[name] = run_lines_cell(name, src, argv_extra, env_extra)
            print(f"LINES {name}: {lines_out[name]['lines']}")
    with open(args.lines_json, "w") as fh:
        json.dump(lines_out, fh, indent=2)
        fh.write("\n")

    cap_out = {}
    for name, src, argv_extra in CAPTURE_CELLS:
        cap_out[name] = run_capture_cell(name, src, argv_extra)
        print(f"CAPTURE {name}: arm_parseable="
              f"{cap_out[name]['arm_line_parseable']} "
              f"parsed={cap_out[name]['parsed_arm_lines']}")
    with open(args.capture_json, "w") as fh:
        json.dump(cap_out, fh, indent=2)
        fh.write("\n")
    print("wrote", args.json, args.lines_json, args.capture_json)


if __name__ == "__main__":
    main()
