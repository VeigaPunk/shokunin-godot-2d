#!/usr/bin/env python3
"""r103-G4-MATRIX — receipt-shape META gate replay harness (G4 seat).

Replays the patched G1 gate over stored verdict records:
  green   — 4 stored green runs (r101 x2, r102 x2)          expect 0 flags
  attacks — 5 G2 adversary record mutations                  expect 5/5 flagged
  corrupt — 6 synthetic corrupt record variants              expect 6/6 flagged

Gate consumes ONLY: stored verdict records + pinned design-time constants
(CASES table, w4 multi-PASS census, case census, fixture print-literals, engine grammar).
Never re-runs the battery, never edits a classifier.
"""
import ast, collections, json, os, re, sys

ROOT = os.environ.get('R103_ROOT', '/home/vgpnk/Projects/shokunin/game-dev-2d-shokunin')
GREEN_RUNS = {
    'r101-1': 'corpus/live/runs/20261018T200239625248Z/verdicts.json',
    'r101-2': 'corpus/live/runs/20261018T202131127599Z/verdicts.json',
    'r102-1': 'corpus/live/runs/20261018T212500022987Z/verdicts.json',
    'r102-2': 'corpus/live/runs/20261018T213443471189Z/verdicts.json',
}
CENSUS = os.path.join(ROOT, 'reports/round-103/mutations/r103-G4-case-census.json')

# ---------------------------------------------------------------- design-time constants
def load_cases():
    src = open(os.path.join(ROOT, 'corpus/fixtures/run_battery.py')).read()
    tree = ast.parse(src)
    cn = None
    for node in tree.body:
        if isinstance(node, ast.Assign) and any(getattr(t, 'id', None) == 'CASES' for t in node.targets):
            cn = node.value; break
    rows = {}
    for el in cn.elts:
        evs = []
        def walk(n):
            if isinstance(n, ast.Constant) and isinstance(n.value, str): evs.append(n.value)
            elif isinstance(n, (ast.Tuple, ast.List)):
                for x in n.elts: walk(x)
        walk(el.elts[4] if len(el.elts) > 4 else None)
        rows[el.elts[0].value] = {'script': el.elts[1].value, 'evidence': evs}
    return rows

CASES = load_cases()

def load_allow():
    cen = json.load(open(os.path.join(ROOT, 'reports/round-103/mutations/r103-w4-census.json')))
    allow, mult = {}, {}
    for run in ('run1', 'run2'):
        for m in cen[run]['multi']:
            allow.setdefault(m['case'], set()).update(m['pass_lines'])
            per = collections.Counter(m['pass_lines'])          # per-run multiplicity
            cur = mult.setdefault(m['case'], collections.Counter())
            for L, n in per.items():
                cur[L] = max(cur[L], n)                          # never sum across runs
    return allow, mult

ALLOW, MULT = load_allow()

def load_case_census():
    return json.load(open(CENSUS))

PRINT_RE = re.compile(r"""print(?:_rich|_err)?\(\s*(?:'([^']*)'|"([^"]*)")""")
_lit_cache = {}
def fixture_literals(script):
    if script in _lit_cache: return _lit_cache[script]
    p = os.path.join(ROOT, 'corpus/fixtures', script or '')
    exact, prefix = set(), set()
    if os.path.exists(p):
        txt = open(p, encoding='utf-8', errors='replace').read()
        for m in PRINT_RE.finditer(txt):
            lit = m.group(1) if m.group(1) is not None else m.group(2)
            lit = lit.encode().decode('unicode_escape')
            if not lit: continue
            if '%' not in lit and '{' not in lit and '\\n' not in lit:
                for part in lit.split('\n'):
                    if part: exact.add(part)
            else:
                cut = len(lit)
                for hook in ('%', '{', '\\'):
                    i = lit.find(hook)
                    if i >= 0: cut = min(cut, i)
                if lit[:cut]: prefix.add(lit[:cut])
    _lit_cache[script] = (exact, prefix)
    return exact, prefix

