#!/usr/bin/env python3
"""r68 simplifier: mirror-fidelity truth table.
AST-extract the REAL nested matchers (allowed_error inside classify_process,
line_allowed inside classify_streams) and the r68 mirrors
(sd_merged_line_allowed / sd_stream_line_allowed) from the landed
run_battery.py, exec standalone, compare verdicts over a (line, entry)
matrix. Receipt for "the mirrors are faithful, not driftable copies"."""
import ast, sys
src = open('corpus/fixtures/run_battery.py').read()
tree = ast.parse(src)
fns = {}
for node in ast.walk(tree):
    if isinstance(node, ast.FunctionDef):
        fns.setdefault(node.name, []).append(node)
ae = fns['allowed_error'][0]
la = fns['line_allowed'][0]
sml = fns['sd_merged_line_allowed'][0]
ssl = fns['sd_stream_line_allowed'][0]
ns = {}
for name, fn in [('allowed_error', ae), ('sd_merged_line_allowed', sml),
                 ('sd_stream_line_allowed', ssl)]:
    exec(compile(ast.Module(body=[fn], type_ignores=[]), '<ast>', 'exec'), ns)
la_src = ast.unparse(la)
ns2 = {}
exec("def make_line_allowed(allowed):\n    allowed = set(allowed)\n"
     + "\n".join("    " + l for l in la_src.splitlines())
     + "\n    return line_allowed", ns2)
real_merged = ns['allowed_error']
real_stream_factory = ns2['make_line_allowed']
mir_merged = ns['sd_merged_line_allowed']
mir_stream = ns['sd_stream_line_allowed']
ENTRIES = [
    "ERROR: SAVE EXPECTED NEGATIVE: malformed JSON rejected signature=JSON_PARSE_ERROR",
    "ERROR: SAVE PROCESS EXPECTED NEGATIVE: missing file rejected signature=FILE_NOT_FOUND,",
    "ERROR: chain incomplete",
    "STREAM_STDERR: unrelated attribution diagnostic",
    ": STREAMDIV seam phantom merged-only line",
    "marker",
]
LINES = [
    "ERROR: SAVE EXPECTED NEGATIVE: malformed JSON rejected signature=JSON_PARSE_ERROR",
    "ERROR: SAVE EXPECTED NEGATIVE: malformed JSON rejected signature=JSON_PARSE_ERROR EXTRA",
    "ERROR: SAVE PROCESS EXPECTED NEGATIVE: missing file rejected signature=FILE_NOT_FOUND, path=/tmp/x",
    "ERROR: SAVE PROCESS EXPECTED NEGATIVE: missing file rejected signature=FILE_NOT_FOUND, a ERROR: b",
    "ERROR: chain incomplete collections=1 scene=SceneB:<Node#7> old_alive=false",
    "ERROR: chain incomplete",
    "ERROR: chain incomplete collections=1 scene=SceneB:<Node#7>",
    "  ERROR: chain incomplete collections=streamdiv scene=SceneB:<Node#6700> old_alive=false  ",
    "random stderr chatter",
    "ERROR: STREAMDIV stderr-carried diagnostic",
    "",
]
mism = []
for e in ENTRIES:
    rsf = real_stream_factory((e,))
    for l in LINES:
        r = real_merged(l, e); m = mir_merged(l, e)
        if r != m:
            mism.append(('merged', e, l, r, m))
        rs = rsf(l.strip()); ms = mir_stream(l.strip(), (e,))
        if rs != ms:
            mism.append(('stream', e, l, rs, ms))
print('merged cells:', len(ENTRIES)*len(LINES), 'stream cells:', len(ENTRIES)*len(LINES))
print('MISMATCHES:', len(mism))
for x in mism: print(' ', x)
sys.exit(1 if mism else 0)
