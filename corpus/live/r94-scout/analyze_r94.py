#!/usr/bin/env python3
"""r94-scout analyzer — per-cell reps / byte-uniqueness / stderr / rc vectors and
the longest common prefix per cell (used to separate the stable gating prefix
from the volatile measured tail).

Output: runs/analyze_r94.json  (printed summary on stdout).
"""
import collections
import json
import pathlib

HERE = pathlib.Path(__file__).parent
RUNS = HERE / "runs"

CELLS = [
    "particles_census", "particles_ppm", "particles_convert",
    "particles_cpu_lifetime", "particles_cpu_expl", "particles_cpu_speed_pre",
    "particles_cpu_stop", "particles_cpu_never", "particles_cpu_contam",
    "particles_cpu_oneshot_off", "particles_cpu_oneshot_flag", "particles_cpu_pause",
    "particles_cpu_restart", "particles_cpu_retrigger", "particles_cpu_lt_mid",
    "particles_cpu_speed_mid", "particles_cpu_amount_mid", "particles_cpu_request",
    "particles_gpu_headless",
]


def common_prefix(strings):
    if not strings:
        return ""
    s = strings[0]
    for t in strings[1:]:
        i = 0
        while i < len(s) and i < len(t) and s[i] == t[i]:
            i += 1
        s = s[:i]
    return s


def scan(run_dir):
    out = {}
    for cell in CELLS:
        reps = sorted(run_dir.glob(f"r94_{cell}.rep*.out"))
        if not reps:
            continue
        lines, errs, rcs = [], [], []
        for f in reps:
            text = f.read_text()
            pass_lines = [l for l in text.splitlines() if l.startswith("PASS particles_lattice")]
            lines.append(pass_lines[0] if pass_lines else "<NO PASS LINE>")
            e = f.with_suffix(".err")
            errs.append(e.read_text() if e.exists() else "")
            r = f.with_suffix(".rc")
            rcs.append(int(r.read_text().strip()) if r.exists() else None)
        out[cell] = {
            "reps": len(reps),
            "out_uniq": len(set(lines)),
            "err_uniq": len(set(errs)),
            "err_bytes": sorted({len(e) for e in errs}),
            "rc": rcs,
            "common_prefix": common_prefix(lines),
            "lines": sorted(set(lines)),
        }
    return out


def main():
    canonical = scan(RUNS)
    loadtest = scan(RUNS / "loadtest")
    summary = {
        "canonical": canonical,
        "loadtest": loadtest,
        "canonical_unstable": sorted(c for c, v in canonical.items() if v["out_uniq"] > 1),
        "canonical_prefixes_hold_under_load": sorted(
            c for c, v in canonical.items()
            if c in loadtest and all(
                l.startswith(v["common_prefix"]) for l in loadtest[c]["lines"])),
        "loadtest_prefix_violations": sorted(
            c for c, v in canonical.items()
            if c in loadtest and not all(
                l.startswith(v["common_prefix"]) for l in loadtest[c]["lines"])),
    }
    (RUNS / "analyze_r94.json").write_text(json.dumps(summary, indent=1))
    for label, data in [("canonical", canonical), ("loadtest", loadtest)]:
        print(f"== {label} ==")
        for cell, v in data.items():
            print(f"{cell:30s} reps={v['reps']} out_uniq={v['out_uniq']} err_uniq={v['err_uniq']} "
                  f"err_bytes={v['err_bytes']} rc={v['rc']}")
    print("canonical_unstable =", summary["canonical_unstable"])
    print("loadtest_prefix_violations =", summary["loadtest_prefix_violations"])
    print("loadtest_prefixes_hold =", summary["canonical_prefixes_hold_under_load"])


if __name__ == "__main__":
    main()
