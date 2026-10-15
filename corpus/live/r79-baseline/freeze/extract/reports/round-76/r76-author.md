# game-dev-2d round 76 — author (seat: author; host: devin)

Lane `g2d`, wave `shokunin-train-20261101-w16`. HEAD at seat start `ddd455b`
(r75 report-last). Runtime: LOVE 11.5 (`/usr/bin/love`, LuaJIT
2.1.1788460057), Python 3.14.7. Leaf discipline: no subagent, no git
mutation; writes = this report + `corpus/live/r76-author/**` + the two
tracked fixture files.

## Declared move (verbatim)

"r76 AUTHOR (g2d) — drain-observer cells + destroy edges …
ARM — `love_battery.py` + `love_phys_probe/` extension (insertion-only;
all 44 prior cases byte-identical; fatal cells still last):
- drain-deferral hazard cell (r75 boundary): an accepted queued destroy
  PLUS an uncontained throw inside the same callback — the queued
  destroy's epilogue drain is skipped (drains one step late). Arm the
  measured class honestly (it may be `anomaly`-shaped today; if it
  earns a real class, name it).
- `world:destroy()` inside a callback + double-`destroy()` on the same
  body (in-callback then post-update). Pin whatever lands.
- SayGoodbye-instrumented drain observer (stretch): if LOVE 11.5
  exposes `world:setCallbacks`-adjacent joint/fixture destroy
  notification or a per-contact drain event, arm a witness that makes
  the joint drain *point* observed rather than inferred (closes the
  r75-critic F3 residual). If nothing exists, record blocked honestly.
- per-contact `preSolve return false` variant (stretch): return false
  for ONE contact of a multi-contact pair — pin whether the impulse
  mask is contact-scoped or pair-scoped.
Report -> reports/round-76/r76-author.md."

