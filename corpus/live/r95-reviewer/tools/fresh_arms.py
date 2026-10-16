#!/usr/bin/env python3
"""r95 reviewer fresh-process arm runner.

Launches the 52 committed r95 arms from the *pinned export* of 9cd47507 in the
battery's exact launch shape, with the production `classify_process` extracted
verbatim (AST segment) from the pinned harness. Conditions: `load` (seat hogs
already running) plus per-arm `--fixed-fps 30` and `--fixed-fps 120` extras.

Receipts: corpus/live/r95-reviewer/fresh/<stamp>/{case}.{cond}.rep{i}.{out,err,rc}
Summary:  corpus/live/r95-reviewer/fresh.json
"""
import ast
import hashlib
import json
import os
import pathlib
import shutil
import subprocess
import sys
from datetime import datetime, timezone

REPO = pathlib.Path("/home/vgpnk/Projects/shokunin/game-dev-2d-shokunin")
PINNED = REPO / "corpus/live/r95-reviewer/pinned-tmp/corpus/fixtures"
SEAT = REPO / "corpus/live/r95-reviewer"
REPS = int(sys.argv[1]) if len(sys.argv) > 1 else 5
FF_EXTRA = True


def extract_classifier(text):
    tree = ast.parse(text)
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "classify_process":
            seg = ast.get_source_segment(text, node)
            ns = {}
            exec(seg, ns)
            return ns["classify_process"], hashlib.sha256(seg.encode()).hexdigest()
    raise SystemExit("classify_process not found")


def parse_cases(text):
    tree = ast.parse(text)
    for node in tree.body:
        if isinstance(node, ast.Assign) and any(
                isinstance(t, ast.Name) and t.id == "CASES" for t in node.targets):
            return [ast.literal_eval(e) for e in node.value.elts]
    raise SystemExit("CASES not found")


def stage_scratch(dest, stamp):
    if dest.exists():
        shutil.rmtree(dest)
    dest.mkdir(parents=True)
    for item in PINNED.iterdir():
        if item.name == "run_battery.py" or item.name.startswith("."):
            continue
        if item.is_dir():
            shutil.copytree(item, dest / item.name)
        else:
            shutil.copy2(item, dest / item.name)
    pf = dest / "project.godot"
    pf.write_text(pf.read_text().replace(
        'config/name="MechanicOneShotTest"',
        f'config/name="MechanicOneShotTest-{stamp}"', 1))
    shutil.copy2(dest / "controls" / "pickup.tscn", dest / "pickup.tscn")
    chain = dest / "causal_chain.gd"
    text = chain.read_text()
    anchor = "    await process_frame\n    var old := current_scene"
    assert anchor in text
    chain.write_text(text.replace(
        anchor, "    await process_frame\n    await process_frame\n    var old := current_scene", 1))


def main():
    harness_text = (PINNED / "run_battery.py").read_text()
    classify, seg_sha = extract_classifier(harness_text)
    cases = [c for c in parse_cases(harness_text)
             if c[0].startswith(("dss_lattice_", "r95b_order_"))]
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    fresh = SEAT / "fresh" / stamp
    fresh.mkdir(parents=True)
    scratch = fresh / "proj"
    stage_scratch(scratch, stamp)

    conditions = [("load", [])]
    if FF_EXTRA:
        conditions += [("ff30", ["--fixed-fps", "30"]),
                       ("ff120", ["--fixed-fps", "120"])]

    summary = {"stamp": stamp, "classifier_segment_sha256": seg_sha,
               "pinned_fixtures": str(PINNED), "reps": REPS,
               "conditions": [c for c, _ in conditions], "rows": []}
    n = 0
    for case, script, flags, expected_exit, signature in cases:
        row = {"case": case, "runs": [], "all_pass": True}
        for cond, prefix in conditions:
            reps = REPS if cond == "load" else 1
            for rep in range(1, reps + 1):
                cmd = (["godot", "--headless", "--path", str(scratch),
                        "--script", f"res://{script}"] + prefix + ["--"] + list(flags))
                rec = {"cond": cond, "rep": rep}
                try:
                    p = subprocess.run(cmd, capture_output=True, text=True, timeout=8)
                    out, err, code = p.stdout, p.stderr, p.returncode
                    rec["timeout"] = False
                except subprocess.TimeoutExpired as exc:
                    out = (exc.stdout or "") if isinstance(exc.stdout, str) else (exc.stdout or b"").decode()
                    err = (exc.stderr or "") if isinstance(exc.stderr, str) else (exc.stderr or b"").decode()
                    code = None
                    rec["timeout"] = True
                ok = classify(code, None if not rec["timeout"] else "TIMEOUT", out + err,
                              expected_exit, signature)
                rec.update({"rc": code, "pass": ok, "sig_in_stdout": signature in out,
                            "stderr_bytes": len(err.encode()),
                            "error_lines": [l for l in (out + err).splitlines() if "ERROR:" in l],
                            "out": out, "err": err})
                row["runs"].append(rec)
                row["all_pass"] = row["all_pass"] and ok
                n += 1
                (fresh / f"{case}.{cond}.rep{rep}.out").write_text(out)
                (fresh / f"{case}.{cond}.rep{rep}.err").write_text(err)
                (fresh / f"{case}.{cond}.rep{rep}.rc").write_text(
                    f"{code}\n")
                print(f"[{n}] {cond} {case} rep{rep} rc={code} pass={ok}", flush=True)
        summary["rows"].append(row)
    summary["all_pass"] = all(r["all_pass"] for r in summary["rows"])
    (SEAT / "fresh.json").write_text(json.dumps(summary, indent=2) + "\n")
    (fresh / "fresh.json").write_text(json.dumps(summary, indent=2) + "\n")
    print(f"ALL_PASS={summary['all_pass']} runs={n} classifier_seg={seg_sha}")


if __name__ == "__main__":
    main()
