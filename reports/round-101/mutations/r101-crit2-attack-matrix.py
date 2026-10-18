#!/usr/bin/env python3
"""r101-crit2 attack matrix — C2: pins vs CRLF seam / split-stream / timeout truncation / echo.

Replicates run_battery.py's capture+classification for the r100b_seq_* rows
(subprocess.run(capture_output=True, text=True, timeout=8); signature is a raw
substring test on stdout+stderr; per-case allowlist = ('ERROR: Parameter "t" is null.',)).

All Godot runs use scratch projects under /tmp/r101-crit2/ (never the lane repo).
Writes r101-crit2-attack-matrix.json next to itself.
"""
import json
import re
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
FIXTURE = ROOT / "corpus" / "fixtures" / "r100b_seq.gd"
PROJECT = ROOT / "corpus" / "fixtures" / "project.godot"
SCRATCH = Path("/tmp/r101-crit2")
GODOT = "/usr/bin/godot"
ALLOWED = ('ERROR: Parameter "t" is null.',)

PRISTINE = FIXTURE.read_text()
PROJ_TXT = PROJECT.read_text()


def harness_run(proj: Path, args, timeout=8):
    cmd = [GODOT, "--headless", "--path", str(proj), "--script", "res://r100b_seq.gd", "--", *args]
    t0 = time.monotonic()
    try:
        p = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        return p.stdout, p.stderr, p.returncode, None, time.monotonic() - t0
    except subprocess.TimeoutExpired as exc:
        out = (exc.stdout or b"").decode(errors="replace") if isinstance(exc.stdout, bytes) else (exc.stdout or "")
        err = (exc.stderr or b"").decode(errors="replace") if isinstance(exc.stderr, bytes) else (exc.stderr or "")
        return out, err, None, f"TIMEOUT after {timeout} seconds", time.monotonic() - t0


def raw_run(proj: Path, args, timeout=8):
    cmd = [GODOT, "--headless", "--path", str(proj), "--script", "res://r100b_seq.gd", "--", *args]
    try:
        p = subprocess.run(cmd, capture_output=True, timeout=timeout)
        return p.stdout, p.stderr, p.returncode
    except subprocess.TimeoutExpired as exc:
        return (exc.stdout or b""), (exc.stderr or b""), None


def classify_process(code, error, output, expected_exit, signature, allowed_errors=ALLOWED):
    lines = output.splitlines()

    def allowed_error(line, allowed):
        stripped = line.strip()
        if stripped == allowed:
            return True
        if allowed.endswith(","):
            return stripped.startswith(allowed) and stripped.count("ERROR:") == 1
        return False

    unrelated = [ln for ln in lines if "ERROR:" in ln and not any(allowed_error(ln, a) for a in allowed_errors)]
    return (code == expected_exit and error is None and signature in output
            and not unrelated and "SCRIPT ERROR:" not in output and "Parse Error:" not in output)


def closure_guards(stdout, stderr, cells, seq_done):
    merged = stdout + stderr
    lines = [ln for ln in merged.splitlines() if ln.strip()]
    pass_lines = [ln for ln in lines if ln.startswith("PASS r100_gui ")]
    counts = {}
    for ln in pass_lines:
        cell = ln.split(" ")[4] if len(ln.split(" ")) > 4 else "?"
        counts[cell] = counts.get(cell, 0) + 1
    return {
        "merged_has_block": all(c in merged for c in cells) and ("\n".join(cells) in merged),
        "block_in_stdout_only": "\n".join(cells) in stdout,
        "stderr_has_no_pass_line": not any(ln.startswith("PASS ") for ln in stderr.splitlines()),
        "exactly_one_per_cell": all(v == 1 for v in counts.values()) and len(counts) == 14,
        "pass_line_total_14": len(pass_lines) == 14,
        "seq_done_once": merged.count(seq_done) == 1,
        "no_cr_in_output": "\r" not in merged,
    }


def mk_proj(name, script_text, keep_pbs=False):
    d = SCRATCH / name
    d.mkdir(parents=True, exist_ok=True)
    (d / "project.godot").write_text(PROJ_TXT)
    (d / "r100b_seq.gd").write_text(script_text)
    return d


def replace_once(text, old, new, label):
    n = text.count(old)
    if n != 1:
        sys.exit(f"ERROR: anchor {label!r} matched {n} times, expected 1")
    return text.replace(old, new, 1)


