#!/usr/bin/env python3
"""Per-row emitted-payload stability for the 52 r95 rows across battery runs.

For each run, find the emitted line containing the committed signature; count
distinct full lines and distinct pinned blocks per row across runs.
"""
import importlib.util
import json
import sys
from collections import defaultdict
from pathlib import Path

V = Path("/home/vgpnk/Projects/shokunin/game-dev-2d-shokunin/corpus/live/r95-verifier")
spec = importlib.util.spec_from_file_location("m", V / "freeze/corpus/fixtures/run_battery.py")
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)
SIG = {c[0]: c[4] for c in m.CASES if c[0].startswith(("dss_lattice_", "r95b_order_"))}

runs = [Path(p) for p in sys.argv[1:]]
lines = defaultdict(set)
verdicts = defaultdict(set)
for run in runs:
    d = json.loads((run / "verdicts.json").read_text())
    for r in d["results"]:
        if r["case"] in SIG:
            sig = SIG[r["case"]]
            verdicts[r["case"]].add(r["verdict"])
            hit = next((l for l in r["output"] if sig in l), None)
            lines[r["case"]].add(hit)

out = {
    "runs": [r.name for r in runs],
    "rows": len(SIG),
    "rows_with_mixed_verdicts": sorted(c for c, v in verdicts.items() if len(v) > 1),
    "rows_with_multiple_emitted_lines": {c: len(v) for c, v in lines.items() if len(v) > 1},
    "rows_with_zero_emitted_lines": sorted(c for c, v in lines.items() if None in v),
}
print(json.dumps(out, indent=2))
