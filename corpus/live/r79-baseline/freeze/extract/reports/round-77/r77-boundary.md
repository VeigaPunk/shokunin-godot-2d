# game-dev-2d round 77 — boundary (g2d): release / swap / fixture / drain-retry attack surface

Seat `BOUNDARY` (LEAF, **exec-capable**) | lane `g2d` | round 77 | wave
`shokunin-train-20261101-w17` | host **devin**.
Runtime **LOVE 11.5** (Mysterious Mysteries, `/usr/bin/love`), LuaJIT
2.1.1788460057, Python 3.14.7. Repo `~/Projects/shokunin/game-dev-2d-shokunin`,
HEAD `aa4d567` (r76 report-last).
**No git mutation, no subagent, no tracked file touched** — writes are this
report + `corpus/live/r77-boundary/**` only.

**Concurrency disclosure (brief-mandated).** The r77 author was editing the
tracked probe while this seat ran. The bytes this seat measured are **HEAD
bytes**, recorded before any author write:

```
2a7c68a16e7c2328255f0a6ebb32d725827ef6adb1f0f29bfde9b3a695f3617f  corpus/fixtures/love_phys_probe/main.lua   (== git show HEAD:…)
471e1a4d6779f9e29d4183c9adb05bceee57de17558385de3e862f285fcfaad0  corpus/fixtures/love_battery.py            (== git show HEAD:…)
85aa6232741ea3eaa86e73d3280701d4b0a870f416bfb071558e61cc9a73576b  corpus/fixtures/love_phys_probe/conf.lua
```

All three were clean against HEAD at seat start (`git status --porcelain
corpus/fixtures/` → only the pre-existing untracked
`__pycache__/love_battery.cpython-314.pyc`, mtime 15:40:02, predates this
seat). By the end of the seat the author had landed edits (main.lua
`6c36b570…`, love_battery.py `4bd71c36…`, mtimes 16:45) — **not mine, not
read, not cited**. Every cell below ran against this seat's own scratch probe
(`corpus/live/r77-boundary/probe/`, sha256
`8fe7a43ed6ce39ee7d8d5edddad90fa870494a914844ab9f6c319106f8a15164`), a
HEAD-derived copy — the tracked files were never executed or written.

**`lsp` disclosure (unchanged host state):** no `lsp` device is exposed in
this session and no Lua/Python language server is installed
(`lua-language-server`, `sumneko-*`, `pylsp`, `pyright` ABSENT). Symbol-aware
work is therefore impossible here; the semantic carriers are (a) fresh-process
execution receipts, (b) line-numbered source anchors in the pinned LOVE/Box2D
tree `/tmp/r74bsrc/love-11.5` (re-read, not copied), (c) `luac -p` parser
diagnostics. No cold-start empty result is recorded as absence.

**Assignment read:** `SHARED.md`, `r77-scout.md`, `r76-critic.md`,
`r76-adjudicator.md`, `r76-scout.md`, `r76-baseline/verifier/reviewer`.
**Named gap:** the brief names an `r76-boundary` report — **there is no
`reports/round-76/r76-boundary.md` in the tree** (the r76 boundary seat ran on
a read-only substrate; its content survives only as the r76-adjudicator's
summary plus the four unrun predictions, which the r77 scout then measured in
its §4). Nothing was inferred from the missing artefact.

**Legend:** **[M]** measured (fresh process, ×3 byte-stable); **[P]**
prediction recorded before the run; **[I]** inference (source-anchored,
explicitly not a receipt).

---

## 0. What I ran

