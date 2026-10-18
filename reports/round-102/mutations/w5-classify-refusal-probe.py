#!/usr/bin/env python3
"""W5 r102 classifier counterfactual on the measured --main-pack refusal bytes.

Extracts classify_process and surface_allowed_error FROM THE COMMITTED
corpus/fixtures/run_battery.py via AST (the module itself is never executed,
per hard rule 1) and runs discriminations on the verbatim refusal capture at
/var/tmp/r102-w5/mp.err (x.x86_64 --headless --main-pack x.pck --quit-after 2).

Usage: python3 reports/round-102/mutations/w5-classify-refusal-probe.py
"""
import ast
import pathlib
import sys

REPO = pathlib.Path(__file__).resolve().parents[3]
SRC = REPO / "corpus/fixtures/run_battery.py"
REFUSAL = pathlib.Path("/var/tmp/r102-w5/mp.err")

tree = ast.parse(SRC.read_text())


def extract(name):
    node = next(n for n in ast.walk(tree)
                if isinstance(n, ast.FunctionDef) and n.name == name)
    mod = ast.Module(body=[node], type_ignores=[])
    ast.fix_missing_locations(mod)
    ns = {}
    exec(compile(mod, f"{SRC}:{name}", "exec"), ns)
    return ns[name]


classify_process = extract("classify_process")
surface_allowed_error = extract("surface_allowed_error")

refusal = REFUSAL.read_text()
lines = refusal.splitlines(keepends=True)
first = lines[0].strip()
sig = "PASS export_launch_mainpack_refusal rc=1"
row_output = refusal + sig + "\n"   # fixture-style receipt appended to echoed child stderr
stripped = refusal.replace(lines[0], "")   # sole-cause counterfactual: remove the ERROR line
at_line = next((l.strip() for l in lines if l.strip().startswith("at:")), None)

print(f"refusal_bytes={len(refusal)} refusal_lines={len(lines)}")
print(f"line0={first!r}")
print(f"at_line={at_line!r}")

entry_exact = first                       # measured first line, verbatim
entry_comma = first + ","

d = {
    "A_empty_allowlist_rejects_refusal_row":
        classify_process(1, None, row_output, 1, sig, ()) is False,
    "B_exact_entry_absorbs_refusal_row":
        classify_process(1, None, row_output, 1, sig, (entry_exact,)) is True,
    # Measured: the comma-prefix shape needs the live line to CONTINUE past the
    # comma, so a comma entry for this complete line absorbs nothing (would be
    # dead_in_run under the census) — C2 shows where the shape does match.
    "C_comma_prefix_entry_does_not_absorb_complete_line":
        classify_process(1, None, row_output, 1, sig, (entry_comma,)) is False,
    # Shape semantics only: comma entries match lines that CONTINUE past the
    # comma; the refusal line has no comma, so no comma-form entry can absorb it.
    "C2_comma_shape_matches_only_lines_continuing_past_comma":
        classify_process(1, None, "ERROR: SYNTH_PREFIX, detail\n" + sig + "\n", 1,
                         sig, ("ERROR: SYNTH_PREFIX,",)) is True,
    "D_entry_does_not_forgive_wrong_exit":
        classify_process(0, None, row_output, 1, sig, (entry_exact,)) is False,
    "E_entry_does_not_forgive_missing_signature":
        classify_process(1, None, row_output, 1, "SIG_ABSENT", (entry_exact,)) is False,
    "F_sole_cause_stripped_error_line_passes_empty_allowlist":
        classify_process(1, None, stripped + sig + "\n", 1, sig, ()) is True,
    "G_at_line_is_verdict_inert":
        classify_process(1, None, sig + "\n" + at_line + "\n", 1, sig, ()) is True,
    "H_census_entry_matches_live_line_exact":
        len([l for l in row_output.splitlines() if surface_allowed_error(l, entry_exact)]) == 1,
    "I_census_entry_dead_on_stripped_counterfactual":
        len([l for l in (stripped + sig + "\n").splitlines()
             if surface_allowed_error(l, entry_exact)]) == 0,
}
for k, v in d.items():
    print(f"{'PASS' if v else 'FAIL'} {k}")
print("all_pass =", all(d.values()))
sys.exit(0 if all(d.values()) else 1)
