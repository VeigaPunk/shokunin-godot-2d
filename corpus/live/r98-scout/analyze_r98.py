#!/usr/bin/env python3
"""r98-scout stability analyzer — per-cell reps / out_uniq / err_uniq / rc /
PASS-line uniqueness + longest common prefix of the PASS lines (the gating
prefix candidates).  Emits runs/analyze_r98.json and runs/analyze_r98.txt."""
import hashlib
import json
import pathlib
import re

HERE = pathlib.Path(__file__).parent
RUNS = HERE / "runs"


def load(pattern):
    cells = {}
    for out in sorted(RUNS.glob(pattern)):
        m = re.match(r"(r98_canvas_[a-z_]+)\.rep(\d+)\.out$", out.name)
        if not m:
            continue
        cell, rep = m.group(1), int(m.group(2))
        err = out.with_suffix(".err")
        rc = out.with_suffix(".rc")
        cells.setdefault(cell, []).append({
            "rep": rep,
            "out": out.read_text(),
            "out_sha": hashlib.sha256(out.read_bytes()).hexdigest(),
            "err": err.read_text() if err.exists() else "",
            "err_sha": hashlib.sha256(err.read_bytes()).hexdigest() if err.exists() else "",
            "rc": int(rc.read_text().strip()) if rc.exists() else None,
        })
    return cells


def pass_line(text):
    for line in reversed(text.splitlines()):
        if line.startswith("PASS "):
            return line
    return None


def common_prefix(strings):
    if not strings:
        return ""
    p = strings[0]
    for s in strings[1:]:
        while not s.startswith(p):
            p = p[:-1]
            if not p:
                return ""
    return p


def analyze(cells, label):
    report = {}
    unstable, crashes = [], []
    for cell in sorted(cells):
        reps = cells[cell]
        outs = {r["out_sha"] for r in reps}
        errs = {r["err_sha"] for r in reps}
        rcs = sorted({r["rc"] for r in reps})
        plines = [pass_line(r["out"]) for r in reps]
        puniq = len({p for p in plines})
        prefix = common_prefix([p for p in plines if p is not None])
        report[cell] = {
            "reps": len(reps),
            "out_uniq": len(outs),
            "err_uniq": len(errs),
            "err_bytes": sorted({len(r["err"]) for r in reps}),
            "rc": rcs,
            "pass_uniq": puniq,
            "pass_prefix": prefix,
            "pass_lines": sorted({p for p in plines if p is not None}),
        }
        if len(outs) != 1 or puniq != 1:
            unstable.append(cell)
        if rcs != [0]:
            crashes.append(cell)
    return report, unstable, crashes


def main():
    canonical = load("r98_canvas_*.rep*.out")
    loadtest = load("loadtest/r98_canvas_*.rep*.out")
    rep, unstable, crashes = analyze(canonical, "canonical")
    lrep, lunstable, lcrashes = analyze(loadtest, "loadtest")
    out = {
        "canonical": rep,
        "loadtest": lrep,
        "UNSTABLE": unstable,
        "CRASH_CELLS": crashes,
        "LOADTEST_UNSTABLE": lunstable,
        "LOADTEST_CRASH_CELLS": lcrashes,
    }
    (RUNS / "analyze_r98.json").write_text(json.dumps(out, indent=1, sort_keys=True) + "\n")
    lines = []
    for label, r in (("canonical", rep), ("loadtest", lrep)):
        lines.append(f"== {label} ==")
        for cell in sorted(r):
            d = r[cell]
            lines.append(f"{cell}: reps={d['reps']} out_uniq={d['out_uniq']} err_uniq={d['err_uniq']} "
                         f"err_bytes={d['err_bytes']} rc={d['rc']} pass_uniq={d['pass_uniq']}")
        lines.append("")
    lines.append(f"UNSTABLE={unstable}")
    lines.append(f"CRASH_CELLS={crashes}")
    lines.append(f"LOADTEST_UNSTABLE={lunstable}")
    lines.append(f"LOADTEST_CRASH_CELLS={lcrashes}")
    text = "\n".join(lines) + "\n"
    (RUNS / "analyze_r98.txt").write_text(text)
    print(text)


if __name__ == "__main__":
    main()