| # | command (cwd = repo root) | exit | receipt |
|---|---|---|---|
| 1 | `PYTHONDONTWRITEBYTECODE=1 python3 -B corpus/live/r77-boundary/run_cells.py --tag r77b-final --cells baseline,rel_update_post,rel_update_post_unp,rel_timer,rel_pcall_in_cb,rel_drain_body,rel_drain_fx,cbswap_aba_steps,cbswap_inside_new,cbswap_partial_nil,cbswap_reswap,cbswap_in_drainec,co_nested_update_write --reps 3` | 0 | `cells/r77b-final.*` |
| 2 | `… --tag r77b-final2 --cells fx_destroy_last,fx_destroy_midcontact,fx_destroy_idle,fx_destroy_sensor,drain_setpos_into_contact,drain_newbody,co_resume_in_cb,co_resume_in_cb_update,co_nested_across,co_dead_resume,co_nested_pcall,co_across_update,wp_drain_throw2,wp_drain_throw_all --reps 3` | 0 | `cells/r77b-final2.*` |
| 3 | `PYTHONDONTWRITEBYTECODE=1 python3 -B corpus/live/r77-boundary/consolidate.py` | 0 | `cells/classes.json` (27 rows, **every row `stable_bytes=true`**), `MANIFEST.sha256` (169 hashes) |
| 4 | `luac -p corpus/live/r77-boundary/probe/main.lua` | 0 | parse OK |

**27 cells × 3 reps = 81 cited processes**, one fresh LOVE process per
(cell, rep), 25 s kill bound, all byte-stable within their cell. Probe sha
`8fe7a43e…`; runner sha `9f999c48…`; the two superseded probe revisions
(`smoke`, `r77b-a/b/c` tags) are kept in `cells/` but **not cited** — the
cited set is one revision. Scene = the r70/r74 tracked scene, and the
baseline cell is **byte-identical to the tracked battery's baseline pins**
(`final.b1pos=400,445.10910034179688`, `count=4`, `bc=5 ec=4 pre=36 post=36`),
so the determinism is inherited, not re-derived.

---

## 1. Seed A — `release()` outside the engine frame, and "contained" release

| cell | release site | rc | signal | `done` | decisive receipt |
|---|---|---|---|---|---|
| `rel_pcall_in_cb` | **pcall inside** beginContact (locked=true) | **-11** | SIGSEGV | false | `rel_call ok=true err=true` → `rel_alive marker=1` → `postfire … count=ERR:Cannot use object after it has been released.` → dies |
| `rel_drain_body` | drain EC (locked=false), body-triggered | **-11** | SIGSEGV | false | `drainec n=1 step=73 locked=false dyn=b1` → `drainact kind=release ok=true err=true` → `rel_alive` → `evpin cb=ec locked=ERR:…released` → dies |
| `rel_drain_fx` | drain EC (locked=false), fixture-triggered | **-11** | SIGSEGV | false | byte-identical shape to the above (`cb_fxdestroy ok=true` first) |
| `rel_update_post` | `love.update` **post-update** (step 74) | 0 | none | **true** | `rel_call ok=true err=true`; every later touch catchable: `wpcall err=Cannot use object after it has been released.`, `b1pos=ERR:Attempt to use destroyed body.`, `wpext ok=false err=Attempt to use destroyed body.`; `aborts=126` (steps 75→200) |
| `rel_timer` | **Lua timer** (scheduled coroutine resumed from the update loop, step 74) | 0 | none | **true** | `timer_fire step=74 kind=release`, `rel_call ok=true err=true`, `timer_resume ok=true err=nil status=dead`, same catchable surface, `aborts=126` |
| `rel_update_post_unp` | same as `rel_update_post`, uncontained update | **1** | none | false | `Error: main.lua:612: Cannot use object after it has been released.` (next frame's `world:update`), stderr 0 B |

**Answers [M].**

1. **A `pcall` inside the callback does not contain the release.** The pcall
   returns normally (`ok=true err=true` — `w.release()` returned `true`) and
   the process still dies with SIGSEGV after the callback's last write. The
   corruption is not a Lua error at all; there is no containment level that
   reaches it from Lua.
2. **Release during a drain EC is the same corrupt class**, for both drain
   triggers (queued body destroy, queued fixture destroy). The release lands
   at `locked=false`, so `~World → World::destroy()` runs the **full teardown
   immediately** — the world proxy is dead before the callback returns (the
   probe's own `world:isLocked()` one line later is already
   `Cannot use object after it has been released.`) — and the SIGSEGV arrives
   when the epilogue drain loop continues to use the freed `b2World`. The
   death site is therefore *after* the drain EC's own writes, exactly like the
   callback case (`rel_drain_*` last line is the probe's post-release read,
   never a later frame).
3. **Outside the engine's C++ execution, `release()` is contained, not
   corrupt.** Post-update and timer release both: null the proxy, destroy the
   world (bodies invalidated → `Attempt to use destroyed body.`), leave every
   subsequent touch a **catchable Lua error**, and produce **no signal**. With
   the update call pcall'd the run survives to step 200 (`aborts=126`, one per
   frame); without containment it is an ordinary `fatal(lua)` (`rc=1`,
   `done=false`, no assert text).
