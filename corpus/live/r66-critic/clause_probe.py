#!/usr/bin/env python3
"""r66 critic probe: rejection-clause surface counterexample arms.

Extracts classify_process / classify_streams / classify_audio_process and the
per-case expected_errors map VERBATIM from run_battery.py (dedent + exec), so
classification semantics cannot drift from the tracked code under review.

Measurements are organized by the five brief attack questions. Pure-Python
clause arms need no Godot; real-pipe arms use subprocess pipes on this host.
Writes clause-probe-results.json next to this script.
"""
import json
import re
import subprocess
import sys
import textwrap
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent
FIXTURES = ROOT.parent.parent / "fixtures"
SRC = (FIXTURES / "run_battery.py").read_text()

# --- verbatim extraction: classifiers ---
_NS = {"re": re}

def extract(name, next_pattern):
    m = re.search(r"(    def %s\(.*?\n)(?=    %s)" % (name, next_pattern), SRC, re.S)
    assert m, f"{name} block not found"
    exec(textwrap.dedent(m.group(1)), _NS)
    return _NS[name]

classify_process = extract("classify_process", r"def classify_streams")
classify_streams = extract("classify_streams", r"def classify_audio_process")
classify_audio = extract("classify_audio_process", r"if args\.fault_injection")

# --- verbatim extraction: expected_errors allowlist map ---
m = re.search(r"expected_errors = (\{.*?\n            \})\.get\(name, \(\)\)", SRC, re.S)
assert m, "expected_errors map not found"
ALLOWMAP = eval(m.group(1))  # dict-literal of string tuples only

# CASES names verbatim
m = re.search(r"CASES = \[(.*?)\n\]", SRC, re.S)
CASE_NAMES = re.findall(r'\("([a-z0-9_]+)",', m.group(1))

SIG = "DESCENDANT_PIPE_PROBE: expected signature"
BENIGN = f"{SIG}\nGodot Engine v4.7.2\n"
results = {}

def cls(output, allowed=(), code=0, error=None, expected_exit=0, signature=SIG):
    return classify_process(code, error, output, expected_exit, signature, allowed)

def error_line_set(text):
    # verbatim shape of errforge record["error_lines"] (run_battery.py:1200)
    return sorted({line.strip() for line in text.splitlines() if "ERROR:" in line})

def record_output_field(text):
    # verbatim shape of CASES record["output"] (run_battery.py:455)
    return text.strip().splitlines()

SAVE_ALLOW = ALLOWMAP["save_corrupt_negative"]          # exact-form entry
PREFIX_ALLOW = ALLOWMAP["save_process_missing"]         # ','-prefix entry
CHAIN_ALLOW = ("ERROR: chain incomplete",)              # structured entry

# =====================================================================
# Attack (1): allowlist absorption — verdict-inert vs record-faithful
# =====================================================================
allow_line = SAVE_ALLOW[0]
out_a1 = BENIGN + allow_line + "\n"
results["a1_allowlist_absorption"] = {
    "allowlisted_line_verdict": cls(out_a1, SAVE_ALLOW),
    "line_still_in_error_lines": allow_line in error_line_set(out_a1),
    "line_still_in_output_field": allow_line in record_output_field(out_a1),
    "note": "verdict-inert but record-faithful: the absorbed line remains in "
            "error_lines extraction and the CASES output field"},
# twin: same line minus the exact tail -> un-allowlisted -> rejects
twin = "ERROR: SAVE EXPECTED NEGATIVE: malformed JSON rejected signature=FORGED"
out_a1b = BENIGN + twin + "\n"
results["a1_unallowlisted_twin"] = {"verdict": cls(out_a1b, SAVE_ALLOW),
                                    "line": twin}

# =====================================================================
# Attack (2): newline-split — which splits evade vs still trip
# =====================================================================
splits = {}
for tag, body in [
    ("split_inside_ERROR_token",      "ERR\nOR: split diagnostic"),
    ("split_before_colon",            "ERROR\n: split diagnostic"),
    ("split_inside_token_offset",     "ERRO\nR: split diagnostic"),
    ("split_after_token",             "ERROR: head\ncontinued tail"),
    ("split_before_token",            "prefix\nERROR: split diagnostic"),
    ("script_error_inside_ERROR",     "SCRIPT ERR\nOR: parse blew up"),
    ("script_error_inside_SCRIPT",    "SCR\nIPT ERROR: parse blew up"),
    ("script_error_split_prefix",     "SCRIPT \nERROR: parse blew up"),
    ("script_error_before_colon",     "SCRIPT ERROR\n: parse blew up"),
    ("parse_error_inside_Error",      "Parse Err\nor: parse blew up"),
    ("parse_error_inside_Parse",      "Par\nse Error: parse blew up"),
    ("parse_error_keep_Error_intact", "Parse \nError: parse blew up"),
]:
    out = BENIGN + body + "\n"
    line_trip = bool([l for l in out.splitlines() if "ERROR:" in l])
    splits[tag] = {
        "verdict": cls(out),
        "blob_SCRIPT_ERROR_trips": "SCRIPT ERROR:" in out,
        "blob_ParseError_trips": "Parse Error:" in out,
        "line_clause_would_trip": line_trip,
    }
