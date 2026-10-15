# game-dev-2d round 77 — scout (g2d): pre-measured interior-write frontier

Seat `SCOUT` (LEAF) | lane `g2d` | round 77 | host **devin**.
Runtime **LOVE 11.5** (Mysterious Mysteries, `/usr/bin/love`), LuaJIT
2.1.1788460057, Python 3.14.7. Repo `~/Projects/shokunin/game-dev-2d-shokunin`,
HEAD `aa4d567` (r76 report-last).
**No git mutation, no subagent, no tracked file touched** — writes are this
report + `corpus/live/r77-scout/**` only. `corpus/fixtures/` is clean against
HEAD (one untracked `__pycache__/*.pyc`, mtime 15:40:02, predates this seat).

**`lsp` disclosure (unchanged host state):** no `lsp` device is exposed in this
session and no Lua/Python language server is installed (`lua-language-server`,
`sumneko-*`, `pylsp`, `pyright` ABSENT; only `clangd`, and the LOVE C++ tree is
not in the repo). Text/`grep` reads of the pinned tree `/tmp/r74bsrc/love-11.5`
are **literal** evidence and are never presented as semantic proof. Semantic
carriers here are: (a) fresh-process execution receipts, (b) line-numbered
source anchors in the pinned LOVE/Box2D tree, (c) `luac -p` parser diagnostics.
No cold-start empty result is recorded as absence.

**Assignment:** pre-measure the next interior-write frontier so the r77 author's
cells land already-informed — 6 seeds: (1) `world:release()` in a callback,
(2) `world:setCallbacks` mid-dispatch, (3) `Fixture:destroy()` in a callback,
(4) the r76-boundary's four unrun predictions, (5) coroutine-wrap containment,
(6) `love.physics.setMeter` in a callback. Every seed was measured **live**, one
isolated LOVE process per probe, timeout-bound.

**Legend:** **[M]** measured (fresh process, ×3 byte-stable unless stated);
**[P]** prediction recorded before the run; **[I]** inference (source-anchored
or bounded, explicitly not a receipt).

---

## 0. What I ran

| # | command (cwd = repo root) | exit | receipt |
|---|---|---|---|
| 1 | `PYTHONDONTWRITEBYTECODE=1 python3 -B corpus/live/r77-scout/run_cells.py --tag s1 --cells baseline,bc_worldrelease,pre_worldrelease,post_worldrelease,bc_worldrelease_next,drain_worldrelease,drain_worlddestroy,ext_worldrelease,ext_worldrelease_touch --reps 3` | 0 | `cells/s1.*` (§1) |
| 2 | `… --tag s1b --cells ec_worldrelease --reps 3` | 0 | `cells/s1b.*` (§1) |
| 3 | `… --tag s2 --cells bc_setcallbacks,bc_setcallbacks_nil,bc_setcallbacks_back,multi_baseline,multi_setcallbacks --reps 3` | 0 | `cells/s2.*` (§2) |
| 4 | `… --tag s2b4 --target b4 --cells multi_setcallbacks --reps 3` | 0 | `cells/s2b4.*` (§2) |
| 5 | `… --tag s2c --cells pre_setcallbacks --reps 3` | 0 | `cells/s2c.*` (§2) |
| 6 | `… --tag s3 --cells bc_fixture_destroy,bc_fixture_destroy2,ext_fixture_destroy --reps 3` | 0 | `cells/s3.*` (§3) |
| 7 | `… --tag s4 --cells wp_throw_then_queue,wp_queue_then_throw,wp_drain_throw,drain_setpos_b2,drain_queue_b2 --reps 3` | 0 | `cells/s4.*` (§4) |
| 8 | `… --tag s4j --target b2 --cells drain_order_joint --reps 3` | 0 | `cells/s4j.*` (§4d) |
| 9 | `… --tag s5 --cells bc_cowrap_setpos,bc_cowrap_unp,bc_coyield,wp_coyield,co_update,co_update_yield --reps 3` | 0 | `cells/s5.*` (§5) |
| 10 | `… --tag s5b --cells cowrap_update_yield --reps 3` | 0 | `cells/s5b.*` (§5) |
| 11 | `… --tag s6 --cells bc_meter,pre_meter,ext_meter --reps 3` | 0 | `cells/s6.*` (§6) |
| 12 | `python3 -B corpus/live/r77-scout/…` consolidation (inline) | 0 | `classes.json` (36 rows, **every row `stable_bytes=true`**), `MANIFEST.sha256` (227 hashes) |