HOVER = '\tprint("PASS r100_gui hover %s" % " ".join(out))'
CURSOR = '\tprint("PASS r100_gui cursor %s" % " ".join(out))'
SEQ = '\tprint("SEQ_DONE clean=%d" % do_clean)'
QUIT = '\tquit(0)'
ARG_LIST = ("\tvar seq_arms := ['census', 'routing', 'hover', 'motion', 'localpos', 'cursor', "
            "'clip', 'drag', 'touch', 'subvp', 'warp', 'focus', 'render', 'osmeta']")
FOCUS_FIRST = "\tf.grab_focus()\n"

results = []
runtime = {}


def record(name, note, stdout, stderr, code, error, elapsed, pins):
    guards = {k: v for k, v in pins.items()}
    results.append({"variant": name, "note": note, "exit": code, "error": error,
                    "elapsed_s": round(elapsed, 2), **guards})
    print(f"--- {name}: exit={code} err={error} {elapsed:.1f}s", flush=True)
    for k, v in guards.items():
        print(f"      {k}: {v}", flush=True)


# ---------------- R1/R2: pristine clean=1 (x2 determinism), R3: clean=0
d = mk_proj("pristine", PRISTINE)
out1, err1, code1, e1, t1 = harness_run(d, ["--clean=1"])
out2, err2, code2, e2, t2 = harness_run(d, ["--clean=1"])
out0, err0, code0, e0, t0_ = harness_run(d, ["--clean=0"])
raw1_s, raw1_e, raw1_c = raw_run(d, ["--clean=1"])

c1 = [ln for ln in (out1 + err1).splitlines() if ln.startswith("PASS r100_gui ")]
c0 = [ln for ln in (out0 + err0).splitlines() if ln.startswith("PASS r100_gui ")]
seq1 = next(ln for ln in (out1 + err1).splitlines() if ln.startswith("SEQ_DONE"))
seq0 = next(ln for ln in (out0 + err0).splitlines() if ln.startswith("SEQ_DONE"))
runtime["pristine"] = {"clean1_elapsed": [round(t1, 2), round(t2, 2)], "clean0_elapsed": round(t0_, 2),
                       "clean1_bytes": {"stdout": len(raw1_s), "stderr": len(raw1_e)},
                       "clean1_has_cr": b"\r" in raw1_s or b"\r" in raw1_e,
                       "determinism_clean1": out1 == out2 and err1 == err2 and code1 == code2,
                       "cells": len(c1), "seq1": seq1, "seq0": seq0}
print(json.dumps(runtime["pristine"], indent=1), flush=True)

full_pin = "\n".join(c1)
full_pin_done = "\n".join(c1 + [seq1])
prefix_pin = "\n".join(c1[:7] + [seq1])
cursor_pin = next(ln for ln in c1 if ln.startswith("PASS r100_gui cursor "))
hover_pin = next(ln for ln in c0 if ln.startswith("PASS r100_gui hover "))


def evaluate(tag, note, out, err, code, error, elapsed, pin, seq_expected, pin_name):
    outmerge = out + err
    guards = {
        f"{pin_name}_landed": classify_process(code, error, outmerge, 0, pin),
        "full14_nl_pin": classify_process(code, error, outmerge, 0, full_pin),
        "full14_plus_seqdone_pin": classify_process(code, error, outmerge, 0, full_pin_done),
    }
    guards.update(closure_guards(out, err, c1, seq1))
    record(tag, note + f" | pin={pin_name}", out, err, code, error, elapsed, guards)


# ---------------- V1a: forged extra line after cursor print (clean=1)
v = replace_once(PRISTINE, CURSOR, CURSOR + '\n\tprint("FORGED_EXTRA_CELL_OUTPUT")', "cursor")
d = mk_proj("v_inside_cursor", v)
o, e, c, er, t = harness_run(d, ["--clean=1"])
evaluate("v1_inside_after_cursor", "extra unlisted print inserted between cursor and clip cells",
         o, e, c, er, t, cursor_pin, seq1, "cursor_pin")

# ---------------- V1b: forged extra line after hover print (clean=0) — m_seq replica
v = replace_once(PRISTINE, HOVER, HOVER + '\n\tprint("FORGED_EXTRA_CELL_OUTPUT")', "hover")
d = mk_proj("v_inside_hover", v)
o, e, c, er, t = harness_run(d, ["--clean=0"])
evaluate("v1b_inside_after_hover_noclean", "m_seq replica: forged line inside replay (noclean)",
         o, e, c, er, t, hover_pin, seq0, "hover_pin")

