# R78 adjudicator — nested-update damage surface

Round: 78. Wave: `shokunin-train-20261101-w19`. Work commit `1a03b7a`,
fold commit `1fde57d`.

## Declared move

17 new cells arming the r77 boundary's measured hole — nested
`world:update` inside a callback. Box2D's `e_locked` is cleared by the
INNER update's epilogue, so code after the inner call runs unlocked
mid-dispatch: writes apply, destroys execute immediately, and the
inner update owns its own contact drain. Armed classes:
`nested_lockclear`, `inner_drain`, `dispatch_escape` (Memoizer escape
from the outer dispatch → love throws, rc=1 no signal),
`contact_invalidated`/`contact_live_after_abort` (zombie-contact UAF
is silent), `livelock`, `drain_converge` (abort-every-entry while the
contact persists → drain_n=aborts, converges when it dies),
`corrupt` (nested update from a body-drain EC → SIGSEGV rc=-11),
`refused`, `anomaly`.

## Claim adjudication

- **CONFIRMED.** 92/92 folded battery; author measured 92/92 ×4 plus
  37/37 ablations. Reviewer ACCEPT with F1–F7; verifier (labrat,
  swe-2) confirmed all three falsifications stand at claim/coverage
  level — gates fail closed, never mis-pass.
- **Insertion-only verified.** 56 prior cells: 45 byte-identical, 11
  moved by `srcline=`/`main.lua:NNN` line-token shifts only
  (`bc_setpos_unp`, `bc_draindefer`, `wp_drain_throw`, `wp_coyield`,
  `bc_worlddestroy`, `bc_setpos_unp`, `bc_newbody_unp`, `bc_coyield`,
  `cowrap_update_yield`, `ext_worldrelease`, `bc_cowrap_unp`) — the
  declared drift class; zero semantic drift.
- **Simplifier P1–P4 folded** (−1181 B): dead `ext` fields, a dead
  disjunct, 67 redundant pins, dead params — proven byte-identical
  receipts over 457×100 fuzz evals and 146/146 receipts.

## Fold corrections (critic C1–C3, reviewer F1–F7, labrat findings)

- **C1 (depth-1 vs depth-2 attribution)** — the crash reproduces at
  nested depth 1 from a body-drain EC, not only depth 2. Re-keyed the
  `corrupt` gate on drain-origin provenance (`depth_before`, `own_n`)
  and reworded "depth-2" → "nested update from a body-drain EC".
- **C2 (forgeable drain-EC witness)** — `r78drainec` lines could be
  produced by immediate-destroy EndContacts or foreign processes. Each
  drainec line now carries `own`/`own_n` (the EC drained a destroy the
  cell itself queued); pinned on the affected rows.
  - **Fix defect found mid-fold**: `r78_dead()` returns the strings
    `"true"`/`"false"` — Lua truthiness made `not r78_dead(x)` always
    false, so `own` was everywhere false. Corrected to explicit
    `== "false"` comparisons (three sites); provenance then
    discriminated exactly (queue cells `own=true`,
    immediate-destroy `own=false`).
- **C3 (`drain_converge` without a drain)** — bare numeric conjuncts
  were forgeable. Now requires `r78drainact.kind` in
  {throw,throwall,noop}, `r78wpcall.err` beginning `R78-DRAIN-`,
  `aborts >= 1`, `drain_n >= 1`.
- **C4 (classifier-level fail-opens)** — bounded acceptance: the
  named classifier-level mutation routes fail closed at the verdict
  level (verifier re-ran the mutations against the folded gates);
  classifier-string ablations remain a known coverage limit,
  dispositioned as scope for a later surface pass.
- **Reviewer F1/F2** — corroborate C1/C2; folded.
- **Reviewer/scanner wording** — "drain EC" misnomer on
  immediate-destroy EndContacts corrected; "fatal cells last"
  comments updated; docstring class list completed.
- **Record correction (scribe)** — the r77 fold's D2 conjunct was
  demonstrated *inert* by the scribe (tested a key `parse_iw` never
  emits); the r78 author's re-keyed conjunct is the actually
  discriminating form. Recorded here so r77's ledger reads correctly.
- **Linearity claim** — the "linear in step budget" claim had a
  single step-budget point; report's claim is scoped to the measured
  window (bounded acceptance; second point deferred).

## Verdict

**ADMIT-corr.** The lattice is earned; the fold corrected the
provenance holes the critic demonstrated. Residuals: classifier-level
fail-open routes (C4), linearity pinned at one budget point, and the
love.errorhandler windowed-surface guard proposed for r79 (a stray
windowed love run surfaced the risk this wave — the fatal cells'
stdout class is unchanged by the guard).

## Files

- Work: `1a03b7a` (battery + probe, 17 cells)
- Fold: `1fde57d` (simplifier P1–P4 + C1–C3 + F1–F7)
- Reports: `reports/round-78/r78-{scout,author,boundary,baseline,
  critic,reviewer,scribe,verifier,simplifier}.md`
- Receipts: `corpus/live/runs/` + `corpus/live/r78-*` seat trees.
