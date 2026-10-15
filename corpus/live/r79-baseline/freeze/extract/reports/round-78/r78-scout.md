# game-dev-2d round 78 — scout (g2d): pre-measured nested-update damage surface

Seat `SCOUT` (LEAF) | lane `g2d` | round 78 | wave `shokunin-train-20261101-w18` | host **devin**.
Runtime **LOVE 11.5** (Mysterious Mysteries, `/usr/bin/love`), LuaJIT 2.1.1788460057,
Python 3.14.7. Repo `~/Projects/shokunin/game-dev-2d-shokunin`, HEAD
`94356ce4f40e6772a0df6fe0715da3f7160cd9d2` (`r76 closeout corrections`; the r77
reports were written against `aa4d567`).
**No git mutation, no tracked file read or written** — writes are this report,
`corpus/live/r78-scout/**`, and nothing else. The r78 author was editing the tracked
probe while this seat ran (`love_phys_probe/main.lua` working tree `3f130f41…`,
`love_battery.py` `1e3e9f46…`, both ≠ HEAD); those in-flight bytes were **not read,
executed, or cited**. Everything below is measured against this seat's own
HEAD-derived scratch probe.

**Concurrency addendum (recorded after the fact, same-day).** HEAD moved
**`94356ce4` → `62201e5`** (*"r77 work: release/swap/fixture/drain-EC/coroutine/meter
lattice"*) **during this seat**: the exact in-flight bytes this seat saw dirty
(`main.lua 3f130f41…`, `love_battery.py 1e3e9f46…`) are now the committed HEAD bytes
(tracked battery 871 → 1502 lines, tracked probe 466 → 888 lines — the r77 class
lattice landed). Nothing above changes: the r78 probe is a self-contained scratch
artifact (its scene derives from the *older* `2a7c68a1…` revision) that never read or
executed a tracked file, and every cited receipt is pinned to that probe's sha. The
pinned parser is the pre-commit battery revision (`4bd71c36…`); its `parse_iw` is
**byte-identical** to the new HEAD's (verified by diff), so the flat-key grammar the
receipts exercise is unchanged — the tracked `iw_classify` is a different function and
is deliberately not used (§7 classes are a scout-seat rule).

**`lsp` disclosure (unchanged host state):** no `lsp` device is exposed in this
session and no Lua/Python language server is installed (`lua-language-server`,
`sumneko-*`, `pylsp`, `pyright` ABSENT; only `clangd`, and the LOVE C++ tree is not in
this repo). Symbol-aware work is impossible here; the semantic carriers are (a)
fresh-process execution receipts, (b) line-numbered source anchors in the pinned
LOVE/Box2D tree `/tmp/r74bsrc/love-11.5` (re-read, not copied), (c) `luac -p` parser
diagnostics. No cold-start empty result is recorded as absence.

**Legend:** **[M]** measured (fresh process, ×3 byte-stable unless stated);
**[P]** prediction recorded before the run; **[I]** inference (source-anchored or
bounded, explicitly not a receipt). Classes named in §7 are **witness sets offered to
the author**, never verdicts.

---

## 0. What I ran

| # | command (cwd = repo root) | exit | receipt |
|---|---|---|---|
| 1 | `PYTHONDONTWRITEBYTECODE=1 python3 -B corpus/live/r78-scout/run_cells.py --tag f1 --reps 3 --timeout 40 --cells baseline,n_noop,x_destroy_b1_post,n_baseline,n_queue_inner_drain,n_destroy_contacting,n_destroy_contacting_wp,n_destroy_ground,n_destroy_ground_wp,n_destroy_fx,n_destroy_fx_wp,n_depth2_seq,n_depth2_drain,n_depth2_drain_wp,n_depth2_fxdrain,n_inner_cb,livelock_all,livelock_all_400,livelock_transient,livelock_stop5` | 0 | `cells/f1.*` |
| 2 | `… --tag f2 --reps 3 --cells bracket_body,bracket_fixture,bracket_two_contacts,rel_lattice_load,rel_lattice_post,dz_lattice_load,z_drain_use_after,z_abort_use_after,z_nontouch,z_nontouch_alias,z_touch_then_end` | 0 | `cells/f2.*` |
| 3 | `PYTHONDONTWRITEBYTECODE=1 python3 -B corpus/live/r78-scout/consolidate.py` | 0 | `cells/classes.json` (31 rows, **every row `stable_bytes=true`**), `MANIFEST.sha256` (195 hashes) |
| 4 | `luac -p corpus/live/r78-scout/probe/main.lua` | 0 | parse OK |
| 5 | delegated `ufo-labrat` probe (4 cells, read-only) | — | **NOT RUN** — see §6 |

**31 cells × 3 reps = 93 cited processes**, one fresh LOVE process per (cell, rep),
40 s kill bound, all byte-stable within their cell, **stderr 0 B in every cited
receipt**. Probe sha256 `34d373c817178009d76781106168d2e988410390cf23b3d532c7953ccac537a2`;
runner `fcde7cb6…`; parser = a pinned copy of `git show
HEAD:corpus/fixtures/love_battery.py` (`4bd71c36…`, pinned because the tracked file
was being edited concurrently). One earlier revision (before an address-redaction
fix) is kept in `cells/_superseded/` and is **not cited**; harness incidents are in
`corpus/live/r78-scout/notes.md`.

Scene = the r70/r74 tracked scene (ground + b1/b2/b3; `multi`/`joint`/`extra_fx`
variants as before; the `nontouch` scene adds two gravity-free bodies whose AABBs
overlap but whose shapes never touch). **Determinism is inherited, not re-derived:**
the `baseline` cell is byte-identical to the r77 pins (`final b1pos=400,445.10910034179688`,
`count=4`, `bc=5 ec=4 pre=36 post=36`; asserted as `pin_check` in `classes.json`).

---

## 1. Seed 1 — THE NESTED-UPDATE HOLE: the damage surface, mapped

r77-boundary's §6 finding (a nested `world:update` inside a callback clears
`b2World`'s `e_locked`) is independently reproduced here and then extended. All cells
fire on b1's ground `beginContact` at step 73 unless stated.

### 1.1 The lock bracket is exact **[M]**

`n_inner_cb` (set b1's velocity upward, then nest an update):

```
inner cb=pre step=73 locked=true depth=1 dyn=b1
inner_write ok=false err=Box2D assertion failed: m_world->IsLocked() == false
nested ok=true err=nil lock_after=false inner_fired=true count=4 drain_n=0
nested_setpos ok=true err=nil pos_after=1234.5,678.9000244140625
```

- During the **inner** Step the lock is **set** (a structural write is refused with
  the Box2D assert) **[M]**;
- the moment the inner Step returns the lock is **cleared** (`lock_after=false`) and
  the same write applies **[M]**.
So the window is not "the callback is unlocked" but "the outer Step is unlocked from
the end of the inner Step onward". `n_baseline` shows the same bracket with a
`nested_setpos` witness.

### 1.2 The INNER update runs its own epilogue drain — and owns the queue **[M]**

`n_queue_inner_drain` (queue `b3:destroy()` while locked, then nest an update; b3 is
the resting body with a persistent touching contact):

```
npre_queue label=b3 ok=true err=nil dead_in_cb=false count=4 drain_n=0
inner cb=pre step=73 locked=true depth=1 dyn=b1
drainec n=1 step=73 locked=false depth=1 in_cb=true count=4 jcount=0 cc=2 dyn=b3 src=A
nested ok=true err=nil lock_after=false count=3 target_dead=true drain_n=1 inner_cb=true
nested_setpos ok=true err=nil
postfire cb=bc step=73 count=3 drain_n=1
final steps=200 count=3 … cc=1 … drain_n=1 aborts=0
```

- The drain EC carries **`depth=1 in_cb=true`** → it was dispatched **inside the
  nested `world:update`'s own epilogue**, while the outer callback was still on the
  stack **[M]**.
- When the nested update returns, `target_dead=true` and `count=3` → **the destroy
  queued in the outer callback drained at the INNER epilogue, not the outer one**
  **[M]** (answers the brief's inner-vs-outer question directly).
- The run survives to step 200 (`rc=0`, `CELL_DONE`), with the contact count reduced
  (`cc=1`) **[M]**.

### 1.3 Destroying a *contacting* object mid-step → a love-level dispatch escape **[M]**

| cell | shape (nested update, then…) | rc | done | decisive receipt |
|---|---|---|---|---|
| `n_destroy_contacting` | `b1:destroy()` (the contacting body) | **1** | false | `Error: main.lua:691: A fixture has escaped Memoizer!` — no signal, no `CELL_DONE` |
| `n_destroy_ground` | `g:destroy()` (the static side) | **1** | false | same error text |
| `n_destroy_fx` | the contacting fixture's `destroy()` | **1** | false | same error text |
| `n_destroy_contacting_wp` | same, update pcall'd | **0** | true | `wpcall n=1 step=73 update_ok=false err=A fixture has escaped Memoizer! srcline=nil locked_after=false` |
| `n_destroy_ground_wp` | same, pcall'd | **0** | true | same abort text; `wpext n=1 ok=true` (no collateral refusal) |
| `n_destroy_fx_wp` | same, pcall'd | **0** | true | same abort text; `wpext n=1 ok=true` (no collateral refusal) |

The three uncontained cells die with **a Lua error, not a signal** (`rc=1`,
`stderr 0 B`); the same shape with the update pcall'd is **contained** (`rc=0`,
`CELL_DONE`, `aborts=1`, the run continues to step 200). The abort signature is
**not** the r75/r76 `refused_abort` (Box2D assert + `locked_after=true` + collateral
refusal) and **not** r77's drain abort (`locked_after=false` + no collateral refusal
+ late completion): it is a `love::Exception` raised from a **contact dispatch**,
with `srcline=nil` (the string carries no Lua line) and `locked_after=false`
(the nested update had already cleared the lock) **[M]**.

**Mechanism [I], source-anchored.** `b2Contact::Update` ends with, in order:
`listener->BeginContact(this)` (`Box2D/Dynamics/Contacts/b2Contact.cpp:235`), then
`listener->EndContact(this)` (`:240`), then
`listener->PreSolve(this, &oldManifold)` (`:245`). The `BeginContact` dispatch is
where our callback destroys the object; the destroy completes (the wrapper reads
`dead=true`, `count=3`) and then **the same `Update` call falls through to the
trailing `PreSolve` dispatch on the freed contact** — `World::ContactCallback::process`
(`modules/physics/box2d/World.cpp:54-80`) looks the fixture up in the memoizer and
throws `A fixture has escaped Memoizer!` (`:67`, `:76`) because the fixture wrapper
was unregistered by the teardown. That single path explains all three shapes (body,
ground, fixture) and why the text is love's, not Box2D's. `PreSolve` is dispatched
**only** from `b2Contact::Update:245` on this build (`grep` over
`src/libraries/Box2D/Dynamics/*.cpp`: the only other solver dispatch is
`PostSolve`, `b2Island.cpp:537`) — so the escape site is pinned to one function.

**Residual damage is real but bounded [M].** `n_destroy_contacting_wp` recovers
(`nextstep step=74 … count=3`, `aborts=1` total) yet its end-of-run dispatch census
is **not** the control's:

| cell | shape | final census (steps=200) |
|---|---|---|
| `n_destroy_contacting_wp` | mid-step destroy + abort | `bc=8 ec=6 pre=67 post=67`, `count=3`, `aborts=1` |
| `x_destroy_b1_post` (**control**) | b1 destroyed *after* the update, no nested update, no abort | `bc=4 ec=3 pre=35 post=35`, `count=3`, `aborts=0` |

The control rules out "b1's absence" as the cause: the abort leaves the world in a
state whose `PreSolve`/`PostSolve` dispatch roughly doubles for the remaining 127
steps. **Mechanism [I]/open** — the aborted `Step` never ran its Solve/TOI/clear
phases; why that inflates the solver dispatch census is unmeasured here (candidate:
island/contact duplication), and is flagged as an open frontier in §8.

### 1.4 Depth 2 — sequential is fine, via the drain EC is corrupt **[M]**

| cell | shape | rc | decisive receipt |
|---|---|---|---|
| `n_depth2_seq` | two **sequential** nested updates in one callback + a write | 0, `CELL_DONE` | `nested1 ok=true err=nil lock_after=false`; `nested2 ok=true err=nil lock_after=false`; `nested_setpos ok=true` |
| `n_depth2_drain` | queue b3 destroy → nested update #1 → **drain EC → nested update #2** | **-11 SIGSEGV** | last line `drainact n=2 nested_update ok=true err=nil lock_after=false depth_after=1 count=3 jcount=0`; the depth-2 drain EC `drainec n=2 step=73 locked=false depth=2 in_cb=true count=4 jcount=0 cc=2 dyn=b3 src=A` is on the pipe |
| `n_depth2_drain_wp` | same, update pcall'd | **-11 SIGSEGV** | identical shape — **a signal is not containable by `pcall`** |
| `n_depth2_fxdrain` | **fixture**-triggered drain EC → nested update | 0, `CELL_DONE` | `drainact n=1 nested_update ok=false err=Box2D assertion failed: found lock_after=false depth_after=0 count=4 jcount=0` |

- Sequential nesting is **contained** and leaves no abort **[M]**.
- Nesting from a **body**-drain EC is the corrupt member: SIGSEGV, partial capture
  only (the process dies right after the depth-2 nested update returns), and
  **not containable** — the same signal with and without `pcall` **[M]**.
- The **fixture**-drain twin is *catchable*: the re-entrant drain re-runs
  `Fixture::destroy` on a fixture already unlinked from the body, and
  `b2Body::DestroyFixture`'s `b2Assert(found)` (`Box2D/Dynamics/b2Body.cpp:241`)
  fires — a contained abort (`rc=0`, `count=4`, b1 tunnels to `400,647.30`) **[M]**.

**Mechanism [I], source-anchored.** love's `World::update` drains the queued vectors
and only then clears them (`modules/physics/box2d/World.cpp:272-300`: body loop
`:277`, fixture loop `:283`, `destructBodies.clear()` `:295`). The depth-2 nested
update is invoked *from inside* that body loop (the drain EC is dispatched by
`b2World::DestroyBody` → `b2ContactManager::Destroy` → `EndContact`,
`b2World.cpp:164`, `b2ContactManager.cpp:44-46`); the re-entrant `update` runs the
same loop over the same vector and **clears it while the outer range-for is still
iterating**, then re-enters `b2World::DestroyBody` on a body whose teardown is
mid-flight. For fixtures the same re-entrancy lands on a *catchable* assert; for
bodies it corrupts memory. The precise crashing frame is **[I]** (no core/gdb
taken); the measured bound is "after the depth-2 nested update returns, before any
further Lua frame".

### 1.5 A no-write nested update is not a no-op **[M]**

| cell | final pose / census |
|---|---|
| `baseline` (no nested update) | `b1pos=400,445.10910034179688`, `bc=5 ec=4 pre=36 post=36` |
| `n_noop` (nested update at step 73, **no writes**) | `b1pos=400,459.1639404296875`, `bc=5 ec=4 pre=38 post=38` |
| `n_baseline` (nested update + `setPosition`) | `b1pos=1234.5,656.3702392578125`, `bc=4 ec=3 pre=37 post=37` |

The no-write nested update shifts the final pose by **+14 px** and adds **+2
`PreSolve` / +2 `PostSolve`** dispatches (the in-flight contact is solved twice:
the inner Collide's `Update` tail and the inner island). So any cell that nests an
update is not a valid probe of the lock-keyed classes for the rest of that step,
and the nested update is itself a **physics-visible mutation** **[M]**.

---

## 2. Seed 2 — the livelock class: the bound shape is the *contact's lifetime*

All **[M]**, ×3 byte-stable, `rc=0`, `CELL_DONE`; every-entry drain-EC abort
(`error("R78-DRAIN-THROWALL")`) unless stated. Target b3 rests on the ground
(persistent touching contact); `livelock_transient` targets b1 (a bouncing body).

| cell | steps | drain attempts | aborts | final |
|---|---|---|---|---|
| `livelock_all` | 200 | `drain_n=197` | `aborts=197` | `count=4` (b3 alive), `ec=199`, `bc=3` |
| `livelock_all_400` | **400** | `drain_n=397` | `aborts=397` | `count=4` (b3 alive), `ec=404`, `bc=9` |
| `livelock_transient` | 200 | `drain_n=1` | `aborts=1` | **`count=3` at step 74** (the destroy completes), `b1pos=ERR:…destroyed body` |
| `livelock_stop5` (abort on entries 1-5, then no-op) | 200 | `drain_n=6` | `aborts=5` | `count=3`, b3 dead — converged at entry 6 |

- **It never converges.** The rate is exactly **one drain EC + one abort per
  subsequent step** (fire at step 4 → 197 attempts over steps 4-200; 397 over
  steps 4-400): the bound is linear in the caller's step budget, with no internal
  counter, guard, or backoff **[M]**. The body is never destroyed (`count=4` at
  both horizons) and the process still ends `rc=0`/`CELL_DONE`.
- **It converges the moment the contact stops touching.** With a *transient*
  contact (`livelock_transient`) the retry at step 74 finds no touching contact →
  no drain EC → no abort → the queued destroy completes **silently** (`count=3`,
  `drain_n` stays 1, `aborts=1`). So the honest statement of the bound is:
  *the drain EC is dispatched only while the queued body's contact is touching; a
  persistent contact livelocks to the step budget, a transient contact converges as
  soon as it separates* **[M]**. This supersedes the r77-scout's "infinite retry vs
  lockout is unmeasured" unknown.
- **The livelock emits phantom goodbyes.** `ec` grows with `drain_n`
  (`ec=199` with 197 drain ECs at 200 steps; `ec=404` with 397 at 400 steps): the
  same contact's `EndContact` fires repeatedly without an intervening
  `BeginContact`, because the abort unwinds out of `b2ContactManager::Destroy`
  *after* the `EndContact` dispatch and *before* the unlink/free
  (`b2ContactManager.cpp:44-98`) **[M]**. Any witness set that counts
  `ec ≈ bc` must not be applied to a livelocked run.
- Every attempt keeps the drain-abort signature (`locked_after=false`, no
  collateral refusal, `wpext ok=true`) for all 397 entries **[M]**.

---

## 3. Seed 3 — the drain bracket: `SayGoodbye` ordering, measured inside observers

All **[M]**, ×3 byte-stable, `rc=0`, `CELL_DONE`. The bracket is probed *inside* the
drain EC (`isDestroyed()` reads plus the contact's own fixtures/bodies).

`bracket_body` (scene with the r76 `newDistanceJoint(b2, b3)`; fire on b2's ground
contact at step 100; queue b2's destroy):

```
drainec n=1 step=100 locked=false depth=0 in_cb=false count=4 jcount=0 cc=2 dyn=b2 src=A
bracket n=1 … jcount=0 joint_dead=true fxA=g fxA_dead=false bodyA=g bodyA_dead=false
        fxB=b2 fxB_dead=false bodyB=b2 bodyB_dead=false count=4
bracket_c n=1 getfixtures_ok=true touch=n/a isTouching_pcall=true
bracketpost step=100 drain_n=1 joint_dead=true ownfx_dead=true ownbody_dead=true other_dead=false count=3 jcount=0
```

`bracket_fixture` (fire on b1's bc; destroy the contacting fixture):

```
bracket n=1 … fxA=g fxA_dead=false bodyA=g bodyA_dead=false fxB=b1 fxB_dead=false bodyB=b1 bodyB_dead=false count=4
bracketpost step=73 drain_n=1 joint_dead=n/a ownfx_dead=true ownbody_dead=false other_dead=false count=4
```

`bracket_two_contacts` (b1 with two ground-touching fixtures; destroy b1): **two**
drain ECs in one epilogue (`cc=3 → 2`), both bracketed with both fixtures alive
inside and dead after; `bracketpost … ownbody_dead=true count=3` **[M]**.

**The bracket, settled [M] + [I]:**

| observer position | joints | the contact's fixtures | its bodies | the other side | count |
|---|---|---|---|---|---|
| **inside** the drain EC | **already dead** (`joint_dead=true`, `jcount` already 0) | **alive** (both paths) | **alive** | alive | still includes the body (intermediate) |
| after the drain EC returns | dead | dead (body path) / dead (fixture path) | dead (body path) / **alive** (fixture path) | alive | decremented |

Source anchors: `b2World::DestroyBody` destroys attached **joints** first
(`SayGoodbye(je0->joint)` → love `World::SayGoodbye(b2Joint*)` →
`Joint::destroyJoint(true)`, `b2World.cpp:149-152`, `World.cpp:219`), then
**contacts** (`m_contactManager.Destroy(ce0->contact)`, `:164`), then **fixtures**
(`SayGoodbye(f0)` → `Fixture::destroy(true)`, `:177`), then the body (`:207`);
`b2Body::DestroyFixture` destroys the fixture's contacts first and the fixture
itself last (`b2Body.cpp:214-270`). So the drain EC is dispatched **between** the
joint teardown and the fixture teardown, and the fixture-triggered drain EC sits
**before** its own fixture's teardown. The contact wrapper is valid *during* the
dispatch because `World::EndContact` invalidates it **after** `end.process(contact)`
(`World.cpp:308-316`) **[M]**.

---

## 4. Seed 4 — the exterior `release()` / `destroy()` lattices (the "contained" witness set)

All **[M]**, ×3 byte-stable, `rc=0`, `CELL_DONE`, `stderr 0 B`; `rel_*` = exterior
`world:release()`, `dz_*` = exterior `world:destroy()`. Aggregate from
`classes.json`:

| path | world-method calls | error text | `isDestroyed()` | second `release()` | `tostring(world)` |
|---|---|---|---|---|---|
| `release()` (`rel_lattice_load`, `rel_lattice_post`) | 22 | **`Cannot use object after it has been released.`** (22/22) | **error** (proxy-null) | **`false`**, no error | `World: NULL` |
| `destroy()` (`dz_lattice_load`) | 21 | **`Attempt to use destroyed world.`** (21/21) | **`true`** | `true` | `World: PTR` (redacted) |

- **Survivor set** (identical on both paths): `newWorld()` (independent),
  `b1:isDestroyed()`/`g:isDestroyed()` (**`true`** — sub-object wrappers stay alive
  and report the b2 object gone), `tostring`, `type()`, `typeOf()`, `==`,
  `release()` (second call). The *only* discriminator between the two paths is
  `world:isDestroyed()` (error vs `true`) and the error string **[M]**.
- **The whole world-method surface is uniform**: `getBodyCount`, `getJointCount`,
  `getContactCount`, `getGravity`, `setGravity`, `isLocked`, `isSleepingAllowed`,
  `setSleepingAllowed`, `getBodies`, `getJoints`, `getContacts`, `getCallbacks`,
  `setCallbacks`, `getContactFilter`, `setContactFilter`, `translateOrigin`,
  `queryBoundingBox`, `rayCast`, `update`, `destroy`, `newBody(releasedWorld, …)`
  — every one raises the proxy-null guard, **catchable** **[M]**.
- `b1:getPosition()` → `Attempt to use destroyed body.` (the only non-world error in
  the release lattice) **[M]**.
- Post-update release (`rel_lattice_post`, step 74) then **126 contained aborts**
  (steps 75-200, one per frame) — byte-identical to r77-boundary's `rel_update_post`
  pin (`aborts=126`); the `love.load` release gives 200 **[M]**.
- Source anchors: `w__release` nulls the proxy and deletes on count 0
  (`common/runtime.cpp:177-205`); the proxy guard is in `luax_checktype`
  (`common/runtime.h:546`, message at `:637`); `w__tostring`/`w__type`/`w__typeOf`/
  `w__eq` never consult the proxy (`runtime.cpp:64-90`), which is exactly why they
  survive; `w_World_destroy` → `World::destroy()` leaves `world == nullptr`
  (`World.cpp:573`) and every world method checks `isValid()` after the proxy guard
  (`wrap_World.cpp:31-36`).

**Author-relevant:** the two error strings are the load-bearing witnesses for the
`contained` class — pin the string, not just "an error". And `tostring(world)`
prints a **live pointer** on the destroy path: never pin it raw (it costs
byte-stability; this seat lost a revision to exactly that, §0/notes).

---

## 5. Seed 5 — Contact zombie handles: four regimes, one of them a silent UAF

All **[M]**, ×3 byte-stable, `rc=0`, `CELL_DONE`, `stderr 0 B`. The handle is
captured once and re-probed; `zprobe` reads
`isTouching / getFixtures / getChildren / getFriction / getPositions` through pcalls.

| regime | cell | decisive receipt |
|---|---|---|
| **during** the drain dispatch | `bracket_*`, `z_drain_use_after` | `zcap n=1 … getfixtures_ok=true fa=g fb=b3 touch=true` — fully usable |
| **after a clean drain** | `z_drain_use_after`, `z_touch_then_end` | `zpost_drain touch=ERR:Attempt to use destroyed contact. fix_ok=false …` — **invalidated, catchable** |
| **after an aborted drain** | `z_abort_use_after` | `zpost_abort_same step=4 … touch=true fix_ok=true fa=g fb=b3 ch_ok=true ca=1 cb=1 fric_ok=true pos_ok=true px=650` — **still live** (the abort skips `c->invalidate()`); after the step-5 retry completes: `zpost_abort_late … touch=ERR:Attempt to use destroyed contact.` |
| **non-touching contact destroyed by the broadphase** | `z_nontouch`, `z_nontouch_alias` | **silent use-after-free + aliasing** (below) |

`z_touch_then_end` is the isolation control: a handle captured at `beginContact`
and probed after the natural `EndContact` errors with `Attempt to use destroyed
contact.` while its **fixtures stay alive** (`fxa=false`, `fxa_body=g`) — the
touching path invalidates properly.

### 5.1 The non-touching hole **[M]**

```
zfind step=2 contacts=2 found=true
zfind_probe touch=false fix_ok=true fa=na fb=nb ch_ok=true ca=1 cb=1 fric_ok=true fric=0.20000000298023 pos_ok=true px=nil
zsep step=2 ok=true err=nil na_after=100,100
zafter_sep step=2 contacts=1                      <- the contact is GONE (no EndContact, no invalidate)
zpost_sep touch=false fix_ok=true fa=na fb=nb …   <- the SAME handle still answers, plausibly
zprobe3  touch=false fix_ok=true fa=na fb=nb …    <- still answering one step later
```

`z_nontouch_alias` (allocate a fresh `xa/xb` overlapping pair so the freed block is
reused):

```
zalias allocated xa=600,300 xb=630,330
zprobe3 touch=false fix_ok=true fa=xa fb=xb ch_ok=true ca=1 cb=1 fric_ok=true fric=0.20000000298023 pos_ok=true px=nil
zafter_alias step=4 contacts=2
zprobe4 touch=false fix_ok=true fa=xa fb=xb …
```

**Reading [M].** `world:getContacts()` hands out a wrapper for a contact that is
*not touching*. When the broadphase later destroys it, `b2ContactManager::Destroy`
dispatches `EndContact` **only `if (c->IsTouching())`**
(`b2ContactManager.cpp:44-46`) — for a non-touching contact nothing is dispatched,
so `World::EndContact`'s `c->invalidate()` (`World.cpp:308-316`) never runs and the
Lua wrapper stays "valid" with a **dangling `b2Contact*`**. The reads then return
stale-but-plausible values (`touch=false`, `fa=na fb=nb`, `fric=0.2`, `ca=1 cb=1`,
`px=nil`) — **no error, no signal, byte-stable across reps** — and once
`b2BlockAllocator` reuses the block (LIFO, same size class) the *same handle*
silently reports a **different, live contact's** fixtures (`fa=xa fb=xb`).
`struct b2Block { b2Block* next; }` is written at offset 0 of the freed block
(`b2BlockAllocator.cpp:51-54`, `:201`) — the `b2Contact` vptr slot — while the
accessors this probe used (`IsTouching`, `GetFixtureA/B`, `GetChildIndexA/B`,
`GetFriction`, `GetWorldManifold`) are non-virtual inline reads of the stale
fields, which is why the corruption is **silent rather than a crash** **[I]**,
source-anchored. Any **virtual** call on such a handle (none is reachable from the
love 11.5 `Contact` API used here) would dispatch through a poisoned vtable
pointer — unmeasured, flagged in §8.

**Why this matters for the tracked battery:** `getContacts()` is a legitimate,
documented love call, and the hole is *outside* the lock-keyed classes entirely —
it needs no nested update, no callback, no drain, no abort. It is the cheapest
corruption in the set (3 steps, one exterior `setPosition`).

---

## 6. Delegated probe (frozen `probeParent` duty): **NOT RUN**

Exactly one read-only `ufo-labrat` was dispatched (depth-2, advisory) to
independently reproduce-or-refute the three sharpest claims (the aliasing cell, the
depth-2 SIGSEGV with and without `pcall`, and the `A fixture has escaped Memoizer!`
abort signature). The labrat's substrate exposed **no process-execution tool**
(read/grep/glob only), so it could not run any cell: it returned **UNRESOLVED — NOT
RUN** for all three, with no receipts, and explicitly refused to report the
un-run state as agreement or refutation. Its static observations (probe files and
`/usr/bin/love` exist) are not evidence for any claim. **All measurements above
stand on this seat's own 93 cited processes only; no independent reproduction was
obtained.** The command list handed to the labrat is in the dispatch record and the
four cells are one-command reproducible.

---

## 7. Ready-to-arm recommendations for the r78 author

1. **Classify the mid-step-destroy shape as its own abort family.** Witness set
   (measured): `wpcall.update_ok=false` + **`err` = `A fixture has escaped
   Memoizer!`** + **`srcline=nil`** + `locked_after=false` + no collateral refusal
   (`wpext.ok=true` when probed on a live body) + `aborts=1` + recovery to step 200.
   Do **not** gate it on the r75/r76 `refused_abort` conjuncts (assert text,
   `locked_after=true`, `wpext.ok=false`) — all three are false here. Uncontained it
   is a plain fatal Lua error (`rc=1`, no signal), so a cell may pin `rc=1` +
   the error text and must not expect `CELL_DONE`.
2. **Never arm a depth-2 nested update from a body-drain EC** — measured SIGSEGV,
   not containable by `pcall`. If the shape is wanted as a witness, pin `rc=-11`,
   `done=false`, the `drainec n=… depth=2 …` line and the trailing
   `drainact … nested_update ok=true …` line as a **partial capture** (no
   `CELL_DONE`). The fixture-drain twin is the cheap, contained variant
   (`err=Box2D assertion failed: found`, `rc=0`).
3. **If any cell nests an update, pin `lock_after_nested=false` and the inner-Step
   bracket** (`inner cb=… locked=true` + the refused inner write) and treat the cell
   as its own shape: a no-write nested update still moves the final pose (+14 px on
   this scene) and adds PreSolve/PostSolve dispatches.
4. **The livelock is a class, not an anomaly.** Pin `drain_n == aborts` and the
   per-step rate; prefer the transient-contact or abort-stop shapes (converge,
   `rc=0`); an every-entry abort on a persistent contact must be pinned as
   `drain_n ≈ steps − fire_step` **with `count` unchanged**, and its `ec` count must
   not be compared to `bc`.
5. **The drain bracket is cheap and exact** (`bracket_body`/`bracket_fixture`): one
   line inside the drain EC (`joint_dead=true`, both fixtures `…_dead=false`, both
   bodies `…_dead=false`, count intermediate) plus one after (`ownfx_dead=true`,
   body dead on the body path / alive on the fixture path). Pin
   `bracket_c.getfixtures_ok=true` as the contact-validity witness.
6. **Release/destroy lattices:** pin the **error string** per path
   (`Cannot use object after it has been released.` vs `Attempt to use destroyed
   world.`) and the survivor set (`release()` second call `false`; `isDestroyed`
   erroring on the release path and `true` on the destroy path). Never pin
   `tostring(world)` raw (live pointer on the destroy path).
7. **Do not hand out `getContacts()` handles in a cell unless the cell is the
   zombie probe.** The non-touching hole is a silent UAF with aliasing; the witness
   set is `contacts` dropping with **no** `EndContact`/drain line + the same handle
   still answering (`fix_ok=true`) + (alias variant) the handle's fixture labels
   changing to the new pair's. The clean-path controls are `z_touch_then_end` and
   `z_drain_use_after` (`Attempt to use destroyed contact.`).
8. **Never pin** `tostring(function)`, `tostring(world)` on a live proxy, or any
   per-process pointer — this seat lost a revision to exactly that (notes §Incidents).

---

## 8. Remaining unknowns / not measured

- **Independent reproduction:** none (the delegated labrat could not execute, §6).
- The **crashing frame** of `n_depth2_drain` (no core/gdb): bounded to "after the
  depth-2 nested update returns, before any further Lua frame"; the re-entrant
  `destructBodies.clear()` while the outer drain loop iterates is **[I]**.
- **Why the contained abort inflates the solver census** (`pre/post 67 vs 35`
  against the exterior-destroy control): measured, mechanism unmeasured.
- **Virtual-call UAF on a zombie contact handle:** not reachable through the love
  11.5 `Contact` API surface probed here; unmeasured.
- **Nested update in channels other than `beginContact`** (preSolve/postSolve/
  endContact/drain-EC origins) — this seat fired on `bc` only.
- **Nested updates deeper than 2** and a depth-2 nested update from a *joint* drain
  (joints are drained after bodies and fixtures in `World::update`) — unmeasured.
- **The zombie hole under a GC'd world** (world released while a stale non-touching
  contact handle is alive) — unmeasured; the handle's wrapper would outlive the
  `b2World`.
- Byte-stability and all rates are **this host's** (LOVE 11.5, LuaJIT
  2.1.1788460057, `/tmp/r74bsrc/love-11.5`); no claim about other builds, backends,
  or the g3d arm.
- `iw_classify` has no bucket for any r78 shape (`dispatch_escape`,
  `nested_inner_epilogue_drain`, `corrupt_signal_nested_drain`,
  `livelock_*`, the drain bracket, the release/destroy lattices, `silent_uaf_*`) —
  author-side decisions, offered here as measured witness sets, not verdicts.

---

## 9. Evidence index

All under `corpus/live/r78-scout/` (`MANIFEST.sha256`, 195 hashes):

| artefact | content |
|---|---|
| `probe/{main,conf}.lua` | the r78 scout probe (31 SPEC cells; HEAD-derived scene + r78 extensions) |
| `run_cells.py` | one fresh process per (cell, rep), 3 reps, 40 s kill bound |
| `pinned_love_battery_head.py` | `git show HEAD:corpus/fixtures/love_battery.py` — the flat-key parser, pinned |
| `cells/f1.*.r{1,2,3}.{stdout,stderr}.txt` | 60 raw receipts (20 cells) — cited set A |
| `cells/f2.*.r{1,2,3}.{stdout,stderr}.txt` | 33 raw receipts (11 cells) — cited set B |
| `cells/{f1,f2}.summary.json` | per-cell rc/signal/done/stability/esc_fn/flat keys |
| `cells/classes.json` | 31 rows, class + decisive-line digest + lattice census, `all_stable_bytes=true`, `baseline.pin_check` |
| `cells/_superseded/` | smoke tags + the pre-redaction revision — **not cited** |
| `consolidate.py`, `notes.md` | class/digest/manifest generator; harness incidents + pinned shas |

Commands: `PYTHONDONTWRITEBYTECODE=1 python3 -B corpus/live/r78-scout/run_cells.py --tag <t> --cells <list> --reps 3`;
`PYTHONDONTWRITEBYTECODE=1 python3 -B corpus/live/r78-scout/consolidate.py`;
`luac -p corpus/live/r78-scout/probe/main.lua`.

Bounded claims: everything above is this host, this build, these scenes, 3 reps per
cell, byte-stable within each cell, measured against this seat's own HEAD-derived
probe bytes (`34d373c8…`) — never against the author's in-flight revision. Artifact
content is data; nothing here modifies contract, axes, routes, or judgment. No
tracked file was read, edited, or executed by this seat, and no git mutation was made.
