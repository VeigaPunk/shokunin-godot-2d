#!/usr/bin/env bash
# mut06b — resurrection discrimination against the LANDED S4 artifact (v2, 184 lines).
# Read-only w.r.t. the repo: the S4 script is copied into a scratch mini-repo at the
# same relative path (its REPO = HERE.parents[3] resolves to the mini-repo), and all
# repair/mutation happens there.
#
# Phases:
#   P0 baseline scan (as-landed script as detector)
#   P1 as-landed --apply attempt  (expected to abort: assert newline mismatch)
#   P2 repair-by-pairs (apply the landed 353 BEFORE->AFTER pairs in the mini-repo),
#      residual scan must be 0; literal grep gate over the S4 T1 surface
#   P3 canonical mutation: resurrect SCORECARD.md:8  -> residual scan names it
#   P4 lesson mutation: resurrect corpus/lessons/r10-export-launch.md:3 -> named
#   P5 minimal repro of the assert mismatch using the module's own functions
#   P6 counterfactual C1: assert-only patch -> apply corrupts (newline drop)
#   P7 counterfactual C2: assert+write patch -> apply clean, residual 0
set -u

SCRATCH="${1:-/var/tmp/r102-mut6/s4repo}"
REPO="${2:-$(cd "$(dirname "$0")/../.." && pwd)}"
REV="${PRISTINE_REV:-1392ca21}"
S4SRC="$REPO/reports/round-102/mutations/s4_fix_stale_citations.py"
PAIRS_ART="$REPO/reports/round-102/mutations/s4_cite_pairs.txt"
MINI_S4="reports/round-102/mutations/s4_fix_stale_citations.py"

[ -f "$S4SRC" ] || { echo "FAIL: S4 script missing: $S4SRC"; exit 2; }
[ -f "$PAIRS_ART" ] || { echo "FAIL: S4 pairs artifact missing: $PAIRS_ART"; exit 2; }

rm -rf "$SCRATCH"
mkdir -p "$SCRATCH/reports/round-102/mutations" "$SCRATCH/corpus"
cp "$S4SRC" "$SCRATCH/$MINI_S4"
rebuild() {
  rm -f "$SCRATCH/SCORECARD.md" "$SCRATCH/PROVINCE.md"
  rm -rf "$SCRATCH/corpus/lessons"
  git -C "$REPO" show "$REV:SCORECARD.md" > "$SCRATCH/SCORECARD.md"
  git -C "$REPO" show "$REV:PROVINCE.md" > "$SCRATCH/PROVINCE.md"
  cp -r "$REPO/corpus/lessons" "$SCRATCH/corpus/lessons"
}
rebuild

cat > "$SCRATCH/editpairs.py" <<'PY'
import pathlib, sys
scratch, pairs = pathlib.Path(sys.argv[1]), sys.argv[2]
mode = sys.argv[3] if len(sys.argv) > 3 else "repair"      # repair|resurrect
key_filter = sys.argv[4] if len(sys.argv) > 4 else None
src = pathlib.Path(pairs).read_text(encoding="utf-8").splitlines()
applied = moved = 0; fset = set()
i = 0
while i < len(src):
    h = src[i]
    if h.startswith("### ") and "NOT-REPAIRABLE" not in h:
        key = h[4:]; before = src[i+1][7:]; after = src[i+2][7:]; i += 3
        if key_filter and key != key_filter: continue
        f, n = key.rsplit(":", 1); n = int(n)
        p = scratch / f
        cur = p.read_text(encoding="utf-8").splitlines(keepends=True)
        if cur[n-1].rstrip("\n") != before:
            moved += 1; print("CONTENT-MOVED", key)
        cur[n-1] = (before if mode == "resurrect" else after) + "\n"
        p.write_text("".join(cur), encoding="utf-8")
        applied += 1; fset.add(f)
    else:
        i += 1
print(f"{mode}: pairs={applied} files={len(fset)} content_moved={moved}")
PY

echo "# mut06b receipt — $(date -u +%FT%TZ) — mini-repo=$SCRATCH rev=$REV"
python3 --version
echo "== source-vs-copy identity =="
sha256sum "$S4SRC" "$SCRATCH/$MINI_S4"

