#!/usr/bin/env python3
"""r91 verifier — fresh-arm reps on the frozen committed bytes.

Launch shape mirrors the battery's `execute()`: godot --headless --path <proj>
--script res://nav_lattice.gd -- --arm=<a>, stdout/stderr kept separate.
Shell-bounded (`timeout -s KILL 15`) plus a Python-side bound.

Writes receipts to corpus/live/r91-verifier/arms/ and prints a machine summary
to stdout (also saved by the caller).
"""
import ast
import json
import pathlib
import re
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parents[4]
V = ROOT / "corpus/live/r91-verifier"
TREE = V / "tree"
PROJ = V / "arms/proj"
HARNESS = TREE / "corpus/fixtures/run_battery.py"
ARMS_DIR = V / "arms"

REPS = int(sys.argv[1]) if len(sys.argv) > 1 else 3

TAIL_FIELDS = {
    "census": [],
    "path": ["settle=", "iter="],
    "query": ["settle=", "iter="],
    "sync": ["dis_same=", "chg_iter_same=", "chg_iter_settled=", "gate=",
             "ladder=", "first_reach=", "first_reach_sync="],
    "region": ["dis_same=", "settle=", "iter="],
    "agent": ["walk_steps=", "reached_at=", "first_reachable="],
    "avoid": ["seq_a=", "seq_b=", "vel_a=", "vel_b=", "sum_max=", "settle="],
    "bake": ["iter_b=", "settle_a=", "settle_b="],
    "link": ["fwd_disabled_same=", "settle=", "iter=", "link_iter="],
    "teardown_crash": [],
    "teardown_clean": [],
}
EXPECTED_ERRORS = {
    "nav_lattice_sync": (
        "ERROR: NavigationServer navigation map query failed because it was made before first map synchronization.",
    ),
    "nav_lattice_bake": ("ERROR: The root node needs to be inside the SceneTree.",),
}
REQUIRED_STDERR = {"nav_lattice_teardown_crash": ("double free or corruption",)}

# ---- committed CASES via AST -------------------------------------------------
tree = ast.parse(HARNESS.read_text())
cases = None
for node in tree.body:
    if isinstance(node, ast.Assign) and any(
            isinstance(t, ast.Name) and t.id == "CASES" for t in node.targets):
        cases = ast.literal_eval(node.value)
nav = [c for c in cases if c[0].startswith("nav_lattice_")]
assert len(nav) == 11, len(nav)

ARMS_DIR.mkdir(parents=True, exist_ok=True)
summary = []
for name, script, flags, expected_exit, sig in nav:
    arm = name.removeprefix("nav_lattice_")
    for rep in range(1, REPS + 1):
        cmd = ["timeout", "-s", "KILL", "15", "godot", "--headless",
               "--path", str(PROJ), "--script", "res://" + script, "--", *flags]
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=25)
        out, err, rc = proc.stdout, proc.stderr, proc.returncode
        stem = str(ARMS_DIR / f"{arm}.rep{rep}")
        pathlib.Path(stem + ".out").write_text(out)
        pathlib.Path(stem + ".err").write_text(err)
        pathlib.Path(stem + ".rc").write_text(f"{rc}\n")
        rec = {"arm": arm, "rep": rep, "rc": rc, "expected_exit": expected_exit,
               "sig_in_stdout": sig in out, "sig_prefix_line": any(l.startswith(sig) for l in out.splitlines())}
        # stdout line discipline
        pass_lines = [l for l in out.splitlines() if l.startswith("PASS nav_lattice")]
        rec["pass_lines"] = len(pass_lines)
        rec["stale_lines"] = [l for l in out.splitlines() if l.startswith("STALE")]
        # tail (text after the signature on its line)
        tail_fields = []
        if rec["sig_prefix_line"]:
            line = next(l for l in out.splitlines() if l.startswith(sig))
            tail = line[len(sig):]
            tail_fields = [tok.split("=")[0] + "=" for tok in tail.split() if "=" in tok]
        rec["tail_fields"] = tail_fields
        allowed = TAIL_FIELDS[arm]
        rec["tail_fields_allowed"] = all(t in allowed for t in tail_fields)
        rec["tail_fields_present"] = sorted(set(tail_fields))
        # stderr discipline
        err_lines = [l.strip() for l in err.splitlines() if l.strip()]
        rec["err_lines"] = err_lines
        if name in EXPECTED_ERRORS:
            rec["err_exact_allowlist"] = err_lines == list(EXPECTED_ERRORS[name])
        else:
            rec["err_exact_allowlist"] = None
        if name in REQUIRED_STDERR:
            rec["required_stderr_ok"] = all(f in err for f in REQUIRED_STDERR[name])
            rec["marker_on_stdout"] = sig in out
        else:
            rec["required_stderr_ok"] = None
            rec["marker_on_stdout"] = None
        rec["err_bytes"] = len(err)
        rec["ok"] = (rc == expected_exit and sig in out
                     and rec["tail_fields_allowed"]
                     and (rec["err_exact_allowlist"] is not False)
                     and (rec["required_stderr_ok"] is not False))
        summary.append(rec)
        print(f"{'OK ' if rec['ok'] else 'BAD'} {arm}.rep{rep} rc={rc} "
              f"pass_lines={rec['pass_lines']} tail={rec['tail_fields_present']} "
              f"err={err_lines}")

# aggregate
agg = {}
for rec in summary:
    a = agg.setdefault(rec["arm"], {"reps": 0, "ok": 0, "rcs": [], "tails": set()})
    a["reps"] += 1
    a["ok"] += 1 if rec["ok"] else 0
    a["rcs"].append(rec["rc"])
    a["tails"].update(rec["tail_fields_present"])
print("\nAGGREGATE")
for arm, a in agg.items():
    print(f"  {arm}: {a['ok']}/{a['reps']} ok rcs={a['rcs']} tail_union={sorted(a['tails'])}")
print("\nALL_OK:", all(r["ok"] for r in summary))