results["a2_newline_split"] = splits

# =====================================================================
# Attack (b): allowlist match shapes — exact vs ,-prefix vs structured
# =====================================================================
shapes = {}
# exact-form: byte-identical only
shapes["exact_verbatim"] = cls(BENIGN + SAVE_ALLOW[0] + "\n", SAVE_ALLOW)
shapes["exact_trailing_space_line"] = cls(BENIGN + SAVE_ALLOW[0] + "   \n", SAVE_ALLOW)  # stripped
shapes["exact_extra_tail"] = cls(BENIGN + SAVE_ALLOW[0] + " EXTRA\n", SAVE_ALLOW)
shapes["exact_indented"] = cls(BENIGN + "      " + SAVE_ALLOW[0] + "\n", SAVE_ALLOW)
# ,-prefix form: startswith(allowed) + count==1 — tail is a wildcard
pa = PREFIX_ALLOW[0]
assert pa.endswith(","), pa
shapes["prefix_exact"] = cls(BENIGN + pa + "\n", PREFIX_ALLOW)
shapes["prefix_with_tail"] = cls(BENIGN + pa + " path=/tmp/forged attacker_text\n", PREFIX_ALLOW)
shapes["prefix_tail_no_space"] = cls(BENIGN + pa + "glued_tail\n", PREFIX_ALLOW)
shapes["prefix_tail_second_ERROR"] = cls(BENIGN + pa + " t ERROR: second\n", PREFIX_ALLOW)
shapes["prefix_tail_lower_error"] = cls(BENIGN + pa + " t error: lowercase\n", PREFIX_ALLOW)
shapes["prefix_wrong_base"] = cls(BENIGN + "ERROR: SAVE PROCESS EXPECTED NEGATIVE: other signature=FILE_NOT_FOUND,\n", PREFIX_ALLOW)
# mid-line position: a non-line-start occurrence of the allowlisted prefix
shapes["prefix_midline"] = cls(BENIGN + "banner: " + pa + " tail\n", PREFIX_ALLOW)
shapes["exact_midline"] = cls(BENIGN + "banner: " + SAVE_ALLOW[0] + "\n", SAVE_ALLOW)
# structured chain-incomplete form
chain_ok = "ERROR: chain incomplete collections=2 scene=SceneB:<Node#123> old_alive=false"
shapes["chain_full_form"] = cls(BENIGN + chain_ok + "\n", CHAIN_ALLOW)
shapes["chain_missing_scene"] = cls(BENIGN + "ERROR: chain incomplete collections=2 old_alive=false\n", CHAIN_ALLOW)
shapes["chain_forged_tail"] = cls(BENIGN + chain_ok + " forged=1\n", CHAIN_ALLOW)
shapes["chain_double_ERROR"] = cls(BENIGN + chain_ok + " ERROR: x\n", CHAIN_ALLOW)
shapes["chain_bare_allowed"] = cls(BENIGN + "ERROR: chain incomplete\n", CHAIN_ALLOW)
results["b_allowlist_shapes"] = shapes

# =====================================================================
# Attack (3): splice fabrication at the stdout+stderr concat seam —
# does it need the child to leave a half-token, or can a pure
# post-death descendant fabricate alone?
# =====================================================================
def merge(stdout, stderr):
    return stdout + stderr   # verbatim: text = (ef_out or "") + (ef_err or "")

splice = {}
# r65 shape: child leaves half-token at stdout tail
m1 = merge(BENIGN + "line ends in ERROR", ": PHANTOM spliced\n")
splice["child_half_token"] = {
    "merged_trips": cls(m1),
    "stdout_error_lines": error_line_set(BENIGN + "line ends in ERROR"),
    "stderr_error_lines": error_line_set(": PHANTOM spliced\n"),
    "merged_error_lines": error_line_set(m1),
}
# pure descendant: child stdout ends cleanly; descendant writes the stdout
# half AND the stderr half post-death — both pipes inherited
dout = BENIGN + "clean child line\n" + "descendant tail ERROR"
derr = ": PHANTOM both-halves-post-death\n"
m2 = merge(dout, derr)
splice["descendant_only_splice"] = {
    "merged_trips": cls(m2),
    "stdout_error_lines": error_line_set(dout),
    "stderr_error_lines": error_line_set(derr),
    "merged_error_lines": error_line_set(m2),
    "note": "child output line-clean; both fragments authored post-death by "
            "one descendant holding both pipe fds"},
