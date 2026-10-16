#!/usr/bin/env python3
"""r95-scribe fresh single-arm receipts on the LANDED fixture bytes.

Stages a scratch project the same way the battery does (copy fixtures, unique
app name, pickup.tscn staging, causal_chain readiness fix), then launches the
52 r95 arms as fresh processes under bounded timeout.  Modes: default 60 tps,
--fixed-fps 30, --fixed-fps 120, threaded physics (separate project copy).

Read-only wrt tracked files: writes only under corpus/live/r95-scribe/.
"""
import argparse
import ast
import json
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

REPO = Path("/home/vgpnk/Projects/shokunin/game-dev-2d-shokunin")
LANE = REPO / "corpus/live/r95-scribe"
GODOT = "/usr/bin/godot"


def stage_project(dest: Path, threaded: bool = False):
    if dest.exists():
        shutil.rmtree(dest)
    dest.mkdir(parents=True)
    seed = REPO / "corpus/fixtures"
    for item in seed.iterdir():
        if item.name == "run_battery.py" or item.name.startswith("."):
            continue
        if item.is_dir():
            shutil.copytree(item, dest / item.name)
        else:
            shutil.copy2(item, dest / item.name)
    project_file = dest / "project.godot"
    text = project_file.read_text()
    text = text.replace('config/name="MechanicOneShotTest"',
                        'config/name="MechanicOneShotTest-r95-scribe-fresh"', 1)
    if threaded:
        assert "[physics]" not in text
        text += "\n[physics]\n\n2d/run_on_separate_thread=true\n"
    project_file.write_text(text)
    shutil.copy2(dest / "controls" / "pickup.tscn", dest / "pickup.tscn")
    chain = dest / "causal_chain.gd"
    t = chain.read_text()
    anchor = "    await process_frame\n    var old := current_scene"
    assert anchor in t
    chain.write_text(t.replace(anchor, "    await process_frame\n    await process_frame\n    var old := current_scene", 1))


def r95_cases():
    src = subprocess.run(["git", "show", "HEAD:corpus/fixtures/run_battery.py"],
                         cwd=REPO, capture_output=True, text=True).stdout
    tree = ast.parse(src)
    for node in tree.body:
        if isinstance(node, ast.Assign):
            for t in node.targets:
                if isinstance(t, ast.Name) and t.id == "CASES":
                    vals = [tuple(ast.literal_eval(e) for e in c.elts) for c in node.value.elts]
                    return [v for v in vals
                            if str(v[0]).startswith(("dss_lattice_", "r95b_order_"))]
    raise SystemExit("CASES not found")


def launch(scratch, case, script, flags, mode, rep, outdir, bound=12):
    outdir.mkdir(parents=True, exist_ok=True)
    tag = f"{case}.{mode}.rep{rep}"
    cmd = ["timeout", "-s", "KILL", str(bound), GODOT, "--headless"]
    if mode == "ff30":
        cmd += ["--fixed-fps", "30"]
    elif mode == "ff120":
        cmd += ["--fixed-fps", "120"]
    cmd += ["--path", str(scratch), "--script", f"res://{script}", "--", *flags]
    t0 = time.time()
    p = subprocess.run(cmd, capture_output=True, text=True)
    wall = time.time() - t0
    text = p.stdout + p.stderr
    (outdir / f"{tag}.out").write_text(text)
    (outdir / f"{tag}.err").write_text(p.stderr)
    (outdir / f"{tag}.rc").write_text(f"{p.returncode}\n")
    return {"case": case, "mode": mode, "rep": rep, "rc": p.returncode,
            "stderr_bytes": len(p.stderr.encode()), "wall_s": round(wall, 2),
            "text": text}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--reps", type=int, default=2)
    ap.add_argument("--modes", default="default,ff30,ff120,threaded")
    ap.add_argument("--only", default="")
    args = ap.parse_args()
    modes = args.modes.split(",")
    cases = r95_cases()
    if args.only:
        wanted = set(args.only.split(","))
        cases = [c for c in cases if c[0] in wanted]

    scratch = LANE / "fresh-proj"
    scratch_thr = LANE / "fresh-proj-threaded"
    stage_project(scratch, threaded=False)
    if "threaded" in modes:
        stage_project(scratch_thr, threaded=True)

    records = []
    for mode in modes:
        proj = scratch_thr if mode == "threaded" else scratch
        reps = args.reps if mode == "default" else 1
        # mode scope: every arm for default; the ordering/point families for ff,
        # a 12-cell sentinel set for threaded
        if mode == "ff30":
            sel = [c for c in cases if str(c[0]).startswith("r95b_order_")]
        elif mode == "ff120":
            sel = [c for c in cases if str(c[0]).startswith("r95b_order_")
                   and any(k in c[0] for k in ("canon", "perm0", "period_k5", "celloff_x0", "cap40_p0"))]
        elif mode == "threaded":
            sel = [c for c in cases if any(k in c[0] for k in
                   ("canon", "perm0", "period_k5", "celloff_x0", "twopiles", "cap40_p0",
                    "census", "ray_order", "point_cap", "shape", "order_core", "cast_rest"))]
        else:
            sel = cases
        for case, script, flags, _exit, sig in sel:
            for rep in range(1, reps + 1):
                r = launch(proj, case, script, flags, mode, rep, LANE / "fresh")
                r["signature"] = sig
                r["signature_found"] = sig in r["text"]
                del r["text"]
                records.append(r)
                print(f"{case} {mode} rep{rep}: rc={r['rc']} sig={r['signature_found']} "
                      f"stderr={r['stderr_bytes']}B wall={r['wall_s']}s", flush=True)
    (LANE / "audit/fresh_arms.json").write_text(json.dumps(records, indent=2))
    bad = [r for r in records if r["rc"] != 0 or not r["signature_found"] or r["stderr_bytes"]]
    print(f"\nTOTAL {len(records)} receipts; bad={len(bad)}")
    for r in bad:
        print("BAD", r)


if __name__ == "__main__":
    main()
