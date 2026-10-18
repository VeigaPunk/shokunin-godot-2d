#!/usr/bin/env python3
"""Compare two r101-simp3 receipt files row by row.

Levels:
  raw   : stdout and stderr byte-identical
  mask  : same after masking (a) GDScript backtrace line refs res://f.gd:NNN,
          (b) declared-unstable diagnostic keys (env/proc counters etc.)
"""
import json, re, sys

BT = re.compile(r'res://[A-Za-z0-9_]+\.gd:\d+')
UNSTABLE = [
    re.compile(r'env=tps=\d+ pf=\d+ proc=\d+ sep2d_has=\w+ sep2d=\w+ maxsteps=\d+'),
]


def mask(text):
    t = BT.sub('res://<file>.gd:<LINE>', text)
    for p in UNSTABLE:
        t = p.sub('env=<UNSTABLE>', t)
    return t


def load(path):
    return {json.loads(l)['name']: json.loads(l) for l in open(path)}


def diff_report(a, b, label, verbose=True):
    only_a = sorted(set(a) - set(b))
    only_b = sorted(set(b) - set(a))
    rows = sorted(set(a) & set(b))
    counts = {'raw_same': 0, 'mask_same': 0, 'rc_same': 0, 'diff': 0}
    details = []
    for name in rows:
        ra, rb = a[name], b[name]
        same_rc = ra['rc'] == rb['rc']
        counts['rc_same'] += same_rc
        if ra['stdout'] == rb['stdout'] and ra['stderr'] == rb['stderr']:
            counts['raw_same'] += 1
        elif mask(ra['stdout']) == mask(rb['stdout']) and mask(ra['stderr']) == mask(rb['stderr']):
            counts['mask_same'] += 1
        else:
            counts['diff'] += 1
            la, lb = ra['stdout'].splitlines(), rb['stdout'].splitlines()
            first = next((i for i in range(max(len(la), len(lb)))
                          if (la[i] if i < len(la) else None) != (lb[i] if i < len(lb) else None)), None)
            details.append({
                'name': name, 'rc': (ra['rc'], rb['rc']),
                'a_line': la[first] if first is not None and first < len(la) else None,
                'b_line': lb[first] if first is not None and first < len(lb) else None,
                'stderr_diff': ra['stderr'] != rb['stderr'],
            })
    print(f"[{label}] rows={len(rows)} onlyA={only_a} onlyB={only_b} "
          f"raw_same={counts['raw_same']} mask_same={counts['mask_same']} "
          f"DIFF={counts['diff']} rc_same={counts['rc_same']}/{len(rows)}")
    if verbose:
        for d in details[:12]:
            print('   DIFF', json.dumps(d)[:400])
    return counts['diff']


if __name__ == '__main__':
    a, b, label = sys.argv[1], sys.argv[2], sys.argv[3]
    sys.exit(1 if diff_report(load(a), load(b), label) else 0)