Probe: `corpus/live/r77-scout/probe_r77` (sha256
`ebf67346d9aa8838a89876c1dbb6f91a23e84c316282944371759fb16d651cc2`).
Runner: `corpus/live/r77-scout/run_cells.py` (sha256
`8264b8e363cfc397b8acbfae332bf6328a55207d648699d9a9f716696f57e769`).
36 rows = 35 cells + the `--target b4` variant; **108 cited processes**
(3 reps each) plus one superseded pre-trace probe revision kept in
`cells/_superseded/` (196 receipts, not cited).
`luac -p probe_r77/main.lua` OK. Scratch incidents (shadowed local; a pinned
`tostring(function)` address; fixture-list order) are recorded in
`corpus/live/r77-scout/notes.md` and are not evidence.

Scene: the r70/r74 tracked scene (ground + b1/b2/b3) so the fire step and poses
inherit the frozen determinism; `multi` adds b4 (two pairs land on step 73);
the joint cell pre-builds the r76 `newDistanceJoint(b2, b3, …)`.

---

## 1. Seed 1 — `world:release()` inside a callback

### Verdict table (all **[M]**, ×3 byte-stable, stderr 0 B in every row)

| cell | channel / phase | rc | signal | `done` | last emitted line | witness after release? |
|---|---|---|---|---|---|---|
| `bc_worldrelease` | beginContact, locked=true, step 73 | **-11** | SIGSEGV | false | `postfire marker=1` | yes |
| `pre_worldrelease` | preSolve, locked=true, step 73 | **-11** | SIGSEGV | false | `postfire marker=1` | yes |
| `post_worldrelease` | postSolve, locked=true, step 73 | **-11** | SIGSEGV | false | `postfire marker=1` | yes |
| `ec_worldrelease` | **natural** endContact, locked=true, step 74 | **-11** | SIGSEGV | false | `postfire marker=1` | yes |
| `drain_worldrelease` | **drain** endContact, locked=false, step 73 | **-11** | SIGSEGV | false | `drainact n=1 rel_alive marker=1` | yes |
| `drain_worlddestroy` (bonus) | `world:destroy()` at locked=false in the drain EC | **-11** | SIGSEGV | false | `drainact n=1 wd_alive marker=1` | yes |
| `ext_worldrelease` | exterior (love.load) | 1 | none | false | `Error: …: Cannot use object after it has been released.` | n/a — **contained** |
| `ext_worldrelease_touch` | exterior, no touch until the loop | 1 | none | false | `Error: …: Cannot use object after it has been released.` | n/a — **contained** |

Common interior receipt (all five channels, byte-identical shape):

```
fire cb=bc kind=worldrelease/- step=73 locked=true count=4 pos=400,520.1500244140625 vel=0,763.8724365234375
rel_pre kind=worldrelease
rel_call ok=true err=true          <- pcall(world.release, world) succeeded; release() returned true
rel_alive marker=1                 <- plain io.write, no world access
postfire marker=1                  <- end of the callback body; then the process dies
```

### Answers

1. **Reproducible ×3** for every channel: 18 interior processes, 6 distinct
   shapes, all `rc=-11`, all byte-stable **[M]**. r76-scout's single
   `bc_worldrelease` observation reproduces exactly (`ok=true err=true`, then
   SIGSEGV, stderr 0 B).
2. **Which callback kinds trigger it:** all of them — `beginContact`,
   `preSolve`, `postSolve`, a **natural** `endContact` (locked=true, inside
   `b2World::Step`) and the **drain** `endContact` (locked=false, inside the
   update epilogue) **[M]**. It is not a channel property: the release destroys
   the `World` object the engine is currently executing inside.
3. **Can a witness line be captured before death? YES** **[M]**. stdout is
   flushed per line, so the marker written *immediately after* the release call
   (`rel_alive`) and the end-of-callback marker (`postfire`) both land on the
   pipe. The last emitted line is always the callback's own final write.
4. **Can a `CELL_DONE`-like marker ever exist? NO** **[M]**. `done=false` and
   `rc=-11` in all six interior shapes: the process dies inside the step, so no
   end-of-run marker is reachable. A *partial* receipt is the honest shape.
