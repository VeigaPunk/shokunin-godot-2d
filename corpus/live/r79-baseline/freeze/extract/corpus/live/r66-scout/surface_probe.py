#!/usr/bin/env python3
"""r66-scout: rejection-clause surface matrix over the VERBATIM
classify_process extracted from corpus/fixtures/run_battery.py via
ast.get_source_segment (r65-boundary method — zero re-implementation).

Godot-free: every arm is byte-level reclassification, isolating the clause
geometry the r66 author must pin. Run from the lane root."""
import ast
import json
import sys
from pathlib import Path

RUNNER = Path("corpus/fixtures/run_battery.py")
OUT = Path("corpus/live/r66-scout/surface-probe-results.json")

tree = ast.parse(RUNNER.read_text())
seg = None
for node in ast.walk(tree):
    if isinstance(node, ast.FunctionDef) and node.name == "classify_process":
        seg = ast.get_source_segment(RUNNER.read_text(), node)
        break
assert seg, "classify_process not found"
ns = {}
exec(seg, ns)
cp = ns["classify_process"]

SIG = "DESCENDANT_PIPE_PROBE: expected signature"

def cls(output, expected_exit=0, signature=SIG, allowed=(), code=0, error=None):
    return cp(code, error, output, expected_exit, signature, allowed)

EXACT = "ERROR: SAVE EXPECTED NEGATIVE: malformed JSON rejected signature=JSON_PARSE_ERROR"
PREFIX = "ERROR: UI BUTTON ASSERTION FAILED: expected release1 text=Activated 1 receipts=1,"
CHAIN = "ERROR: chain incomplete"
CHAIN_LINE = "ERROR: chain incomplete collections=[1] scene=SceneB:<Node#123> old_alive=false"

rows = []

def row(name, output, expected, allowed=(), note=""):
    got = cls(output, allowed=allowed)
    rows.append({"arm": name, "expected_verdict": expected, "observed": got,
                 "discriminates": got == expected, "note": note,
                 "error_lines": [l for l in output.splitlines() if "ERROR:" in l]})
    return got

base = SIG + "\n"

# --- (a) allowlist-as-preemptor: forged error matching the allowlist is verdict-inert
row("a_exact_forge_nolist", base + EXACT + "\n", False, (),
    "un-allowlisted twin rejects")
row("a_exact_forge_allowlisted", base + EXACT + "\n", True, (EXACT,),
    "same forged line, matching allowlist -> absorbed")
row("a_exact_forge_wronglist", base + EXACT + "\n", False,
    ("ERROR: unrelated different diagnostic",),
    "non-matching allowlist is inert -> still rejects")

# --- (b) match-shape gates: exact / ,-prefix / structured
row("b_prefix_exactline", base + PREFIX + "\n", True, (PREFIX,),
    "emitted line == prefix literal: first-branch exact match also hits")
row("b_prefix_forged_tail", base + PREFIX + "FORGED arbitrary tail\n", True, (PREFIX,),
    "startswith + count==1: ARBITRARY suffix absorbed")
row("b_prefix_tail_second_ERROR", base + PREFIX + " ERROR: tailforge\n", False, (PREFIX,),
    "count==2: tail-forge defeats the allowlist -> rejects")
row("b_exact_tail_second_ERROR", base + EXACT + " ERROR: tailforge\n", False, (EXACT,),
    "exact entry + appended ERROR: -> line no longer == entry -> unrelated -> rejects")
row("b_exact_whitespace_pad", base + "  " + EXACT + "  \n", True, (EXACT,),
    "strip() makes exact matching whitespace-insensitive")
row("b_chain_full", base + CHAIN_LINE + "\n", True, (CHAIN,),
    "structured form: all three substrings + count==1")
row("b_chain_missing_scene", base + "ERROR: chain incomplete collections=[1] old_alive=false\n", False, (CHAIN,),
    "missing 'scene=SceneB:<Node#' -> not allowed -> rejects")
