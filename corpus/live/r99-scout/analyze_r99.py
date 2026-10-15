#!/usr/bin/env python3
"""r99-scout analyzer — per-cell rep counts, byte-stability, stable-prefix census.

For every canonical cell (runs/r99_<cell>.rep<N>.{out,err,rc}) plus any loadtest
receipts (runs/loadtest/<cell>.rep<N>.*), report:
  - rc vector
  - out_uniq / err_uniq (byte-identical reps?)
  - pass_uniq (the PASS line alone)
  - prefix_uniq (the PASS line cut at ' | ' — the author-row prefix)
  - for unstable cells: the tokens that vary across reps
Writes runs/analyze_r99.json and prints a compact table.
"""
import json
import pathlib
import re

HERE = pathlib.Path(__file__).parent
RUNS = HERE / "runs"
CELLS = ["census", "bus", "autoplay", "stoppos", "peak_calib", "mixblock", "advance",
         "finish", "loop_degenerate", "loop_pts", "gen", "gen_peak", "poly",
         "bus_peak", "p2d", "pan_law", "gen2d", "pause"]


def receipts(cell):
    out = []
    for p in sorted(RUNS.glob(f"r99_{cell}.rep*.out")):
        out.append((p.name, p.read_text(), p.with_suffix(".err").read_text(),
                    int(p.with_suffix(".rc").read_text().strip())))
    lt = RUNS / "loadtest"
    if lt.exists():
        for p in sorted(lt.glob(f"{cell}.rep*.out")):
            out.append(("loadtest/" + p.name, p.read_text(), p.with_suffix(".err").read_text(),
                        int(p.with_suffix(".rc").read_text().strip())))
    return out


def pass_line(text):
    for line in text.splitlines():
        if line.startswith("PASS r99_audio "):
            return line
    return ""


def tokens(text):
    return dict(re.findall(r"([A-Za-z_][A-Za-z0-9_]*)=(\S+)", text))


def main():
    report = {"cells": {}, "unstable": [], "crash_cells": [], "err_nonzero": []}
    for cell in CELLS:
        rows = receipts(cell)
        if not rows:
            report["cells"][cell] = {"reps": 0}
            continue
        outs = {r[1] for r in rows}
        errs = {r[2] for r in rows}
        rcs = [r[3] for r in rows]
        passes = {pass_line(r[1]) for r in rows}
        prefixes = {pass_line(r[1]).split(" | ")[0] for r in rows}
        varying = {}
        if len(prefixes) > 1:
            base = tokens(list(prefixes)[0])
            for other in list(prefixes)[1:]:
                oth = tokens(other)
                for k in sorted(set(base) | set(oth)):
                    if base.get(k) != oth.get(k):
                        varying.setdefault(k, set()).update({base.get(k, "<missing>"), oth.get(k, "<missing>")})
        report["cells"][cell] = {
            "reps": len(rows), "out_uniq": len(outs), "err_uniq": len(errs),
            "pass_uniq": len(passes), "prefix_uniq": len(prefixes),
            "rc": rcs, "err_bytes": sorted({len(r[2]) for r in rows}),
            "varying_prefix_tokens": {k: sorted(v) for k, v in varying.items()},
        }
        if len(outs) > 1:
            report["unstable"].append(cell)
        if any(rc != 0 for rc in rcs):
            report["crash_cells"].append(cell)
        if any(len(r[2]) for r in rows):
            report["err_nonzero"].append(cell)
    (RUNS / "analyze_r99.json").write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(f"UNSTABLE={report['unstable']}")
    print(f"CRASH_CELLS={report['crash_cells']}")
    print(f"ERR_NONZERO={report['err_nonzero']}")
    for cell in CELLS:
        c = report["cells"][cell]
        if not c.get("reps"):
            print(f"{cell:18s} NO_RECEIPTS")
            continue
        print(f"{cell:18s} reps={c['reps']:2d} out_uniq={c['out_uniq']} err_uniq={c['err_uniq']} "
              f"pass_uniq={c['pass_uniq']} prefix_uniq={c['prefix_uniq']} rc={c['rc']} "
              f"err_bytes={c['err_bytes']}"
              + (f" VARYING={c['varying_prefix_tokens']}" if c["varying_prefix_tokens"] else ""))


if __name__ == "__main__":
    main()
