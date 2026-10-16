#!/usr/bin/env python3
"""r94 scribe — pre-existing classifier properties probed on the landed rows.

For each of the 19 landed signatures, with a real landed-fixture receipt:
  (1) trailing token appended AFTER the pin on the same line   -> production verdict?
  (2) PASS line delivered on stderr only (stdout otherwise same) -> production verdict?
  (3) control: signature removed from stdout                    -> must reject
These characterise the merged-blob substring classifier battery-wide (r89-fold
critic F1 closed them only for required_stderr rows); the r94 rows are
required_stderr-less, so both shapes are reachable only by a forged process.

Writes corpus/live/r94-scribe/audit/classifier_properties.json.
"""
import ast
import hashlib
import json
import subprocess
from pathlib import Path

REPO = Path("/home/vgpnk/Projects/shokunin/game-dev-2d-shokunin")
OUT = REPO / "corpus/live/r94-scribe/audit"

src = subprocess.run(["git", "show", "HEAD:corpus/fixtures/run_battery.py"],
                     cwd=REPO, capture_output=True).stdout.decode()
tree = ast.parse(src)
fn_src = next(ast.get_source_segment(src, n) for n in ast.walk(tree)
              if isinstance(n, ast.FunctionDef) and n.name == "classify_process")
ns = {}
exec("import re\n" + fn_src, ns)
classify = ns["classify_process"]

cases = next(n.value for n in ast.walk(tree)
             if isinstance(n, ast.Assign) and getattr(n.targets[0], "id", "") == "CASES")
rows = {t[0]: t for t in (ast.literal_eval(e) for e in cases.elts) if t[0].startswith("r94_")}

res = {"segment_sha256": hashlib.sha256(fn_src.encode()).hexdigest(), "rows": {}}
for name, (_, script, flags, exitc, sig) in sorted(rows.items()):
    arm = flags[0].split("=", 1)[1]
    f = next((REPO / "corpus/live/r94-scribe/fresh").glob(f"*.{arm}.default.rep1.out"))
    text = f.read_text()
    assert sig in text
    idx = text.find(sig)
    # (1) trailing token after the pin
    t1 = text[:idx + len(sig)] + " extra=1" + text[idx + len(sig):]
    # (2) PASS line moved to stderr: stdout without the PASS line, stderr with it
    lines = text.splitlines()
    pass_line = next(l for l in lines if l.startswith("PASS particles_lattice"))
    stdout_only = "\n".join(l for l in lines if l is not pass_line)
    stderr_only = pass_line + "\n"
    # (3) control: signature destroyed (last char corrupted)
    t3 = text.replace(sig, sig[:-1] + "X", 1)
    res["rows"][name] = {
        "trailing_token_accepted": classify(exitc, None, t1, exitc, sig, ()),
        "stderr_only_accepted": classify(exitc, None, stdout_only + stderr_only, exitc, sig, ()),
        "control_signature_removed_rejected": not classify(exitc, None, t3, exitc, sig, ()),
    }
res["summary"] = {
    "trailing_token_accepted": sum(1 for v in res["rows"].values() if v["trailing_token_accepted"]),
    "stderr_only_accepted": sum(1 for v in res["rows"].values() if v["stderr_only_accepted"]),
    "control_rejected": sum(1 for v in res["rows"].values() if v["control_signature_removed_rejected"]),
    "rows": len(res["rows"]),
}
(OUT / "classifier_properties.json").write_text(json.dumps(res, indent=2) + "\n")
print(json.dumps(res["summary"], indent=1))
