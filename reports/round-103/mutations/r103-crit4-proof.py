#!/usr/bin/env python3
"""r103-C4 proof: (1) author the print-verb candidate for the two probe reject
arms at HEAD 6e3e87f7, (2) prove the diff is print-only, (3) measure the verb
mapping matrix, (4) measure patch-order independence vs
reports/round-103/mutations/w5_export_div.patch.

NEVER executes corpus/fixtures/run_battery.py (hard rule 1). Static + scratch only.
"""
import difflib, hashlib, py_compile, subprocess
from pathlib import Path

REPO = Path("/home/vgpnk/Projects/shokunin/game-dev-2d-shokunin")
WT = Path("/var/tmp/r103c-C4/wt")
HEAD = "6e3e87f7"
W5 = REPO / "reports/round-103/mutations/w5_export_div.patch"
CAND = Path("/var/tmp/r103c-C4/r103-crit4-printfix-candidate.patch")  # scratch only; S4 patch is the record
REL = "corpus/fixtures/run_battery.py"
PRINT = 'print(f"{\'PASS\' if inner else \'FAIL\'} {label}: exit={code} classification={inner}", flush=True)'

pristine = subprocess.run(["git", "-C", str(REPO), "show", f"{HEAD}:{REL}"],
                          capture_output=True, text=True, check=True).stdout
lines = pristine.splitlines(keepends=True)
hits = [i for i, l in enumerate(lines) if l.strip() == PRINT]
assert len(hits) == 2, f"print sites: {hits}"

DESIGN = {}
for i in hits:
    back = "".join(lines[max(0, i - 20):i])
    tok = [t for t in ("godot_error_unrelated", "stream_reject") if t in back]
    assert len(tok) == 1, (i, tok)
    DESIGN[i] = tok[0]
assert set(DESIGN.values()) == {"godot_error_unrelated", "stream_reject"}, DESIGN
print(f"[obs] print sites at HEAD lines {[i+1 for i in hits]} -> designed rejects {DESIGN}")

patched = list(lines)
for i in sorted(hits, reverse=True):
    ind = lines[i][:len(lines[i]) - len(lines[i].lstrip())]
    patched[i] = ind + f'verb = "PASS" if inner else ("REJECT-ARM" if label in ("{DESIGN[i]}",) else "FAIL")\n'
    patched.insert(i + 1, ind + 'print(f"{verb} {label}: exit={code} classification={inner}", flush=True)\n')

diffs = [l.rstrip("\n") for l in difflib.unified_diff(lines, patched, n=3)
         if l[:1] in "-+" and not l.startswith(("---", "+++", "@@"))]
removed = [l[1:] for l in diffs if l.startswith("-")]
added = [l[1:] for l in diffs if l.startswith("+")]
assert len(removed) == 2 and set(l.strip() for l in removed) == {PRINT}, removed
assert all(l.strip().startswith(('verb = "PASS" if inner else', 'print(f"{verb} {label}:')) for l in added), added
bad = [l for l in diffs if __import__("re").search(r"meta_pass|inner_classification|same_script|verdict|emitted_", l)]
assert not bad, bad
print(f"[obs] diff lines: -{len(removed)}/+{len(added)}; verdict-logic lines touched: {len(bad)}")
for l in removed:
    print(f"  -{l.strip()}")
for l in added:
    print(f"  +{l.strip()}")

for site, i in zip(("godot_error", "stream"), hits):
    d = DESIGN[i]
    f = lambda inner, label, d=d: "PASS" if inner else ("REJECT-ARM" if label in (d,) else "FAIL")
    acc = {"godot_error_unrelated": "godot_error_expected_negative", "stream_reject": "stream_accept"}[d]
    for name, lab, inner in (("accept arm inner=True ", acc, True), ("designed reject inner=False", d, False),
                             ("designed reject inner=True ", d, True), ("accept arm inner=False ", acc, False)):
        print(f"[obs] {site:12s} {name} -> {f(inner, lab)}")

CAND.write_text("".join(difflib.unified_diff(lines, patched,
                                            fromfile=f"a/{REL}", tofile=f"b/{REL}", n=3)))
print(f"[obs] candidate patch written: {CAND} ({len(CAND.read_text().splitlines())} lines)")
tmp = Path("/var/tmp/r103c-C4/patched_run_battery.py")
tmp.write_text("".join(patched))
py_compile.compile(str(tmp), doraise=True)
print(f"[obs] py_compile OK on patched copy; patched sha256 {hashlib.sha256(tmp.read_bytes()).hexdigest()}")

def sh(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def git(*a, check=True):
    r = subprocess.run(["git", "-C", str(WT), *a], capture_output=True, text=True)
    if check and r.returncode:
        raise SystemExit(f"git {' '.join(a)} rc={r.returncode}: {r.stderr}")
    return r

git("checkout", "--", REL)
r = git("apply", "--check", "-v", str(CAND), check=False)
print(f"[obs] pristine-tree candidate check rc={r.returncode} {r.stderr.strip()[:120]}")
assert r.returncode == 0 and len(CAND.read_text().splitlines()) == 22
print(f"[obs] wt clean: {git('status', '--porcelain').stdout.strip()!r}")
# ---- order A: w5 first (real apply), then candidate ----
r = git("apply", "-v", str(W5), check=False)
assert r.returncode == 0, r.stderr
print(f"[obs] orderA step1: applied w5 -> {git('status', '--porcelain').stdout.strip()}")
r = git("apply", "--check", "-v", str(CAND), check=False)
print(f"[obs] orderA step2: git apply --check candidate onto w5-applied tree rc={r.returncode}\n      {r.stderr.strip()}")
assert r.returncode == 0
r = git("apply", "-v", str(CAND), check=False)
print(f"[obs] orderA step3: apply candidate rc={r.returncode}\n      {r.stderr.strip()}")
assert r.returncode == 0
shaA, linesA = sh(WT / REL), sum(1 for _ in (WT / REL).open())
# ---- order B: candidate first, then w5 ----
git("checkout", "--", REL)
r = git("apply", "-v", str(CAND), check=False)
assert r.returncode == 0, r.stderr
r = git("apply", "--check", "-v", str(W5), check=False)
print(f"[obs] orderB step2: git apply --check w5 onto candidate-applied tree rc={r.returncode}\n      {r.stderr.strip()}")
assert r.returncode == 0
r = git("apply", "-v", str(W5), check=False)
assert r.returncode == 0, r.stderr
shaB, linesB = sh(WT / REL), sum(1 for _ in (WT / REL).open())
print(f"[obs] orderA (w5 then candidate) sha256 {shaA} lines {linesA}")
print(f"[obs] orderB (candidate then w5) sha256 {shaB} lines {linesB}")
print(f"[obs] ORDER-FREE: {shaA == shaB}")
git("checkout", "--", REL)
print(f"[obs] wt restored; dirty: {git('status', '--porcelain').stdout.strip()!r}")
