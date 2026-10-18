#!/usr/bin/env python3
"""r102-ver10: independent execution verification of the r101 simplifier queue
(final-third fixtures: particles / dss+r95b / scene_io) at HEAD bytes.

Replicates run_battery.py's staging block (lines 1730-1744) and launch shape
(execute(), line 1912): godot --headless --path <scratch> --script res://<s> -- <flags>.
Never runs run_battery.py itself.
"""
import ast, json, re, shutil, subprocess, sys, time
from pathlib import Path

REPO = Path('/home/vgpnk/Projects/shokunin/game-dev-2d-shokunin')
ROOT = Path('/var/tmp/r102-ver10')
FIX = REPO / 'corpus/fixtures'
GODOT = 'godot'
TIMEOUT = 15

FIXTURES = {
    'particles': {'scripts': ['particles_lattice.gd'],
                  'overlays': {'particles_lattice.gd': ROOT / 'apply-particles/corpus/fixtures/particles_lattice.gd'}},
    'r95': {'scripts': ['dss_lattice.gd', 'r95b_order.gd'],
            'overlays': {'dss_lattice.gd': ROOT / 'apply-r95/corpus/fixtures/dss_lattice.gd',
                         'r95b_order.gd': ROOT / 'apply-r95/corpus/fixtures/r95b_order.gd'}},
    'sceneio': {'scripts': ['scene_io_lattice.gd'],
                'overlays': {'scene_io_lattice.gd': ROOT / 'apply-sceneio/corpus/fixtures/scene_io_lattice.gd'}},
}

MASKS = [
    ('env-counter', re.compile(r'(env=tps=[0-9.]+ pf=[0-9.]+ proc=)[0-9]+'), r'\1N'),
    ('engine-ids', re.compile(r'\bids?=[0-9,]+'), 'ids=N'),
    ('fresh-id', re.compile(r'fresh_id=[0-9]+'), 'fresh_id=N'),
    ('timesec-bodypos', re.compile(r't[0-9]+_bodypos=\[[^\]]*\]'), 'tbodypos=N'),
    ('gd-backtrace-line', re.compile(r'(res://[A-Za-z0-9_]+\.gd:)[0-9]+'), r'\1L'),
]


def extract_rows():
    tree = ast.parse((FIX / 'run_battery.py').read_text())
    cases = None
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign) and any(
                isinstance(t, ast.Name) and t.id == 'CASES' for t in node.targets):
            cases = node.value
    rows = []
    for el in cases.elts:
        name, script, flags, exit_code, sig = ast.literal_eval(el)
        if isinstance(sig, str):
            sig = [sig]
        rows.append(dict(name=name, script=script, flags=list(flags),
                         expected_exit=exit_code, signature=list(sig)))
    return rows


def build_tree(dest, overlays):
    if dest.exists():
        shutil.rmtree(dest)
    dest.mkdir(parents=True)
    for item in FIX.iterdir():
        if item.name == 'run_battery.py' or item.name.startswith('.'):
            continue
        if item.is_dir():
            shutil.copytree(item, dest / item.name)
        else:
            shutil.copy2(item, dest / item.name)
    pf = dest / 'project.godot'
    text = pf.read_text().replace('config/name="MechanicOneShotTest"',
                                  'config/name="MechanicOneShotTest-r102v10"', 1)
    pf.write_text(text)
    shutil.copy2(dest / 'controls' / 'pickup.tscn', dest / 'pickup.tscn')
    ch = dest / 'causal_chain.gd'
    tx = ch.read_text()
    anchor = "    await process_frame\n    var old := current_scene"
    assert anchor in tx, "causal fixture changed"
    ch.write_text(tx.replace(anchor, "    await process_frame\n    await process_frame\n    var old := current_scene", 1))
    for rel, src in overlays.items():
        shutil.copy2(src, dest / rel)


