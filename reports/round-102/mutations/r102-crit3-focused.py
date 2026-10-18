#!/usr/bin/env python3
"""r102 CRIT-3 focused null control: interleaved base/folded reps for rows whose
sweep merged-outputs differed, to classify fold-conditional vs run-to-run variance."""
import importlib.util, json, re
from pathlib import Path

spec = importlib.util.spec_from_file_location(
    "probe", "/home/vgpnk/Projects/shokunin/game-dev-2d-shokunin/reports/round-102/mutations/r102-crit3-probe.py")
probe = importlib.util.module_from_spec(spec)
spec.loader.exec_module(probe)

NAMES = ["nav_lattice_avoid", "nav_lattice_sync",
         "r94_particles_cpu_lifetime", "r94_particles_cpu_speed_pre", "r94_particles_cpu_stop",
         "r94_particles_cpu_pause", "r94_particles_gpu_headless",
         "r98b_qflush_suppress", "r98b_qorder_tree", "r98b_qorder_flat",
         "r99_audio_finish", "r99_audio_bus_peak"]
sub = [r for r in probe.rows if r[0] in NAMES]
out = {}
for rep in (1, 2):
    for tag in ("base", "folded"):
        for row in sub:
            r = probe.run_row(row, probe.S / tag)
            out.setdefault(row[0], {}).setdefault(tag, []).append(r["merged"])


def passtokens(merged):
    for ln in merged.splitlines():
        if ln.startswith("PASS ") or ln.startswith("R9") or ln.startswith("R95B") or ln.startswith("R96"):
            toks = {}
            for m in re.finditer(r"([A-Za-z0-9_]+)=([^\s]*)", ln):
                toks[m.group(1)] = m.group(2)
            return toks
    return {}


print(f"focused rows: {len(sub)}, {len(out[NAMES[0]]['base'])*2*len(sub)} launches")
for n in NAMES:
    b, f = out[n]["base"], out[n]["folded"]
    bset, fset = sorted(set(b)), sorted(set(f))
    tb = [passtokens(x) for x in b]
    tf = [passtokens(x) for x in f]
    # fields that differ within base reps / within folded reps
    wb = sorted({k for t in tb for k in t if any(t.get(k) != t2.get(k) for t2 in tb)})
    wf = sorted({k for t in tf for k in t if any(t.get(k) != t2.get(k) for t2 in tf)})
    # fields whose value sets differ between trees
    keys = set().union(*[set(t) for t in tb], *[set(t) for t in tf]) if tb else set()
    cross = sorted({k for k in keys
                    if {t.get(k) for t in tb} != {t.get(k) for t in tf}})
    exact = "IDENTICAL-4/4" if bset == fset and len(bset) == 1 else (
        "SAME-SET" if set(b) == set(f) else "RAW-DIFF")
    print(f"{n}: {exact} base_distinct={len(bset)} folded_distinct={len(fset)} "
          f"within-base-varying={wb} within-folded-varying={wf} cross-value-set-diff={cross}")
json.dump(out, open("/var/tmp/r102-crit3/focused.json", "w"), indent=1)
