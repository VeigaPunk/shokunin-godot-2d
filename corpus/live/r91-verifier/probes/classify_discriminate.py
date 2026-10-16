#!/usr/bin/env python3
"""r91 verifier — production-classifier discrimination on the fresh receipts.

The classifier is AST-extracted from the committed harness (same technique the
author/scout used), not re-implemented: classify_process is a nested function
inside main(), so its source segment is exec'd here.
"""
import ast
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[4]
V = ROOT / "corpus/live/r91-verifier"
HARNESS = V / "tree/corpus/fixtures/run_battery.py"

src = HARNESS.read_text()
tree = ast.parse(src)

ns = {}
for node in ast.walk(tree):
    if isinstance(node, ast.FunctionDef) and node.name in ("classify_process", "classify_streams"):
        seg = ast.get_source_segment(src, node)
        exec(seg, ns)
classify_process = ns["classify_process"]
classify_streams = ns["classify_streams"]
print("extracted:", [n for n in ns if n.startswith("classify")])

cases = None
for node in tree.body:
    if isinstance(node, ast.Assign) and any(
            isinstance(t, ast.Name) and t.id == "CASES" for t in node.targets):
        cases = ast.literal_eval(node.value)
nav = {c[0]: c for c in cases if c[0].startswith("nav_lattice_")}

EXPECTED_ERRORS = {
    "nav_lattice_sync": ("ERROR: NavigationServer navigation map query failed because it was made before first map synchronization.",),
    "nav_lattice_bake": ("ERROR: The node needs to be inside the SceneTree.",),  # deliberate wrong entry probe below
}
EXPECTED_ERRORS_CORRECT = {
    "nav_lattice_sync": ("ERROR: NavigationServer navigation map query failed because it was made before first map synchronization.",),
    "nav_lattice_bake": ("ERROR: The root node needs to be inside the SceneTree.",),
}

for name, script, flags, expected_exit, sig in nav.values():
    arm = name.removeprefix("nav_lattice_")
    for rep in (1, 2, 3):
        stem = str(V / f"arms/{arm}.rep{rep}")
        out = pathlib.Path(stem + ".out").read_text()
        err = pathlib.Path(stem + ".err").read_text()
        rc = int(pathlib.Path(stem + ".rc").read_text().strip())
        merged = out + err
        allow = EXPECTED_ERRORS_CORRECT.get(name, ())
        bare = classify_process(rc, None, merged, expected_exit, sig, ())
        allow_v = classify_process(rc, None, merged, expected_exit, sig, allow)
        if name == "nav_lattice_teardown_crash":
            row = (classify_process(rc, None, merged, expected_exit, sig, ())
                   and "double free or corruption" in err and sig in out)
            no_frag = (classify_process(rc, None, merged, expected_exit, sig, ())
                       and "double free or corruption" in out and sig in out)  # fragment spoofed onto stdout only
            no_sig_stdout = (classify_process(rc, None, merged, expected_exit, sig, ())
                             and "double free or corruption" in err and sig in err)
            print(f"  {arm}.rep{rep}: row={row} spoof_fragment_on_stdout={no_frag} "
                  f"sig_on_stderr_only={no_sig_stdout} streams_bare={classify_streams(rc, None, out, err, expected_exit, sig, ())} "
                  f"streams_allow={classify_streams(rc, None, out, err, expected_exit, sig, ('double free or corruption',))}")
        else:
            print(f"  {arm}.rep{rep}: bare={bare} allowlist={allow_v}")