ANSI_RE = re.compile(r'\x1b\[[0-9;?]*[A-Za-z]')

# engine + harness grammar (pinned; each class has a source citation in the shard)
ENGINE_PATTERNS = [re.compile(p) for p in (
    r'^\s*$',
    r'^Godot Engine v[0-9]+\.[0-9]+.*https://godotengine\.org$',
    r'^ERROR: ',
    r'^\s+at: ',
    r'^\s*GDScript backtrace \(most recent call first\):$',
    r'^\s*\[[0-9]+\] 0x[0-9a-f]+ .*',
    r'^\s*\[[0-9]+\] .*\(.*:[0-9]+\)$',
    r'^WARNING: ',
    r'^SCRIPT ERROR:',
    r'^Parse Error:',
    r'^\s+res://',
    r'^\s+user://',
    r'.*ObjectDB instances were leaked.*',
    r'^={4,}$', r'^-{4,}$',
    r'^-- END OF .*BACKTRACE --$',
    r'^Dumping the backtrace.*',
    r'^Engine version: .*',
    r'^Load address: (0x)?[0-9a-f]+$',
    r'^handle_crash: Program crashed with signal [0-9]+$',
    r'^Program crashed with signal .*',
    r'^/usr/include/c\+\+/.*$',
    r'^(double free or corruption|corrupted size vs\. prev_size|free\(\): .*|malloc\(\): .*)\b.*$',
    r'^ *\[\s*[0-9]{1,3}%?\s*\]\s*\S+.*$',
    r'^\[ DONE \]\s*\S+$',
    r'^The following presets were detected in this project.s `export_presets\.cfg`:',
    r'^\s+"[^"]+"$',
    r'^Use NavigationServer(2D)?\..*$',
    r'^\tNavigationServer .*$',
    r'^DESCENDANT_PIPE( godot_pid| spawned_pid)=[0-9]+$',
    r'^DESCENDANT_PIPE_FORGE write_ppid=[0-9]+$',
    r'^DESCENDANT_PIPE_ERRFORGE write_ppid=[0-9]+$',
)]

# dynamic receipts measured over the 4 green runs
DYN_PATTERNS = [re.compile(p) for p in (
    r'^PASS save_process (writer|reader|missing)=.* pid=[0-9]+ path=\S+.*$',
)]

BANNER_RE = re.compile(r'^Godot Engine v(\S+) \(([^)]*)\) - https://godotengine\.org$')
EXPORT_SCRIPTS = ('__godot_export__', '__godot_export_missing__')

def strip_ansi(s):
    return ANSI_RE.sub('', s)

def _allowed_error(line, allowed):
    """Same admission rule as run_battery.classify_process.allowed_error (1793-1805)."""
    s = line.strip()
    if s == allowed: return True
    if allowed.endswith(','):
        return s.startswith(allowed) and s.count('ERROR:') == 1
    if allowed == 'ERROR: chain incomplete':
        return (s.startswith('ERROR: chain incomplete collections=')
                and 'scene=SceneB:<Node#' in s and 'old_alive=false' in s
                and s.count('ERROR:') == 1)
    return False

class Ctx:
    def __init__(self, run):
        self.run = run
        self.banner_version = None
        for r in run['results']:
            for L in (r.get('output') or []):
                m = BANNER_RE.match(L)
                if m: self.banner_version = m.group(1); break
            if self.banner_version: break

CASE_CENSUS = load_case_census()

# ---------------------------------------------------------------- accounting
def line_accounted(row, line, ctx):
    stripped = strip_ansi(line)
    if stripped.startswith('Godot Engine v'):
        m = BANNER_RE.match(stripped)
        if not m: return None
        if ctx.banner_version is not None and m.group(1) != ctx.banner_version: return None
        return 'engine_banner'
    if any(p.match(stripped) for p in ENGINE_PATTERNS):
        return 'engine_grammar'
    if any(p.match(stripped) for p in DYN_PATTERNS):
        return 'dynamic'
    pins = row.get('signature')
    pins = pins if isinstance(pins, list) else [pins]
    for P in pins:
        if isinstance(P, str) and P and (line == P or P in line): return 'own_pin'
    if line in ALLOW.get(row.get('case'), ()): return 'allowlist'
    exact, prefix = fixture_literals(row.get('script'))
    if line in exact or stripped in exact: return 'fixture_literal'
    for p in prefix:
        if p and (line.startswith(p) or stripped.startswith(p)): return 'fixture_prefix'
    return None

