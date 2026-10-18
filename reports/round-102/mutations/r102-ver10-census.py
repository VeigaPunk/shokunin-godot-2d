#!/usr/bin/env python3
"""r102-ver10: discrimination census (text/scope based).

For each '-' line of a patch (final-third: particles, r95-fold; scene_io hunk 8),
extract every identifier mentioned, find the enclosing GDScript function in the
base file (old line number), then list every occurrence of that identifier
inside the SAME function in the FOLDED file, with strings stripped. Any
occurrence at all is printed for judgement; zero occurrences => binding-only removal.
"""
import re, sys
from pathlib import Path

ROOT = Path('/var/tmp/r102-ver10')
REPO = Path('/home/vgpnk/Projects/shokunin/game-dev-2d-shokunin')
IDENT = re.compile(r'\b[A-Za-z_][A-Za-z0-9_]*\b')
STRIP = re.compile(r'"[^"]*"|\'[^\']*\'')

def func_spans(text):
    lines = text.splitlines()
    starts = [i for i, l in enumerate(lines) if re.match(r'^func\s+([A-Za-z_]\w*)', l)]
    spans = []
    for idx, s in enumerate(starts):
        e = starts[idx + 1] - 1 if idx + 1 < len(starts) else len(lines) - 1
        m = re.match(r'^func\s+([A-Za-z_]\w*)', lines[s])
        spans.append((s + 1, e + 1, m.group(1)))
    return spans, lines

def span_of(spans, line):
    for s, e, name in spans:
        if s <= line <= e:
            return s, e, name
    return 1, len(spans) and spans[-1][1] or 0, '<module>'

def patch_deletions(patch_path):
    """Return list of (target_path, old_lineno, line_text) for '-' lines."""
    hunks = []
    cur = None
    target = None
    for raw in Path(patch_path).read_text().splitlines():
        if raw.startswith('+++ '):
            target = raw[4:].strip()
            if target.startswith('b/'):
                target = target[2:]
            continue
        if raw.startswith('@@'):
            m = re.match(r'@@ -(\d+)', raw)
            cur = {'old': int(m.group(1)), 'lines': [], 'target': target}
            hunks.append(cur)
        elif cur is not None:
            if raw.startswith('-') and not raw.startswith('---'):
                hunks[-1]['lines'].append((cur['old'], raw[1:]))
                cur['old'] += 1
            elif raw.startswith('+') and not raw.startswith('+++'):
                pass
            elif raw.startswith(' '):
                cur['old'] += 1
    out = []
    for h in hunks:
        for ln, t in h['lines']:
            out.append((h['target'], ln, t))
    return out

def census(label, patch_path, base_path, folded_path, only_files=None):
    print(f'\n== {label} ==')
    base_text = Path(base_path).read_text()
    fold_text = Path(folded_path).read_text()
    bspans, blines = func_spans(base_text)
    fspans, flines = func_spans(fold_text)
    dels = [(t, o, x) for (t, o, x) in patch_deletions(patch_path)
            if str(base_path).endswith(t)]
    names_seen = {}
    for tgt, old, txt in dels:
        stripped = STRIP.sub('', txt)
        ids = IDENT.findall(stripped)
        # candidate binding names: after `var ` or before ` :=` / ` = ` or `.append(` or as args
        cand = set()
        m = re.match(r'\s*(?:var\s+)?([A-Za-z_]\w*)', stripped)
        if m:
            cand.add(m.group(1))
        for t in re.findall(r'\bvar\s+([A-Za-z_]\w*)', stripped):
            cand.add(t)
        for name in cand:
            names_seen.setdefault(name, []).append((old, txt.strip()))
    for name, sites in names_seen.items():
        print(f'-- name `{name}` deleted at base lines {[s[0] for s in sites]}')
        for old, txt in sites:
            s, e, fname = span_of(bspans, old)
            # folded function span: same name (functions shift by deletions)
            fspan = next(((a, b) for a, b, n in fspans if n == fname), None)
            occ = []
            if fspan:
                for i in range(fspan[0] - 1, fspan[1]):
                    line = flines[i]
                    if name in IDENT.findall(STRIP.sub('', line)):
                        occ.append((i + 1, line.strip()[:110]))
            print(f'   base@L{old} in func {fname} ({s}-{e}); folded occurrences in {fname}: {len(occ)}')
            for ln, t in occ:
                print(f'      folded L{ln}: {t}')

import sys as _s
what = _s.argv[1] if len(_s.argv) > 1 else 'all'
if what in ('all', 'particles'):
    census('particles_lattice.gd fold (r94 queue)',
           REPO/'reports/round-101/mutations/r101-simp3-particles-fold.patch',
           REPO/'corpus/fixtures/particles_lattice.gd',
           ROOT/'apply-particles/corpus/fixtures/particles_lattice.gd')
if what in ('all', 'dss'):
    census('dss_lattice.gd fold (r95 queue)',
           REPO/'reports/round-101/mutations/r101-simp3-r95-fold.patch',
           REPO/'corpus/fixtures/dss_lattice.gd',
           ROOT/'apply-r95/corpus/fixtures/dss_lattice.gd')
if what in ('all', 'r95b'):
    census('r95b_order.gd fold (r95 queue)',
           REPO/'reports/round-101/mutations/r101-simp3-r95-fold.patch',
           REPO/'corpus/fixtures/r95b_order.gd',
           ROOT/'apply-r95/corpus/fixtures/r95b_order.gd')
if what in ('all', 'sceneio'):
    census('scene_io_lattice.gd fold (r96 queue, hunk 8 = final-third boundary)',
           REPO/'reports/round-101/mutations/r101-simp2-scene_io_lattice.gd.diff',
           REPO/'corpus/fixtures/scene_io_lattice.gd',
           ROOT/'apply-sceneio/corpus/fixtures/scene_io_lattice.gd')