row("b_chain_two_errors", base + CHAIN_LINE + " ERROR: x\n", False, (CHAIN,),
    "structured + second ERROR: -> count==2 -> rejects")
row("b_prefix_entry_as_exact", base + PREFIX + "\n", True, (PREFIX,),
    "save_process_missing-shape: emitted line ends AT the comma -> exact branch")
row("b_case_mismatch", base + "error: lowercase twin\n", True, (),
    "lowercase 'error:' is not the token -> invisible to the scan")

# --- (c) line-faithfulness: splitlines geometry + merge seam
row("c_newline_split_evasion", base + "ERR\nOR: FORGED newline-split diagnostic\n", True, (),
    "token split ACROSS newline: no captured line contains 'ERROR:' -> EVADES")
row("c_same_line_split_detected", base + "ER" + "ROR: FORGED contiguous diagnostic\n", False, (),
    "token contiguous on one line -> detected")
row("c_midline_unanchored", base + "prefix text ERROR: midline diagnostic\n", False, (),
    "'ERROR:' is a substring check, not line-anchored")
# merge-seam fabrication: stdout tail (unterminated) + stderr head
stdout_tail = SIG + "\nending in ERROR"
stderr_head = ": PHANTOM fabricated reject line\n"
merged = stdout_tail + stderr_head  # run_process does proc.stdout + proc.stderr
row("c_seam_splice_fabricated", merged, False, (),
    "stdout lacks any ERROR: line; stderr lacks any ERROR: line; merged fabricates one -> rejects",
    )
rows[-1]["stdout_error_lines"] = [l for l in stdout_tail.splitlines() if "ERROR:" in l]
rows[-1]["stderr_error_lines"] = [l for l in stderr_head.splitlines() if "ERROR:" in l]
# newline-split seam EVASION is symmetric: line split across streams re-merges
row("c_seam_signature_splice", "sig-head DESCENDANT_PIPE_PRO" + "BE: expected signature\n", True, (),
    "signature clause is blob-substring: a seam-spliced signature ACCEPTS")
# splitlines boundary census: which control bytes split the token
boundaries = ["\n", "\r", "\r\n", "\x0b", "\x0c", "\x1c", "\x1d", "\x1e", "\x85", "\u2028", "\u2029", "\x1f", "\t"]
split_census = {}
for b in boundaries:
    probe_text = base + "ERR" + b + "OR: split-token diagnostic\n"
    evades = cls(probe_text) is True
    split_census[repr(b)] = {"evades_scan": evades,
                             "splitlines_count": len(("ERR" + b + "OR:").splitlines())}
# blob clauses (SCRIPT ERROR:/Parse Error:) — same seam/split geometry
row("c_script_error_forged", base + "SCRIPT ERROR: forged post-death\n", False, (),
    "blob clause fires on forged SCRIPT ERROR:")
row("c_script_error_newline_split", base + "SCRIPT ERR\nOR: forged\n", True, (),
    "newline-split evades the blob clause too (non-contiguous bytes)")
row("c_parse_error_forged", base + "Parse Error: forged post-death\n", False, (),
    "blob clause fires on forged Parse Error:")
row("c_script_error_seam_splice", "SCRIPT ERR" + "OR: seam-forged\n" + SIG + "\n", False, (),
    "contiguous seam bytes satisfy the blob substring -> fabricated reject")

payload = {
    "extracted_from": str(RUNNER),
    "extraction": "ast.get_source_segment -> exec (verbatim)",
    "rows": rows,
    "splitlines_boundary_census": split_census,
    "all_discriminate": all(r["discriminates"] for r in rows),
}
OUT.write_text(json.dumps(payload, indent=2) + "\n")
print(json.dumps({"rows": len(rows), "all_discriminate": payload["all_discriminate"],
                  "failures": [r["arm"] for r in rows if not r["discriminates"]]}, indent=2))
sys.exit(0 if payload["all_discriminate"] else 1)
