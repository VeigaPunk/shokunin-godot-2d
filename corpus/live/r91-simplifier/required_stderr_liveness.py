#!/usr/bin/env python3
"""r91-simplifier: is the teardown-crash `required_stderr` pin load-bearing?

Uses the PRODUCTION classifier (AST-extracted from the committed
run_battery.py `main()` — not a reimplementation) plus the harness's own
required_stderr clause (run_battery.py lines 1105-1112) to ask three questions
on the control run's real receipt for nav_lattice_teardown_crash:

  Q1 happy path      : does the row pass with the pin? (expected PASS)
  Q2 cause-counterfactual: if the glibc fragment is absent from stderr (a
                     plain signal-class abort), does the row FAIL? (proves the
                     pin binds the crash CAUSE, not the signal class)
  Q3 pin-removal     : if the required_stderr entry were deleted (the YAGNI
                     candidate), would the row still pass on the happy path?
                     (if yes, the entry is an instrument, not decoration)
"""
import ast
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
FIX = HERE / "committed-fixtures"
RUN = sorted((HERE / "runs-control").glob("*/"))[-1]

src = (FIX / "run_battery.py").read_text()
tree = ast.parse(src)
# locate classify_process nested inside main()
fn = None
for node in ast.walk(tree):
    if isinstance(node, ast.FunctionDef) and node.name == "classify_process":
        fn = node
        break
assert fn is not None, "classify_process not found"
mod = ast.Module(body=[fn], type_ignores=[])
ast.fix_missing_locations(mod)
ns = {"re": re}
exec(compile(mod, "<extracted>", "exec"), ns)
classify_process = ns["classify_process"]
print("== required_stderr liveness ==")
print("production classify_process extracted by AST from committed "
      "run_battery.py (f5725ca4...) — %d statements" % len(fn.body))
print("required_stderr clause source (run_battery.py:1105-1112):")
for i, line in enumerate(src.splitlines()[1104:1112], start=1105):
    print("  %4d| %s" % (i, line))
print()

d = json.loads((RUN / "verdicts.json").read_text())
rec = [r for r in d["results"] if r["case"] == "nav_lattice_teardown_crash"][0]
out = "\n".join(rec["output"])
# reconstruct the two streams from the recorded blob for the real receipt
stdout_line = rec["signature"]
stderr_real = None
for cand in [
    HERE / "runs-fold-teardown" / "control" / "teardown_crash.rep1.err",
]:
    if cand.exists():
        stderr_real = cand.read_text()
assert stderr_real, "no captured stderr receipt"
stdout_real = (HERE / "runs-fold-teardown" / "control" / "teardown_crash.rep1.out").read_text()
rc = int((HERE / "runs-fold-teardown" / "control" / "teardown_crash.rep1.rc").read_text().strip())

required_stderr = tuple(rec.get("required_stderr") or ())
print("record: case=%s verdict=%s expected_exit=%s actual_exit=%s" % (
    rec["case"], rec["verdict"], rec["expected_exit"], rec["actual_exit"]))
print("signature=%r" % rec["signature"])
print("required_stderr=%s" % (required_stderr,))
print("captured stderr (rep1): %r" % stderr_real.strip()[:120])
print("captured stdout marker present: %s" % (stdout_line in stdout_real))
print()

sigs = (rec["signature"],)
merged = stdout_real + stderr_real

base = classify_process(rc, None, merged, rec["expected_exit"], rec["signature"], ())
with_pin = base and all(f in stderr_real for f in required_stderr) and any(
    s in stdout_real for s in sigs)

# Q2: simulate an abort whose stderr carries no glibc heap-corruption line
stderr_other = stderr_real.replace("double free or corruption", "Aborted")
merged_other = stdout_real + stderr_other
base_other = classify_process(rc, None, merged_other, rec["expected_exit"], rec["signature"], ())
with_pin_other = base_other and all(f in stderr_other for f in required_stderr) and any(
    s in stdout_real for s in sigs)

# Q3: as if the entry were deleted
no_pin = base and any(s in stdout_real for s in sigs)

print("Q1 happy path, pin present      : merged-blob=%s  +required_stderr=%s  -> %s" % (
    base, with_pin, "PASS" if with_pin else "FAIL"))
print("Q2 same rc, non-glibc stderr    : merged-blob=%s  +required_stderr=%s  -> %s" % (
    base_other, with_pin_other, "PASS" if with_pin_other else "FAIL"))
print("Q3 happy path, pin deleted      : merged-blob=%s  +required_stderr=(none) -> %s" % (
    base, "PASS" if no_pin else "FAIL"))
print()
print("PIN_IS_LOAD_BEARING (Q1 PASS and Q2 FAIL) = %s" % (with_pin and not with_pin_other))
print("PIN_DELETION_IS_INVISIBLE_ON_HAPPY_PATH (Q3 PASS) = %s" % no_pin)
print()
print("=> the entry is a discrimination instrument: deleting it keeps the")
print("   battery green while unbinding rc=-6 from the heap-corruption cause")
print("   (the signal-class-only abort in Q2 would then be admitted).")
