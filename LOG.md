# game-dev-2d append-only log

## Mint 2026-10-12
- Explicit operator directive; no craft round, no verdict or promotion yet.
- Evidence: .shokunin/mints/game-dev-2d.md; seed knowledge: corpus/knowledge/seed.md.
- Lane git identity for all round commits: game-dev-2d-shokunin <game-dev-2d@shokunin.local>.
- Next falsifiable move: declare one axis-move claim, cite before/after, named non-author review, L1 closure.

## Round 1 — 2026-10-12 — coverage
- Claim: “A scratch-copy Godot battery detects a broken scene route and records machine-readable PASS/FAIL verdicts for the seeded fixtures without modifying them.”
- Before: no executable runner or verdict JSON; 29 inherited fixture files only (`git ls-tree -r --name-only 87c49620 .shokunin/game-dev-2d/corpus/fixtures | wc -l`); first unadjusted runner attempt 8/15 PASS (`corpus/lessons/r1-initial.json`).
- After: 15/15 PASS including a targeted broken-scene mutation with exit 2 and `chain incomplete`; `corpus/lessons/r1-passing.json`, reproduced by `python .shokunin/game-dev-2d/corpus/fixtures/run_battery.py --probe-failing`. Two scratch-only compatibility steps are documented in `corpus/lessons/r1-headless-verification.md`.
- Verdicts: coverage **improved** (new serial verified fixtures and mutation detection); depth **improved** (cited decision/error tables and agent checklist); calibration **unchanged** (no untested production features claimed). No harmed axis. Admitted subject to named non-author rerun.
- Named non-author verifier `game-dev-2d-r1-verifier` (openai-codex/gpt-6-luna) independently reran 15/15 PASS, confirmed targeted exit-2 mutant, all cited paths and clean seeded fixtures; defects: none. SHONEN boxes remain unchecked; verifier of round evidence is not an operator-appointed promotion reviewer.
- Next falsifiable move: measure camera-follow positioning and demonstrate a no-follow mutant detected under Godot headless while leaving inherited seeds untouched.