def run_row(tree, script, flags):
    cmd = [GODOT, '--headless', '--path', str(tree), '--script', 'res://' + script, '--', *flags]
    t0 = time.time()
    try:
        p = subprocess.run(cmd, capture_output=True, text=True, timeout=TIMEOUT)
        out = p.stdout + p.stderr
        return dict(rc=p.returncode, out=out, cmd=' '.join(cmd), secs=round(time.time() - t0, 2))
    except subprocess.TimeoutExpired as e:
        def dec(x):
            return x.decode(errors='replace') if isinstance(x, bytes) else (x or '')
        return dict(rc=None, out=dec(e.stdout) + dec(e.stderr), timeout=True,
                    cmd=' '.join(cmd), secs=round(time.time() - t0, 2))


def masked_lines(out):
    lines = [l for l in out.splitlines() if l.strip()]
    for _, rx, rep in MASKS:
        lines = [rx.sub(rep, l) for l in lines]
    return lines


def main():
    rows = extract_rows()
    print(f'CASES rows: {len(rows)}', flush=True)
    report = {'rows': [], 'summary': {}}
    # build trees
    build_tree(ROOT / 'tree-base', {})
    for key, cfg in FIXTURES.items():
        build_tree(ROOT / f'tree-{key}', cfg['overlays'])
    print('trees built', flush=True)
    in_scope = [r for r in rows if r['script'] in {s for c in FIXTURES.values() for s in c['scripts']}]
    print(f'in-scope rows: {len(in_scope)}', flush=True)
    for i, r in enumerate(in_scope):
        ckey = next(k for k, c in FIXTURES.items() if r['script'] in c['scripts'])
        b = run_row(ROOT / 'tree-base', r['script'], r['flags'])
        f = run_row(ROOT / f'tree-{ckey}', r['script'], r['flags'])
        bl, fl = b['out'].splitlines(), f['out'].splitlines()
        raw_diff = [l for l in bl if l.strip() and l not in set(fl)] + \
                   [l for l in fl if l.strip() and l not in set(bl)]
        bm, fm = set(masked_lines(b['out'])), set(masked_lines(f['out']))
        still = sorted(bm ^ fm)
        rec = dict(name=r['name'], script=r['script'], expected_exit=r['expected_exit'],
                   base_rc=b['rc'], fold_rc=f['rc'],
                   sig_in_base=all(s in b['out'] for s in r['signature']),
                   sig_in_fold=all(s in f['out'] for s in r['signature']),
                   raw_diff_n=len(raw_diff), masked_diff_n=len(still),
                   still_diff=still[:4], raw_diff=raw_diff[:4],
                   base_secs=b['secs'], fold_secs=f['secs'])
        report['rows'].append(rec)
        flag = 'OK' if (rec['base_rc'] == rec['fold_rc'] and rec['sig_in_base'] and rec['sig_in_fold'] and not still) else 'CHECK'
        print(f"[{i+1}/{len(in_scope)}] {flag} {r['name']} rc={b['rc']}/{f['rc']} "
              f"sig={rec['sig_in_base']}/{rec['sig_in_fold']} raw={rec['raw_diff_n']} masked={rec['masked_diff_n']}", flush=True)
    # summary
    n = len(report['rows'])
    report['summary'] = dict(
        rows=n,
        rc_mismatch=sum(1 for x in report['rows'] if x['base_rc'] != x['fold_rc']),
        sig_missing=sum(1 for x in report['rows'] if not (x['sig_in_base'] and x['sig_in_fold'])),
        masked_diff_rows=sum(1 for x in report['rows'] if x['masked_diff_n']),
        raw_diff_rows=sum(1 for x in report['rows'] if x['raw_diff_n']),
        timeout=sum(1 for x in report['rows'] if x['base_rc'] is None or x['fold_rc'] is None),
    )
    (ROOT / 'verify-report.json').write_text(json.dumps(report, indent=1))
    print('SUMMARY', json.dumps(report['summary']), flush=True)


if __name__ == '__main__':
    main()
