#!/usr/bin/env python3
"""r101 MUT-7 — harness-dead class: battery runs but the fixture silently does nothing.

Precedent: r93/r94/r95 critic harness mutants (trimmed-CASES battery copy, synthetic
never-matching expected_errors entry => per-round gate flips True->False).

Stages:
  harness  — 5 trimmed-CASES battery copies under /tmp/r101-mut7/:
             base, deadentry, blankseq, blankgui, blankneg
  export   — raw Godot 4.7.2 export measurements on a scratch project:
             templates-present / templates-absent / filter-misses-everything

The shared corpus/fixtures tree is only READ (shutil.copytree); every run happens
in /tmp/r101-mut7/. The shared run_battery.py is never executed.
"""
import ast
import hashlib
import json
import os
import shutil
import subprocess
import sys

REPO = "/home/vgpnk/Projects/shokunin/game-dev-2d-shokunin"
SRC = REPO + "/corpus/fixtures"
WORK = "/tmp/r101-mut7"
GODOT = "godot"

KEEP = ["save_process_writer", "save_process_reader", "save_process_missing",
        "r100b_seq_clean", "r100b_seq_noclean", "r100_gui_cursor"]

# The harness-dead unit: a valid SceneTree script that quits immediately,
# prints nothing, rc=0. Measured (blanktest): stdout=101-byte engine banner, stderr=0 B.
BLANK = "extends SceneTree\n\nfunc _initialize() -> void:\n    quit(0)\n"

DEAD_ANCHOR = ("                'r100b_seq_clean': (\n"
               "                    'ERROR: Parameter \"t\" is null.',\n"
               "                ),\n")
DEAD_ADDED = ("                    'ERROR: synthetic never-matching r101-mut7 entry',\n")


def build(variant):
    dst = os.path.join(WORK, "fix-" + variant)
    if os.path.exists(dst):
        shutil.rmtree(dst)
    shutil.copytree(SRC, dst, ignore=shutil.ignore_patterns("__pycache__", ".godot"))
    harness = os.path.join(dst, "run_battery.py")
    text = open(harness).read()

    tree = ast.parse(text)
    node = next(n for n in tree.body if isinstance(n, ast.Assign)
                and getattr(n.targets[0], "id", None) == "CASES")
    keep = [e for e in node.value.elts if e.elts[0].value in KEEP]
    assert len(keep) == len(KEEP), [e.elts[0].value for e in node.value.elts if e.elts[0].value in KEEP]
    lines = text.splitlines(keepends=True)
    new = ["CASES = [\n"]
    for e in keep:
        row = tuple(ast.literal_eval(x) for x in e.elts)
        new.append("    " + repr(row) + ",\n")
    new.append("]\n")
    text = "".join(lines[:node.lineno - 1]) + "".join(new) + "".join(lines[node.end_lineno:])

    meta = {"variant": variant, "kept_cases": KEEP}
    if variant == "deadentry":
        assert text.count(DEAD_ANCHOR) == 1, text.count(DEAD_ANCHOR)
        text = text.replace(DEAD_ANCHOR, DEAD_ANCHOR.replace(
            "                ),\n", DEAD_ADDED + "                ),\n"), 1)
        meta["mutation"] = "synthetic never-matching expected_errors entry added to r100b_seq_clean"
    elif variant in ("blankseq", "blankgui", "blankneg"):
        target = {"blankseq": "r100b_seq.gd",
                  "blankgui": "r100_gui.gd",
                  "blankneg": "save_process.gd"}[variant]
        path = os.path.join(dst, target)
        original = open(path).read()
        open(path, "w").write(BLANK)
        meta["mutation"] = f"{target} replaced with silent {BLANK!r}"
        meta["blanked_bytes"] = len(original.encode())
    open(harness, "w").write(text)
    json.dump(meta, open(os.path.join(dst, "mutant.json"), "w"), indent=2)
    return dst


def summarize(rundir):
    path = os.path.join(rundir, "verdicts.json")
    raw = open(path, "rb").read()
    try:
        payload = json.loads(raw)
    except json.JSONDecodeError as exc:
        # Observed on this host: /tmp is tmpfs + usrquota; the battery's final
        # write can be cut short by EDQUOT (Errno 122) before the run returns.
        return {"verdict": None, "parse_error": str(exc),
                "verdicts_bytes": len(raw),
                "verdicts_tail": raw[-300:].decode(errors="replace"),
                "rundir": rundir}
    rows = {r["case"]: r["verdict"] for r in payload["results"]}
    meta = next((r for r in payload["results"]
                 if r["case"] == "probe_error_clause_surface"), {})
    disc = meta.get("discriminations", {})
    census = meta.get("census", {})
    return {
        "verdict": payload["verdict"],
        "row_verdicts": {k: rows.get(k) for k in KEEP},
        "dead_entry_count": census.get("dead_entry_count"),
        "dead_entries": census.get("dead_entries"),
        "r100_expected_errors_all_matched": disc.get("r100_expected_errors_all_matched"),
        "cases_integrity": disc.get("cases_integrity"),
    }


