# game-dev-2d round 75 — author (seat: author; host: devin)

## Declared move (verbatim)

"r75 AUTHOR (g2d) — deferred interior-write cells + containment lattice …
ARM — `love_battery.py` + `love_phys_probe/` extension (insertion-only;
prior cells byte-identical; fatal cells still last, per-cell process
isolation kept):
- critic C1 additive twins: `bc_destroy_unp` (unprotected destroy inside
  a callback — predicted deferred-drain class) and `bc_setvel_unp`
  (predicted applied). Pin the MEASURED class, falsify the prediction
  honestly if it lands elsewhere.
- critic C3 containment-level cell: pcall wrapping `world:update` vs
  pcall wrapping the interior write — the same write reads as
  `refused` under one containment and `refuse-with-step-abort` under
  the other. Pin the level-relative class partition.
- `esc_fn` pin on unp rows: the escape-function identity as evidence.
- joints surface (stretch): joint create/destroy inside callbacks;
  `Fixture:setFilterData`; `preSolve` return-false — arm only what
  lands falsifiably, record the rest as blocked.
Report -> reports/round-75/r75-author.md."

All five items armed — nothing left blocked. Every prediction confirmed by
measurement; two new expected classes added where the landed partition had
no honest bucket (`refused_abort`, `ignored`).

## Landed changes

- `corpus/fixtures/love_phys_probe/main.lua` (+100/−3; the 3 removed
  lines are anchors, not prior emissions):
  - `c_pre` one-liner → same body + `if retfalse_mode then return false end`
    (returns `nil` for every other cell — prior receipts unaffected).
  - `world:update(FIXED)` → `uok,uerr = wp_mode and pcall(world.update,…) or
    bare world:update(FIXED)` — non-wp cells run the identical bare call.
  - `if fired and …` guard → `if uok and fired …` (`uok` is always true
    outside wp_mode).
  - New locals: `wp_mode`, `retfalse_mode`, `wp_aborted/wp_recovered`,
    `j_pre`. New `do_mutation` branches: `destroy_unp`, `setvel_unp`
    (r74-critic v2 tag reuse — emit `cb_destroy`/`cb_setvel` so the
    classifier needs no special-casing), `setpos_wp`, `joint_new`,
    `joint_destroy`, `setfilter`, `retfalse`. `jdrain` witness line
    (post-update `jcount`+`isDestroyed`, conditional on `j_pre`).
    `setpos_wp`'s escaped err is emitted stripped (`gsub("^[^:]+:%d+: ")`)
    so `wpcall.err`/`wp_setpos.err` equal the contained cells' pinned text
    byte-for-byte; the raw location is kept as unpinned evidence
    (`srcline=`).
- `corpus/fixtures/love_battery.py` (+153/−8; removed lines = 6 comment
  lines in the IW_CELLS header + the two unp rows' closing pin lines,
  re-added with `esc_fn` appended — no prior row or pinned value removed):
  - 7 new `IW_CELLS` rows (table order: the 5 non-fatal contained cells,
    then the two C1 `*_unp` twins, then the two fatal cells LAST — fatal
    spawn order preserved).
  - `iw_classify`: two new expected classes — `refused_abort` (requires the
    full wp witness: update_ok=false + locked_after=true + wp_setpos.ok
    refusal + wpext collateral refusal + wpcall_next recovery; anything
    less → `anomaly`, never a silent `refused`) and `ignored` (requires
    `cb_retfalse.returned=false` AND the impulse actually landing:
    `after_update.b1vel` y-component < 0 — the suppressed-control value is
    positive, so a binding that honors the return classifies `anomaly`).
  - `cb_joint_destroy` deferred variant: `jdrain.jcount` ==
    `jcount_before − 1` AND `jdrain.isDestroyed == "true"`.
  - Mut tag tuple gains `cb_joint_new`, `cb_joint_destroy`, `cb_setfilter`.
  - `iw_flat_extras`: `esc_fn` = first quoted `in function '<name>'`
    traceback frame (r74 critic C4; boot.lua's `<…>` frames can't match);
    pinned on both unp rows.
  - Docstring: r75 paragraph (class scope, level-relative refused).
- `corpus/fixtures/love_probe/`, `pygame_*` UNTOUCHED (control).

## Measured result (44/44 PASS, 4 stable reps)

15 CASES + 4 splice + 25 IW cells. Concatenated `iw-*.stdout.txt` sha256
identical across all 4 run dirs:
`74db3f10331228a08b8072c25f797dca62a518b65f17e60d35aee583d6469004`.
New-cell receipts byte-identical across all 4 reps AND against the
pre-landing scratch runs (`corpus/live/r75-author/cells/`), modulo
`srcline` (unpinned evidence: the escape's file line differs scratch↔landed
by construction — exactly why it is not pinned).

The measured r75 partition additions (this host, LOVE 11.5):

