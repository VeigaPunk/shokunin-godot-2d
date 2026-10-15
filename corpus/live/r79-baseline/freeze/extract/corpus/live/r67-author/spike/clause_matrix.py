#!/usr/bin/env python3
"""r67 bounded spike: extract classify_process + classify_streams verbatim from
run_battery.py via ast.get_source_segment, exec them, and run the synthetic
stream-attribution matrix through BOTH classifiers on identical stream pairs."""
import ast
import json
import sys
from pathlib import Path

SRC = Path(sys.argv[1] if len(sys.argv) > 1 else
           "corpus/fixtures/run_battery.py").read_text()
tree = ast.parse(SRC)
funcs = {}
for node in ast.walk(tree):
    if isinstance(node, ast.FunctionDef) and node.name in (
            "classify_process", "classify_streams"):
        funcs[node.name] = ast.get_source_segment(SRC, node)
assert set(funcs) == {"classify_process", "classify_streams"}, funcs.keys()
ns = {}
exec(funcs["classify_process"], ns)
exec(funcs["classify_streams"], ns)
classify_process = ns["classify_process"]
classify_streams = ns["classify_streams"]

S = "STREAM_STDOUT: expected attribution marker"
STRUCT = ("ERROR: chain incomplete collections=z scene=SceneB:<Node#9> "
          "old_alive=false")

ARMS = [
    # (name, stdout, stderr, merged_allowed, stream_allowed)
    ("stdout_error_bare", S + "\nERROR: X diag\n", "", (), ()),
    ("stderr_error_bare", S + "\n", "ERROR: Y diag\n", (), ()),
    ("stderr_error_exact", S + "\n", "ERROR: Y diag\n",
     ("ERROR: Y diag",), ("ERROR: Y diag",)),
    ("stderr_error_foreign", S + "\n", "ERROR: Y diag\n",
     ("ERROR: foreign",), ("ERROR: foreign",)),
    ("stderr_structured_entry", S + "\n", STRUCT + "\n",
     ("ERROR: chain incomplete",), ("ERROR: chain incomplete",)),
    ("stderr_structured_exactline", S + "\n", STRUCT + "\n",
     (STRUCT,), (STRUCT,)),
    ("stderr_structured_bare", S + "\n", STRUCT + "\n", (), ()),
    ("sig_on_stderr_bare", "", S + "\n", (), ()),
    ("sig_on_stderr_allowlisted", "", S + "\n", (), (S,)),
    ("seam_error_head_allowlisted", S + "\ntail ends in ERROR",
     ": phantom seam line\n", (), (": phantom seam line",)),
    ("seam_error_bare", S + "\ntail ends in ERROR",
     ": phantom seam line\n", (), ()),
    ("seam_script_head_allowlisted", S + "\ntail ends in SCRIPT ERR",
     "OR: blob\n", (), ("OR: blob",)),
    ("seam_sig_head_allowlisted", "STREAM_STDOUT: expected attribution ",
     "marker\n", (), ("marker",)),
    ("plain_stderr_nonerror", S + "\n",
     "STREAM_STDERR: unrelated attribution diagnostic\n", (), ()),
]

rows = []
for name, so, se, ma, sa in ARMS:
    merged = classify_process(0, None, so + se, 0, S, ma)
    streams = classify_streams(0, None, so, se, 0, S, sa)
    rows.append({"arm": name, "merged_allowed": list(ma),
                 "stream_allowed": list(sa),
                 "merged": merged, "streams": streams,
                 "divergent": merged != streams})
    print(f"{name:34s} merged={merged!s:5s} streams={streams!s:5s} "
          f"divergent={merged != streams}")

print("\ndivergent:", [r["arm"] for r in rows if r["divergent"]])
print("concordant:", [r["arm"] for r in rows if not r["divergent"]])
Path(sys.argv[2] if len(sys.argv) > 2 else
     "corpus/live/r67-author/spike/clause-matrix.json").write_text(
    json.dumps({"source_sha_note": "ast-extracted verbatim clauses",
                "arms": rows}, indent=2) + "\n")
