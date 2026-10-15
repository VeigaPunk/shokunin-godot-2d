#!/usr/bin/env python3
"""r100-scout receipt census — per-cell reps / out_uniq / err_uniq / rc for the
canonical and loadtest receipt sets (the r94/r95 analyze_*.py shape)."""
import glob
import json
import pathlib
import sys

HERE = pathlib.Path(__file__).parent
CELLS = ["census", "routing", "hover", "motion", "localpos", "cursor", "clip",
         "drag", "touch", "subvp", "warp", "focus", "render", "osmeta"]


def collect(subdir, prefix="r100_gui_"):
    per = {}
    for cell in CELLS:
        outs = sorted((HERE / subdir).glob(f"{prefix}{cell}.rep*.out"))
        if not outs:
            continue
        out_set, err_set, rc_set = set(), set(), set()
        err_bytes = set()
        for out in outs:
            err = out.with_suffix(".err")
            rc = out.with_suffix(".rc")
            out_set.add(out.read_text())
            err_set.add(err.read_text() if err.exists() else "")
            err_bytes.add(len(err.read_text() if err.exists() else ""))
            rc_set.add(rc.read_text().strip() if rc.exists() else "?")
        per[cell] = {
            "reps": len(outs),
            "out_uniq": len(out_set),
            "err_uniq": len(err_set),
            "err_bytes": sorted(err_bytes),
            "rc": sorted(rc_set),
            "pass_line_uniq": len({ln for t in out_set for ln in t.splitlines()
                                   if ln.startswith("PASS r100_gui ")}),
        }
    return per


report = {
    "canonical": collect("runs"),
    "loadtest": collect("runs/loadtest"),
}
(HERE / "runs" / "analyze_r100.json").write_text(json.dumps(report, indent=2) + "\n")

lines = []
for section in ("canonical", "loadtest"):
    lines.append(f"## {section}")
    for cell, d in report[section].items():
        unstable = "" if (d["out_uniq"] == 1 and d["err_uniq"] == 1 and d["rc"] == ["0"]) else "  <-- UNSTABLE"
        lines.append(
            f"{cell:9s} reps={d['reps']} out_uniq={d['out_uniq']} err_uniq={d['err_uniq']} "
            f"err_bytes={d['err_bytes']} rc={d['rc']} pass_uniq={d['pass_line_uniq']}{unstable}")
    unstable_cells = [c for c, d in report[section].items()
                      if not (d["out_uniq"] == 1 and d["err_uniq"] == 1 and d["rc"] == ["0"])]
    lines.append(f"UNSTABLE={unstable_cells}")
(HERE / "runs" / "analyze_r100.txt").write_text("\n".join(lines) + "\n")
print("\n".join(lines))