| cell | predicted | measured | decisive pins |
|---|---|---|---|
| bc_destroy_unp | deferred | **deferred** ✓ | ok=true in-cb, count 4→3 only after update, drain `evpin_ec locked=false step=73`, b1pos=ERR |
| bc_setvel_unp | applied | **applied** ✓ | vel_after=55,-7; after_update.b1vel=55,-7 (x-vel persists — effect-bearing, closes r74-critic's legality-only nit) |
| bc_setpos_wp | refuse-with-step-abort | **refused_abort** (new class) | wpcall update_ok=false + locked_after=**true** (transient lock), wpext.ok=false (an unrelated LEGAL exterior write refused as collateral), wpcall_next update_ok=true step=74, final pre/post=37 (vs 36/36) |
| bc_joint_new | refused (world-level assert) | **refused** ✓ | `IsLocked() == false` (no `m_world->` prefix — world-level fn like newBody), jcount 0→0 |
| bc_joint_destroy | deferred? | **deferred** ✓ | ok=true, isDestroyed_in_cb=**false**, jcount 1→1 in-cb; `jdrain jcount=0 isDestroyed=true` in the update epilogue |
| bc_setfilter | unknown | **applied** | ok=true filter_after=2,2,0 — NOT locked-asserted on this build; effect witness: refilter tunnels b1 through the ground (`final.b1pos y=635.16 > 540`, bc=4/ec=3 vs baseline 5/4) |
| pre_retfalse | ignored (Box2D PreSolve is void) | **ignored** (new class) | `after_update.b1vel=0,-611.09…` = the full impulse landed (contrast `pre_contactmask` suppressed `0,763.87`); final pre/post counts identical to baseline |

Level-relative partition now pinned: the same `setPosition` write is
`refused` under callback-level pcall (step continues: b1pos 400,511.13)
and `refused_abort` under update-level pcall (step aborted: b1pos
400,509.53 on recovery, transient lock, collateral refusal). C3's
collision is closed as a class distinction, not a docstring scope.

`esc_fn` pins verified live: `iw_bc_setpos_unp` → `setPosition`,
`iw_bc_newbody_unp` → `newBody` (44/44 runs pass them).

## Prior-cell byte-identity accounting

- 16/18 prior iw receipts byte-identical vs r74 run dirs (verified per
  file with `cmp`).
- The 2 `*_unp` receipts differ ONLY in traceback line numbers
  (`main.lua:91`→104, `:95`→108, `:174`→237, `:179`→242, `:220`→294) —
  insertions above the escape sites shift Lua's source refs; the
  function names, `Error:` text, rc=1, empty stderr, and every pinned
  key are unchanged (this drift is structural to ANY additive extension;
  `esc_fn` is precisely the pin that is immune to it).
- `probe.stdout`/`splice-*` differ only in bound-checked ms jitter —
  pre-existing: r74's own run1-vs-run4 `probe.stdout` shows the same
  jitter class (`dt_max_ms`, `l1_wait_ms`, `total_ms`, `osx ms`).

## Evidence

- `python3 corpus/fixtures/love_battery.py --runs corpus/live/r75-author/runs`
  → `totals: cases=44 pass=44 fail=0 launch_ok=True done_marker=True
  exit=0`, battery exit 0, ~15s, ×4 reps:
  `love-20261014T173642593012Z`, `…T173738748447Z`, `…T173748952061Z`,
  `…T173810495744Z`. Per-run `verdicts.json` + `iw-<cell>.{stdout,stderr}.txt`.
- Pre-landing measurement: `IW_CELL=<c> timeout -s KILL 15 love
  corpus/live/r75-author/scratch_probe` → receipts in
  `corpus/live/r75-author/cells/*.r{1,2,3}` — every armed cell
  byte-identical across ≥2 reps before landing (joint_destroy ×3).
- API surface verified first: `corpus/live/r75-author/api_probe/` —
  `newDistanceJoint`/`getJointCount`/`setFilterData`/`getFixtures`/
  `isDestroyed` all present on this build (receipt in dir).
- Sibling corroboration (verified): `corpus/live/r74-critic/cells/
  m_unp_v2.*` receipts — my landed `bc_destroy_unp`/`bc_setvel_unp`
  reproduce them field-for-field; `m_wp_v2.bc_setpos_wp` same shape
  modulo the tag cleanup + stripped err documented above.
- `git diff --numstat corpus/fixtures/`: battery 153/8, probe 100/3.
  Removed lines enumerated in this report — anchors only. Nothing
  committed (leaf seat).
- `lsp` disclosure (unchanged host state): no LSP servers on PATH; all
  edits additive insertions or 3 named anchor lines; names verified by
  4 green battery runs.

## Remaining unknowns / risks

- `bc_joint_destroy`'s scene perturbation: the pre-built b2↔b3 distance
  joint changes b2/b3 dynamics for that cell only (`final.b2pos`
  −766,2284; bc/ec=8/8, pre/post=172) — deterministic ×4, but the pin
  deliberately avoids those downstream values and stands on the
  drain-witness triple (jcount 1→1→0, isDestroyed flip). A scene edit
  must re-derive.
- `setpos_wp` `srcline`/`wpcall.step` and the two unp traceback numbers
  are file-layout values — `srcline` is emitted unpinned for exactly
  this reason; the `wpcall.step`/`final.pre`/`post` pins are
  scene-deterministic, not layout-dependent.
- `bc_setfilter` is `applied` ON THIS BUILD (loveAssert-unconditional +
  Box2D filter refilter unguarded inside the lock). A build that guards
  it → `ok=false` → measured FAIL (intended). The tunneling witness
  (`final.b1pos` y>540) is an effect pin, not just legality.
- `pre_retfalse` returns false on EVERY preSolve for that cell (return
  ignored → zero effect, counts identical to baseline). If a future
  LÖVE consumes the return, ALL contacts get masked — the
  `after_update.b1vel` pin (negative y = impulse landed) and
  `ignored`-vs-`anomaly` classification catch it.
- `died`/`fatal` semantics unchanged; `esc_fn` scans stdout only —
  a SIGABRT-shape death (`terminate called …` on stderr) still
  classifies `died` and its `esc_fn` reads `none`.
- pygame battery untouched (control). No git mutations.

## Blockers

None — all five assignment items armed and green; nothing recorded as
blocked (joint create/destroy, setFilterData, and preSolve return-false
all landed falsifiably).
