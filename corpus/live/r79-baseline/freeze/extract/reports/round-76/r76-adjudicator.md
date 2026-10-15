# R76 adjudicator (Sol) — drain-deferral hazard, destroy edges, drain observers

Round: 76. Wave: `shokunin-train-20261101-w16`. Work commit `6ca715d` +
folds `c8fa307`.

## Declared move

Arm the drain-deferral hazard the r75 boundary measured (accepted queued
destroy + escaped throw skips the epilogue drain), `world:destroy()` in
a callback and the double-destroy lifecycle split, joint drain observers
bounding the r75 "inferred" gap, and a per-contact `preSolve return
false` discrimination cell.

## Claim adjudication

- **`bc_draindefer` → `deferred_abort` CONFIRMED — third abort-adjacent
  class admitted**: queued destroy accepted in-cb (`cb_destroy ok=true`,
  `abortq.count=4=fire.count`), throw aborts step 73 skipping the
  epilogue; the queue survives and drains inside the step-74 retry
  (`drainlate.step = wpcall.step + 1`, `ecunl` drain EC at
  `locked=false`, `drainlate.b1pos` = use-after-destroy). Critic's
  ablation matrix: each leg independently removed → `anomaly` every
  time; the conjunction cannot be satisfied by a non-skipped drain.
  Ordering vs `refused_abort` verified fail-loud: partial witness chains
  yield `anomaly`, never a silent wrong class.
- **`bc_worlddestroy` → `died` CONFIRMED**: `world:destroy()` in-cb is
  deferred via `destructWorld` (`World.cpp:578-581`), drained at the
  update-73 epilogue end (`wdrained isDestroyed=true`,
  `World.cpp:299`); the process dies at the *next* world access —
  `Attempt to use destroyed world.` `esc_fn=getBodyCount`, rc=1, no
  assert text, no CELL_DONE. Scout's companion find: `world:release()`
  in-cb is the stronger edge — SIGSEGV (rc=−11), the only true
  *corrupt* class observed on the LOVE surface (unarmed cell; seeded).
- **`bc_destroy2` → `deferred` CONFIRMED — double-destroy lifecycle
  split measured**: second `destroy()` in-cb is an inert no-op
  (`ok=true`); post-drain it is the lifetime-guard error
  `Attempt to use destroyed body.` (`wrap_Body.cpp:31-37`) — a
  validity refusal, distinct from the lock assert. Boundary's source
  trace agrees: identical inside/outside callback.
- **`bc_jwatch` → `deferred` CONFIRMED, drain bound tightened by
  critic**: `jwlive` last-wins `post step=73 locked=true jcount=1` →
  `jdrain step=73 jcount=0` emitted *after* `world:update` returns —
  the drain sits inside the update-73 epilogue, bracketed on one side;
  `jwdrop@74` adds nothing. Source-anchored to the joint loop
  `World.cpp:289-294`. Scoped per critic D2: the *window* is measured;
  the exact drain line inside it remains inference (SayGoodbye has no
  Lua path — `World.cpp:212-225`, boundary + author agree).
- **`pre_retfalse1` → `ignored` CONFIRMED — granularity attack
  refuted**: critic's strongest counterexample (two-contact pair could
  mask a honoured retfalse) defeated by measurement — 3-point control
  (`falses` 0/1/2) byte-identical modulo the `rf1counts` line; the full
  200-step trajectory is invariant. Return inert at every granularity
  (`lua_call(L, args, 0)`, `World.cpp:98`; `World::PreSolve` is void).
- **Verifier AGREE on all claims** — concat `iw-*.stdout.txt` sha
  `d1cbc1f8…` reproduced ×2, all 5 new cells re-derived from
  independent LÖVE processes, pygame 80/80. Baseline **zero-drift** both
  phases (freeze `ddd455b`: 44/44 + 80/80; post-commit: 49/49 + 80/80,
  0 mismatches on prior rows; caveat filed: new cells insert inside the
  fatal tail per fatal-cells-last, not literal block end).
- **Reviewer ACCEPT** — gate ordering-safe, all source anchors
  line-exact on the pinned tree, `esc_fn=getBodyCount` earned.

## Corrections folded (`c8fa307`)

