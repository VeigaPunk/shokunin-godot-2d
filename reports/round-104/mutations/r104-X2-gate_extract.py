#!/usr/bin/env python3
"""r104-X2 — AST-extract the receipt-shape gate from run_battery.py into scratch.

run_battery.py is NEVER imported or executed (hard rule 1). We parse its source,
keep only the module-level assignments + the named functions the gate needs, and
write a side-effect-free module under /var/tmp/r104-X2/.
"""
import ast, sys
from pathlib import Path

SRC = Path("corpus/fixtures/run_battery.py")
DEST = Path("/var/tmp/r104-X2/gate_extract.py")
WANT_FUNCS = {"receipt_shape_flag", "receipt_shape_audit", "receipt_allowed_error"}
WANT_NAMES = {"CASES", "CASES_SIG_BY_CASE", "RECEIPT_SHAPE_DERIVED_EVIDENCE",
              "RECEIPT_MULTI_PASS_GRAMMAR", "RECEIPT_ANCHOR_MULTIPLICITY",
              "RECEIPT_BANNER_RE", "RECEIPT_DIAG_RE", "RECEIPT_SEQ_RE",
              "RECEIPT_PROGRESS_RE", "RECEIPT_ANSI_ONLY_RE"}

src = SRC.read_text()
tree = ast.parse(src)
keep = []
for node in tree.body:
    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name in WANT_FUNCS:
        keep.append(node)
    elif isinstance(node, ast.Assign):
        for t in node.targets:
            if isinstance(t, ast.Name) and t.id in WANT_NAMES:
                keep.append(node)
    elif isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name) and node.target.id in WANT_NAMES:
        keep.append(node)

mod = ast.Module(body=keep, type_ignores=[])
ast.fix_missing_locations(mod)
hdr = ("# r104-X2 AST extraction from corpus/fixtures/run_battery.py\n"
       "import re\n"
       "from pathlib import Path\n")
DEST.write_text(hdr + ast.unparse(mod) + "\n")
print("WROTE", DEST, DEST.stat().st_size, "bytes")
print("kept:", [getattr(n, 'name', getattr(n.targets[0], 'id', '?')) for n in keep])
