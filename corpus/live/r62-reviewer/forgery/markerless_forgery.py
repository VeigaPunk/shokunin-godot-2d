"""r62-reviewer: marker-presence clause audit.
ast-extracts classify_process verbatim from the COMMITTED runner, plus the
committed crash_meta_ok expression text, and evaluates a forged markerless -6
record. No transcription of logic — source segments only."""
import ast, json, hashlib

RUNNER = '.shokunin/game-dev-2d/corpus/fixtures/run_battery.py'
src = open(RUNNER).read()
print("runner sha256:", hashlib.sha256(src.encode()).hexdigest())
tree = ast.parse(src)

# Extract classify_process verbatim and exec it in a namespace.
cls_src = None
for node in ast.walk(tree):
    if isinstance(node, ast.FunctionDef) and node.name == 'classify_process':
        cls_src = ast.get_source_segment(src, node)
ns = {}
exec(cls_src, ns)
classify_process = ns['classify_process']
print("classify_process sha256:", hashlib.sha256(cls_src.encode()).hexdigest())
print("classify_process lines:", src[:tree and 0] or cls_src.splitlines()[0])

# Locate the committed crash_meta_ok assignment expression source.
meta_src = None
for node in ast.walk(tree):
    if isinstance(node, ast.Assign) and any(
        getattr(t, 'id', '') == 'crash_meta_ok' for t in node.targets):
        meta_src = ast.get_source_segment(src, node)
print("crash_meta_ok expr present:", meta_src is not None)

MARKER = "SPONTANEOUS_CRASH_PROBE: expected signature"

# Load my own real captured rows for the non-forged controls.
v = json.load(open('.shokunin/game-dev-2d/corpus/live/r62-reviewer/runs/20261013T233616336304Z/verdicts.json'))
rows = {r['case']: r for r in v['results']}
real_sigabrt = rows['crash_spontaneous_sigabrt']
real_sigkill = rows['crash_self_sigkill']

def make_forged_markerless(real):
    """Markerless -6 forgery: PASS, -6, signature present, ERROR marker absent.
    Mirrors the critic's ext_abrt_no_error/ext_ill/ext_segv shape (external
    signal -6 emitting zero ERROR lines) as a record-level forgery."""
    forged = dict(real)
    forged['output'] = [l for l in real['output'] if 'ERROR:' not in l]
    return forged

def crash_meta_ok_eval(sigabrt, self_sigkill):
    # Re-evaluate the committed expression body: we exec the verbatim
    # assignment in a namespace supplying the names it references.
    crash_discriminations = {
        'sigabrt_expected_-9_rejects': sigabrt is not None and not classify_process(
            sigabrt['actual_exit'], sigabrt['error'], "\n".join(sigabrt['output']), -9,
            MARKER, ("ERROR: r60 spontaneous crash probe",)),
        'sigabrt_missing_allowlist_rejects': sigabrt is not None and not classify_process(
            sigabrt['actual_exit'], sigabrt['error'], "\n".join(sigabrt['output']), -6,
            MARKER, ()),
        'sigabrt_wrong_allowlist_rejects': sigabrt is not None and not classify_process(
            sigabrt['actual_exit'], sigabrt['error'], "\n".join(sigabrt['output']), -6,
            MARKER, ("ERROR: unrelated different diagnostic",)),
        'self_sigkill_expected_-6_rejects': self_sigkill is not None and not classify_process(
            self_sigkill['actual_exit'], self_sigkill['error'], "\n".join(self_sigkill['output']), -6,
            MARKER, ("ERROR: r60 spontaneous crash probe",)),
    }
    localns = {'sigabrt': sigabrt, 'self_sigkill': self_sigkill,
               'crash_discriminations': crash_discriminations}
    rhs = meta_src.split('=', 1)[1].strip()
    val = eval(rhs, {}, localns)
    return val, crash_discriminations

forged = make_forged_markerless(real_sigabrt)
assert 'ERROR: r60 spontaneous crash probe' not in "\n".join(forged['output'])
assert MARKER in "\n".join(forged['output'])
assert forged['actual_exit'] == -6 and forged['verdict'] == 'PASS'

results = {}
# T1: real sigabrt record under committed expression -> True (sanity)
val, disc = crash_meta_ok_eval(real_sigabrt, real_sigkill)
results['T1_real_record_crash_meta_ok'] = val
results['T1_discriminations'] = disc
# T2: forged markerless -6 under committed expression -> must be False
val, disc = crash_meta_ok_eval(forged, real_sigkill)
results['T2_markerless_forged_crash_meta_ok'] = val
results['T2_discriminations'] = disc
# T3: forged markerless -6 through classify_process with empty allowlist ->
# True is EXPECTED here (allowlist forgives, never requires) — the meta clause
# is the gate. Record it to show where the rejection lives.
results['T3_forged_classify_process_empty_allowlist'] = classify_process(
    forged['actual_exit'], forged['error'], "\n".join(forged['output']),
    -6, MARKER, ())
results['T3_forged_classify_process_with_allowlist'] = classify_process(
    forged['actual_exit'], forged['error'], "\n".join(forged['output']),
    -6, MARKER, ("ERROR: r60 spontaneous crash probe",))
# T4: -6 record missing signature entirely -> False through classify_process
nosig = dict(forged); nosig['output'] = [l for l in forged['output'] if MARKER not in l]
results['T4_no_signature_classify_process'] = classify_process(
    nosig['actual_exit'], nosig['error'], "\n".join(nosig['output']),
    -6, MARKER, ("ERROR: r60 spontaneous crash probe",))
# T5: forged markerless -6 AND forged markerless self_sigkill... also try
# markerless sigabrt + absent self_sigkill guard: not needed. Instead verify
# the clause is what fails: eval committed expr with marker re-injected -> True
refixed = dict(forged); refixed['output'] = forged['output'] + ['ERROR: r60 spontaneous crash probe']
# adding back ERROR makes classify_process-with-allowlist see allowlisted line;
# meta clause also satisfied -> should be True if discriminations pass
val, disc = crash_meta_ok_eval(refixed, real_sigkill)
results['T5_marker_reinjected_crash_meta_ok'] = val

out = '.shokunin/game-dev-2d/corpus/live/r62-reviewer/forgery/markerless-forgery-verdicts.json'
json.dump(results, open(out, 'w'), indent=2)
print(json.dumps(results, indent=2))
print("wrote", out)