def gate_row(row, ctx):
    flags = []
    for k in ('case', 'script', 'signature', 'output', 'verdict'):
        if k not in row: flags.append(f'F1_malformed:missing_{k}')
    if flags: return flags, {}
    if not isinstance(row['case'], str) or not row['case']: flags.append('F1_malformed:case')
    if row['case'] not in CASE_CENSUS: flags.append('F2_unknown_case')
    elif row['script'] != CASE_CENSUS[row['case']]: flags.append('F2_case_script_mismatch')
    sig = row['signature']
    if isinstance(sig, str):
        pins = [sig]
    elif isinstance(sig, list) and sig and all(isinstance(x, str) for x in sig):
        pins = list(sig)
    else:
        return flags + ['F1_malformed:signature'], {}
    if not any(P.strip() for P in pins): flags.append('F1_malformed:empty_signature')
    out = row['output']
    if not isinstance(out, list) or not all(isinstance(x, str) for x in out):
        return flags + ['F1_malformed:output'], {}
    if row['verdict'] not in ('PASS', 'FAIL'): flags.append('F1_malformed:verdict')
    if row['verdict'] != 'PASS':
        return flags, {'scope': 'FAIL row — receipt-shape checks not bound'}
    text = '\n'.join(out)
    detail = {}
    # F3 own pin present (any-alternative, mirroring run_battery.py:2343);
    # export rows bind to their own contract ([ DONE ] + savepack, run_battery.py:1956)
    pin_ok = any(P in text for P in pins)
    if row['script'] in EXPORT_SCRIPTS:
        # export rows bind either to their receipt pin or to their own contract
        # ([ DONE ] + savepack, run_battery.py:1956); the stored signature is a
        # derived receipt for __godot_export__, a diagnostic for __godot_export_missing__
        pin_ok = pin_ok or ('[ DONE ]' in text and 'savepack' in text)
    if not pin_ok:
        flags.append('F3_own_pin_absent')
    # F5 whole-output accounting
    unacc = [(i, L) for i, L in enumerate(out) if line_accounted(row, L, ctx) is None]
    if unacc:
        flags.append(f'F5_line_unaccounted({len(unacc)})')
        detail['unaccounted'] = unacc[:5]
    # F4 PASS-line accounting
    obs_pass = [L for L in out if L.startswith('PASS ')]
    bad = [L for L in obs_pass if line_accounted(row, L, ctx) not in ('own_pin', 'allowlist', 'dynamic')]
    if bad:
        flags.append(f'F4_pass_line_unaccounted({len(bad)})')
        detail['bad_pass'] = bad[:3]
    # F6 PASS-line multiplicity: every PASS line at most its pinned multiplicity
    # (census multiplicity for allowlisted rows, else one per own payload)
    counts = collections.Counter(obs_pass)
    for L, n in counts.items():
        allowed = MULT.get(row['case'], {}).get(L, 1)
        if n > allowed:
            flags.append(f'F6_pass_line_duplicate({n}>{allowed})'); break
    # F8 exit-field consistency on the certified record
    if 'expected_exit' in row and 'actual_exit' in row and row['expected_exit'] != row['actual_exit']:
        flags.append('F8_exit_mismatch')
    # F9 unrelated-ERROR invariant re-check (classify_process rule, run_battery.py:1792-1808).
    # Scoped to rows whose governing classifier passes the record's own expected_errors list:
    # mutant_* rows classify through classify_mutant, export rows through classify_export —
    # both are carved out (documented ceiling: 3 such rows per run).
    if (not row['case'].startswith('mutant_') and row['script'] not in EXPORT_SCRIPTS
            and 'expected_errors' in row):
        allowed_errs = row['expected_errors'] or []
        for L in out:
            if 'ERROR:' in L and not any(_allowed_error(L, a) for a in allowed_errs):
                flags.append('F9_unrelated_error'); break
    # F7 multiline pin: exactly one contiguous exact-bytes occurrence
    for P in pins:
        if '\n' in P:
            n = text.count(P)
            if n != 1: flags.append(f'F7_multiline_pin_occurrences={n}')
    return flags, detail