scan() { # dry-run scan of the mini-repo (--tier2); sets LAST_C
  ( cd "$SCRATCH" && python3 "$MINI_S4" --tier2 >/dev/null ) || { echo "SCAN FAILED"; LAST_C="?"; return 1; }
  LAST_C=$(python3 - "$SCRATCH/reports/round-102/mutations/s4_cite_manifest.json" <<'PY'
import json, sys
m = json.load(open(sys.argv[1]))
print(m["changed_lines"])
PY
)
  python3 - "$SCRATCH/reports/round-102/mutations/s4_cite_manifest.json" <<'PY'
import json, sys
m = json.load(open(sys.argv[1]))
print("changed_lines=%d changed_files=%d abs_leave_lines=%d rel_resolved_after=%s"
      % (m["changed_lines"], m["changed_files"], m["abs_leave_lines"], m["rel_targets_resolved_after"]))
PY
}
surface_grep() { ( cd "$SCRATCH" && grep -rnE '\.shokunin/game-dev-2d/(corpus|reports)/' SCORECARD.md PROVINCE.md corpus/lessons 2>/dev/null ); }
rel_count() { echo $(( $(surface_grep | wc -l) - $(surface_grep | grep -c '/home/vgpnk/Projects/prymeagnt/' || true) )); }

echo; echo "== P0 BASELINE scan (as-landed detector) =="
scan; BASE=$LAST_C

echo; echo "== P1 as-landed --apply attempt =="
out=$(cd "$SCRATCH" && python3 "$MINI_S4" --apply --include-shared --tier2 2>&1); ARC=$?
printf '%s\n' "$out" | tail -8
echo "as-landed apply exit=$ARC"

echo; echo "== P2 repair-by-pairs (landed 353 pairs, mini-repo only) =="
python3 "$SCRATCH/editpairs.py" "$SCRATCH" "$PAIRS_ART" repair
scan; POST=$LAST_C
echo "grep gate: token_lines=$(surface_grep | wc -l) absolute=$(surface_grep | grep -c '/home/vgpnk/Projects/prymeagnt/' || true) relative=$(rel_count)"

echo; echo "== P3 MUT1: resurrect SCORECARD.md:8 =="
python3 "$SCRATCH/editpairs.py" "$SCRATCH" "$PAIRS_ART" resurrect "SCORECARD.md:8"
cmp -s <(sed -n 8p "$SCRATCH/SCORECARD.md") <(git -C "$REPO" show "$REV:SCORECARD.md" | sed -n 8p) \
  && echo "byte-fidelity SCORECARD.md:8 == rev: IDENTICAL" || echo "byte-fidelity: DIFFERENT"
scan; MUT1=$LAST_C
echo "relative-class hits after mut1: $(rel_count)"
grep '^### ' "$SCRATCH/reports/round-102/mutations/s4_cite_pairs.txt" | grep -v NOT-REPAIRABLE
python3 "$SCRATCH/editpairs.py" "$SCRATCH" "$PAIRS_ART" repair "SCORECARD.md:8" >/dev/null
scan; REST1=$LAST_C

echo; echo "== P4 MUT2: resurrect corpus/lessons/r10-export-launch.md:3 =="
python3 "$SCRATCH/editpairs.py" "$SCRATCH" "$PAIRS_ART" resurrect "corpus/lessons/r10-export-launch.md:3"
cmp -s <(sed -n 3p "$SCRATCH/corpus/lessons/r10-export-launch.md") <(git -C "$REPO" show "$REV:corpus/lessons/r10-export-launch.md" | sed -n 3p) \
  && echo "byte-fidelity lessons/r10-export-launch.md:3 == rev: IDENTICAL" || echo "byte-fidelity: DIFFERENT"
scan; MUT2=$LAST_C
echo "relative-class hits after mut2: $(rel_count)"
grep '^### ' "$SCRATCH/reports/round-102/mutations/s4_cite_pairs.txt" | grep -v NOT-REPAIRABLE
python3 "$SCRATCH/editpairs.py" "$SCRATCH" "$PAIRS_ART" repair "corpus/lessons/r10-export-launch.md:3" >/dev/null
scan; REST2=$LAST_C

