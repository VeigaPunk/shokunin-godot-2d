#!/usr/bin/env python3
"""r101-crit2 seqfull probes — attacks against the E12 r101_seqfull.gd self-digest design.

Scratch copies under /tmp/r101-crit2/sf_*/ only; corpus fixture is never edited, battery never run.
Row-pin candidates evaluated:
  D  = the single SEQ_END digest line (presence, merged)
  DS = SEQ_END digest line + SEQ_CENSUS line, contiguous, merged
  SPAN = SEQ_BEGIN..SEQ_END contiguous span, merged
  SPAN_S = same span required in stdout alone + no PASS/CENSUS/END/SEQ_ line on stderr
"""
import hashlib
import json
import re
import subprocess
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
SRC = (ROOT / "corpus" / "fixtures" / "r101_seqfull.gd").read_text()
PROJ = (ROOT / "corpus" / "fixtures" / "project.godot").read_text()
SCRATCH = Path("/tmp/r101-crit2")
ALLOWED = ('ERROR: Parameter "t" is null.',)


def run(proj, flag="--clean=1", timeout=8):
    cmd = ["/usr/bin/godot", "--headless", "--path", str(proj), "--script", "res://r101_seqfull.gd", "--", flag]
    t0 = time.monotonic()
    p = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
    return p.stdout, p.stderr, p.returncode, None, time.monotonic() - t0


def mk(name, text):
    d = SCRATCH / name
    d.mkdir(parents=True, exist_ok=True)
    (d / "project.godot").write_text(PROJ)
    (d / "r101_seqfull.gd").write_text(text)
    return d


def rep1(t, old, new, tag):
    assert t.count(old) == 1, (tag, t.count(old))
    return t.replace(old, new, 1)


def classify(code, error, output, sig):
    unrelated = [ln for ln in output.splitlines() if "ERROR:" in ln and ln.strip() != ALLOWED[0]]
    return (code == 0 and error is None and sig in output and not unrelated
            and "SCRIPT ERROR:" not in output and "Parse Error:" not in output)


out = {}
d = mk("sf_base", SRC)
o1, e1, c1, er1, t1 = run(d, "--clean=1")
o0, e0, c0, er0, t0 = run(d, "--clean=0")
lines1 = [ln for ln in (o1 + e1).splitlines() if ln.startswith("PASS r100_gui ")]
begin1 = next(ln for ln in (o1 + e1).splitlines() if ln.startswith("SEQ_BEGIN"))
census1 = next(ln for ln in (o1 + e1).splitlines() if ln.startswith("SEQ_CENSUS"))
end1 = next(ln for ln in (o1 + e1).splitlines() if ln.startswith("SEQ_END"))
census0 = next(ln for ln in (o0 + e0).splitlines() if ln.startswith("SEQ_CENSUS"))
end0 = next(ln for ln in (o0 + e0).splitlines() if ln.startswith("SEQ_END"))
span1 = "\n".join([begin1] + lines1 + [census1, end1])
span0 = "\n".join([next(ln for ln in (o0 + e0).splitlines() if ln.startswith("SEQ_BEGIN"))] + 
                  [ln for ln in (o0 + e0).splitlines() if ln.startswith("PASS r100_gui ")] + [census0, end0])
internal_digest = hashlib.sha256("\n".join(lines1).encode()).hexdigest()
out["base"] = {
    "clean1_s": round(t1, 2), "clean0_s": round(t0, 2), "exit": [c1, c0],
    "begin": begin1, "census1": census1, "census0": census0,
    "end1": end1, "end0": end0,
    "printed_digest_matches_recomputed_over_captured_cells": ("digest=" + internal_digest) in end1,
    "stdout_pass_lines": sum(1 for ln in o1.splitlines() if ln.startswith("PASS r100_gui ")),
    "stderr_pass_lines": sum(1 for ln in e1.splitlines() if ln.startswith("PASS r100_gui ")),
    "stderr_line_count": len(e1.splitlines()),
    "span1_in_stdout": span1 in o1, "end1_in_stdout": end1 in o1,
    "span_lines": len(lines1),
}
pins = {"D": (end1, merged := True), "DS": (census1 + "\n" + end1, True), "SPAN": (span1, True)}
print(json.dumps(out["base"], indent=1), flush=True)


def evaluate(tag, note, o, e, c, er, elapsed, pinset, span_stdout_only):
    merged = o + e
    row = {"variant": tag, "note": note, "exit": c, "error": er, "s": round(elapsed, 2)}
    for name, (sig, _m) in pinset.items():
        row[f"pin_{name}"] = classify(c, er, merged, sig)
    row["span_stdout_anchor"] = classify(c, er, o, span1) and not any(
        ln.startswith(("PASS r100_gui", "SEQ_")) for ln in e.splitlines())
    row["pass_lines_total"] = sum(1 for ln in merged.splitlines() if ln.startswith("PASS r100_gui "))
    out[row["variant"]] = row
    print(json.dumps(row), flush=True)


