#!/usr/bin/env python3
"""r102 CRIT-3 probe runner — committed vs folded trees for the 10 simp-fold fixtures.

Reads CASES / expected_errors / required_stderr from corpus/fixtures/run_battery.py by AST
(never executes it), launches every row of the 10 folded fixtures in the battery's launch
shape on two staged trees (base = committed r102 HEAD bytes; folded = all 10 simp patches
applied, folded shas verified), records rc + merged output (stdout+stderr, the battery's
merge convention), classifies with a port of the production classify_process, and reports
base-vs-folded discordance.

Writes only /var/tmp/r102-crit3/receipts-<tag>.json. No repo writes.
"""
import ast, json, subprocess, sys, time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

REPO = Path("/home/vgpnk/Projects/shokunin/game-dev-2d-shokunin")
S = Path("/var/tmp/r102-crit3")
FILES = ["nav_lattice.gd", "canvas_lattice.gd", "r98b_attack.gd", "r98b_rksenum.gd",
         "audio_lattice.gd", "stree_lattice.gd", "scene_io_lattice.gd", "dss_lattice.gd",
         "r95b_order.gd", "particles_lattice.gd"]


def get_assign(tree, name):
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            for t in node.targets:
                if isinstance(t, ast.Name) and t.id == name:
                    return node.value
    raise SystemExit(f"assign {name} not found")


def dict_assign(tree, name):
    """Select the assignment whose literal value is a dict (skips tuple defaults)."""
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            for t in node.targets:
                if isinstance(t, ast.Name) and t.id == name:
                    v = node.value
                    if isinstance(v, ast.Call) and isinstance(v.func, ast.Attribute):
                        v = v.func.value
                    try:
                        val = ast.literal_eval(v)
                    except Exception:
                        continue
                    if isinstance(val, dict):
                        return val
    return {}


src = (REPO / "corpus/fixtures/run_battery.py").read_text()
tree = ast.parse(src)
CASES = ast.literal_eval(get_assign(tree, "CASES"))
EE = dict_assign(tree, "expected_errors")
REQ = dict_assign(tree, "required_stderr")
rows = [c for c in CASES if c[1] in FILES]
print(f"rows in scope: {len(rows)}", flush=True)
arm_count = {}
for c in rows:
    arm_count[c[1]] = arm_count.get(c[1], 0) + 1
print("per fixture:", json.dumps(arm_count), flush=True)


def allowed_error(line, allowed):
    stripped = line.strip()
    if stripped == allowed:
        return True
    if allowed.endswith(","):
        return stripped.startswith(allowed) and stripped.count("ERROR:") == 1
    if allowed == "ERROR: chain incomplete":
        return (stripped.startswith("ERROR: chain incomplete collections=")
                and "scene=SceneB:<Node#" in stripped and "old_alive=false" in stripped
                and stripped.count("ERROR:") == 1)
    return False


def run_row(row, tree_dir):
    name, script, flags, exp, evid = row
    cmd = ["godot", "--headless", "--path", str(tree_dir), "--script",
           "res://" + script, "--", *flags]
    t0 = time.time()
    try:
        p = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        stdout, stderr, code, error = p.stdout, p.stderr, p.returncode, None
    except subprocess.TimeoutExpired as exc:
        stdout = exc.stdout if isinstance(exc.stdout, str) else ""
        stderr = exc.stderr if isinstance(exc.stderr, str) else ""
        code, error = None, "TIMEOUT"
    except OSError as exc:
        stdout, stderr, code, error = "", "", None, f"launch error: {exc}"
    merged = stdout + stderr
    if isinstance(evid, str):
        sig_ok = evid in merged
    else:
        sig_ok = any(e in merged for e in evid)
    allowed = EE.get(name, ())
    unrelated = [ln for ln in merged.splitlines() if "ERROR:" in ln
                 and not any(allowed_error(ln, a) for a in allowed)]
    verdict = (code == exp and error is None and sig_ok and not unrelated
               and "SCRIPT ERROR:" not in merged and "Parse Error:" not in merged)
    return {"name": name, "script": script, "flags": list(flags), "exp": exp, "rc": code,
            "error": error, "merged": merged, "verdict": verdict, "sig_in": sig_ok,
            "unrelated": unrelated[:3], "wall": round(time.time() - t0, 2)}


def run_tree(tag):
    tree_dir = S / tag
    out = {}
    for i, row in enumerate(rows):
        r = run_row(row, tree_dir)
        out[r["name"]] = r
        print(f"[{tag}] {i+1}/{len(rows)} {r['name']} rc={r['rc']} pass={r['verdict']} "
              f"{r['wall']}s", flush=True)
    return tag, out


if __name__ == "__main__":
    tags = sys.argv[1:] or ["base", "folded"]
    t0 = time.time()
    with ThreadPoolExecutor(max_workers=len(tags)) as ex:
        results = dict(ex.map(run_tree, tags))
    (S / "receipts-sweep.json").write_text(json.dumps(results, indent=1))
    print(f"done in {time.time()-t0:.0f}s -> {S}/receipts-sweep.json")
