#!/usr/bin/env python3
"""r67 simplifier: pre-land divergence truth table.

Extracts classify_process + classify_streams VERBATIM from run_battery.py via
AST (no re-typed copy) and enumerates the stream-attribution axis:
which (stdout,stderr) byte placements diverge between merged and per-stream
classification. Output: JSON table to stdout.
"""
import ast
import json
import sys
from pathlib import Path

SRC = Path(sys.argv[1] if len(sys.argv) > 1 else
           "/home/vgpnk/Projects/shokunin/game-dev-2d-shokunin/corpus/fixtures/run_battery.py")

tree = ast.parse(SRC.read_text())
wanted = {"classify_process", "classify_streams"}
found = {}


def walk(node):
    for child in ast.iter_child_nodes(node):
        if isinstance(child, ast.FunctionDef) and child.name in wanted:
            found[child.name] = child
        walk(child)


walk(tree)
missing = wanted - set(found)
if missing:
    sys.exit(f"missing functions: {missing}")

ns = {}
for name, node in found.items():
    mod = ast.Module(body=[node], type_ignores=[])
    exec(compile(mod, str(SRC), "exec"), ns)

classify_process = ns["classify_process"]
classify_streams = ns["classify_streams"]

SIG = "STREAM_STDOUT: expected attribution marker"
ERR = "ERROR: DESCENDANT_PIPE_ERRFORGE unrelated descendant diagnostic"
BANNER = "Godot Engine v4.7.2.stable.official - https://godotengine.org"


def row(case, stdout, stderr, exp_exit=0, code=0, error=None,
        sig=SIG, allowed=()):
    merged = stdout + stderr
    p = classify_process(code, error, merged, exp_exit, sig, allowed)
    s = classify_streams(code, error, stdout, stderr, exp_exit, sig, allowed)
    return {"case": case, "merged": p, "streams": s, "divergent": p != s}


clean_out = BANNER + "\n" + SIG + "\n"
rows = []

# 1. clean control — both pass
rows.append(row("clean_control", clean_out, ""))
# 2. ERROR: on stdout only — THE declared divergence cell
rows.append(row("error_on_stdout", clean_out + ERR + "\n", ""))
# 3. ERROR: on stderr only — both reject (different clauses)
rows.append(row("error_on_stderr", clean_out, ERR + "\n"))
# 4. ERROR: on both — both reject
rows.append(row("error_on_both", clean_out + ERR + "\n", ERR + "\n"))
# 5. signature on stderr only — streams rejects (sig not in stdout), merged passes
rows.append(row("sig_on_stderr", BANNER + "\n", SIG + "\n"))
# 6. sig on stdout, ERROR on stderr, allowlisted — both absorb
rows.append(row("stderr_error_allowlisted", clean_out, ERR + "\n", allowed=(ERR,)))
# 7. stdout ERROR: allowlisted — merged absorbs, streams never sees it
rows.append(row("stdout_error_allowlisted", clean_out + ERR + "\n", "", allowed=(ERR,)))
# 8. stderr ERROR: foreign allowlist — both reject
rows.append(row("stderr_error_foreign_allow", clean_out, ERR + "\n",
                allowed=("ERROR: unrelated different diagnostic",)))
# 9. seam fabrication: stdout tail ends 'ERROR' unterminated, stderr head ': x'
seam_tail = "DESCENDANT_PIPE_SEAMFORGE tail ends in ERROR"
seam_head = ": SEAMFORGE phantom fabricated line"
rows.append(row("seam_fabricated", clean_out + seam_tail, seam_head + "\n"))
# 10. seam where stderr head is EMPTY-allowlisted shape? stderr head allowlisted
rows.append(row("seam_stderr_allowlisted", clean_out + "prefix ERR",
                "OR: fake\n", allowed=("OR: fake",)))
# 11. SCRIPT ERROR: on stdout — both reject (streams scans stdout+stderr for it)
rows.append(row("script_error_stdout", clean_out + "SCRIPT ERROR: boom\n", ""))
# 12. SCRIPT ERROR: seam-split — merged fabricates, streams never sees it
rows.append(row("script_error_seam", clean_out + "tail SCRIPT ERR",
                "OR: split\n", allowed=("OR: split",)))
# 13. Parse Error: on stderr — both reject
rows.append(row("parse_error_stderr", clean_out, "Parse Error: x\n"))
# 14. stderr line that is EMPTY/whitespace — streams skips empty, merged sees it
rows.append(row("stderr_blank_only", clean_out, "\n\n"))
# 15. non-ERROR stderr noise — streams rejects (any non-allowlisted stderr line),
#     merged accepts (no ERROR: token)
rows.append(row("stderr_noise_no_error", clean_out, "random noise line\n"))
# 16. ERROR: token split across newline ON STDERR: "ERR\nOR:" — merged evades,
#     streams rejects on BOTH non-allowlisted lines
rows.append(row("stderr_split_evasion", clean_out, "ERR\nOR: forged\n"))
# 17. comma-prefix allowlist on stderr
rows.append(row("stderr_comma_allow", clean_out, ERR + ", extra\n",
                allowed=(ERR + ",",)))
# 18. stdout SCRIPT ERR + stderr OR: — merged whole-blob sees "SCRIPT ERR\nOR:" nope.
#     correct seam: stdout ends mid-token without newline.
rows.append(row("script_error_true_seam",
                clean_out + "x SCRIPT ERR", "OR: y\n"))
# 19. sig split across seam: stdout tail 'STREAM_STDOUT: expected attr', stderr 'ibution marker'
rows.append(row("sig_seam_fabricated",
                BANNER + "\nSTREAM_STDOUT: expected attr",
                "ibution marker\n"))
# 20. exit-code divergence is impossible (shared clause) — sanity: code=1
rows.append(row("exit_mismatch", clean_out, "", code=1))

print(json.dumps(rows, indent=2))
