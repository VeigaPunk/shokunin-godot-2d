#!/usr/bin/env python3
"""r91 verifier — re-check the saved fresh-arm receipts with the production
stderr rule (multi-line Godot error blocks: one ERROR: line + at:/backtrace
continuation lines; the classifier only counts lines containing ERROR:)."""
import ast
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[4]
V = ROOT / "corpus/live/r91-verifier"
HARNESS = V / "tree/corpus/fixtures/run_battery.py"

tree = ast.parse(HARNESS.read_text())
cases = None
for node in tree.body:
    if isinstance(node, ast.Assign) and any(
            isinstance(t, ast.Name) and t.id == "CASES" for t in node.targets):
        cases = ast.literal_eval(node.value)
nav = {c[0]: c for c in cases if c[0].startswith("nav_lattice_")}

EXPECTED_ERRORS = {
    "nav_lattice_sync": ["ERROR: NavigationServer navigation map query failed because it was made before first map synchronization."],
    "nav_lattice_bake": ["ERROR: The root node needs to be inside the SceneTree."],
}
TAILS = {
    "census": [], "path": ["settle=", "iter="], "query": ["settle=", "iter="],
    "sync": ["dis_same=", "chg_iter_same=", "chg_iter_settled=", "gate=",
             "ladder=", "first_reach=", "first_reach_sync="],
    "region": ["dis_same=", "settle=", "iter="],
    "agent": ["walk_steps=", "reached_at=", "first_reachable="],
    "avoid": ["seq_a=", "seq_b=", "vel_a=", "vel_b=", "sum_max=", "settle="],
    "bake": ["iter_b=", "settle_a=", "settle_b="],
    "link": ["fwd_disabled_same=", "settle=", "iter=", "link_iter="],
    "teardown_crash": [], "teardown_clean": [],
}

bad = 0
total = 0
for name, script, flags, expected_exit, sig in nav.values():
    arm = name.removeprefix("nav_lattice_")
    for rep in (1, 2, 3):
        total += 1
        stem = V / f"arms/{arm}.rep{rep}"
        o = pathlib.Path(str(stem) + ".out").read_text()
        e = pathlib.Path(str(stem) + ".err").read_text()
        rc = pathlib.Path(str(stem) + ".rc").read_text().strip()
        reasons = []
        if rc != str(expected_exit):
            reasons.append(f"rc={rc}!={expected_exit}")
        if sig not in o:
            reasons.append("signature_missing")
        line = next((l for l in o.splitlines() if l.startswith(sig)), None)
        tail = [t.split("=")[0] + "=" for t in line[len(sig):].split() if "=" in t] if line else []
        if any(t not in TAILS[arm] for t in tail):
            reasons.append(f"tail_leak={tail}")
        pass_lines = [l for l in o.splitlines() if l.startswith("PASS nav_lattice")]
        if arm != "teardown_crash" and len(pass_lines) != 1:
            reasons.append(f"pass_lines={len(pass_lines)}")
        err_lines = [l.strip() for l in e.splitlines() if l.strip()]
        error_lines = [l for l in err_lines if "ERROR:" in l]
        want = EXPECTED_ERRORS.get(name, [])
        if error_lines != want:
            reasons.append(f"error_lines={error_lines}")
        if name == "nav_lattice_teardown_crash":
            if "double free or corruption" not in e:
                reasons.append("stderr_fragment_missing")
        if name == "nav_lattice_teardown_clean":
            if e != "":
                reasons.append(f"err_bytes={len(e)}")
        ok = not reasons
        bad += 0 if ok else 1
        print(f"{'OK ' if ok else 'BAD'} {arm}.rep{rep} rc={rc} tail={tail} "
              f"err_nonempty={len(err_lines)} {';'.join(reasons)}")
print(f"\nFRESH-ARMS CHECK: {total - bad}/{total} clean")