# ---------------------------------------------------------------- replay driver
def load_run(path):
    run = json.load(open(os.path.join(ROOT, path)))
    ctx = Ctx(run)
    rows = [r for r in run['results'] if isinstance(r, dict) and 'signature' in r and 'output' in r]
    return run, ctx, rows

def replay_green(verbose=True):
    report = {}
    for tag, path in GREEN_RUNS.items():
        run, ctx, rows = load_run(path)
        nflag = 0; percase = {}
        for r in rows:
            f, d = gate_row(r, ctx)
            if f: nflag += 1; percase[r.get('case')] = {'flags': f, 'detail': d}
        report[tag] = {'rows': len(rows), 'flagged': nflag, 'cases': percase}
        if verbose:
            print(f'== {tag}: rows={len(rows)} flagged={nflag}')
            for c, v in list(percase.items())[:25]:
                print(f'   {c}: {v["flags"]}')
                for i, L in v['detail'].get('unaccounted', []):
                    print(f'      unacc[{i}] {L[:110]!r}')
                for L in v['detail'].get('bad_pass', []):
                    print(f'      badpass  {L[:110]!r}')
    return report

# ---------------------------------------------------------------- mutants
def row_by_case(rows, case, run_idx=0):
    hits = [r for r in rows if r.get('case') == case]
    return hits[run_idx] if hits else None

def build_attacks(rows):
    """5 G2 adversaries, each a record mutation over a real r102 row."""
    A = []
    r_launch = row_by_case(rows, 'export_launch_embed_boot')
    r_seq = row_by_case(rows, 'r101_seqfull_clean')
    # ATK1 mut09 A1 shape: foreign line inside the launch receipt window
    m = json.loads(json.dumps(r_launch))
    idx = next(i for i, L in enumerate(m['output']) if L.startswith('EXPORT_LAUNCH_DIAG'))
    m['output'].insert(idx + 1, 'FOREIGN_EXTRA injected=into_span')
    A.append(('ATK1_mut09_A1_in_span_launch', m))
    # ATK2 mut09 A2/A3 shape: foreign line after the receipt (post-span)
    m = json.loads(json.dumps(r_launch))
    m['output'].append('FOREIGN_EXTRA injected=post_span')
    A.append(('ATK2_mut09_A2_post_span', m))
    # ATK3 PASS-line flood: foreign PASS lines spliced from another family
    m = json.loads(json.dumps(r_launch))
    m['output'] += ['PASS r99b mixfree first=0.000000 first_q=true blocks=1 blocks_ge6=false sub=1 other=0 all_jumps_q=false period_is_block=false'] * 3
    A.append(('ATK3_pass_line_flood', m))
    # ATK4 foreign line inside the 17-line seqfull pinned span
    m = json.loads(json.dumps(r_seq))
    pin = m['signature'] if isinstance(m['signature'], str) else m['signature'][0]
    plines = pin.split('\n')
    pos = next(i for i, L in enumerate(m['output']) if L == plines[1])
    m['output'].insert(pos + 1, 'FOREIGN_EXTRA injected=span_mid')
    A.append(('ATK4_foreign_line_in_seqfull_span', m))
    # ATK5 engine-banner spoof
    m = json.loads(json.dumps(r_launch))
    m['output'] = [re.sub(r'^Godot Engine v\S+', 'Godot Engine v4.6.0.stable.arch_linux.deadbeef', L)
                   if L.startswith('Godot Engine v') else L for L in m['output']]
    A.append(('ATK5_engine_banner_spoof', m))
    return A