# blob-clause splice: SCRIPT ERROR: fabricated across the seam
m3 = merge(BENIGN + "tail SCRIPT ERROR", ": fabricated blob\n")
splice["script_error_blob_splice"] = {
    "verdict": cls(m3),
    "blob_present": "SCRIPT ERROR:" in m3,
    "line_clause_also_trips": bool([l for l in m3.splitlines() if "ERROR:" in l]),
}
# seam-inverse: stderr tail + stdout head never splices (concat order fixed)
m4 = merge("sig-needs-this\n" + SIG, "stderr tail ERROR")  # stdout is one blob
m4 = merge(BENIGN, "stderr ends ERROR")  # stderr tail has no following bytes
splice["stderr_tail_no_splice"] = {"verdict": cls(m4),
                                   "note": "stderr tail cannot splice: nothing follows it in merge order"}
# allowlisted phantom: splice fabricates an ABSORBED line -> verdict-inert.
# Split INSIDE the "ERROR:" token: stdout tail is bare "ERROR" (a new merged
# line start, no colon), stderr head is ": <rest>" — neither fragment alone
# contains "ERROR:", yet the merged line byte-equals the allowlist entry.
m5 = merge(BENIGN + "ERROR", ": " + SAVE_ALLOW[0][len("ERROR: "):] + "\n")
splice["allowlisted_phantom"] = {
    "stdout_fragment": "ERROR",
    "stderr_fragment": ": " + SAVE_ALLOW[0][len("ERROR: "):],
    "verdict": cls(m5, SAVE_ALLOW),
    "merged_error_lines": error_line_set(m5),
    "stdout_had_error_line": bool(error_line_set(BENIGN + "ERROR")),
    "stderr_had_error_line": bool(error_line_set(
        ": " + SAVE_ALLOW[0][len("ERROR: "):] + "\n")),
    "note": "spliced line byte-equals the allowlist entry: fabricated AND "
            "verdict-inert — neither stream wrote it as a line"}
# control: same splice with the allowlist EMPTY -> phantom rejects
splice["allowlisted_phantom_no_allowlist"] = {"verdict": cls(m5, ())}
results["a3_splice"] = splice

# =====================================================================
# Attack (4): double-sided forge — one descendant evades AND fabricates
# in the same record
# =====================================================================
double = {}
# record X: descendant emits a real error as ERR\nOR: (evades scan) AND
# splices a phantom ERROR: line (fabricated reject)
d4out = BENIGN + "desc tail ERROR"          # stdout half of phantom
d4err = ": PHANTOM fabricated\nERR\nOR: real emitted diagnostic\n"
m6 = merge(d4out, d4err)
double["evade_and_fabricate"] = {
    "verdict": cls(m6),
    "error_lines": error_line_set(m6),
    "real_emission_line_present": "real emitted diagnostic" in m6,
    "real_emission_trips": any("real emitted diagnostic" in l and "ERROR:" in l
                               for l in m6.splitlines()),
}
# record Y: evasion + allowlisted fabrication -> verdict stays PASS while a
# real error emission is invisible and a fabricated line is absorbed.
# stdout tail "ERROR" starts a merged line; stderr ": <tail>" completes the
# byte-exact allowlist phantom; the same stderr stream then emits the real
# diagnostic split inside its ERROR: token.
d5out = BENIGN + "ERROR"
d5err = (": " + SAVE_ALLOW[0][len("ERROR: "):] + "\n"
         + "ERR\nOR: hidden real diagnostic\n")
m7 = merge(d5out, d5err)
double["evade_and_absorbed_fabricate"] = {
    "verdict": cls(m7, SAVE_ALLOW),
    "control_verdict_no_allowlist": cls(m7, ()),
    "error_lines": error_line_set(m7),
    "note": "PASS verdict with (a) a real error emission that escaped the "
            "scan and (b) a fabricated line that never existed per-stream"},
results["a4_double_sided"] = double

# =====================================================================
# Attack (5): census — which allowlist entries are grep-absent, and is
# grep-absence valid deadness evidence? (reachability measured separately)
# =====================================================================
census = {"map_keys_total": len(ALLOWMAP),
          "empty_entries": sorted(k for k, v in ALLOWMAP.items() if not v),
          "keys_not_in_CASES": sorted(set(ALLOWMAP) - set(CASE_NAMES)),
          "entries": []}
for case, entries in sorted(ALLOWMAP.items()):
    for ent in entries:
        body = ent[len("ERROR: "):] if ent.startswith("ERROR: ") else ent
        # grep fixture sources for the message body (allow push_error bodies)
        hits = []
        for gd in FIXTURES.rglob("*.gd"):
            t = gd.read_text(errors="replace")
            if body.rstrip(",") in t or ent.rstrip(",") in t:
                hits.append(gd.name)
        census["entries"].append({"case": case, "entry": ent[:80],
                                  "shape": ("prefix" if ent.endswith(",")
                                            else "structured" if ent == "ERROR: chain incomplete"
                                            else "exact"),
                                  "grep_hits_in_fixtures": hits})
results["a5_census_static"] = census

out_path = ROOT / "clause-probe-results.json"
out_path.write_text(json.dumps(results, indent=2) + "\n")
print(json.dumps({"written": str(out_path),
                  "allowmap_keys": len(ALLOWMAP),
                  "case_names": len(CASE_NAMES)}, indent=2))
