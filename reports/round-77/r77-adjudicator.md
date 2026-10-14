# R77 adjudicator (Sol) — release/swap/fixture/drain-EC/coroutine/meter lattice

Round: 77. Wave: `shokunin-train-20261101-w17`. Work commit `62201e5`,
folds commit `d48e0fd`.

## Declared move

26 new iw cells arming the r77 scout's pre-measured frontier:
`corrupt` ×5 (world:release() inside engine execution → SIGSEGV
rc=-11, partial receipt, no CELL_DONE — all five channels incl.
natural + drain EC), `swapped` ×4 + `muted` ×1 (setCallbacks is read
per-dispatch: later channels AND later contacts same-step go to the new
table; nil table mutes the surface, physics untouched), `deferred` ×3
(fixture member with fixture-scoped witness set), the drain-EC
legality set (`applied`/`immediate`/`drain_abort` — the deferred rule
is a lock-state rule, not a phase rule), `yield_abort` ×2 +
`died` ×3 + `refused` ×1 (coroutine.resume IS a containment level,
wrap is not), `applied` meter ×2 (ratio witness).

## Claim adjudication

- **All claims CONFIRMED.** 75/75 across author×4, baseline×2,
  reviewer×4, verifier×2, integrator-fold replay — six independent
  executions. Verifier AGREE 5/5 (field-by-field re-derivation of
  corrupt/swapped/drain_abort/yield_abort cells in own processes).
- **Insertion-only verified**: +631/−0 + +422/−0 vs 94356ce; 43/49
  prior rows byte-identical (6 differ in `observed` jitter only);
  declared unpinned `main.lua:NNN` tokens enumerated.
- **Boundary's new hazard independently measured**: nested
  `world:update` inside a callback clears Box2D `e_locked` → writes
  apply, destroy executes immediately, run survives. NOT armed as a
  tracked cell this round — parked to r78 (r78-scout has since fully
  mapped it: inner update owns its own drain; contacting-body destroy
  → Memoizer fatal; depth-2 from body-drain EC = SIGSEGV; zombie
  contact handles = silent UAF).
- **Drain-EC mechanics confirmed**: abort inside drain EC leaves the
  world UNLOCKED with no collateral refusal; queue survives, completes
  one step late, abandoned goodbye re-fires next step at locked=true;
  every-entry abort livelocks (drain_n=aborts, never converges while
  the contact persists).

## Corrections landed (fold `d48e0fd`)

- Simplifier P3: 67 redundant pins removed — each restated a decisive
  gate conjunct; failure attribution moves to class=anomaly, verdicts
  unmoved (byte-identical replay). P1/P2/P4 dead code removed.
- Critic D2: `corrupt` gate now enforces death-site absence
  (`"postfire" not in flat`) — was vacuous to an appended line.
- Critic D3: abortq/drainec count equality now fail-closed on key
  presence (was `None==None`).
- Reviewer F1/F2: process-death ordering wording; docstring class
  enumeration complete.

## Corrections recorded, not folded

- Critic D1: the author's ablation matrix derived `rc` from the
  expected class — degenerate for corrupt rows (8/43 entries could not
  fail). Harness is scratch (untracked); the real gate checks were
  re-verified post-fold by direct receipt mutation (postfire →
  anomaly, absent-count → anomaly, clean → class).
- Critic D4: several r77 conjuncts compare against probe-side literals
  — hygiene note, not a defect (the conjuncts gate on emitted keys,
  just against constants emitted as literals).
- Critic D5 + simplifier P6 (withheld): drain-entry counting is
  entry-granular not contact-granular; dead `r77obs` observer fields —
  cost/byte-bar decisions documented.
- Reviewer N3: the nested-update hazard is documented-unarmed —
  deliberately r78 territory.

## Verdict

**ADMIT-corr** — six new classes land with ablation + fuzz + multi-seat
byte-identical evidence; two real gate defects (D2 vacuity, D3
absent-key) closed in the fold. Bounded: LOVE 11.5, LuaJIT
2.1.1788460057, this host. Work `62201e5` + folds `d48e0fd`;
report-last follows.

r78 frontier (scout-landed): nested-update hole cells (inner drain
ownership, Memoizer fatal, depth-2 SIGSEGV), livelock bound shape,
SayGoodbye/drain-bracket observer cells, contact zombie-handle UAF,
release/destroy survivor lattices.