# SF1: forged print() inside the span (after hover cell, between cells)
v = rep1(SRC, '	print("SEQ_CENSUS', '\tprint("FORGED_EXTRA_CELL_OUTPUT")\n\tprint("SEQ_CENSUS', "sf1")
d = mk("sf_inside", v)
o, e, c, er, t = run(d)
evaluate("SF1_forged_print_inside_span", "foreign print() between cells (m_seq shape)", o, e, c, er, t, pins, False)

# SF2: forged print() after SEQ_END
v = rep1(SRC, "	quit(0)", '\tprint("FORGED_AFTER_END")\n\tquit(0)', "sf2")
d = mk("sf_after", v)
o, e, c, er, t = run(d)
evaluate("SF2_forged_print_after_end", "foreign print() after receipt", o, e, c, er, t, pins, False)

# SF3: stderr-only forged payload (printerr in the render cell path)
v = rep1(SRC, '	print("SEQ_CENSUS', '\tprinterr("FORGED_STDERR_LINE")\n\tprint("SEQ_CENSUS', "sf3")
d = mk("sf_stderr", v)
o, e, c, er, t = run(d)
evaluate("SF3_stderr_forgery", "printerr payload", o, e, c, er, t, pins, False)

# SF4: SEQ_CENSUS + SEQ_END routed to stderr (single-line/merged pins blind)
v = rep1(SRC, '	print("SEQ_CENSUS', '\tprinterr("SEQ_CENSUS', "sf4a")
v = rep1(v, '	print("SEQ_END', '\tprinterr("SEQ_END', "sf4b")
d = mk("sf_recv_stderr", v)
o, e, c, er, t = run(d)
evaluate("SF4_receipts_on_stderr", "census+digest lines on stderr", o, e, c, er, t, pins, False)

# SF5: mechanism mutation (m_focus removal) — does the self-digest move?
v = rep1(SRC, "\tf.grab_focus()\n", "\tpass\n", "sf5")
d = mk("sf_mfocus", v)
o, e, c, er, t = run(d)
evaluate("SF5_mfocus_mutation", "f.grab_focus() removed in focus cell", o, e, c, er, t, pins, False)
row = out["SF5_mfocus_mutation"]
row["focused_cell_line_changed"] = next(
    (ln for ln in (o + e).splitlines() if ln.startswith("PASS r100_gui focus ")), None) != \
    next((ln for ln in (o1 + e1).splitlines() if ln.startswith("PASS r100_gui focus ")), None)
row["digest_line_changed"] = next(
    (ln for ln in (o + e).splitlines() if ln.startswith("SEQ_END")), None) != end1
row["census_line_changed"] = next(
    (ln for ln in (o + e).splitlines() if ln.startswith("SEQ_CENSUS")), None) != census1

# SF6: CRLF on all receipt prints (BEGIN/CENSUS/END + cells via _emit->printraw)
v = SRC
v = re.sub(r'print\("SEQ_BEGIN ([^"]*)" % \[seq_arms\.size\(\), do_clean, FRESH_PINS\.size\(\)\]\)',
           r'printraw("SEQ_BEGIN \1\r\n" % [seq_arms.size(), do_clean, FRESH_PINS.size()])', v)
v = re.sub(r'print\("SEQ_CENSUS ([^"]*)" % \[\n', r'printraw("SEQ_CENSUS \1\r\n" % [\n', v)
v = re.sub(r'print\("SEQ_END digest=%s" % "\\n"\.join\(_transcript\)\.sha256_text\(\)\)',
           r'printraw("SEQ_END digest=%s\r\n" % "\n".join(_transcript).sha256_text())', v)
v = v.replace("	_transcript.append(line)\n	print(line)", "	_transcript.append(line)\n	printraw(line + \"\\r\\n\")")
assert "	printraw(line + \"\\r\\n\")" in v, "emit replace failed"
n_crlf = v.count("printraw")
assert n_crlf == 4, n_crlf  # 3 receipt prints + 1 _emit call site (covers all 14 cell lines)
d = mk("sf_crlf", v)
o, e, c, er, t = run(d)
evaluate("SF6_crlf_receipts", "BEGIN/CELLS/CENSUS/END emitted CRLF (printraw)", o, e, c, er, t, pins, False)
out["SF6_crlf_receipts"]["textmode_has_cr"] = "\r" in (o + e)
raw = subprocess.run(["timeout", "8", "/usr/bin/godot", "--headless", "--path", str(d),
                      "--script", "res://r101_seqfull.gd", "--", "--clean=1"], capture_output=True).stdout
out["SF6_crlf_receipts"]["raw_has_crlf"] = b"\r\n" in raw

p = Path(__file__).resolve().parent / "r101-crit2-seqfull.json"
p.write_text(json.dumps(out, indent=1))
print("wrote", p)
