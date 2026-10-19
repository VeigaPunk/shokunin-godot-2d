#!/usr/bin/env python3
"""r104-X2 C2a — PASS-prefix census tightening measurement.

Loads the AST-extracted gate (side-effect-free), then for every stored run:
  * baseline: receipt_shape_audit (gate's own `startswith("PASS ")` census)
  * tightened: same gate with the pass-line census widened to all PASS-prefixed lines
    (line.startswith("PASS")) — measured by monkeypatching a widened variant.
Reports per-run flag deltas and per-line false-positive analysis.
"""
import importlib.util, json, glob, os, sys
from pathlib import Path

spec = importlib.util.spec_from_file_location("g", "/var/tmp/r104-X2/gate_extract.py")
G = importlib.util.module_from_spec(spec); spec.loader.exec_module(G)

REPO = Path("/home/vgpnk/Projects/shokunin/game-dev-2d-shokunin")
runs = sorted(glob.glob(str(REPO / "corpus/live/runs/*/verdicts.json")))
print("runs:", len(runs))
for p in runs:
    raw = Path(p).read_bytes()
    import hashlib
    sha = hashlib.sha256(raw).hexdigest()[:16]
    d = json.loads(raw)
    rows = d["results"]
    audit = G.receipt_shape_audit(rows)
    # tightened census: count PASS-prefixed-but-not-"PASS " lines per audited row
    nonstd = []
    for r in rows:
        if r.get("verdict") != "PASS": continue
        o = r.get("output")
        if not isinstance(o, list): continue
        for ln in o:
            if isinstance(ln, str) and ln.startswith("PASS") and not ln.startswith("PASS "):
                nonstd.append((r.get("case"), repr(ln[:60])))
    print(f"{os.path.basename(os.path.dirname(p))} sha={sha} rows={len(rows)} "
          f"audited={audit['audited']} flags={len(audit['flags'])} "
          f"nonstd_pass_prefixed={len(nonstd)}")
    for c, l in nonstd[:5]:
        print("    NONSTD", c, l)
