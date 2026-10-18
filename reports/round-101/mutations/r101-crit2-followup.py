#!/usr/bin/env python3
"""r101-crit2 follow-up probes: stderr-carried pinned line, full-transcript echo, timeout-path newline type."""
import json
import subprocess
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
FIXTURE = ROOT / "corpus" / "fixtures" / "r100b_seq.gd"
PROJ = (ROOT / "corpus" / "fixtures" / "project.godot").read_text()
PRIS = FIXTURE.read_text()
SCRATCH = Path("/tmp/r101-crit2")
ALLOWED = ('ERROR: Parameter "t" is null.',)
CURSOR = '\tprint("PASS r100_gui cursor %s" % " ".join(out))'
QUIT = '\tquit(0)'
FOCUS_FIRST = "\tf.grab_focus()\n"


def run(proj, args=("--clean=1",), timeout=8):
    cmd = ["/usr/bin/godot", "--headless", "--path", str(proj), "--script", "res://r100b_seq.gd", "--", *args]
    t0 = time.monotonic()
    p = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
    return p.stdout, p.stderr, p.returncode, None, time.monotonic() - t0


def classify(code, error, output, sig):
    lines = output.splitlines()
    unrelated = [ln for ln in lines if "ERROR:" in ln and ln.strip() != ALLOWED[0]]
    return (code == 0 and error is None and sig in output and not unrelated
            and "SCRIPT ERROR:" not in output and "Parse Error:" not in output)


def mk(name, text):
    d = SCRATCH / name
    d.mkdir(parents=True, exist_ok=True)
    (d / "project.godot").write_text(PROJ)
    (d / "r100b_seq.gd").write_text(text)
    return d


def rep1(t, old, new, tag):
    assert t.count(old) == 1, (tag, t.count(old))
    return t.replace(old, new, 1)


out = {}
# fresh clean=1 transcript to build pins
d = mk("fo_base", PRIS)
o, e, c, er, t = run(d)
lines = [ln for ln in (o + e).splitlines() if ln.startswith("PASS r100_gui ")]
seq = next(ln for ln in (o + e).splitlines() if ln.startswith("SEQ_DONE"))
full = "\n".join(lines)
full_done = full + "\n" + seq
cursor = next(ln for ln in lines if ln.startswith("PASS r100_gui cursor "))
out["base"] = {"run_s": round(t, 2), "exit": c, "cells": len(lines),
               "full_pin_in_stdout": full in o, "seq_in_stdout": seq in o}

# A: cursor cell's PASS line moved to stderr alone
v = rep1(PRIS, CURSOR, '\tprinterr("PASS r100_gui cursor %s" % " ".join(out))', "cursor_stderr")
d = mk("fo_cursor_stderr", v)
o, e, c, er, t = run(d)
out["A_cursor_line_on_stderr"] = {
    "run_s": round(t, 2), "exit": c,
    "landed_cursor_pin_merged": classify(c, er, o + e, cursor),
    "full14_pin": classify(c, er, o + e, full),
    "cursor_in_stdout": cursor in o, "cursor_in_stderr": cursor in e,
    "stdout_pass_lines": sum(1 for ln in o.splitlines() if ln.startswith("PASS r100_gui ")),
    "stderr_pass_lines": sum(1 for ln in e.splitlines() if ln.startswith("PASS r100_gui ")),
}

# B: full transcript (14 cells + SEQ_DONE) echoed first as a literal, real focus mechanism mutated
block_gd = '\\n'.join(lines + [seq])
assert '"' not in block_gd
v = rep1(PRIS, "func _run() -> void:", 'func _run() -> void:\n\tprint("%s")' % block_gd, "echo_full")
v = rep1(v, FOCUS_FIRST, "\tpass\n", "mfocus")
d = mk("fo_echo_full", v)
o, e, c, er, t = run(d)
merged = o + e
out["B_echo_full_transcript_plus_mfocus"] = {
    "run_s": round(t, 2), "exit": c,
    "block_matches_merged": full in merged,
    "block_plus_seq_matches_merged": full_done in merged,
    "landed_cursor_pin": classify(c, er, merged, cursor),
    "pass_line_total": sum(1 for ln in merged.splitlines() if ln.startswith("PASS r100_gui ")),
    "focus_real_line": next((ln for ln in merged.splitlines() if ln.startswith("PASS r100_gui focus ")), None),
    "closure_one_per_cell_would_reject": sum(
        1 for ln in merged.splitlines() if ln.startswith("PASS r100_gui focus ")) != 1,
}

# C: timeout-path newline semantics on THIS python: does TimeoutExpired.stdout keep \r?
probe = SCRATCH / "fo_timeout"
probe.mkdir(parents=True, exist_ok=True)
(probe / "project.godot").write_text(PROJ)
(probe / "r100b_seq.gd").write_text(
    'extends SceneTree\n'
    'func _initialize() -> void:\n'
    '\tprintraw("PROBE_A\\r\\nPROBE_B\\r\\n")\n'
    '\tOS.delay_msec(10000)\n'
    '\tquit(0)\n')
cmd = ["/usr/bin/godot", "--headless", "--path", str(probe), "--script", "res://r100b_seq.gd", "--"]
t0 = time.monotonic()
type_seen, raw_type, cr_in_text, exc_stdout_repr = None, None, None, None
try:
    subprocess.run(cmd, capture_output=True, text=True, timeout=3)
except subprocess.TimeoutExpired as exc:
    type_seen = type(exc.stdout).__name__
    cr_in_text = ("\r" in exc.stdout) if isinstance(exc.stdout, str) else (b"\r" in exc.stdout)
    raw_type = type(exc.stdout).__name__
    exc_stdout_repr = repr(exc.stdout)[:120]
out["C_timeout_expired_stdout_type"] = {
    "elapsed_s": round(time.monotonic() - t0, 2), "type": type_seen, "cr_present": cr_in_text,
    "repr": exc_stdout_repr,
    "note": "text=True on this Python -> str; universal-newline translation applies to timeout capture too"
            if isinstance(exc_stdout_repr, str) and type_seen == "str" else "bytes path"}

p = Path(__file__).resolve().parent / "r101-crit2-followup.json"
p.write_text(json.dumps(out, indent=1))
print(json.dumps(out, indent=1))
print("wrote", p)