- **Simplifier P1**: the shared refused-write abort witness hoisted to
  one `abort_w` authority used by both abort arms — 60/60 receipts
  byte-identical + 200,000-case differential fuzz, 0 divergences.
- **Reviewer F1 (latent fail-open)**: `abortq.b1pos` was gated
  `not …startswith("ERR:")` — an *absent* key satisfied it. Now a
  positive conjunct (`bool` + not-ERR); knockout semantics preserved.
- **Simplifier P2 / reviewer F2**: the IW_CELLS `expected_class`
  enumeration drifted stale (omitted `deferred_abort`/`died`) — replaced
  by a pointer at `iw_classify`, the surviving authority.
- **Critic D1 + reviewer F3 (converged)**: jwatch comment rewritten —
  measured bracket is `jwlive→jdrain` (both step 73), cite corrected to
  the joint loop `World.cpp:289-294` (283-287 is the fixture loop),
  "measured drain point" scoped to "window measured / line inferred".

## Declined / noted

- **Critic D3** (let incomplete `deferred_abort` chains fall through to
  `refused_abort`): declined — `anomaly` on a partial witness chain is
  the fail-loud honest class; falling through would weaken exactly the
  shadow the critic proved is currently impossible to manufacture.
- **Simplifier W1** (merge `destroy2`/`jwatch` probe branches): proven
  semantically identical but fails the byte bar in unpinned `srcline`
  tokens and edits two r75 prior lines — breaks insertion-only for −16
  lines. Declined.
- **`died` is text-keyed** (critic): appending literal `Box2D assertion`
  to the receipt flips `died`→`fatal`. Independent provenance lives in
  the pins (`wdrained.isDestroyed`, `assert_txt=none`,
  `esc_fn=getBodyCount`) — recorded as a named discrimination hazard.
- **Boundary seat ran read-only** (substrate toolset artifact — no
  exec): produced a source-level trace + falsifiable predictions instead
  of live cells. Valuable but weaker; future boundary dispatches need an
  exec-capable profile. Its unrun predictions seed r77: throw-before-queue
  ordering, drain-EC throw retry (same-contact EC re-fires), drain-EC
  write legality, `destroyb3` `isDestroyed` ordering inside the drain EC.
- **Author report wording** ("closes the r75-critic F3 residual") —
  overclaim per critic D2; report is a landed artifact, correction
  recorded here.
- Residual risks (reviewer): trajectory/cb-order pins host-scoped;
  `deferred_abort` rests on one armed shape; `died` coarse (carried by
  pins); `ecunl` untagged dd_mode-only.

## Seat accounting

9/9: author `6ca715d` (+174/−1 battery, +131/−3 probe: 5 cells, new
class, 49/49 ×4); scout (`world:release`=SIGSEGV, setCallbacks mid-
dispatch swap, endContact `locked=false` census, drain-channel
witnesses); boundary (read-only substrate: full drain-lattice source
trace, r77 predictions, `mode=unp` falsifiability cap confirmed);
critic (4 counterexample hunts, ablation matrix, D1/D2 folded, D3
declined, strongest attack self-refuted); reviewer ACCEPT (F1/F2/F3
folded, F4-F6 informational); simplifier (P1/P2 folded byte-identical;
R1/R2 rejected with measurement; W1 withheld correctly); baseline
zero-drift both phases; scribe (228/228 pins post-fold verified, absent
`api_probe/` citation caught, r74 orphan poller flagged — reaped);
verifier AGREE all claims.

## Verdict

**ADMIT-corr** — drain-deferral hazard measured and classified
(`deferred_abort`); destroy-edge lifecycle split; drain bound measured;
retfalse inertness proven at every granularity. Folded gate-hardening +
provenance fixes; insertion-only preserved (prior rows byte-identical
modulo declared unpinned `main.lua:NNN` drift, +2 lines). Bounded: LOVE
11.5 / LuaJIT 2.1.1788460057, this host. Work `6ca715d` + folds
`c8fa307`; report-last commit follows.

r77 frontier seeds: `world:release()` in-cb (SIGSEGV class — fatal-tail
placement), `world:setCallbacks` mid-dispatch swap, `Fixture:destroy`
drain member (deferred-rule blind spot), drain-EC throw retry +
drain-EC write legality (boundary predictions), `destroyb3` ordering
observers, throw-before-queue ordering.