All four items armed — nothing left blocked, one recorded limitation
(SayGoodbye is not exposed; a bounded observer closes the F3 residual
instead — §SayGoodbye below). One new expected class earned:
`deferred_abort` (accepted write + abort + late drain — parallel to
`refused_abort`'s refused write + abort).

## Landed changes

- `corpus/fixtures/love_phys_probe/main.lua` (+131/−3; the 3 removed
  lines are anchors, re-added extended — `local j_pre …` comment,
  `if kind == "joint_destroy"` guard now also `or jw_mode`,
  `if wp_mode` guard now `or dd_mode`; no prior emission path altered):
  - 5 mode flags + 3 helpers (`dd_mode`, `d2_mode`, `wd_mode`,
    `jw_mode`, `rf1_mode`, `jw_prev`, `rf1_falses/passes`, `f_mask`).
  - `do_mutation` gains `draindefer` (pcalled `body:destroy()` then an
    UNCONTAINED `setPosition` — queue + escape in one cb), `destroy2`
    (same emission shape as `destroy`), `worlddestroy` (pcalled
    `world:destroy()` + `isDestroyed`/`getBodyCount` probes), `jwatch`
    (same emission as `joint_destroy`), `retfalse1` (`cb_retfalse`
    tag reused, `scope=contact mask=f_mask`).
  - `on_event`: `ecunl` emission (dd_mode only — an `ec` event at
    `locked=false`, i.e. a drain-synthesized EndContact) and the
    `jwlive`/`jwdrop` jcount observer (jw_mode only, steps
    fire..fire+1).
  - `love.update`: `wp_mode or dd_mode` pcalled update; `abortq` line in
    the abort branch (dd_mode only — the drain-skipped witness);
    `drainlate` line in the recovery branch (dd_mode only — the
    late-drain witness); `wdrained` line before `after_update`
    (wd_mode only — `world:isDestroyed()` survives on a dead world via
    `luax_checktype`, while `after_update`'s `getBodyCount` is the
    measured death site); `post_destroy2` (d2_mode) and `rf1counts`
    (rf1_mode) lines after `jdrain`.
  - `build()`: `f_mask` second circle fixture on b1 for `retfalse1`
    only (two simultaneous (b1,ground) contacts).
  - `c_pre`: rf1 discrimination — `return false` only when the contact
    involves `f_mask`; sibling-contact events counted as passes.
- `corpus/fixtures/love_battery.py` (+174/−1; the removed line is the
  `iw_classify` docstring class enumeration, re-added with
  `deferred_abort` inserted):
  - 5 new `IW_CELLS` rows — `iw_bc_draindefer` (deferred_abort),
    `iw_bc_destroy2` (deferred), `iw_bc_jwatch` (deferred),
    `iw_pre_retfalse1` (ignored) appended after the r75 non-fatal block;
    `iw_bc_worlddestroy` (died, rc=1) appended after the unp twins and
    BEFORE the two fatal rows — fatal cells still last, the died cell
    sits in the process-death tail.
  - `iw_classify`: inside the `wpcall.update_ok == "false"` gate, a
    `cb_destroy.ok == "true"` check dispatches to the new
    `deferred_abort` branch BEFORE `refused_abort` (a refused_abort
    receipt has no `cb_destroy.ok` — ordering is safe; verified: the
    setpos_wp row still classifies refused_abort on all 4 reps). The
    branch requires the full abort witness set (locked_after, refused
    wp_setpos with assert text, refused collateral, recovery) PLUS the
    deferral witnesses (abortq.count == fire.count, readable pose,
    drainlate.step == wpcall.step+1, dead handle, ecunl at
    locked=false); anything less → `anomaly`.
  - Docstring: r76 paragraph (all five cells + the SayGoodbye census
    result).
- `corpus/fixtures/love_probe/`, `pygame_*` UNTOUCHED (control).

## Measured result (49/49 PASS, 4 stable reps)

15 CASES + 4 splice + 30 IW cells (25 prior + 5 new). Concatenated
`iw-*.stdout.txt` sha256 identical across all 4 run dirs:
`d1cbc1f8d23f4cbc4706406fddcfb38046b2f3693a8866e43480a07ebb9321f0`.

The measured r76 partition additions (this host, LOVE 11.5):

| cell | armed for | measured class | decisive pins |
|---|---|---|---|
| bc_draindefer | drain-deferral hazard | **deferred_abort** (new) | `cb_destroy ok=true count_after=4` (queued); `wpcall update_ok=false locked_after=true`; `abortq step=73 count=4 b1pos=400,520.15` (drain SKIPPED — pose still readable post-abort); `wpcall_next step=74 update_ok=true`; `drainlate step=74 count=3 b1pos=ERR`; `ecunl step=74 locked=false` + `evpin_ec lck=false step=74` (the drain's synthesized EC is the run's first ec event) |
| bc_destroy2 | double destroy, same body | **deferred** | in-cb `cb_destroy ok=true` → drains normally at 73 (`after_update count=3`, `evpin_ec lck=false step=73`); second call post-drain `post_destroy2 ok=false err="Attempt to use destroyed body." count=3 isDestroyed=true` — refused by the LIFETIME guard (`luax_checkbody`, wrap_Body.cpp:33-35), NOT the IsLocked assert |
| bc_worlddestroy | world:destroy() in cb | **died** | `cb_worlddestroy ok=true isDestroyed_in_cb=false count_after=4` (deferred via destructWorld flag, World.cpp:578-581); `wdrained step=73 isDestroyed=true` (world gone by update-73 return — drained at epilogue end, World.cpp:299); process dies at the NEXT world access: `Error: main.lua:NNN: Attempt to use destroyed world.`, `esc_fn=getBodyCount`, rc=1, no assert text, no CELL_DONE |
| bc_jwatch | SayGoodbye substitute | **deferred** (+ bounded drain point) | `jwlive` last-wins = `cb=post step=73 locked=true jcount=1` (last cb of the step still sees the queued joint); `jdrain step=73 jcount=0`; `jwdrop cb=ec step=74 locked=true jcount=0` (first cb of next step) — drain bounded to the update-73 epilogue window by two adjacent observations |
| pre_retfalse1 | per-contact return false | **ignored** | `cb_retfalse returned=false scope=contact`; `rf1counts falses=1 passes=1` (exactly one of the two b1-ground contacts got `false`); `after_update.b1vel=-2.81,-611.97` full impulse lands |

### SayGoodbye — recorded honestly

LOVE 11.5 exposes **no** destruction-listener surface: the `wrap_World.cpp`
method table (the same r74-boundary source tree, tarball sha
`6f55c265…`) lists exactly {update, setCallbacks, getCallbacks,
setContactFilter, getContactFilter, setGravity, getGravity,
translateOrigin, setSleepingAllowed, isSleepingAllowed, isLocked,
getBodyCount, getJointCount, getContactCount, getBodies, getJoints,
getContacts, queryBoundingBox, rayCast, destroy, isDestroyed,
getBodyList, getJointList, getContactList} — no SayGoodbye/
DestructionListener hook. `World` IS a `b2DestructionListener`
internally (`World.cpp:212-225`, `SetDestructionListener(this)` at
:238/:256) but its SayGoodbye only invalidates wrapper objects — nothing
reaches Lua. So the literal stretch ask is **blocked-by-absence**; the
r75-critic F3 residual is instead closed by `bc_jwatch`'s bounded
witness: jcount=1 through the last step-73 callback → 0 at update-73
return and at the first step-74 callback. The only engine code between
those observations is the epilogue drain loop (World.cpp:283-299,
source-anchored) — the drain *point* is now bounded-measured, not bare
inferred. (Residual inference, marked: "no other code drains" rests on
the source anchor, not on a Lua-visible event.)

`pre_retfalse1` answers the scope question negatively on this build:
the return is not consumed at ANY granularity (World.cpp:98
`lua_call(L, args, 0)` — r75 anchor), so "contact-scoped vs
pair-scoped" is moot here. The cell pins that the per-contact
discrimination executed (falses=1, passes=1) and the unmasked
trajectory; on a future build that consumes the return, exactly one
contact masking shows up as a partial impulse — falsifiable.

## Prior-cell byte-identity accounting

The correct baseline is post-fold HEAD (`be79ad1`/`ddd455b`): all r75
run dirs predate the folds, so prior-cell identity was measured by
running `git show HEAD:corpus/fixtures/love_phys_probe/main.lua` as an
independent probe per cell (receipts in
`corpus/live/r76-author/head_receipts/`):

- **22/25 prior iw receipts byte-identical** to the HEAD-probe output.
- The 3 differing receipts differ ONLY in `main.lua:NNN` source-line
  references (structural drift of additive edits, documented since r75):
  - `iw-bc_setpos_unp` / `iw-bc_newbody_unp`: `Error: main.lua:104→125`
    / `:108→129` and traceback frame lines (`do_mutation`, `on_event`,
    `update` sites) — all raw, unpinned text; `esc_fn` pins
    (`setPosition`/`newBody`), rc=1, assert bytes, every pinned key
    unchanged.
  - `iw-bc_setpos_wp`: `srcline=160→181` — the key is emitted-unpinned
    by design for exactly this reason.
- `probe.stdout`/`splice-*` / CASES rows unaffected (separate probe).
- The new cells' scratch↔landed receipts are likewise identical modulo
  `srcline=`/`main.lua:` numbers (scratch lacked the +12-line header
  comment); `bc_destroy2`, `bc_jwatch`, `pre_retfalse1` identical
  outright.

## Evidence

- `python3 -B corpus/fixtures/love_battery.py --runs
  corpus/live/r76-author/runs` → `totals: cases=49 pass=49 fail=0
  launch_ok=True done_marker=True exit=0`, battery exit 0, ~15s, ×4 reps:
  `love-20261014T182933442897Z`, `…T182951134560Z`,
  `…T183002584081Z`, `…T183012927330Z`. Per-run `verdicts.json` +
  `iw-<cell>.{stdout,stderr}.txt`.
- Pre-landing measurement: `IW_CELL=<c> timeout -s KILL 15 love
  corpus/live/r76-author/scratch_probe` → receipts in
  `corpus/live/r76-author/cells/*.r{1,2,3,4}.txt` — every armed cell
  byte-identical across ≥3 reps before landing.
- HEAD-probe prior-cell baseline: `IW_CELL=<c> love
  /tmp/r76-head-probe` → `corpus/live/r76-author/head_receipts/` (25
  cells, `git show HEAD:` source — read-only, no mutation).
- Source anchors (same pinned tree as r75 boundary,
  `/tmp/r74bsrc/love-11.5`): `World::destroy` lock→`destructWorld`
  (`World.cpp:573-581`), epilogue `if (destructWorld) destroy()`
  (`World.cpp:299`), `luax_checkbody`/`luax_checkworld` lifetime guards
  (`wrap_Body.cpp:33-35`, `wrap_World.cpp:32-34`), World method-table
  census (`wrap_World.cpp:231-256`), internal SayGoodbye
  (`World.cpp:212-225`).
- `git diff --numstat corpus/fixtures/`: battery 174/1, probe 131/3.
  Removed lines enumerated above — anchors + one docstring enumeration
  only. Nothing committed (leaf seat).
- `lsp` disclosure (unchanged host state): no LSP servers on PATH; all
  edits additive insertions or 4 named anchor lines; names verified by
  4 green battery runs.

## Remaining unknowns / risks

- `bc_worlddestroy`'s death site is the probe's own `after_update`
  `getBodyCount` — the honest shape (any post-drain world touch dies),
  but a differently-shaped probe would die at a different call; the
  class (`died`, rc=1, no assert, `esc_fn`=site) is what is pinned, and
  `wdrained.isDestroyed=true` carries the drain verdict before the
  death.
- `bc_jwatch`'s bound depends on cb ordering inside the step
  (`jwlive.cb=post` is the last observer of step 73 — measured, pinned).
  A build dispatching callbacks differently would shift the pin while
  keeping the bound — intended FAIL-then-re-measure.
- `bc_draindefer`'s `evpin_ec` captures the drain EC itself
  (`lck=false step=74`) because no natural ec precedes it in this run;
  the ecunl tag is the dedicated witness if a scene change reorders.
  `ecunl.count` is emitted unpinned (mid-teardown value).
- `pre_retfalse1` pins `final.b1pos=455.88,477.90` — a long-horizon
  trajectory pin on the two-fixture b1; deterministic ×7 (3 scratch +
  4 landed reps) but maximally sensitive to solver drift on other
  builds.
- `draindefer`'s `srcline=` and the unp traceback numbers remain
  layout-coupled by construction — unpinned, esc_fn unaffected.
- The `deferred_abort` branch sits before `refused_abort` in the wp
  gate keyed on `cb_destroy.ok == "true"`; a receipt carrying both a
  refused-write abort AND an unrelated queued destroy would dispatch to
  deferred_abort — that is the intended semantics (the accepted write
  is the interesting one), recorded here for the critic.
- pygame battery untouched (control). No git mutations.

## Blockers

One recorded limitation, not a blocker: `b2DestructionListener`/
`SayGoodbye` is not exposed on this build (method-table census,
`wrap_World.cpp:231-256`) — the F3 residual is closed by the bounded
`jwlive`/`jwdrop` observer instead. Everything else armed and green.