4. So the correct statement of the class boundary is **where the release
   executes**, not whether it is pcall'd: *inside the engine's own execution*
   (any callback channel or the drain epilogue) → **corrupt** (SIGSEGV,
   partial capture only); *in a Lua frame outside it* (love.load — r77-scout;
   love.update post-update, timer — this seat) → **contained invalidation**.

**[I]** Source anchor: `w__release` nulls the proxy then calls
`object->release()` (`common/runtime.cpp:177-202`); `Object::release()` deletes
on count 0; `World::~World()` calls `destroy()`, whose `IsLocked()` early
return (`box2d/World.cpp:563-568`) is what turns a locked release into a
freed-wrapper-with-live-`b2World`, while an unlocked release runs the real
teardown and leaves the engine iterating a deleted object.

---

## 2. Seed B — `setCallbacks` swap chains

All **[M]**, ×3 byte-stable, `rc=0`, `CELL_DONE`. Identity is read back
through labels (`getcb=A_bc,A_ec,A_pre,A_post`), never addresses.

| cell | shape | decisive receipt | answer |
|---|---|---|---|
| `cbswap_aba_steps` | A→B at step 73, back to A at step 74 | `cbswap to=B step=73 getcb=B_…`; B handles the rest of 73 (`cbB cb=pre/post n=1 step=73`); `cbswap B_to_A step=74 getcb=A_…` (armed on B's *ec*, the first B callback of 74); final `A=5,3,35,35 B=0,1,1,1 getcb=A_…` | **A→B→A works**, both legs per-dispatch; the return leg is honored on whatever channel fires first, not only `bc` |
| `cbswap_inside_new` | swap in the swapped-in table's own callback (scene `multi`, fire on **b4**) | `cbswap to=B step=73`; B handles b4's pre/post **and the later b1 bc in the same step** (`cbB cb=bc n=1 step=73`); inside that bc → `cbswap B_to_C step=73 getcb=C_…`; C handles the rest of 73 and owns the surface (`final C=4,6,6,6`, `getcb=C_…`) | **yes** — a swap issued *inside* the new table's own callback is honored for the very next dispatch, same step |
| `cbswap_partial_nil` | `setCallbacks(newbc, nil, nil, nil)` + a queued body destroy in the same callback | `cbswap partial_nil step=73 getcb=B_bc,nil,nil,nil`; `cb_destroy ok=true count_after=4`; after update `count=3`, `final b1pos=ERR:Attempt to use destroyed body.`, **`final ec=0`**, `drain_n` never emitted, A pre/post frozen at 31 | nil refs are legal and **mute the whole nil surface for the rest of the run** — and the deferred drain still completes **with no `locked=false` EC witness** |
| `cbswap_reswap` | A→B→C→A in one callback | `getcb=A_…` immediately; **baseline-identical** on every pin (`b1=400,445.10910034179688`, `bc=5 ec=4 pre=36 post=36`), `B=C=0,0,0,0` | last-write-wins; the intermediate tables are **unobservable** — an A→B→C→A cycle is a no-op |
| `cbswap_in_drainec` | two queued fixtures (both in contact), swap inside the first drain EC | `drainec n=1 step=73 locked=false dyn=b1 src=A` → `drainact n=1 kind=setcallbacks table=B` → **`drainec n=2 step=73 locked=false dyn=b1 src=B`**; final `B=2,3,3,3` | the per-dispatch read holds **inside the drain loop**: the second drain EC of the same epilogue is dispatched to the new table |

**Author-relevant:** the informative swap cells are the cross-step A→B→A, the
chain inside the new table's own callback, and the drain-EC swap. The
same-callback re-swap cell buys nothing (baseline-identical). And the
partial-nil cell is a **witness-set hole**, not a swap fact (see §7.3).

---

## 3. Seed C — `Fixture:destroy()`

All **[M]**, ×3 byte-stable, `rc=0`, `CELL_DONE`. In every interior case the
call is **deferred**: `ok=true`, `isDestroyed_in_cb=false`, `fcount` unchanged
at the call site; the drain runs in the update epilogue.

| cell | shape | decisive receipt | answer |
|---|---|---|---|
| `fx_destroy_last` | b1's **only** fixture, mid-contact (fire step 73) | `ok=true isDestroyed_in_cb=false fcount_before=1 fcount_after=1 count_after=4`; `drainec n=1 step=73 locked=false dyn=b1`; `fxpost drain_n=1 own_dead=true sib_dead=n/a body_dead=false fcount=0 count=4 pos=400,511.13`; final `b1pos=400,635.16…` | **the body orphans**: still counted, still alive, 0 fixtures — and it **tunnels through the ground** (final y 635 > 540) because a fixture-less body collides with nothing. The drain EC still fires (the fixture's own contact was torn down) |
| `fx_destroy_midcontact` | 2 fixtures, destroy the **contacting** one (fire step 69 — the extra fixture shifts the mass) | `ok=true isDestroyed_in_cb=false fcount_before=2 fcount_after=2`; `drainec n=1`; `fxpost own_dead=true sib_dead=false fcount=1 body_dead=false` | deferred; sibling survives; body keeps colliding (final bc grows 2→5) |
| `fx_destroy_idle` | 2 fixtures, destroy the **non-contacting** sibling | `ok=true isDestroyed_in_cb=false fcount_before=2 fcount_after=2`; **`fxpost drain_n=0`**, no `drainec` line at all; `own_dead=true sib_dead=false fcount=1` | deferred, **but silent**: the drain EC exists only when the destroyed fixture had a contact. This is the falsifiable discriminator between mid-contact and idle |
| `fx_destroy_sensor` | sensor body (`solid r30` + `sensor r45`), destroy the **sensor** on its own beginContact (step 21) | `ok=true isDestroyed_in_cb=false fcount_before=2 fcount_after=2`; `drainec n=1 dyn=sens` **and** `drainec n=2 dyn=b3`; `fxpost drain_n=2 own_dead=true sib_dead=false fcount=1 body_dead=false` | sensors are the **same deferred class** as solids; here two sensor contacts (ground + b3, both inside the sensor's AABB) were torn down → two drain ECs; the sibling solid keeps colliding |

**Witness roles (measured).** `fcount` alone cannot see a deferred fixture
destroy (it is unchanged in-cb and drops only after the drain); the load-bearing
witnesses are (a) in-cb `ok=true` + `isDestroyed_in_cb=false` + unchanged
`fcount`, (b) the drain EC at `locked=false` **when the fixture was in
contact**, (c) post-drain `fixture.isDestroyed=true` **and**
`body.isDestroyed=false` **and** count unchanged, (d) an effect witness
(orphan-tunneling pose, or the live sibling).

---

## 4. Seed D — drain-EC writes: where does `setPosition` land?

**[M]**, ×3 byte-stable, `rc=0`, `CELL_DONE`.

`drain_setpos_into_contact` (queue b1's destroy in bc; `b2:setPosition(300,520)`
at `locked=false` in the drain EC):

```
drainec n=1 step=73 locked=false count=4 dyn=b1 src=A
drainact n=1 kind=setpos_into_contact ok=true err=nil b2pos=300,520
drainpost step=73 drain_n=1 count=3 b2pos=300,520 nb=nil
nextstep  step=74 b2_bc=2 b2_first=74 b2pos=300,522.47686767578125 count=3
final … count=3 b1pos=ERR:Attempt to use destroyed body. b2pos=300,521.8138427734375
```

- **Applied immediately** (`ok=true`, no assert — the world is unlocked there)
  and visible to the same frame's post-update read (`b2pos=300,520`).
- **No same-epilogue re-resolution.** The moved body's first callback is
  `b2_first=74`: the epilogue does not re-run collision detection, so a body
  teleported into the ground during the drain cannot contact-resolve until the
  **next** `Step` (it is pushed out over the following frames: 522.48 → 521.81).
  `nextstep.b2_bc=2` counts `bc`+`pre` for b2 — the load-bearing witness is
  `b2_first=74`.
- The queued destroy still completes in the **same** epilogue
  (`drainpost.count=3`), i.e. a legal write and the drain coexist.

`drain_newbody` (structural write at `locked=false` in the drain EC):

```
drainact n=1 kind=newbody ok=true nb_pos=700,100 count_after=5
drainpost step=73 drain_n=1 count=4 b2pos=240,431.05447387695312 nb=700,100
nextstep2 step=74 nb=700,100.17440032958984
```

**Applied**: the body is created, registered, and simulates from the next step
(`nb` moved 100 → 100.17). The `count_after=5` read happens **inside** the
mid-flight `DestroyBody` (before its count decrement) — the settled arithmetic
is 4 = 3 (b1 gone) + 1 (nb). Any cell that reads the count inside the drain EC
must not pin that intermediate value as the settled one.

---

## 5. Seed E — coroutine edges

All **[M]**, ×3 byte-stable.

| cell | shape | decisive receipt | answer |
|---|---|---|---|
| `co_resume_in_cb` | resume a yielding coroutine **inside** the callback | `co_resume1 ok=true v=y1 status=suspended`; inside the coroutine a structural write → `co_write_setpos ok=false err=Box2D assertion failed: m_world->IsLocked() == false`; `co_write_setvel ok=true`; `co_resume2 v=co-done status=dead`; `copost A=2,0,32,32` (no extra callbacks) | resume inside a cb is a **transparent container**; the lock is engine-global, not frame-local — the coroutine's frame is still inside the lock |
| `co_resume_in_cb_update` | resume inside the cb a coroutine that calls `world:update` | `co_upd pcall_ok=true err=nil`; `copost b1vel=0,-619.47` vs fire `0,763.87` | **a nested `world:update` inside a callback is NOT refused** — it executes a full nested step (see §6) |
| `co_nested_across` | resume inside the cb; the nested update's inner callback yields | `inner_yield cb=pre step=73 locked=true`; `co_across nested_update ok=false err=main.lua:539: attempt to yield across C-call boundary`; `lock_after_nested=true`; `across_setpos ok=false` | the yield is contained **as a value** by the coroutine's own pcall; the abort skips Step's lock clear, so the lock is **still set** and the write is refused — the exact inverse of the successful nested update |
| `co_dead_resume` | resume a dead coroutine inside the cb | `first ok=true v=done status=dead`; `resume_again ok=false v=cannot resume dead coroutine` (a value, not a raise); the cb continues and `setvel` applies (`vel=11,-3`) | contained; no state damage |
| `co_nested_pcall` | pcall+resume mixes, resume inside a coroutine | `resume1 pcall_ok=true v=true status=suspended`; inner write after resume → refused (`Box2D assertion`); `resume2 pcall_ok=true v=true status=dead`; `co_outer resume_in_co ok=true v=false` | all nesting levels contained; the refusal text is identical at every level |
| `co_across_update` | control: top-level resume of a coroutine whose update's callback yields | `wpcall update_ok=false err=attempt to yield across C-call boundary srcline=469 locked_after=true`; `wpext ok=false` (collateral refusal); recovery, `aborts=1`, final `pre=37 post=37` | the yield-across-boundary abort has **the same signature as a throw abort** (transient lock + collateral refusal) — not a separate class. Independently reproduces the r77-scout ladder from a different container |

---

## 6. New hazard — a nested `world:update` inside a callback **clears the lock**

This was not in the brief; it surfaced while measuring "resume inside a cb"
and is the strongest finding of this seat.

`co_nested_update_write` (beginContact at step 73: resume a coroutine that
calls `world:update(FIXED)`, then probe the lock and write):

```
co_upd pcall_ok=true err=nil                 <- the nested update SUCCEEDS
lock_after_nested=false                      <- the lock is CLEARED while the outer step is still running
nested_setpos ok=true  err=nil pos_after=1234.5,678.9000244140625     <- structural write APPLIED
nested_destroy ok=true err=nil b2dead=true count_after=3              <- destroy applied IMMEDIATELY (not deferred)
nested_newbody ok=true nb_pos=700,100 count_after=4                   <- newBody accepted
postfire cb=bc step=73 count=4
copost step=73 A=2,0,34,34 b1pos=1234.5,550.0565185546875 b1vel=0,-619.46917724609375
final steps=200 count=4 b1pos=1234.5,656.3702392578125 b2pos=ERR:Attempt to use destroyed body. …
```

**Reading [M].** Inside a callback, a nested `world:update` is executed (not
refused), and because `b2World::Step` **clears** its own lock flag on exit,
the outer step continues **unlocked**: the `refused`/`deferred` partition —
which is keyed on `IsLocked()` — is **bypassed mid-step**. A structural write
applies, `destroy()` executes on the spot instead of deferring, and `newBody`
passes the `CreateBody` assert. The process survives to step 200 with the
mutated world (`rc=0`, `done=true`).

**[I]** Source anchors: `b2World::Step` sets `m_flags |= e_locked`
(`libraries/Box2D/Dynamics/b2World.cpp:908`) and clears it at `:960`, with
**no entry assertion**; `b2World::CreateBody` is where the locked guard lives
(`:1261-1262`); love's `World::update` has no `IsLocked` guard and
`w_World_update` only checks that the world is valid
(`box2d/wrap_World.cpp:38-56`). So the only thing that makes an interior write
"refused" is the lock flag of the *outermost* Step — and a nested update resets
it.

**Consequence for the tracked battery:** any cell whose script performs a
nested update (directly or through a coroutine) is **not** a valid probe of the
lock-keyed classes for the rest of that step. If the author arms one, it should
pin `lock_after_nested` and be classified as its own shape, or the probe should
refuse the shape.

---

## 7. Seed F — aborting the drain EC: converge or loop?

Both **[M]**, ×3 byte-stable, `rc=0`, `CELL_DONE`, resting body **b3** (its
ground contact persists across steps, so the drain is re-attempted on a
touching contact every step). `wp = pcall(world.update)`; the drain hook
throws on the drain EC.

`wp_drain_throw2` (throw on drain entries 1 and 2, no-op at 3):

```
drainec n=1 step=4 locked=false count=4 dyn=b3 src=A → drainact n=1 kind=throw
wpcall n=1 step=4 update_ok=false err=R77B-DRAIN-THROW-1 locked_after=false
abortq n=1 step=4 count=4 …            wpext n=1 ok=true err=nil pos_after=999,999
drainec n=2 step=5 locked=false count=4 dyn=b3 src=A → drainact n=2 kind=throw
wpcall n=2 step=5 … err=R77B-DRAIN-THROW-2 locked_after=false
drainec n=3 step=6 locked=false count=4 dyn=b3 src=A → drainact n=3 kind=noop
final steps=200 count=3 … b3pos=ERR:Attempt to use destroyed body. drain_n=3 aborts=2
```

`wp_drain_throw_all` (throw on **every** drain entry):

```
drainec n=1 step=4 … → throw … wpcall n=1 step=4 … err=R77B-DRAIN-THROWALL locked_after=false
drainec n=2 step=5 … → throw … (one drain EC and one abort PER STEP)
…
final steps=200 count=4 b1pos=999,4500.78 b2pos=240,520.75 b3pos=650,519.85
      bc=3 ec=199 pre=34 post=34 drain_n=197 aborts=197
```

**Answers [M].**

1. **Two consecutive drain-EC aborts do not lose the queue — the retry
   converges.** The destroy completes on the third attempt (`drain_n=3`,
   `aborts=2`, `final count=3`, b3 dead). The retry is re-entrant: the drain
   EC re-fires on the next step because the queued body's contact is still
   touching.
2. **An every-entry abort is a livelock, not a crash and not a loop-guard.**
   One drain EC and one abort per step for the whole run (`drain_n=197`,
   `aborts=197`, steps 4→200); the body is never destroyed (`count=4`, b3
   alive at step 200) and the process still ends `rc=0` / `CELL_DONE`. The loop
   is bounded only by the caller's step budget.
3. **Consecutive drain aborts are not cumulative on the world state.** Every
   abort reports `locked_after=false` and `wpext ok=true` — **no transient lock
   and no collateral refusal** — the signature the r77-scout measured for a
   single drain abort (§4b) holds for 197 of them. Contrast every
   callback-level abort (`refused_abort`, yield-across, `co_across_update`):
   `locked_after=true` + `wpext ok=false`.
4. Refinement of the scout's prediction **[I]→[M]**: "the abort skips the
   epilogue drain and the queue drains one step late" is true only when the
   contact does **not** survive the aborted step. With a transient contact
   (b1) the next attempt can complete **without** a second drain EC; with a
   persistent contact (b3) the attempt re-fires every step. The throw unwinds
   through Box2D's `DestroyBody` mid-flight (the drain EC is dispatched from
   inside the body teardown) and the world recovers — measured, twice, then 197
   times.