5. **Where the death sits — bounded** **[M]/[I]**: `bc_worldrelease_next` arms a
   witness for the *next* dispatch; the receipt shows `rel_alive` and
   `postfire` and then dies with **no `after_release` line** — the engine never
   enters another Lua callback after the release. So the crash is C++-side,
   between the callback's return and the next dispatch (or in the freed
   update epilogue). The precise frame is **[I]** — not localized (no gdb/core
   was taken).
6. **`pcall` cannot contain it** **[M]**: `pcall(world.release, world)` returns
   normally (`ok=true err=true`); the signal arrives later, outside any Lua
   protection. This is the **corrupt** member of the class set — parallel to
   r76-scout's `corrupt_signal`, now measured across five channels with a
   witness line and a bounded death site.
7. **Exterior release is a different class** **[M]**: the wrapper nulls the
   proxy (`p->object = nullptr`) and the object is deleted; every later Lua
   touch is a **catchable Lua error** — `world:*` → `Cannot use object after it
   has been released.`, `b1:getPosition()` → `Attempt to use destroyed body.`
   (the body wrappers were invalidated by `World::destroy()`), and the process
   ends `rc=1` at the first uncaught touch (no signal). So `release()` is
   corrupt **only** from inside the engine's own execution.

Source anchors (re-read from the pinned tree, line-exact): `common/runtime.cpp`
`w__release` (proxy nulled, `object->release()`, registry cleanup);
`common/Object.cpp` `Object::release()` → `delete this` when the count hits 0;
`common/runtime.h` proxy guard `"Cannot use object after it has been released."`;
`wrap_World.cpp` `luax_checkworld` (`"Attempt to use destroyed world."`);
`World.cpp` `World::~World()` → `destroy()` with the `IsLocked()` early return
(the destructor therefore frees the wrapper while leaving the `b2World`).

---

## 2. Seed 2 — `world:setCallbacks` inside a callback

All **[M]**, ×3 byte-stable, `rc=0`, `CELL_DONE`, `getcb` printed through stable
identity labels (`cb2_bc,cb2_ec,cb2_pre,cb2_post`).

| question | cell | decisive receipt | answer |
|---|---|---|---|
| effect on **later channels of the same step** | `bc_setcallbacks` (swap in beginContact, step 73) | `cb2 cb=pre n=1 step=73 locked=true`; `cb2 cb=post n=1 step=73 locked=true`; step-73 counts old `bc=2 pre=31 post=31` vs new `pre2=1 post2=1` | **yes** — the new table handles the rest of the step |
| effect on **later contacts of the same step** | `multi_setcallbacks --target b4` (b4's begin is dispatched first at step 73; swap fires there) | `cb2 cb=bc n=1 step=73 locked=true dyn=b1` (b1's begin, dispatched later in the same step, goes to the NEW table); old `bc` frozen at 2 for the whole run | **yes** — later contacts too |
| effect on the **same contact's next channel** | `pre_setcallbacks` (swap in preSolve) | same contact's postSolve → `cb2 cb=post n=1 step=73 locked=true`; old `post=31` never grows again | **yes** |
| can a **swapped-out** callback still fire in the same dispatch? | `bc_setcallbacks`, `multi_setcallbacks`, `pre_setcallbacks` | after the swap the old table's counters never increment again in that step (the swap call itself is the last old-table entry) | **no** — the table is read per dispatch, so there is no queued/retained invocation |
| **last-write-wins** | `bc_setcallbacks_back` (setCallbacks(new) then setCallbacks(old) inside one callback) | `getcb=c_bc,c_ec,c_pre,c_post`; `bc2/ec2/pre2/post2 = 0` for the entire run | **yes** |
| **nil table** | `bc_setcallbacks_nil` | `getcb=nil,nil,nil,nil`; the whole callback surface goes silent for the rest of the run (final `pre=31 post=31 ec=0` vs baseline `pre=36 post=36 ec=4`); physics untouched (final `b1=400,445.10910034179688`, identical to baseline); rc=0, no crash | **nil refs are legal and silently mute the surface** |
| dispatch order control | `multi_baseline` | `cbev cb=bc … step=73 dyn=b4` then `… dyn=b1` | the pair order is measured, so the two `multi_setcallbacks` runs are a controlled target swap |

Source anchors: `World::setCallbacks` (`World.cpp`) deletes and replaces all
four `Reference*`s immediately; `World::ContactCallback::process` reads `ref` at
each dispatch (so the swap is per-dispatch, not per-step); `w_World_update`
calls `setCallbacksL(L)` per update (the callbacks follow the calling Lua
state).