# ---------------- V2: forged lines outside the block (pre, between block&SEQ_DONE, post)
v = replace_once(PRISTINE, "func _run() -> void:", "func _run() -> void:\n\tprint(\"FORGED_PRE_BLOCK\")", "pre")
v = replace_once(v, SEQ, '\tprint("FORGED_BETWEEN_BLOCK_AND_DONE")\n' + SEQ, "between")
v = replace_once(v, QUIT, '\tprint("FORGED_POST_DONE")\n' + QUIT, "post")
d = mk_proj("v_outer", v)
o, e, c, er, t = harness_run(d, ["--clean=1"])
evaluate("v2_outer_forgery", "forged lines before block, between block and SEQ_DONE, after SEQ_DONE",
         o, e, c, er, t, full_pin, seq1, "full14")

# ---------------- V3: stderr-only forgery (no ERROR marker)
v = replace_once(PRISTINE, HOVER, HOVER + '\n\tprinterr("FORGED_STDERR_LINE")', "stderr")
d = mk_proj("v_stderr", v)
o, e, c, er, t = harness_run(d, ["--clean=1"])
evaluate("v3_stderr_only_forgery", "forged payload printed to stderr only", o, e, c, er, t, full_pin, seq1, "full14")

# ---------------- V4: real-fixture split stream — osmeta + SEQ_DONE to stderr
OSMETA = '\tprint("PASS r100_gui osmeta %s" % " ".join(out))'
v = replace_once(PRISTINE, OSMETA, '\tprinterr("PASS r100_gui osmeta %s" % " ".join(out))', "osmeta")
v = replace_once(v, SEQ, '\tprinterr("SEQ_DONE clean=%d" % do_clean)', "seqdone")
d = mk_proj("v_split_osmeta", v)
o, e, c, er, t = harness_run(d, ["--clean=1"])
evaluate("v4_split_osmeta_seqdone_to_stderr", "last cell + terminal receipt printed to stderr",
         o, e, c, er, t, full_pin, seq1, "full14")

# ---------------- V4b: synthetic 7/7 split (classifier-semantics probe, no engine error)
SPLIT_SRC = '''extends SceneTree
func _initialize() -> void:
	var a := ["%s", "%s", "%s", "%s", "%s", "%s", "%s"]
	var b := ["%s", "%s", "%s", "%s", "%s", "%s", "%s"]
	for s in a:
		print(s)
	for s in b:
		printerr(s)
	quit(0)
''' % tuple(c1[:14])
d = mk_proj("v_split_synth", SPLIT_SRC)
o, e, c, er, t = harness_run(d, ["--clean=1"])
evaluate("v4b_split_synthetic_7_7", "synthetic: cells 1-7 stdout, 8-14 stderr (merged seam)",
         o, e, c, er, t, full_pin, seq1, "full14")

# ---------------- V5: echo-pin — block echoed first + real focus mechanism mutated (m_focus)
block_gd = '\\n'.join(c1).replace('"', '')
assert '"' not in block_gd
v = replace_once(PRISTINE, "func _run() -> void:", 'func _run() -> void:\n\tprint("%s")' % block_gd, "echo_pre")
v = replace_once(v, FOCUS_FIRST, "\tpass\n", "focus_removed")
d = mk_proj("v_echo_pre", v)
o, e, c, er, t = harness_run(d, ["--clean=1"])
evaluate("v5_echo_pre_plus_mfocus", "echoed pinned block first + real focus mechanism mutated",
         o, e, c, er, t, full_pin, seq1, "full14")

# ---------------- V5b: same mutation, block echoed after SEQ_DONE
v = replace_once(PRISTINE, QUIT, '\tprint("%s")\n' % block_gd + QUIT, "echo_post")
v = replace_once(v, FOCUS_FIRST, "\tpass\n", "focus_removed")
d = mk_proj("v_echo_post", v)
o, e, c, er, t = harness_run(d, ["--clean=1"])
evaluate("v5b_echo_post_plus_mfocus", "echoed pinned block after SEQ_DONE + real focus mutated",
         o, e, c, er, t, full_pin, seq1, "full14")

