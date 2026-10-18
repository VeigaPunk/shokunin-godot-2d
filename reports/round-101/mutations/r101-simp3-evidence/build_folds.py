#!/usr/bin/env python3
"""r101 SIMP-3: materialise the three queued folds as scratch trees.

Each fold is reproduced from the originating round's own proposal
(corpus/live/r9X-simplifier/fold-proposal.diff), applied to the CURRENT HEAD
bytes. Folded shas are printed so they can be checked against the shas the
originating rounds recorded in their patches/battery comments.
"""
import hashlib, json, os, shutil, subprocess

ROOT = '/var/tmp/r101-simp3'
REPO = '/home/vgpnk/Projects/shokunin/game-dev-2d-shokunin'
BASE = f'{ROOT}/base'


def sha(path):
    return hashlib.sha256(open(path, 'rb').read()).hexdigest()


def tree(key):
    dest = f'{ROOT}/work/{key}'
    if os.path.exists(dest):
        shutil.rmtree(dest)
    shutil.copytree(BASE, dest, symlinks=True)
    return dest


# --- nav (r91) -------------------------------------------------------------
def fold_nav(dest):
    p = f'{dest}/nav_lattice.gd'
    t = open(p).read()
    assert t.count('const SETTLE := 10\n') == 1
    t = t.replace('const SETTLE := 10\n', '', 1)
    old = ('\tvar hits: Array[Vector2] = []\n\tNavigationServer2D.agent_set_map(a, map)'
           '\n\tNavigationServer2D.agent_set_avoidance_enabled(a, true)'
           '\n\tNavigationServer2D.agent_set_avoidance_callback(a, func(v: Vector2) -> void:'
           '\n\t\thits.append(v))')
    new = ('\tNavigationServer2D.agent_set_map(a, map)'
           '\n\tNavigationServer2D.agent_set_avoidance_enabled(a, true)'
           '\n\tNavigationServer2D.agent_set_avoidance_callback(a, func(_v: Vector2) -> void:'
           '\n\t\tpass)')
    assert t.count(old) == 2, t.count(old)
    t = t.replace(old, new)
    open(p, 'w').write(t)
    return {'file': 'nav_lattice.gd', 'before': sha(f'{BASE}/nav_lattice.gd'), 'after': sha(p)}


# --- particles (r94) -------------------------------------------------------
def fold_particles(dest):
    p = f'{dest}/particles_lattice.gd'
    t = open(p).read()
    edits = ['var T0 := 0\n', '\tvar start3: int = PH\n', '\tT0 = Time.get_ticks_usec()\n']
    for e in edits:
        assert t.count(e) == 1, (e, t.count(e))
        t = t.replace(e, '', 1)
    open(p, 'w').write(t)
    return {'file': 'particles_lattice.gd', 'before': sha(f'{BASE}/particles_lattice.gd'), 'after': sha(p)}


# --- r95 (dss + order) -----------------------------------------------------
def fold_r95(dest):
    diff = f'{REPO}/corpus/live/r95-simplifier/fold-proposal.diff'
    text = open(diff).read()
    # keep only the two fixture file sections (drop the run_battery.py comment hunk)
    parts, cur = [], None
    for line in text.splitlines(keepends=True):
        if line.startswith('--- a/'):
            cur = 'run_battery.py' not in line
        if cur is not None and cur:
            parts.append(line)
    sub = f'{ROOT}/work/r95-fold.diff'
    open(sub, 'w').write(''.join(parts))
    r = subprocess.run(['patch', '-p3', '-d', dest, '-i', sub], capture_output=True, text=True)
    assert r.returncode == 0, r.stdout + r.stderr
    return {'patch_log': r.stdout.strip().splitlines(),
            'dss_lattice.gd': {'before': sha(f'{BASE}/dss_lattice.gd'), 'after': sha(f'{dest}/dss_lattice.gd')},
            'r95b_order.gd': {'before': sha(f'{BASE}/r95b_order.gd'), 'after': sha(f'{dest}/r95b_order.gd')}}


out = {}
for key, fn in (('nav', fold_nav), ('particles', fold_particles), ('r95', fold_r95)):
    d = tree(key)
    out[key] = fn(d)
json.dump(out, open(f'{ROOT}/fold-shas.json', 'w'), indent=1)
print(json.dumps(out, indent=1))
