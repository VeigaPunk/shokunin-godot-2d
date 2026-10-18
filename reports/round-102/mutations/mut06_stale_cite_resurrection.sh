#!/usr/bin/env bash
# mut06 — r102 / seat M6: stale-cite resurrection mutation against the OFFICIAL S4 gate.
#
# Official gate (r102-S4.md §6): after the T1 apply this must print NOTHING (exit 1):
#   grep -rn -F '.shokunin/' SCORECARD.md PROVINCE.md corpus/lessons/*.md corpus/fixtures \
#        README.md corpus/README.md SHONEN.md corpus/knowledge
#
# Harness (read-only wrt the repo; scratch under /var/tmp/r102-mut6/gate):
#   A1 baseline on a rev-1392ca21 surface                 (expect 25 lines)
#   A2 repair via the landed S4 pairs artifact            (expect 0, exit 1)
#   A3 resurrect SCORECARD.md:8 (canonical mut06)         (expect 1, named)
#   A4 resurrect corpus/lessons/r10-export-launch.md:3    (expect 1, named)
#   A5 variant '.shokunin/game-dev-2d/fixtures/' in README (official gate catches; narrow token misses)
#   A6 variant 'cd .shokunin/game-dev-2d/corpus' in README (same split)
# Cross-checks against the S4 shard: pre-apply 25 lines [S4 §6]; 353 pairs / 52 files / 384 LEAVE.
set -u

SCRATCH="${1:-/var/tmp/r102-mut6/gate}"
REPO="${2:-$(cd "$(dirname "$0")/../.." && pwd)}"
REV="${PRISTINE_REV:-1392ca21}"
S4_PAIRS="$REPO/reports/round-102/mutations/s4_cite_pairs.txt"
[ -f "$S4_PAIRS" ] || { echo "FAIL: landed pairs artifact missing: $S4_PAIRS"; exit 2; }

echo "# mut06 (official-gate edition) — $(date -u +%FT%TZ) — scratch=$SCRATCH rev=$REV"
uptime
git -C "$REPO" status --porcelain corpus/lessons corpus/knowledge | head -3

rm -rf "$SCRATCH"
mkdir -p "$SCRATCH/corpus"
for f in SCORECARD.md PROVINCE.md README.md SHONEN.md corpus/README.md; do
  git -C "$REPO" show "$REV:$f" > "$SCRATCH/$f"
done
cp -r "$REPO/corpus/lessons" "$SCRATCH/corpus/lessons"
cp -r "$REPO/corpus/fixtures" "$SCRATCH/corpus/fixtures"
[ -d "$REPO/corpus/knowledge" ] && cp -r "$REPO/corpus/knowledge" "$SCRATCH/corpus/knowledge"

cat > "$SCRATCH/editpairs.py" <<'PY'
import pathlib, sys
scratch, pairs = pathlib.Path(sys.argv[1]), sys.argv[2]
mode = sys.argv[3] if len(sys.argv) > 3 else "repair"
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
        if mode == "repair" and cur[n-1].rstrip("\n") != before:
            moved += 1; print("CONTENT-MOVED", key)
        cur[n-1] = (before if mode == "resurrect" else after) + "\n"
        p.write_text("".join(cur), encoding="utf-8")
        applied += 1; fset.add(f)
    else:
        i += 1
print(f"{mode}: pairs={applied} files={len(fset)} content_moved={moved}")
PY

s4gate() { ( cd "$SCRATCH" && grep -rn -F '.shokunin/' SCORECARD.md PROVINCE.md corpus/lessons/*.md corpus/fixtures README.md corpus/README.md SHONEN.md corpus/knowledge 2>/dev/null ); }
narrow() { ( cd "$SCRATCH" && grep -rn -F '.shokunin/game-dev-2d/corpus/' SCORECARD.md PROVINCE.md corpus/lessons/*.md corpus/fixtures README.md corpus/README.md SHONEN.md corpus/knowledge 2>/dev/null ); }

arm() { # $1 label
  local o n1 o2 n2
  o=$(s4gate);  n1=$(printf '%s\n' "$o" | grep -c . || true)
  o2=$(narrow); n2=$(printf '%s\n' "$o2" | grep -c . || true)
  echo "ARM[$1] official_lines=$n1 narrow_token_lines=$n2"
  [ -n "$o" ] && printf '%s\n' "$o" | head -6 | cut -c1-170
  [ "$n1" -gt 6 ] && echo "  ... ($n1 total)"
}

echo; echo "== A1 baseline (rev $REV operative surface) =="; arm A1-pristine
echo; echo "== A2 repair via landed pairs (353) =="
python3 "$SCRATCH/editpairs.py" "$SCRATCH" "$S4_PAIRS" repair
arm A2-repaired

echo; echo "== A3 resurrection: SCORECARD.md:8 =="
python3 "$SCRATCH/editpairs.py" "$SCRATCH" "$S4_PAIRS" resurrect "SCORECARD.md:8"
cmp -s <(sed -n 8p "$SCRATCH/SCORECARD.md") <(git -C "$REPO" show "$REV:SCORECARD.md" | sed -n 8p) \
  && echo "byte-fidelity SCORECARD.md:8 == rev: IDENTICAL" || echo "byte-fidelity: DIFFERENT"
arm A3-mut1
python3 "$SCRATCH/editpairs.py" "$SCRATCH" "$S4_PAIRS" repair "SCORECARD.md:8" >/dev/null; arm A3-restored

echo; echo "== A4 resurrection: corpus/lessons/r10-export-launch.md:3 =="
python3 "$SCRATCH/editpairs.py" "$SCRATCH" "$S4_PAIRS" resurrect "corpus/lessons/r10-export-launch.md:3"
cmp -s <(sed -n 3p "$SCRATCH/corpus/lessons/r10-export-launch.md") <(git -C "$REPO" show "$REV:corpus/lessons/r10-export-launch.md" | sed -n 3p) \
  && echo "byte-fidelity lessons/r10-export-launch.md:3 == rev: IDENTICAL" || echo "byte-fidelity: DIFFERENT"
arm A4-mut2
python3 "$SCRATCH/editpairs.py" "$SCRATCH" "$S4_PAIRS" repair "corpus/lessons/r10-export-launch.md:3" >/dev/null; arm A4-restored

echo; echo "== A5 variant: '.shokunin/game-dev-2d/fixtures/' appended to README.md =="
printf 'Near-miss probe: python .shokunin/game-dev-2d/fixtures/run_battery.py\n' >> "$SCRATCH/README.md"
arm A5-near-miss
git -C "$REPO" show "$REV:README.md" > "$SCRATCH/README.md"

echo; echo "== A6 variant: 'cd .shokunin/game-dev-2d/corpus' appended to README.md =="
printf 'Near-miss probe 2: cd .shokunin/game-dev-2d/corpus\n' >> "$SCRATCH/README.md"
arm A6-no-slash
git -C "$REPO" show "$REV:README.md" > "$SCRATCH/README.md"
arm A6-restored

echo; echo "== cross-pins =="
sha256sum "$REPO/reports/round-102/mutations/s4_fix_stale_citations.py" | cut -c1-80
echo "S4 shard claims: pre-apply gate 25 lines; 353 pairs / 52 files / 384 LEAVE  (r102-S4.md §6, manifest)"