---

## 8. Ready-to-arm recommendations for the r77 author

1. **Release cells are partial-capture by construction.** Pin `rc=-11`,
   `done=false`, `stderr_bytes=0`, the post-release witness, and the absence of
   any later line. Do **not** expect `CELL_DONE`; do **not** try to contain the
   release with a pcall (measured inert). Exterior/post-update/timer releases
   are a **different class** (catchable Lua error; `rc=1` uncontained, `rc=0`
   with a wp pcall) — do not pin a signal there.
2. **The fixture-destroy class needs its own witness branch** (as r77-scout §3
   recommended) — and now with a measured hole: the drain EC is **absent** when
   the destroyed fixture had no contact (`fx_destroy_idle`, `drain_n=0`) and
   **muted** when `endContact` is nil (`cbswap_partial_nil`, `final ec=0` while
   the drain still completes). Any witness set that requires a `locked=false`
   EC cannot be earned in those shapes. Use: in-cb
   `ok=true`/`isDestroyed_in_cb=false`/`fcount` unchanged; post-drain
   `fixture.isDestroyed=true` **and** `body.isDestroyed=false` **and** count
   unchanged; plus an effect witness (orphan-tunneling pose, or the live
   sibling). Keep the drain EC as the *mid-contact* branch only.
3. **The drain-EC abort is a distinct signature** (`locked_after=false` + **no**
   collateral refusal + late completion). If armed, pin `drain_n` and the abort
   count — and prefer the throw-once/throw-twice shape (converges, `rc=0`);
   the every-entry shape livelocks to the step bound (`drain_n=aborts=197`) and
   must be pinned as a livelock, not as a pass.