def run_harness(variant):
    dst = build(variant)
    runs = os.path.join(WORK, "runs-" + variant)
    log = os.path.join(WORK, "battery-" + variant + ".log")
    cmd = [sys.executable, os.path.join(dst, "run_battery.py"), "--runs", runs, "--godot", GODOT]
    with open(log, "w") as fh:
        rc = subprocess.run(cmd, stdout=fh, stderr=subprocess.STDOUT, timeout=900).returncode
    rundir = sorted(os.path.join(runs, d) for d in os.listdir(runs))[-1]
    summary = summarize(rundir)
    summary["harness_rc"] = rc
    summary["rundir"] = rundir
    summary["log"] = log
    json.dump(summary, open(os.path.join(WORK, "summary-" + variant + ".json"), "w"), indent=2)
    print(json.dumps({"stage": "harness", **summary}, indent=2), flush=True)
    return summary


def sha256(path):
    return hashlib.sha256(open(path, "rb").read()).hexdigest()


def export_run(label, project, env, preset="Linux/X11", artifact="fixture.x86_64"):
    out = os.path.join(project, "out")
    if os.path.exists(out):
        shutil.rmtree(out)
    os.makedirs(out)
    target = os.path.join(out, artifact)
    cmd = [GODOT, "--headless", "--path", project, "--export-debug", preset, target]
    proc = subprocess.run(cmd, capture_output=True, timeout=300, env=env)
    record = {
        "label": label,
        "command": cmd,
        "rc": proc.returncode,
        "stdout_bytes": len(proc.stdout),
        "stderr_bytes": len(proc.stderr),
        "stdout_tail": proc.stdout.decode(errors="replace").splitlines()[-12:],
        "stderr_tail": proc.stderr.decode(errors="replace").splitlines()[-12:],
        "artifact_exists": os.path.isfile(target),
        "artifact_bytes": os.path.getsize(target) if os.path.isfile(target) else 0,
        "artifact_sha256": sha256(target) if os.path.isfile(target) else None,
        "out_products": sorted(os.listdir(out)),
    }
    print(json.dumps(record, indent=2), flush=True)
    return record


def export_stage():
    project = os.path.join(WORK, "exp1")
    os.makedirs(project, exist_ok=True)
    for name in ("project.godot", "export_presets.cfg"):
        shutil.copy2(os.path.join(SRC, name), os.path.join(project, name))
    empty_home = os.path.join(WORK, "emptyhome")
    os.makedirs(os.path.join(empty_home, ".local", "share"), exist_ok=True)

    present = export_run("templates_present", project, None)

    env = os.environ.copy()
    env["HOME"] = empty_home
    env["XDG_DATA_HOME"] = os.path.join(empty_home, ".local", "share")
    absent = export_run("templates_absent", project, env)

    # B3: a preset whose filter cannot match anything — content-level silent nothing.
    project2 = os.path.join(WORK, "exp2")
    if os.path.exists(project2):
        shutil.rmtree(project2)
    shutil.copytree(project, project2, ignore=shutil.ignore_patterns("out", ".godot"))
    cfg = os.path.join(project2, "export_presets.cfg")
    text = open(cfg).read()
    text = text.replace('export_filter="all_resources"',
                        'export_filter="customized"', 1)
    text = text.replace('include_filter=""', 'include_filter="no_such_dir/*"', 1)
    text = text.replace('exclude_filter=""', 'exclude_filter=""', 1)
    open(cfg, "w").write(text)
    filtered = export_run("filter_misses_everything", project2, None)

    result = {"present": present, "absent": absent, "filtered": filtered}
    json.dump(result, open(os.path.join(WORK, "summary-export.json"), "w"), indent=2)
    return result


if __name__ == "__main__":
    stage = sys.argv[1] if len(sys.argv) > 1 else "harness"
    if stage == "harness":
        out = {}
        for variant in ("base", "deadentry", "blankseq", "blankgui", "blankneg"):
            out[variant] = run_harness(variant)
        json.dump(out, open(os.path.join(WORK, "summary-harness.json"), "w"), indent=2)
    elif stage == "export":
        export_stage()
    else:
        raise SystemExit("stage must be harness|export")
