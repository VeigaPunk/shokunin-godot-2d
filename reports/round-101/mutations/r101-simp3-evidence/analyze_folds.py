#!/usr/bin/env python3
"""r101 SIMP-3 fold analysis.

For every scenario row of the folded lanes, compare 4 receipts
(base rep1, base rep2, folded rep1, folded rep2):

  gate   : does the harness row's own signature appear on stdout, and is the
           exit code the expected one? (the property the battery actually gates)
  raw    : stdout byte-identical across all four receipts
  keys   : set of `key=value` tokens of the PASS line; a key is *stable* in a
           tree when it takes one value across that tree's two reps. The fold
           is byte-neutral iff the stable-key/value maps agree between trees
           (varying keys are reported separately; they are the declared
           unstable diagnostics).
"""
import json, re, sys

KV = re.compile(r'\b([a-z0-9_]+)=')
ROOT = '/var/tmp/r101-simp3'


def load(p):
    return {json.loads(l)['name']: json.loads(l) for l in open(p)}


def tokens(line):
    out = {}
    for m in KV.finditer(line):
        k = m.group(1)
        start = m.end()
        nxt = line.find(' ', start)
        out[k] = line[start:nxt if nxt != -1 else len(line)]
    return out


def pass_line(rec):
    for line in rec['stdout'].splitlines():
        if line.startswith('PASS '):
            return line
    return None


def analyze(lane, base1, base2, fold1, fold2, rows, out):
    sig = {r[0]: r[3] if len(r) > 3 else None for r in rows}
    exp_exit = {r[0]: None for r in rows}
    sets = {'base': [base1, base2], 'fold': [fold1, fold2]}
    print(f"\n### lane {lane}: {len(base1)} rows")
    all_raw = []
    varying = []
    gate_fail = []
    for name in sorted(base1):
        recs = [base1[name], base2[name], fold1[name], fold2[name]]
        s = sig.get(name)
        # gate check
        for i, r in enumerate(recs):
            ok_sig = (s is None) or (s in r['stdout'])
            if not ok_sig or r['timeout'] or r['rc'] is None:
                gate_fail.append((name, i, r['rc'], ok_sig))
        pl = [pass_line(r) for r in recs]
        if len({r['stdout'] for r in recs}) == 1 and len({r['stderr'] for r in recs}) == 1:
            all_raw.append(name)
            continue
        # key-level analysis
        stable = {}
        for tree, (r1, r2) in sets.items():
            t1, t2 = tokens(pl[0 if tree == 'base' else 2] or ''), tokens(pl[1 if tree == 'base' else 3] or '')
            stable[tree] = {k: v for k, v in t1.items() if t2.get(k) == v}
        common = set(stable['base']) & set(stable['fold'])
        clash = {k: (stable['base'][k], stable['fold'][k]) for k in common if stable['base'][k] != stable['fold'][k]}
        var_keys = sorted(set(tokens(pl[0] or '')) - set(stable['base']))
        varying.append({'name': name, 'stable_keys': len(stable['base']), 'stable_in_fold': len(stable['fold']),
                        'clash': clash, 'var_keys': var_keys,
                        'base_only': sorted(set(stable['base']) - set(stable['fold'])),
                        'fold_only': sorted(set(stable['fold']) - set(stable['base']))})
    print(f"  raw-identical across all 4 receipts: {len(all_raw)}/{len(base1)}")
    print(f"  gate failures: {len(gate_fail)} {gate_fail[:5]}")
    clashes = [v for v in varying if v['clash']]
    print(f"  rows with stable-key/value CLASH between trees: {len(clashes)}")
    for c in clashes[:6]:
        print("   CLASH", json.dumps(c)[:300])
    print(f"  varying-key inventory ({len(varying)} rows), key sets (base|fold):")
    for v in sorted(varying, key=lambda d: d['name'])[:40]:
        print(f"   - {v['name']}: var={v['var_keys']} stable_base={v['stable_keys']} stable_fold={v['stable_in_fold']}"
              f" base_only={v['base_only']} fold_only={v['fold_only']}")
    out[lane] = {'raw_identical': all_raw, 'varying': varying, 'gate_fail': gate_fail}


def main():
    base1 = load(f'{ROOT}/runs/base-all.jsonl')
    base2 = load(f'{ROOT}/runs/base-rep2.jsonl')
    rows = json.load(open(f'{ROOT}/rows.json'))
    out = {}
    for lane, f1, f2, scripts in (('nav', 'fold-nav', 'fold-nav-r2', {'nav_lattice.gd'}),
                                  ('particles', 'fold-particles', 'fold-particles-r2', {'particles_lattice.gd'}),
                                  ('r95-dss', 'fold-r95', 'fold-r95-r2', {'dss_lattice.gd'}),
                                  ('r95-order', 'fold-r95-order', 'fold-r95-order-r2', {'r95b_order.gd'})):
        try:
            a, b = load(f'{ROOT}/runs/{f1}.jsonl'), load(f'{ROOT}/runs/{f2}.jsonl')
        except FileNotFoundError:
            print(f"[{lane}] receipts missing; skipped")
            continue
        sub = [r for r in rows if r[1] in scripts]
        analyze(lane, {k: v for k, v in base1.items() if k in a},
                {k: v for k, v in base2.items() if k in a}, a, b, sub, out)
    json.dump(out, open(f'{ROOT}/fold-analysis.json', 'w'), indent=1)


if __name__ == '__main__':
    main()