**Author trap:** `world:getCallbacks()` returns the functions themselves — a
receipt that prints `tostring(f)` embeds a per-process address and is
`stable_bytes=false` (my first revision hit exactly this). Pin identity through
labels, never addresses.

---

## 3. Seed 3 — `Fixture:destroy()` inside a callback

### Measured shape (`bc_fixture_destroy`, ×3 byte-stable)

```
fire cb=bc kind=fixture_destroy/- step=73 locked=true count=4 pos=400,520.1500244140625
cb_fxdestroy ok=true err=nil isDestroyed_in_cb=false fcount_before=1 fcount_after=1 count_after=4
postfire marker=1
cbev cb=ec table=old n=1 step=73 locked=false dyn=b1      <- the drain EC (the goodbye)
drainec n=1 step=73 locked=false count=4 jcount=0 dyn=b1
stepobs step=73 … count=4 … b1dead=false … fx_a_dead=true …
final steps=200 count=4 b1=400,635.1639404296875 b1dead=false fx_a_dead=true
```

`bc_fixture_destroy2` (two fixtures on b1, destroy `getFixtures()[1]`):
`cb_fxdestroy ok=true err=nil isDestroyed_in_cb=false fcount_before=2
fcount_after=2 sib_dead=false count_after=4` → post-drain `fx_a_dead=true`,
**`fx_b_dead=false`**, `b1dead=false`, and b1 does **not** tunnel
(final `394.08963012695312,445.10308837890625`) **[M]**.

Exterior twin `ext_fixture_destroy`: `ok=true isDestroyed_after=true fcount=0`
immediately, `drain_n=0` (no goodbye), b1 falls forever (final y=3565.44) **[M]**.

### Why the tracked `deferred` rule cannot see it **[M]**

`iw_classify`'s `deferred` gate requires `after_update.count == built.bodies − 1`
**and** `after_update.b1pos` starting with `ERR:`. A fixture destroy leaves the
body alive and the count unchanged, so both conjuncts are false and the row
would land `anomaly`. r76-scout §3.6 flagged this; this seat measures the full
witness set.

### Class recommendation

