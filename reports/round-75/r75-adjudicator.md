# R75 adjudicator (Sol) — deferred/uncontained callback writes, joints, return surface

Round: 75. Wave: `shokunin-train-20261101-w15`. Work commit `2e3ae8e` +
folds `be79ad1`.

## Declared move

Extend the interior-write lattice to the deferred-class and
containment-level axes the r74 critic deferred: `bc_destroy_unp` /
`bc_setvel_unp` twins (C1), update-level `pcall` containment cell (C3),
`esc_fn` pinning on uncontained rows (C4), joints surface
(`newDistanceJoint`, `joint:destroy`), `Fixture:setFilterData`, and
`preSolve return false` consumption.

## Claim adjudication

- **Deferred twins CONFIRMED — containment inert at byte level**:
  `bc_destroy_unp` → `deferred`, `bc_setvel_unp` → `applied`; both
  receipts byte-identical to their contained twins modulo `cell=`/`kind=`
  labels (reviewer §3.2, independent re-derivation). The strongest form
  of C1 holds: fatal is *derived* (`assert-gated write × uncontained`),
  not a property of uncontained writes alone.
- **Two new classes DISCOVERED and CONFIRMED**: `refused_abort`
  (`bc_setpos_wp` — same assert-gated write contained one level up by a
  `pcall` around `world:update`: step aborts, world transiently locked,
  unrelated legal exterior write refused as collateral, next-step
  recovery) and `ignored` (`pre_retfalse` — preSolve `return false` is
  not consumed by the binding; the full impulse lands,
  `b1vel=0,-611.09…` vs the masked `0,763.87…`; source-anchored by
  boundary at `World.cpp:98` `lua_call(L, args, 0)`).
- **Joints surface CONFIRMED**: `newDistanceJoint` inside cb → refused
  (world-level `IsLocked` assert, no `m_world->` prefix);
  `joint:destroy()` → deferred (jcount 1→0, `isDestroyed` flips after;
  drain *point* inferred — no `locked=false` event exists for joints,
  unlike bodies' synthesized EndContact).
- **`bc_setfilter` CONFIRMED applied**: `setFilterData` is not
  locked-asserted on this build; downstream witness is refilter
  tunneling (final `b1pos y=635.16 > 540`).
- **Verifier AGREE 18/18** on `2e3ae8e`; reviewer ACCEPT (LOW only);
  baseline zero-drift (16/18 prior rows byte-identical; the two `*_unp`
  rows differ only in unpinned `main.lua:` traceback line numbers — raw
  `Error:` lines, declared unpinned, provenance-verified vs `2a2c337`).
- **Battery 44/44 ×4 author reps + verifier/reviewer/critic replays**;
  concat iw receipt sha `74db3f10…9004` reproduced across 5 independent
  run dirs.

## Corrections folded (`be79ad1`)

- **Critic F2 (gate defect, the round's real bug)**: `refused_abort`
  selected by `wpcall.update_ok` key *presence*, shadowing the decisive
  `cb_*` path — 18/130 scout L1 receipts misclassified `anomaly`.
  Folded: gate now requires `update_ok == "false"` (value, not
  presence); emit-once-on-abort declared as the last-wins-safe contract.
  Verified by critic's own sweep: 0/100 landed regressions.
- **Critic F1 (arm identity)**: `fire.kind` pinned on all 21 firing
  rows; unp twins emit `mode=unp` (wrong-branch/misdirected receipts now
  fail the pin). Documented limit: for non-throwing writes the
  containment axis is observational-inert — nothing can witness it; the
  twins' byte-identical-ness IS the measurement.
- **Reviewer F1 (collateral witness)**: `wpext.err` +
  `wpext.pos_after` + `fire.pos` pinned — collateral refusal now carries
  the same assert text with pose untouched.
- **Critic F3 / reviewer F5 (inference wording)**: joint drain "in the
  update epilogue" → "by update end, drain point inferred" across
  docstring, row comment, and the classifier detail string.
- **Reviewer F2 / critic F6a**: three stale "`*_unp` last of all"
  comments → "fatal cells last" (the invariant that matters).
- **Critic F6d**: `after_update.b1vel` pinned on `iw_bc_setvel` — r74
  critic rank-5 now closed on the row it named (was half-closed on the
  twin).
- **Critic F5**: `cb_retfalse.returned` documented as harness echo; the
  landed impulse is the falsifiable witness.
- **Reviewer F4**: per-cell `rc` persisted in `verdicts.json` rows
  (fatal/died discriminator re-derivable from landed receipts — closes
  the r75 scribe witness gap on this surface).
- **Simplifier C3**: `iw_classify` docstring lists `refused_abort` +
  `ignored`.

## Deferred / noted (not folded)

- Critic F2-second-half hardening (dedicated `wp_abort.*` tag immune to
  last-wins): not needed for landed rows (emit-once contract
  documented); queued as optional r76 hardening.
- Critic F6b (author-report describes an `and/or` edit form that would
  be wrong in Lua — the landed `if/else` is correct): report-text note;
  the report is a landed artifact, correction recorded here.
- Reviewer F3 ("bound-checked ms jitter" overstates — `osx.ms`/
  `popen.open_ms` carry no CASES row): wording note for future author
  reports; no fixture change.
- Boundary's drain-deferral hazard (queued destroy + uncontained throw
  in same callback skips the epilogue drain; classifier reads it
  `anomaly` and fails `evpin_ec_step`): a genuine discovered class —
  queued as r76 frontier cell, not folded (additive-cell cost).
- Per-receipt `child.log`-style mutable-slot joins and process-counter
  instability: none apply here; G3D r84 carries the analog.

## Seat accounting

9/9: author `2e3ae8e` (+422/−11: 7 cells, 2 new classes, `esc_fn`
pinned, 44/44 ×4); scout (all reachable pins re-verified byte-identical,
`anomaly`/`refused` collision resolved by `refused_abort`); boundary 62
cells (unp twins byte-inertness measured pre-landing, drain-deferral
hazard + source anchors `World.cpp:98`/`:272-297`, `Body.cpp:529`/
`Fixture.cpp:339`/`Joint.cpp:167`); critic F1–F6 (F2 gate defect +
F1 counterexample both folded); reviewer ACCEPT 6-LOW (F1/F2/F4 folded);
simplifier (C3 folded; correctly kept armed witnesses — "deleting them
would spend the falsifiability axis"); scribe (zero-drift across 2,101
case rows, rc-witness gap → reviewer F4 fold); baseline zero-drift
across love/pygame/frozen families (one external SIGKILL flake
documented, identical-command rerun passed); verifier AGREE 18/18.

## Verdict

**ADMIT-corr** — deferred/uncontained partition confirmed at byte level;
two new classes (`refused_abort`, `ignored`) admitted with full witness
sets; F2 gate defect corrected; arm identity pinned. Bounded: LOVE
11.5-3 / LuaJIT 2.1.1788460057, this host. Work `2e3ae8e` + folds
`be79ad1`; report-last commit follows.

r76 frontier seeds: drain-deferral hazard cell; `world:destroy()`
in-callback/double-destroy; joint/fixture drain observers
(SayGoodbye-instrumented); per-contact `pre_retfalse` variant; optional
`wp_abort` last-wins hardening.
