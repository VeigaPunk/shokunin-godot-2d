#!/usr/bin/env python3
"""Focused interleaved A/B replay: alternate baseline and folded trees N times
per row, so any time-varying host load affects both trees equally."""
import json, subprocess, sys, os, time

ROOT = '/var/tmp/r101-simp3'


def run(tree, script, flags, timeout=25):
    cmd = ['godot', '--headless', '--path', tree, '--script', 'res://' + script, '--', *flags]
    p = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
    return p.returncode, p.stdout, p.stderr


def main():
    lane, reps = sys.argv[1], int(sys.argv[2])
    rows = json.load(open(f'{ROOT}/rows-{lane}.json'))
    names = [r[0] for r in rows]
    focus = sys.argv[3:] or names
    trees = {'base': f'{ROOT}/base', 'fold': f'{ROOT}/work/{"nav" if lane == "nav_lattice" else { "particles_lattice": "particles", "dss_lattice": "r95", "r95b_order": "r95"}.get(lane, "r95")}'}
    out = {}
    for row in rows:
        if row[0] not in focus:
            continue
        rec = {'base': [], 'fold': []}
        for i in range(reps):
            for tag in ('base', 'fold'):
                rc, so, se = run(trees[tag], row[1], row[2])
                rec[tag].append({'rep': i, 'rc': rc, 'stdout': so, 'stderr': se})
        out[row[0]] = rec
        vb = sorted({r['stdout'] for r in rec['base']})
        vf = sorted({r['stdout'] for r in rec['fold']})
        same_tree_b = len(rec['base']) if len(vb) == 1 else None
        print(f"{row[0]}: base_distinct={len(vb)} fold_distinct={len(vf)} "
              f"base_stable={'yes' if len(vb)==1 else 'no'} fold_stable={'yes' if len(vf)==1 else 'no'} "
              f"cross_equal={vb[0]==vf[0] if len(vb)==1 and len(vf)==1 else 'n/a'}")
    json.dump(out, open(f'{ROOT}/runs/ab-{lane}.json', 'w'), indent=1)


main()