# ---------------- V6: CRLF seam — every PASS line + receipt emitted as CRLF via printraw
v = PRISTINE
v = re.sub(r'print\("PASS r100_gui ([^"]*)" % " "\.join\((out|facts)\)\)',
           r'printraw("PASS r100_gui \1" % " ".join(\2) + "\r\n")', v)
v = re.sub(r'print\("SEQ_DONE clean=%d" % do_clean\)',
           r'printraw("SEQ_DONE clean=%d\r\n" % do_clean)', v)
assert v.count("printraw") == 15, v.count("printraw")
d = mk_proj("v_crlf", v)
o, e, c, er, t = harness_run(d, ["--clean=1"])
raw_s, raw_e, raw_c = raw_run(d, ["--clean=1"])
runtime["crlf"] = {"raw_stdout_has_crlf": b"\r\n" in raw_s, "raw_crlf_count": raw_s.count(b"\r\n"),
                   "textmode_capture_has_cr": "\r" in (o + e)}
evaluate("v6_crlf_transcript", "all 15 receipt lines emitted CRLF (byte capture keeps \\r\\n)",
         o, e, c, er, t, full_pin, seq1, "full14")
# timeout-path semantics: raw bytes decoded WITHOUT newline translation
raw_decoded = raw_s.decode(errors="replace") + raw_e.decode(errors="replace")
raw_guards = {"raw_decode_full14_pin": full_pin in raw_decoded,
              "raw_decode_has_cr": "\r" in raw_decoded}
record("v6b_crlf_raw_decode", "same bytes via timeout-path decode (no universal newlines)",
       raw_decoded, "", raw_c, None, 0.0, raw_guards)

# ---------------- V7: lone CR injected inside a forged line
v = replace_once(PRISTINE, HOVER, HOVER + '\n\tprint("FORGED_A\\rFORGED_B")', "lonecr")
d = mk_proj("v_lonecr", v)
o, e, c, er, t = harness_run(d, ["--clean=1"])
raw_s, raw_e, raw_c = raw_run(d, ["--clean=1"])
runtime["lonecr"] = {"raw_has_single_cr_line": b"FORGED_A\rFORGED_B" in raw_s,
                     "textmode_split_into_two": "FORGED_A" in (o + e) and "FORGED_B" in (o + e)}
evaluate("v7_lone_cr_forgery", "forged line contains a lone CR", o, e, c, er, t, full_pin, seq1, "full14")

# ---------------- V8: timeout truncation — all 14 lines then hang
v = replace_once(PRISTINE, SEQ, "\tOS.delay_msec(30000)\n" + SEQ, "hang")
d = mk_proj("v_hang", v)
o, e, c, er, t = harness_run(d, ["--clean=1"], timeout=8)
hang_guards = {"full14_in_truncated_text": full_pin in (o + e),
               "seqdone_in_truncated_text": seq1 in (o + e),
               "classified": classify_process(c, er, o + e, 0, full_pin_done)}
record("v8_timeout_hang_after_block", "14 cells printed, then hang -> 8s timeout", o, e, c, er, t, hang_guards)

# ---------------- V9: truncated replay, exit 0 (7 of 14 cells) — prefix-pin ceiling
trunc = ARG_LIST.replace(", 'drag', 'touch', 'subvp', 'warp', 'focus', 'render', 'osmeta'", "")
assert trunc != ARG_LIST
v = replace_once(PRISTINE, ARG_LIST, trunc, "trunc")
d = mk_proj("v_trunc7", v)
o, e, c, er, t = harness_run(d, ["--clean=1"])
trunc_guards = {"full14_pin": classify_process(c, er, o + e, 0, full_pin),
                "full14_plus_seqdone_pin": classify_process(c, er, o + e, 0, full_pin_done),
                "prefix7_plus_seqdone_pin": classify_process(c, er, o + e, 0, prefix_pin),
                "exit0_seqdone_present": seq1 in (o + e)}
record("v9_truncated_replay_exit0", "only first 7 arms run, SEQ_DONE still printed", o, e, c, er, t, trunc_guards)

payload = {"runtime": runtime, "results": results,
           "full_pin_line_count": len(c1), "c1_sha_lines": c1, "c0_sha_lines": c0}
outp = Path(__file__).resolve().parent / "r101-crit2-attack-matrix.json"
outp.write_text(json.dumps(payload, indent=1))
print(f"\nwrote {outp}", flush=True)
