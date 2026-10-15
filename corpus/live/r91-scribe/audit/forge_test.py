#!/usr/bin/env python3
"""r91-scribe: is the nav_lattice_teardown_crash binding load-bearing?

The production classifier and the row's expected_errors/required_stderr pins are
AST-extracted from the COMMITTED harness; the receipts are this seat's fresh
launch. Four synthetic variants are classified against the row's real pins:
  A. genuine receipt (rc=-6, stdout marker, glibc stderr fragment)   -> must PASS
  B. rc=-6, stdout marker, stderr stripped (no fragment)             -> must FAIL
  C. rc=-6, stderr fragment, stdout anchor removed                   -> must FAIL
  D. rc=0, stdout marker, stderr fragment (wrong exit class)         -> must FAIL
"""
import ast, json
from pathlib import Path
ROOT = Path("/home/vgpnk/Projects/shokunin/game-dev-2d-shokunin")
src = (ROOT / "corpus/fixtures/run_battery.py").read_text()
tree = ast.parse(src)

want = {"classify_process", "classify_streams"}
fns = {}
for node in ast.walk(tree):
    if isinstance(node, ast.FunctionDef) and node.name in want:
        mod = ast.Module(body=[node], type_ignores=[])
        ns = {}
        exec(compile(ast.fix_missing_locations(mod), "<extracted>", "exec"), ns)
        fns[node.name] = ns[node.name]

bat = ast.parse(src)
cases = next(n for n in bat.body if isinstance(n, ast.Assign)
             and any(getattr(t, "id", "") == "CASES" for t in n.targets)).value.elts
row = next(e for e in cases if e.elts[0].value == "nav_lattice_teardown_crash")
sig = row.elts[4].value
expected_exit = ast.literal_eval(row.elts[3])
allowed = ('ERROR: NavigationServer navigation map query failed because it was made before first map synchronization.',)  # unrelated to this row
required = ('double free or corruption',)

fresh = ROOT / "corpus/live/r91-scribe/fresh"
out = (fresh / "teardown_crash.out").read_text()
err = (fresh / "teardown_crash.err").read_text()
# the battery launch shape has no `timeout` wrapper; strip the wrapper line so
# variant A is the exact battery stream pair.
err_battery = "\n".join(l for l in err.splitlines() if not l.startswith("timeout: "))
rc = -6

def classify(code, stdout, stderr):
    merged = stdout + stderr
    ok = fns["classify_process"](code, None, merged, expected_exit, sig, allowed)
    if required:
        ok = ok and all(f in stderr for f in required) and sig in stdout
    return ok

variants = {
    "A_genuine_rc-6_marker_fragment": classify(rc, out, err_battery),
    "B_stderr_stripped": classify(rc, out, ""),
    "C_stdout_anchor_removed": classify(rc, "", err_battery),
    "D_wrong_exit_class_rc0": classify(0, out, err_battery),
    "E_fragment_only_in_merged_but_not_stderr": classify(rc, out + required[0], ""),
}
print(json.dumps(variants, indent=1))
expect = {"A_genuine_rc-6_marker_fragment": True, "B_stderr_stripped": False,
          "C_stdout_anchor_removed": False, "D_wrong_exit_class_rc0": False,
          "E_fragment_only_in_merged_but_not_stderr": False}
print("LOAD_BEARING:", all(variants[k] == v for k, v in expect.items()))
print("stderr bytes (fresh, incl. timeout wrapper):", len(err), "| battery-shape:", len(err_battery))
