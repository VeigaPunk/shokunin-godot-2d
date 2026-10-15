#!/usr/bin/env python3
# r89-fold F1 discrimination check: run each probe under the battery launch
# shape (subprocess.run, merged+separate streams) and classify with the
# PRODUCTION classify_process (AST-extracted from corpus/fixtures/run_battery.py)
# AND-ed with the new required_stderr pin predicate (verbatim expression).
import ast
import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
FIXTURES = HERE.parent.parent / "fixtures"
EXPECTED_EXIT = -6
SIGNATURE = "R89 lineempty call=offset_polyline(empty,2.0,JOIN_ROUND,END_JOINED)"
REQUIRED_STDERR = (
    "Clipper2Lib::Point<double>",
    "Assertion '__n < this->size()' failed.",
)

# --- extract production classify_process segment (critic convention) ---
src = (FIXTURES / "run_battery.py").read_text()
tree = ast.parse(src)
seg = None
for node in ast.walk(tree):
    if isinstance(node, ast.FunctionDef) and node.name == "classify_process":
        seg = ast.get_source_segment(src, node)
        break
assert seg, "classify_process not found"
print("classifier segment sha256:", __import__("hashlib").sha256(seg.encode()).hexdigest()[:16])
exec(seg)

def run_streams(script):
    proc = subprocess.run(
        ["godot", "--headless", "--path", str(HERE / "proj"),
         "--script", "res://" + script, "--", "--arm=lineempty"],
        capture_output=True, text=True, timeout=25)
    return proc.stdout, proc.stderr, proc.returncode, None

def pin_predicate(code, error, proc_stdout, proc_stderr, expected_exit, evidence):
    """The production row predicate, post-fold: classify_process on the merged
    blob AND the required_stderr pin block (verbatim semantics)."""
    output = proc_stdout + proc_stderr
    passed = classify_process(code, error, output, expected_exit, evidence, ())
    sigs = evidence if isinstance(evidence, (tuple, list)) else (evidence,)
    passed = (passed
              and all(fragment in proc_stderr for fragment in REQUIRED_STDERR)
              and any(sig in proc_stdout for sig in sigs))
    return passed, output

rows = []
for label, script in (("folded_lineempty", "geo2d_lattice.gd"),
                      ("fp_wrongcause", "fp_wrongcause.gd"),
                      ("fp_stderr_sig", "fp_stderr_sig.gd")):
    so, se, code, error = run_streams(script)
    (HERE / "runs" / f"{label}.out").write_text(so)
    (HERE / "runs" / f"{label}.err").write_text(se)
    (HERE / "runs" / f"{label}.rc").write_text(str(code) + "\n")
    # python convention: signal death -> negative; keep both views
    eff_code = code if code < 128 else code - 256
    bare = classify_process(eff_code, error, so + se, EXPECTED_EXIT, SIGNATURE, ())
    pinned, _ = pin_predicate(eff_code, error, so, se, EXPECTED_EXIT, SIGNATURE)
    rows.append({"probe": label, "script": script, "shell_rc": code,
                 "python_rc": eff_code,
                 "sig_on_stdout": SIGNATURE in so, "sig_on_stderr": SIGNATURE in se,
                 "stderr_bytes": len(se.encode()),
                 "frag_clipper2": "Clipper2Lib::Point<double>" in se,
                 "frag_assert": "Assertion '__n < this->size()' failed." in se,
                 "bare_classify": "PASS" if bare else "FAIL",
                 "pinned_classify": "PASS" if pinned else "FAIL"})
    print(json.dumps(rows[-1]))

expected = {"folded_lineempty": ("PASS", "PASS"),
            "fp_wrongcause": ("PASS", "FAIL"),
            "fp_stderr_sig": ("PASS", "FAIL")}
ok = all((r["bare_classify"], r["pinned_classify"]) == expected[r["probe"]] for r in rows)
payload = {"expected": expected, "ok": ok, "rows": rows}
(HERE / "runs" / "fp_pin_check.json").write_text(json.dumps(payload, indent=2) + "\n")
print("DISCRIMINATION", "PASS" if ok else "FAIL")
sys.exit(0 if ok else 1)
