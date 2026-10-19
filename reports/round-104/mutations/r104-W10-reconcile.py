#!/usr/bin/env python3
"""r104 W10 — G1/S0 semantic reconciliation proof.

G1 closes the tab-PASS census class; S0's stored catalogue still declares the
two tab shapes (s4a, s4d) as ACCOUNTED-SILENT (expected_reasons == ()).  The
patches are textually compatible but the combined tree's probe FAILs with
`shape_class_drift` on both.  This script performs the minimal re-declaration
(replacing the empty expected set with the observed exact reason set) and
proves the combined tree goes green.
"""
import glob
import importlib.util
import json
from pathlib import Path

RB = Path("/var/tmp/r104-W10/realtest/corpus/fixtures/run_battery.py")
OUT = RB.parent / "run_battery_corrected.py"
BS = "\\"  # the catalogue carries the two-character escape, not a tab byte

EDITS = [
    # (exact old line, exact new line)
    ('     (("append", None, "' + BS + 'tPASS forged=true"),), ()),\n',
     '     (("append", None, "' + BS + 'tPASS forged=true"),),\n'
     '     ("pass_line_separator", "unaccounted_pass_lines")),\n'),
    ('     (("append", None, "PASS' + BS + 'tforged=true"),), ()),\n',
     '     (("append", None, "PASS' + BS + 'tforged=true"),),\n'
     '     ("pass_line_separator", "unaccounted_pass_lines")),\n'),
]

text = RB.read_text()
for old, new in EDITS:
    assert text.count(old) == 1, (text.count(old), old)
    text = text.replace(old, new)
# G1's own code already emits `pass_line_separator` once; the two catalogue
# re-declarations make three.
assert text.count("pass_line_separator") == 3, text.count("pass_line_separator")
OUT.write_text(text)
compile(text, str(OUT), "exec")


def load(p, n):
    s = importlib.util.spec_from_file_location(n, p)
    m = importlib.util.module_from_spec(s)
    s.loader.exec_module(m)
    return m


mod = load(OUT, "corrected")
runs = sorted(glob.glob("/home/vgpnk/Projects/shokunin/game-dev-2d-shokunin"
                        "/corpus/live/runs/*/verdicts.json"))
run = runs[-1]
rows = json.loads(Path(run).read_text())["results"]
res = mod.gate_evasion_replay(rows)
print("CORRECTED probe on %s: shapes=%d controls=%d skipped=%d flags=%d"
      % (Path(run).parent.name, len(res["shapes"]), len(res["controls"]),
         len(res["skipped"]), len(res["flags"])))
for f in res["flags"]:
    print("  REMAINING FLAG:", json.dumps(f)[:140])
print("probe verdict:", "PASS" if not res["flags"] else "FAIL")
print()
for sh in res["shapes"]:
    print("  %-42s expected=%-46s flagged=%s"
          % (sh["shape"], str(sh["expected_reasons"]), sh["flagged"]))

print("\n-- gate_evasion_replay over every stored run --")
for r in runs:
    rows_r = json.loads(Path(r).read_text())["results"]
    res_r = mod.gate_evasion_replay(rows_r)
    aud = mod.receipt_shape_audit(rows_r)
    print("  %-28s shapes=%-3d skipped=%-3d probe_flags=%-3d audit_flags=%d"
          % (Path(r).parent.name, len(res_r["shapes"]), len(res_r["skipped"]),
             len(res_r["flags"]), len(aud["flags"])))