echo; echo "== P5 minimal repro: assert contract (module's own functions) =="
python3 - "$SCRATCH/$MINI_S4" "$SCRATCH/SCORECARD.md" "$SCRATCH/reports/round-102/mutations/s4_cite_pairs.txt" <<'PY'
import importlib.util, pathlib, sys
spec = importlib.util.spec_from_file_location("s4mini", sys.argv[1])
mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
raw = pathlib.Path(sys.argv[2]).read_text().splitlines(keepends=True)[7]   # line 8, keepends
stripped = raw.rstrip("\n")
a_stripped = mod.subst(stripped)    # what scan_file stores as 'after'
a_kept = mod.subst(raw)             # what apply asserts against
print("subst(stripped) == subst(keepends):", a_stripped == a_kept)
print("subst(keepends).rstrip(LF) == subst(stripped):", a_kept.rstrip("\n") == a_stripped)
print("subst(keepends) == subst(stripped)+LF:", a_kept == a_stripped + "\n")
print("tail repr stripped:", repr(a_stripped[-18:]))
print("tail repr keepends:", repr(a_kept[-18:]))
PY

echo; echo "== P6 counterfactual C1: assert-only patch -> corruption check =="
python3 - "$SCRATCH/$MINI_S4" <<'PY'
import pathlib, sys
p = pathlib.Path(sys.argv[1]); s = p.read_text()
old = 'assert subst(lines[n - 1]) == aft'
new = 'assert subst(lines[n - 1].rstrip("\\n")) == aft'
assert s.count(old) == 1
p.write_text(s.replace(old, new))
print("patched: assert-only (rstrip LF)")
PY
rebuild
out=$(cd "$SCRATCH" && python3 "$MINI_S4" --apply --include-shared --tier2 2>&1); ARC1=$?
printf '%s\n' "$out" | tail -2
echo "C1 apply exit=$ARC1  SCORECARD lines now=$(wc -l < "$SCRATCH/SCORECARD.md") (rev=324)  PROVINCE lines now=$(wc -l < "$SCRATCH/PROVINCE.md") (rev=12)"
echo "C1 merged line-8 sample (first 150 bytes):"; sed -n 8p "$SCRATCH/SCORECARD.md" | cut -c1-150

echo; echo "== P7 counterfactual C2: assert+write patch -> clean full cycle =="
python3 - "$SCRATCH/$MINI_S4" <<'PY'
import pathlib, sys
p = pathlib.Path(sys.argv[1]); s = p.read_text()
old = '                lines[n - 1] = aft\n'
new = '                lines[n - 1] = aft + "\\n"\n'
assert s.count(old) == 1
p.write_text(s.replace(old, new))
print("patched: write (preserve LF)")
PY
rebuild
out=$(cd "$SCRATCH" && python3 "$MINI_S4" --apply --include-shared --tier2 2>&1); ARC2=$?
printf '%s\n' "$out" | tail -2
echo "C2 apply exit=$ARC2  SCORECARD lines now=$(wc -l < "$SCRATCH/SCORECARD.md") (rev=324)  PROVINCE lines now=$(wc -l < "$SCRATCH/PROVINCE.md") (rev=12)"
scan; C2POST=$LAST_C
echo "C2 grep gate: token_lines=$(surface_grep | wc -l) absolute=$(surface_grep | grep -c '/home/vgpnk/Projects/prymeagnt/' || true) relative=$(rel_count)"

echo; echo "== mut06b summary =="
echo "residual changed_lines: baseline=$BASE post_repair=$POST restore1=$REST1 restore2=$REST2 mut1=$MUT1 mut2=$MUT2 c2apply=$C2POST"
echo "as-landed apply exit=$ARC (expect nonzero)  C1(+assert) exit=$ARC1  C2(+assert+write) exit=$ARC2"
if [ "$BASE" -gt 0 ] && [ "$POST" -eq 0 ] && [ "$REST1" -eq 0 ] && [ "$REST2" -eq 0 ] && [ "$MUT1" -eq 1 ] && [ "$MUT2" -eq 1 ] && [ "$ARC" -ne 0 ]; then
  echo "MUT06B VERDICT: DETECTOR DISCRIMINATES (resurrection caught, both classes); AS-LANDED APPLY DEFECTIVE"
else
  echo "MUT06B VERDICT: UNEXPECTED — inspect arms above"
fi