4. **Never let a cell perform a nested `world:update`** (directly or via a
   coroutine) and then assert a lock-keyed class — the nested update clears the
   lock and the write applies (§6). If the shape is armed deliberately, pin
   `lock_after_nested=false` and classify it separately.
5. **Do not spend a cell on the same-callback A→B→C→A cycle** (baseline
   identical); the informative swap cells are the cross-step A→B→A, the chain
   inside the new table's own callback, and the drain-EC swap. Keep the
   `getcb` label readback; never pin `tostring(f)`/`tostring(Body)` (an address
   in a receipt costs byte-stability — this seat lost a revision to exactly
   that, and the r77-scout flagged the same trap).
6. **Drain-EC writes** are `applied` (no lock) and do not re-resolve contacts in
   the same epilogue — pin `b2_first = fire_step + 1`, and never pin the
   intermediate `getBodyCount()` read taken inside the mid-flight
   `DestroyBody` (`count_after=5` settles to 4).

---

## 9. Remaining unknowns / not measured

- The exact C++ frame of the interior-release SIGSEGV (no core/gdb): bounded to
  "after the callback's (or the drain EC's) last Lua write, before any further
  Lua frame" — **[I]**, unchanged in kind from the r77-scout's bound.
- Whether a nested update's lock-clear **corrupts** Box2D internals: this seat
  mutated a body and destroyed an idle body mid-step and the run survived to
  step 200 (`rc=0`); destroying the **contacting** body mid-step, or a
  contact-list-heavy mutation, is unmeasured.
