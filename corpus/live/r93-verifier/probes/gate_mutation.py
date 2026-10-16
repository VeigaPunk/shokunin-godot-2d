#!/usr/bin/env python3
"""r93 verifier — is the r93 floor gate live?  Mutant run on a scratch copy.

Control = this seat's five real battery reps on the frozen bytes (all report
`r93_expected_errors_all_matched=true`, `dead_entry_count=0`; see
probes/prior-identity.txt).

Mutant = full frozen harness copy + ONE dead r93 expected_errors entry (an
entry that can never match an emitted line).  If the gate is load-bearing it
must flip False while the row itself still PASSes (the allowlist cannot change
a classification; the gate is the only catcher).

Nothing touches the worktree or the frozen extraction: the mutant tree lives
under corpus/live/r93-verifier/gate-probe/.
"""
import json
import pathlib
import shutil
import subprocess
import sys

V = pathlib.Path("/home/vgpnk/Projects/shokunin/game-dev-2d-shokunin/corpus/live/r93-verifier")
FIX = V / "freeze" / "x" / "corpus" / "fixtures"
DEAD = "'r93_tween_census': ('ERROR: r93 verifier dead-entry mutation (never emitted)',),"
ANCHOR = "                'r92_tilemap_physics': (\n                    'ERROR: Parameter \"found\" is null.',\n                ),\n"

root = V / "gate-probe" / "mutant"
if root.exists():
    shutil.rmtree(root)
shutil.copytree(FIX, root)
src = (root / "run_battery.py").read_text()
assert ANCHOR in src, "expected_errors anchor not found"
src = src.replace(ANCHOR, ANCHOR + "                " + DEAD + "\n", 1)
(root / "run_battery.py").write_text(src)

runs = V / "gate-probe" / "mutant-runs"
log = V / "gate-probe" / "mutant.log"
with log.open("w") as fh:
    subprocess.run([sys.executable, str(root / "run_battery.py"), "--godot", "/usr/bin/godot",
                    "--runs", str(runs)], stdout=fh, stderr=subprocess.STDOUT, timeout=900)

verdicts = sorted(runs.glob("*/verdicts.json"))
assert verdicts, "no verdicts.json produced"
d = json.loads(verdicts[-1].read_text())
found = {}


def walk(node):
    if isinstance(node, dict):
        for k, v in node.items():
            if k in ("r93_expected_errors_all_matched", "dead_entries", "dead_entry_count"):
                found[k] = v
            walk(v)
    elif isinstance(node, list):
        for v in node:
            walk(v)


walk(d)
row = next(r for r in d["results"] if r["case"] == "r93_tween_census")
out = [
    f"mutant battery verdict={d['verdict']} rows={len(d['results'])}",
    f"r93_expected_errors_all_matched={found.get('r93_expected_errors_all_matched')}",
    f"dead_entry_count={found.get('dead_entry_count')} dead_entries={found.get('dead_entries')}",
    f"r93_tween_census row verdict={row['verdict']} (allowlist cannot change classification)",
    f"r93 rows pass={sum(1 for r in d['results'] if r['case'].startswith('r93_') and r['verdict'] == 'PASS')}/23",
    f"verdicts={verdicts[-1]} log={log}",
]
(V / "probes" / "gate-mutation.txt").write_text("\n".join(out) + "\n")
print("\n".join(out))
sys.exit(0)
