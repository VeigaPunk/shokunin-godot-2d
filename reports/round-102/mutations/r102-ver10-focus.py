#!/usr/bin/env python3
"""Focused interleaved A/B null-control for the 5 particles rows whose
single-rep base/fold outputs differed on frame counters (r102-ver10)."""
import json, re, sys
from pathlib import Path
sys.path.insert(0, '/var/tmp/r102-ver10')
import verify

ROWS = ['r94_particles_cpu_lifetime', 'r94_particles_cpu_speed_pre',
        'r94_particles_cpu_stop', 'r94_particles_cpu_pause',
        'r94_particles_gpu_headless']
REPS = 3
KV = re.compile(r'([a-z0-9_]+)=(-?[0-9]+(?:\.[0-9]+)?|true|false)')

rows = {r['name']: r for r in verify.extract_rows()}
out = {}
for name in ROWS:
    r = rows[name]
    seq = []
    for i in range(REPS):
        for tree in ('tree-base', 'tree-particles'):
            run = verify.run_row(verify.ROOT / tree, r['script'], r['flags'])
            passlines = [l for l in run['out'].splitlines() if l.startswith('PASS particles')]
            kv = dict(KV.findall(passlines[0])) if passlines else {}
            seq.append(dict(tree=tree, rep=i + 1, rc=run['rc'],
                            sig=all(s in run['out'] for s in r['signature']),
                            kv=kv, line=passlines[0] if passlines else ''))
    # value sets per tree
    keys = sorted({k for s in seq for k in s['kv']})
    report = {}
    for k in keys:
        b = [s['kv'].get(k) for s in seq if s['tree'] == 'tree-base']
        f = [s['kv'].get(k) for s in seq if s['tree'] == 'tree-particles']
        if len(set(b)) > 1 or len(set(f)) > 1 or set(b) != set(f):
            report[k] = dict(base=b, fold=f)
    out[name] = dict(seq=seq, varying=report)
    print(f"== {name}: rc={[s['rc'] for s in seq]} sig={[s['sig'] for s in seq]}")
    if not report:
        print('   no field varies across the 6 runs')
    for k, v in report.items():
        print(f"   {k}: base={v['base']} fold={v['fold']}")
Path('/var/tmp/r102-ver10/focus-particles.json').write_text(json.dumps(out, indent=1))
print('wrote focus-particles.json')