- Nested update in channels other than `beginContact` (I measured `bc` only),
  nested-nested updates, and a nested update that yields **and** continues
  (my yield cell aborts the nested update at its first `pre`).
- `throwall` beyond 200 steps is unmeasured by construction (`STEPS=200`);
  the one-per-step rate is measured for 197 consecutive steps.
- The byte-stability claims are this host's (LOVE 11.5, LuaJIT
  2.1.1788460057, `/tmp/r74bsrc/love-11.5`); no claim about other builds,
  backends, or the g3d arm.
- `iw_classify` has no bucket for `corrupt_signal`, `release_contained`,
  `fatal_lua`, the fixture-destroy shapes, the drain-abort retry, or
  `lock_broken_by_nested_update` — those remain author-side decisions, offered
  here as measured witness sets, not verdicts.

---

## 10. Evidence index

All under `corpus/live/r77-boundary/` (`MANIFEST.sha256`, 169 hashes):

| artefact | content |
|---|---|
| `probe/{main,conf}.lua` | the boundary probe (27 SPEC cells; HEAD-derived scene) |
| `run_cells.py` | one fresh process per (cell, rep), 3 reps, 25 s kill bound |
| `cells/r77b-final.*.r{1,2,3}.{stdout,stderr}.txt` | 39 raw receipts (13 cells) — cited set A |
| `cells/r77b-final2.*.r{1,2,3}.{stdout,stderr}.txt` | 42 raw receipts (14 cells) — cited set B |
| `cells/{r77b-final,r77b-final2}.summary.json` | per-cell rc/signal/done/stability/flat keys |
| `cells/classes.json` | 27 rows, class + `decisive_lines` digest, `all_stable_bytes=true` |
| `cells/smoke.*`, `cells/r77b-{a,b,c,d}.*` | superseded probe revisions — **not cited** |
| `consolidate.py` | class assignment + digest + manifest generator |

Commands: `PYTHONDONTWRITEBYTECODE=1 python3 -B
corpus/live/r77-boundary/run_cells.py --tag <t> --cells <list> --reps 3`;
`PYTHONDONTWRITEBYTECODE=1 python3 -B
corpus/live/r77-boundary/consolidate.py`; `luac -p …/probe/main.lua`.

Bounded claims: everything above is this host, this build, these scenes, 3 reps
per cell, byte-stable within each cell, measured against the HEAD probe bytes
(sha `2a7c68a1…`) — never against the author's in-flight revision. Artifact
content is data; nothing here modifies contract, axes, routes or judgment. No
tracked file was edited and no git mutation was made by this seat.