**Keep the class `deferred`; add a fixture branch with its own witness set.**
The *gating* is identical (locked at the call site → retained + queued → drained
inside `World::update`'s epilogue), so a second class name would encode object
type, not behaviour. If the author prefers one class per object type, mint
`deferred_fixture` — both are defensible; the witness set is what must not be
borrowed from the body case.

Witness roles (which witness is load-bearing, measured):

| witness | separates deferred from… | notes |
|---|---|---|
| in-cb `ok=true` + `isDestroyed_in_cb=false` + `fcount` unchanged | …**applied** (the exterior twin reads `isDestroyed=true` and `fcount` drops *inside* the call) | **[M]** |
| **drain EC at `locked=false`** | …**applied** and from any non-drain path | the only goodbye; interior-only **[M]** |
| post-drain `fixture isDestroyed=true` **AND** `body isDestroyed=false` **AND** count unchanged | …a **body** destroy (which drops the count and kills the body) | **[M]** |
| effect witness: tunneling pose (single-fixture) or the sibling's `isDestroyed=false` + non-tunneling pose (two-fixture) | …a no-op write | **[M]** |
| `count` alone | nothing | **[M]** — it cannot see a fixture destroy |

---

## 4. Seed 4 — the r76-boundary's four unrun predictions

### 4a. Throw-before-queue ordering — **[P] verified [M]**

`wp_throw_then_queue` (uncontained `setPosition` *then* `destroy()`, pcall at the
update level):

```
fire … step=73 locked=true
cb_ttq phase=before_throw
abort step=73 update_ok=false err=Box2D assertion failed: m_world->IsLocked() == false srcline=307 locked_after=true
abortq step=73 count=4 b1=400,520.1500244140625 b1dead=false b2=240,431.05447387695312 b2dead=false jcount=0
abortext ok=false err=Box2D assertion failed: m_world->IsLocked() == false b2=240,431.05447387695312
recover step=74 locked_after=false count=4 b1=400,509.53021240234375 b1dead=false …
final steps=200 count=4 b1=400,461.54888916015625 b1dead=false … drain_n=0
```

No `cb_ttq phase=after_*` line ever appears → the throw landed at the
`setPosition` and `destroy()` never executed. **Count stable (4), no queue, no
drain EC ever (`drain_n=0`), body alive through step 200** — the prediction
holds. Contrast cell `wp_queue_then_throw` (queue *then* throw): `cb_qtt
phase=queued ok=true … count_after=4` → abort → `drainec n=1 step=74
locked=false` → `recover step=74 count=3 b1dead=true` — the accepted destroy
survives the abort and drains one step late (r76's `deferred_abort`,
independently reproduced with a different probe).

### 4b. Abort INSIDE the drain EC — **[P] partly refuted, measured answer**

`wp_drain_throw` (destroy queued in beginContact; uncontained throw on the first
drain entry; pcall at the update level):

```
drainec n=1 step=73 locked=false count=4 jcount=0 dyn=b1
drainact n=1 kind=throw
abort step=73 update_ok=false err=R77-DRAIN-THROW srcline=253 locked_after=false
abortq step=73 count=4 b1=400,511.13113403320312 b1dead=false b2=240,431.05447387695312 b2dead=false jcount=0
abortext ok=true err=nil b2=999,999                 <- legal exterior write STILL LANDS
cbev cb=ec table=old n=2 step=74 locked=true dyn=b1  <- an EndContact for b1 INSIDE step 74
ecev n=2 step=74 locked=true dyn=b1 count=4 jcount=0
recover step=74 locked_after=false count=3 b1=ERR:Attempt to use destroyed body. b1dead=true … drain_n=1
```

Answers:

- **`locked_after=false`** and **`abortext ok=true`** — an abort inside the
  drain EC leaves the world **unlocked** and causes **no collateral refusal**.
  This is a *distinct signature* from every r75/r76 abort (callback-level
  aborts: `locked_after=true` + collateral refusal). The transient lock is a
  property of *where* the abort happened (inside `b2World::Step`), not of the
  abort itself. **[M]**
- **Does the same contact's EndContact re-fire next update?** Not as a drain
  goodbye: `drain_n` stays 1 and no second `drainec` line exists. Instead an
  EndContact for the same dynamic body fires **inside step 74 at
  `locked=true`** (`ecev n=2`). **[M]** (that the step-74 EC is the *same
  contact* is **[I]** — the label witnesses the body, not the contact identity.)
- **Does `DestroyBody` retry?** Effectively yes: the queued destroy was
  abandoned mid-flight (the drain loop never reached its clears) and the destroy
  **completes one step later** (`recover step=74 count=3 b1dead=true`) with no
  goodbye of its own — the contact had already been torn down inside the step.
  **[M]**
- The abort is *not* fatal and *not* a leak in this shape: rc=0, `CELL_DONE`,
  final `count=3`, the run continues to step 200. **[M]**

### 4c. Writes legal inside the drain EC — **[P] verified [M]**

| cell | receipt | reading |
|---|---|---|
| `drain_setpos_b2` (`b2:setPosition(1234.5, 678.9)` at locked=false in the drain EC) | `drainact n=1 kind=setpos_b2 ok=true err=nil b2pos=1234.5,678.9000244140625`; stepobs step=73 `count=3 b2=1234.5,678.9000244140625`; final `b2=1234.5,3713.2890625` | **applied** (no assert; the world is unlocked there), persists, and the b1 destroy in the same drain completes (`count=3`, `drain_n=1`) |
| `drain_queue_b2` (`b2:destroy()` at locked=false in the drain EC) | `drainact n=1 kind=queue_b2 ok=true err=nil count_after=3 b2dead=true` | **immediate, not deferred** — the body dies inside the drain EC (final `count=2`) |

So the deferred rule is a **lock-state** rule, not a phase rule: at the drain
EC the world is unlocked, so `destroy()` executes on the spot and structural
writes are legal. Any cell that wants the drain path must not assume the lock.

### 4d. Drain ordering — **[P] verified exactly [M]**

`drain_order_joint` (`--target b2`, the r76 distance joint b2↔b3; fire step 100):

```
drainec n=1 step=100 locked=false count=4 jcount=0 dyn=b2
drainact n=1 kind=order j_dead=true fx_dead=false body_dead=false other_dead=false jcount=0
final steps=200 count=3 b2=ERR:Attempt to use destroyed body. b1dead=false b2dead=true b3dead=false jcount=0
```

Inside a jointed body's drain EC: the **joint already reads
`isDestroyed=true`**, while the contact's fixture and the body read `false` and
the other body is alive. Source-anchored **[I]**: `b2World::DestroyBody`
destroys the attached joints first (`SayGoodbye` → love's
`World::SayGoodbye(b2Joint*)` → `Joint::destroyJoint(true)` → wrapper
invalidated, `jcount` 1→0) **before** the contacts (`b2ContactManager::Destroy`
→ `EndContact`, and only then the list removal), the fixtures, and finally the
body.

---

## 5. Seed 5 — coroutine containment: the ladder is measured

All **[M]**, ×3 byte-stable.

| cell | container | receipt (decisive line) | rc | class |
|---|---|---|---|---|
| `bc_cowrap_setpos` | `coroutine.wrap` body + pcall **inside** | `cb_cowrap inner ok=false err=Box2D assertion failed: …` / `outer ok=true res=inner-done`; step completes; final identical to the plain refused cell | 0 | contained — **wrap adds nothing**; the container is wherever the pcall sits |
| `bc_cowrap_unp` | `coroutine.wrap` body, uncontained `co()` | `Error: main.lua:336: main.lua:332: Box2D assertion failed: m_world->IsLocked() == false`, traceback `[C]: in function 'co'` | 1 | fatal; **`esc_fn=co`** (distinct from the plain cell's `esc_fn=setPosition`), no `postfire`, no `CELL_DONE` |
| `bc_coyield` | none | `Error: …: attempt to yield across C-call boundary`, `[C]: in function 'yield'` | 1 | fatal; a yield across the callback boundary is an **error**, never a suspension |
| `wp_coyield` | pcall(world.update) | `abort … err=attempt to yield across C-call boundary srcline=372 locked_after=true`; `abortext ok=false` (collateral refusal); `recover step=74 locked_after=false` | 0 | the **same abort shape** as a throw abort — no distinct class |
| `co_update` | `coroutine.resume(world:update)` | rc=0, `CELL_DONE`; final counts/pose **identical to the baseline** (`bc=5 ec=4 pre=36 post=36`, `b1=400,445.10910034179688`) | 0 | transparent container |
| `co_update_yield` | `coroutine.resume` + yield in the callback | `coused step=73 ok=false err=main.lua:372: attempt to yield across C-call boundary costatus=dead`; the error is **returned**, not raised; `abort … locked_after=true`; `abortext ok=false`; `recover step=74 locked_after=false`; run continues | 0 | **resume IS a containment level**: same transient-lock/collateral signature, **no process death**, no wp witness |
| `cowrap_update_yield` | `coroutine.wrap(world:update)` + yield | `Error: main.lua:538: main.lua:375: attempt to yield across C-call boundary`, `[C]: in function 'f'` | 1 | fatal; **`esc_fn=f`** — wrap re-raises in the caller |

**Measured ladder** (weakest → strongest): none → fatal (rc=1) ⊂ `coroutine.wrap`
→ fatal (rc=1, `esc_fn` = the wrap function) ⊂ `coroutine.resume` → the error
comes back as a value, the run survives, the world is transiently locked with
the full collateral signature ⊂ `pcall(world:update)` → the named abort witness
set. `coroutine.wrap` is **not** a containment level; `coroutine.resume` **is**.
A yield across the lock window behaves exactly like a throw at the same
containment level.

---

## 6. Seed 6 — `love.physics.setMeter` inside a callback

**[M]**, ×3 byte-stable, `rc=0`:

```
bc_meter (beginContact, step 73) and pre_meter (preSolve, step 73), identical:
cb_meter ok=true err=nil meter_before=30 meter_after=60 pos_now=800,1040.300048828125 grav_after=0,1255.6800537109
cb_meter2 ok=true err=nil meter=1 pos_now=13.333333015441895,17.338333129882812
ext_meter (exterior control): ok=true err=nil meter_before=30 meter_after=60 pos_now=800,120
```

- **Applied under lock, no assert** — `Physics::setMeter` is a *static module
  global* write (`Physics.cpp`), not a world mutation, so there is nothing for
  the lock to gate. Interior and exterior shapes are identical.
- **Immediate, sharp effect witness:** every *reported* quantity scales by the
  new meter at the Lua boundary — `pos_now` doubles (meter 60) and then divides
  by 30 (meter 1); `world:getGravity()` doubles to `0,1255.6800537109`.
- **Invariance witness [M]:** the meter cells' final pose ×30 =
  `400,445.109…`, i.e. the baseline's `b1=400,445.10910034179688` — the solver's
  b2-space trajectory is untouched; only the reporting scale changes. A cell can
  therefore pin the meter write with a *ratio*, not a trajectory.

---

## 7. Ready-to-arm recommendations for the r77 author

1. **Release cells must be partial-capture by construction.** Pin
   `rc=-11`, `done=false`, `stderr_bytes=0`, the presence of the post-release
   witness line and the **absence** of any later line. Do **not** expect
   `CELL_DONE`; do **not** try to pcall it. One process per cell (already the
   battery's rule). A cell that emits only *after* the release call loses the
   witness; emit immediately after.
2. **Fixture destroy needs its own witness branch** (§3). The cheapest
   falsifiable pin set: in-cb `ok=true`/`isDestroyed=false`/`fcount` unchanged;
   drain EC at `locked=false`; post-drain fixture-dead + body-alive + count
   unchanged; effect witness (tunneling or the live sibling).
3. **The drain-EC abort is a distinct signature** (§4b): `locked_after=false`
   + no collateral refusal + late silent completion. If the author arms it,
   name the class for the *shape*, and pin `abortext ok=true` (the collateral
   control is what separates it from `refused_abort`/`deferred_abort`).
4. **The ordering cell is cheap and exact** (§4d): one joint, one drain EC, one
   line (`j_dead=true fx_dead=false body_dead=false other_dead=false`).
5. **Never pin** `tostring(function)`, per-process pointers, or `srcline`; pin
   identity labels and emitted values only.
6. `setCallbacks`-mid-dispatch cells are safe (rc=0) and can pin the **counts**
   per table (`bc/pre/post` old vs `bc2/pre2/post2` new) plus the `getcb`
   label readback; the nil-table cell adds the "surface goes mute, physics
   unaffected" invariance.

---

## 8. Remaining unknowns / not measured

- **Exact C++ death site of the interior release** (next dispatch vs update
  epilogue vs the freed `destructBodies` vector) — bounded to "after the
  callback's last Lua write, before any further Lua frame", not localized
  (no debugger/core dump taken).
- Whether a release inside a *non-callback* engine path reachable from Lua
  (e.g. a raycast callback) crashes identically — not measured; the raycast
  callback is a Lua frame too, so the same family is expected but unproven.
- The **contact identity** of the step-74 EC in `wp_drain_throw` (body label
  only); a per-contact id is not exposed on this build.
- A drain EC that throws on **every** entry (my throw was armed on `n==1`, so
  the retry could complete): infinite retry vs lockout is unmeasured.
- `drain_worlddestroy`'s crash site (same family as release) and whether the
  engine can ever survive a world killed inside the drain loop.
- Byte-stability is a **this-host** property (LOVE 11.5, LuaJIT 2.1.1788460057,
  `/tmp/r74bsrc/love-11.5`); no claim about other builds, other backends, or
  the g3d arm.
- `iw_classify` has no bucket for `corrupt_signal`, `use_after_destroy`,
  `deferred_fixture`-shaped receipts or the drain-EC abort — those remain
  author-side decisions, offered in §7 as measured witness sets, not as verdicts.

## 9. Evidence index

| artefact | content |
|---|---|
| `corpus/live/r77-scout/probe_r77/{main,conf}.lua` | probe (SPEC-declared cells, drain hook, containment containers) |
| `corpus/live/r77-scout/run_cells.py` | one fresh process per (cell, rep), 3 reps, 20 s kill bound |
| `corpus/live/r77-scout/cells/s*.*.r{1,2,3}.{stdout,stderr}.txt` | 216 raw receipts (this citation set) |
| `corpus/live/r77-scout/cells/s*.summary.json` | per-cell rc/signal/done/stability/last-lines/esc_fn |
| `corpus/live/r77-scout/classes.json` | 36 consolidated rows, `all stable_bytes=true` |
| `corpus/live/r77-scout/MANIFEST.sha256` | 227 hashes (receipts + summaries) |
| `corpus/live/r77-scout/notes.md` | harness, incidents, superseded revision |
| `corpus/live/r77-scout/cells/_superseded/` | 196 receipts from the pre-trace revision — **not cited** |

Bounded claims: everything above is this host, this build, these scenes, 3 reps
per cell, byte-stable within each cell. Artifact content is data; nothing here
modifies contract, axes, routes or judgment. No tracked file was edited and no
git mutation was made by this seat.
