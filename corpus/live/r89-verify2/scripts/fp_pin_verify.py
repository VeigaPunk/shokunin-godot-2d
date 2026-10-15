#!/usr/bin/env python3
# r89-verifier2: independent re-derivation of the F1 forge discrimination on
# the FROZEN 53a0be7 bytes. Extracts classify_process AND the required_stderr
# pin dict from tree/corpus/fixtures/run_battery.py via AST (no hardcoded
# copies), launches each probe under the battery launch shape
# (godot --headless --path proj --script res://<gd> -- --arm=lineempty,
# subprocess.run streams separate), then applies:
#   pre-fold verdict  = classify_process(code, err, stdout+stderr, -6, sig, ())
#   post-fold verdict = pre-fold AND all(frag in stderr) AND any(sig in stdout)
# Expected: folded_lineempty (PASS,PASS); fp_wrongcause (PASS,FAIL);
#           fp_stderr_sig (PASS,FAIL).
import ast
import hashlib
import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent                      # corpus/live/r89-verify2
PROJ = ROOT / "proj"
RB = ROOT / "tree" / "corpus" / "fixtures" / "run_battery.py"
OUT = ROOT / "runs-probe"
OUT.mkdir(exist_ok=True)
EXPECTED_EXIT = -6
SIGNATURE = "R89 lineempty call=offset_polyline(empty,2.0,JOIN_ROUND,END_JOINED)"

src = RB.read_text()
tree = ast.parse(src)

seg = None
pin_dict = None
for node in ast.walk(tree):
    if isinstance(node, ast.FunctionDef) and node.name == "classify_process":
        seg = ast.get_source_segment(src, node)
    if isinstance(node, ast.Assign):
        for t in node.targets:
            if isinstance(t, ast.Name) and t.id == "required_stderr":
                # value is <Dict>.get(name, ()) — take the Dict child
                if isinstance(node.value, ast.Call) and isinstance(
                        node.value.func, ast.Attribute) and node.value.func.attr == "get":
                    pin_dict = ast.literal_eval(node.value.func.value)
assert seg, "classify_process not found"
assert pin_dict is not None, "required_stderr dict not found"
seg_sha = hashlib.sha256(seg.encode()).hexdigest()
print("classify_process segment sha256:", seg_sha)
print("required_stderr pins extracted:", json.dumps(pin_dict))
required = pin_dict["geo2d_lattice_lineempty"]
exec(seg)


def launch(script):
    proc = subprocess.run(
        ["godot", "--headless", "--path", str(PROJ),
         "--script", "res://" + script, "--", "--arm=lineempty"],
        capture_output=True, text=True, timeout=25)
    return proc.stdout, proc.stderr, proc.returncode, None


rows = []
for label, script in (("folded_lineempty", "geo2d_lattice.gd"),
                      ("fp_wrongcause", "fp_wrongcause.gd"),
                      ("fp_stderr_sig", "fp_stderr_sig.gd")):
    so, se, code, error = launch(script)
    (OUT / f"{label}.out").write_text(so)
    (OUT / f"{label}.err").write_text(se)
    (OUT / f"{label}.rc").write_text(str(code) + "\n")
    eff = code if code < 128 else code - 256
    merged = so + se
    bare = classify_process(eff, error, merged, EXPECTED_EXIT, SIGNATURE, ())
    pinned = (bare
              and all(f in se for f in required)
              and SIGNATURE in so)
    rows.append({"probe": label, "shell_rc": code, "python_rc": eff,
                 "sig_on_stdout": SIGNATURE in so,
                 "sig_on_stderr": SIGNATURE in se,
                 "stderr_bytes": len(se.encode()),
                 "frag_clipper2": "Clipper2Lib::Point<double>" in se,
                 "frag_assert": "Assertion '__n < this->size()' failed." in se,
                 "bare_classify": "PASS" if bare else "FAIL",
                 "pinned_classify": "PASS" if pinned else "FAIL"})
    print(json.dumps(rows[-1]))

expected = {"folded_lineempty": ("PASS", "PASS"),
            "fp_wrongcause": ("PASS", "FAIL"),
            "fp_stderr_sig": ("PASS", "FAIL")}
ok = all((r["bare_classify"], r["pinned_classify"]) == expected[r["probe"]]
         for r in rows)
payload = {"classifier_segment_sha256": seg_sha,
           "run_battery_sha256": hashlib.sha256(RB.read_bytes()).hexdigest(),
           "required_stderr": {k: list(v) for k, v in pin_dict.items()},
           "expected": expected, "ok": ok, "rows": rows}
(OUT / "fp_pin_verify.json").write_text(json.dumps(payload, indent=2) + "\n")
print("DISCRIMINATION", "PASS" if ok else "FAIL")
sys.exit(0 if ok else 1)