def build_corrupt(rows):
    """6 synthetic corrupt variants (structural record tampering)."""
    C = []
    r_launch = row_by_case(rows, 'export_launch_embed_boot')
    r_seq = row_by_case(rows, 'r101_seqfull_clean')
    # V1 own receipt line dropped
    m = json.loads(json.dumps(r_launch))
    m['output'] = [L for L in m['output'] if L != m['signature']]
    C.append(('V1_pin_dropped', m))
    # V2 own receipt line duplicated
    m = json.loads(json.dumps(r_launch))
    m['output'] = m['output'] + [m['signature']]
    C.append(('V2_pin_duplicated', m))
    # V3 signature blanked
    m = json.loads(json.dumps(r_launch)); m['signature'] = ''
    C.append(('V3_signature_blank', m))
    # V4 output field removed
    m = json.loads(json.dumps(r_launch)); del m['output']
    C.append(('V4_output_field_removed', m))
    # V5 case renamed (never-seen splice name)
    m = json.loads(json.dumps(r_launch)); m['case'] = 'r999_synthetic_splice'
    C.append(('V5_case_renamed', m))
    # V6 exit-field forgery (verdict PASS while actual_exit contradicts expected_exit;
    # r102-1 has zero FAIL rows, so a promotion variant is not constructible there)
    m = json.loads(json.dumps(r_launch))
    m['actual_exit'] = 7
    C.append(('V6_exit_field_forgery', m))
    return C

def build_evasions(rows):
    """Grammar-shaped forgeries: the account classifies by SHAPE, so a foreign line
    written in engine/harness grammar is accepted. Measured ceiling, not a defect
    claim — the gate is a receipt-shape gate, not a content-authenticity gate."""
    E = []
    r = row_by_case(rows, 'export_launch_embed_boot')
    m = json.loads(json.dumps(r))
    m['output'].append('WARNING: FOREIGN injected=grammar_spoof')
    E.append(('EV1_warning_shaped_forgery', m))
    m = json.loads(json.dumps(r))
    m['output'].append('ERROR: unrelated injected diagnostic')
    E.append(('EV2_error_shaped_forgery', m))
    # EV3: ERROR-shaped forgery inside the F9 carve-out (mutant_* row) — measured hole
    r_mut = next((x for x in rows if x.get('case', '').startswith('mutant_')), None)
    if r_mut is not None:
        m = json.loads(json.dumps(r_mut))
        m['output'].append('ERROR: FOREIGN injected=carveout_spoof')
        E.append(('EV3_error_in_carveout_row', m))
    return E

def run_mutants(mutants, ctx, label, expect=None):
    nflag = 0
    print(f'== {label}: {len(mutants)} mutants')
    for name, rec in mutants:
        f, d = gate_row(rec, ctx)
        if f: nflag += 1
        print(f'   {"FLAG" if f else "CLEAN":5s} {name}: {f if f else "[]"}')
        if not f:
            print(f'         (case={rec.get("case")!r} verdict={rec.get("verdict")!r})')
    print(f'== {label}: flagged {nflag}/{len(mutants)}')
    return nflag

if __name__ == '__main__':
    mode = sys.argv[1] if len(sys.argv) > 1 else 'green'
    if mode == 'green':
        rep = replay_green()
        print('TOTAL FLAGS:', sum(v['flagged'] for v in rep.values()))
    elif mode in ('attacks', 'corrupt', 'allmut', 'evade'):
        run, ctx, rows = load_run(GREEN_RUNS['r102-1'])
        if mode in ('attacks', 'allmut'):
            run_mutants(build_attacks(rows), ctx, 'attacks')
        if mode in ('corrupt', 'allmut'):
            run_mutants(build_corrupt(rows), ctx, 'corrupt')
        if mode == 'evade':
            run_mutants(build_evasions(rows), ctx, 'evasions (expected CLEAN — documented ceiling)')
    else:
        print('usage: gate.py [green|attacks|corrupt|allmut|evade]')
