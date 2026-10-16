#!/usr/bin/env python3
"""r93 verifier — fresh-arm sweep on the FROZEN committed fixtures.

Launches every r93 arm (11 anim_lattice + 6 r93b_anim) x3 reps in the battery's
exact launch shape (`godot --headless --path <proj> --script res://<script> --
--arm=<arm>` via subprocess.run, 8 s bound), then classifies each receipt with
the AST-extracted PRODUCTION `classify_process` (frozen harness segment
749fa0607e7707e6) against every committed r93 row pinned on that arm.

Receipts: arms/<script-stem>.<arm>.rep<N>.{out,err,rc}
Report:   probes/fresh-arms.txt
"""
import ast
import hashlib
import pathlib
import re
import subprocess
import sys

V = pathlib.Path("/home/vgpnk/Projects/shokunin/game-dev-2d-shokunin/corpus/live/r93-verifier")
FIX = V / "freeze" / "x" / "corpus" / "fixtures"
PROJ = V / "arms" / "proj"
GODOT = "/usr/bin/godot"
BOUND = 8

src = (FIX / "run_battery.py").read_text()
tree = ast.parse(src)

# --- production classify_process, AST-extracted from the frozen harness ------
seg = None
for node in ast.walk(tree):
    if isinstance(node, ast.FunctionDef) and node.name == "classify_process":
        seg = ast.get_source_segment(src, node)
        break
assert seg, "classify_process not found"
ns = {"re": re}
exec("import re\n" + seg, ns)  # noqa: S102 - frozen committed source, verifier-side
classify_process = ns["classify_process"]
seg_sha = hashlib.sha256(seg.encode()).hexdigest()[:16]

# --- committed r93 rows ------------------------------------------------------
cases = None
for node in ast.walk(tree):
    if isinstance(node, ast.Assign) and getattr(node.targets[0], "id", "") == "CASES":
        cases = node.value.elts
        break
rows = [ast.literal_eval(e) for e in cases if ast.literal_eval(e)[0].startswith("r93_")]

exp_errors = {}
for node in ast.walk(tree):
    if isinstance(node, ast.Dict):
        keys = [k.value for k in node.keys if isinstance(k, ast.Constant)]
        if "r92_tilemap_atlas" in keys and "nav_lattice_bake" in keys:
            for k, v in zip(node.keys, node.values):
                if isinstance(k, ast.Constant):
                    exp_errors[k.value] = ast.literal_eval(v)

# --- scratch project: copy of the frozen fixtures ---------------------------
if PROJ.exists():
    import shutil
    shutil.rmtree(PROJ)
PROJ.mkdir(parents=True)
import shutil
for item in FIX.iterdir():
    if item.name == "run_battery.py" or item.name.startswith("."):
        continue
    if item.is_dir():
        shutil.copytree(item, PROJ / item.name)
    else:
        shutil.copy2(item, PROJ / item.name)

# --- launch matrix ----------------------------------------------------------
arms = []
for r in rows:
    script, flags = r[1], r[2]
    arm = flags[0].split("=", 1)[1]
    key = (script, arm)
    if key not in arms:
        arms.append(key)
# the boundary's launch fingerprint arm is deliberately un-authored; launched
# anyway so its (unpinned) shape is visible next to the authored arms.
arms.append(("r93b_anim.gd", "clock"))

lines = []
lines.append(f"frozen harness sha256={hashlib.sha256(src.encode()).hexdigest()}")
lines.append(f"classify_process segment sha256={seg_sha} (r89-r92 pinned 749fa0607e7707e6)")
lines.append(f"arms={len(arms)} rows={len(rows)} reps=3 bound={BOUND}s")
lines.append("")

ok_all = True
receipt_index = []
for script, arm in arms:
    stem = script[:-3]
    for rep in range(1, 4):
        base = V / "arms" / f"{stem}.{arm}.rep{rep}"
        try:
            proc = subprocess.run(
                [GODOT, "--headless", "--path", str(PROJ), "--script", f"res://{script}", "--", f"--arm={arm}"],
                capture_output=True, text=True, timeout=BOUND)
            out, err, rc, error = proc.stdout, proc.stderr, proc.returncode, None
        except subprocess.TimeoutExpired as exc:
            out = (exc.stdout or b"").decode(errors="replace") if isinstance(exc.stdout, bytes) else (exc.stdout or "")
            err = (exc.stderr or b"").decode(errors="replace") if isinstance(exc.stderr, bytes) else (exc.stderr or "")
            rc, error = None, f"TIMEOUT after {BOUND} seconds"
        except OSError as exc:
            out, err, rc, error = "", str(exc), None, f"launch error: {exc}"
        (base.parent / (base.name + ".out")).write_text(out)
        (base.parent / (base.name + ".err")).write_text(err)
        (base.parent / (base.name + ".rc")).write_text(f"{rc}\n")
        receipt_index.append(str(base.relative_to(V)))

        # every committed row pinned on this arm
        for r in rows:
            if r[1] != script or r[2][0] != f"--arm={arm}":
                continue
            sig = r[4]
            allowed = tuple(exp_errors.get(r[0], ()))
            merged = out + err
            v = classify_process(rc, error, merged, r[3], sig, allowed)
            # stream anchor: signature must be on stdout, stderr must be empty
            stream_ok = (sig in out) and (err == "")
            full_line = any(ln == sig for ln in out.splitlines())
            tag = "OK" if (v and stream_ok) else "BAD"
            if tag == "BAD":
                ok_all = False
            lines.append(f"{tag} {stem}.{arm}.rep{rep} {r[0]:36s} classify={v} stdout_anchor={stream_ok} "
                         f"full_line={full_line} rc={rc} err={error} stderr_bytes={len(err)}")
    lines.append("")

# stability: pinned signature bytes per arm across reps
lines.append("--- per-arm signature stability (unique rendered PASS lines across 3 reps) ---")
for script, arm in arms:
    stem = script[:-3]
    outs = [(V / "arms" / f"{stem}.{arm}.rep{i}.out").read_text() for i in range(1, 4)]
    pass_lines = [[ln for ln in o.splitlines() if ln.startswith("PASS ")] for o in outs]
    uniq = {tuple(pl) for pl in pass_lines}
    lines.append(f"  {stem}.{arm}: reps_pass_lines={[len(p) for p in pass_lines]} unique={len(uniq)}")

lines.append("")
lines.append(f"ALL_ROWS_OK={ok_all}")
(V / "probes" / "fresh-arms.txt").write_text("\n".join(lines) + "\n")
(V / "probes" / "fresh-arms-index.txt").write_text("\n".join(receipt_index) + "\n")
print("\n".join(lines))
sys.exit(0 if ok_all else 1)
