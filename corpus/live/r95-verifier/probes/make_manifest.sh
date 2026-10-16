#!/usr/bin/env bash
# Build RECEIPTS.md + manifest.sha256 for corpus/live/r95-verifier.
# Scope: every receipt/artefact, excluding regenerable trees
#   (battery scratch copies, the frozen extraction, the gate-mutant copy)
# which are covered by MANIFEST-SCOPE.txt.
set -euo pipefail
V="$(cd "$(dirname "$0")/.." && pwd)"
cd "$V"

cat > MANIFEST-SCOPE.txt <<'EOF'
manifest.sha256 covers every file under corpus/live/r95-verifier/ EXCEPT:
  - runs/*/scratch/**            battery scratch copy of the fixtures (regenerable; byte-identical to freeze/corpus/fixtures)
  - scratch-arms/**              fresh-arms scratch copy (same staging recipe)
  - freeze/**                    git archive of 9cd47507 corpus/fixtures (83 files; blob-identity verified in freeze/blob-identity-mismatches.txt = 0 mismatches)
  - gate-mutant/**               the mutant harness copy (regenerable by probes/make_gate_mutant.py; build log probes/gate-mutant-build.txt)
  - manifest.sha256, RECEIPTS.md themselves
Every other file (probes, run verdicts/logs, arm receipts, gate-mutant run, analysis outputs) is covered.
EOF

find . -type f \
  ! -name 'manifest.sha256' ! -name 'RECEIPTS.md' ! -name 'MANIFEST-SCOPE.txt' \
  ! -path './runs/*/scratch/*' ! -path './scratch-arms/*' \
  ! -path './freeze/*' ! -path './gate-mutant/*' \
  -print0 | sort -z | xargs -0 sha256sum > manifest.sha256
echo "manifest entries: $(wc -l < manifest.sha256)"

{
  echo "# corpus/live/r95-verifier — receipts index (r95 verifier)"
  echo
  echo "Scope: see MANIFEST-SCOPE.txt. \`manifest.sha256\` — $(wc -l < manifest.sha256) entries."
  echo
  echo "| artefact | files | notes |"
  echo "|---|---|---|"
  for d in freeze probes arms runs runs-mutant gate-mutant; do
    [ -d "$d" ] || continue
    n=$(find "$d" -type f | wc -l)
    echo "| \`$d/\` | $n | |"
  done
  echo
  echo "## key files"
  echo
  for f in probes/audit-cases.json probes/cases-delta.txt probes/audit-committed.txt \
           probes/tail-check.txt probes/signature-coverage.json probes/signature-coverage.txt \
           probes/discrimination.json probes/discrimination.txt probes/laws.json probes/laws.txt \
           probes/fresh-arms.json probes/row-stability.txt probes/summarize_runs.py \
           probes/gate-mutant-build.txt probes/receipt-rc.txt probes/receipt-passline-uniq.txt \
           probes/forgery-hygiene.txt probes/result-order.txt probes/receipt-batches.txt \
           freeze/blob-identity-mismatches.txt freeze/ls-tree.txt; do
    [ -f "$f" ] && echo "- \`$f\`"
  done
  echo
  echo "## battery runs"
  echo
  for v in runs/*/verdicts.json runs-mutant/*/verdicts.json; do
    [ -f "$v" ] && echo "- \`$v\`"
  done
} > RECEIPTS.md
echo "RECEIPTS.md written"
