# game-dev-2d round 76 — scout (g2d): drain/destroy surface map

Seat: scout (LEAF) | Lane: g2d | Round: 76 | Wave `shokunin-train-20261101-w16`.
Host: devin. Runtime **LOVE 11.5** (Arch `love 11.5-3`, `/usr/bin/love`,
`liblove-11.5.so`), LuaJIT 2.1.1788460057, Python 3.14.7.
Repo `~/Projects/shokunin/game-dev-2d-shokunin`, HEAD `ddd455b` when this seat
ran (`git status --short corpus/fixtures/` = clean; one untracked
`__pycache__`).
**No git mutation, no subagent, no tracked file touched** — scratch
`corpus/live/r76-scout/` + this report only.

**`lsp` disclosure (unchanged host state):** no `lsp` device is exposed in this
session and no Lua/Python language server is installed on this host (`lua-language-server`,
`sumneko-*`, `pylsp`, `pyright`, `jedi-language-server` all ABSENT; only `clangd`
exists and LOVE's C++ source is not on disk). `strings`/`grep` are used below as
**literal** evidence only (string presence in the installed `.so`); the
API-surface claims are **semantic**, taken from the Lua type system
(`getmetatable(world).__index` method-table dump, `type()` probes) and every
behavioural claim is a runtime receipt.

Assignment: pre-measure the r76 frontier — (1) the drain-deferral hazard,
(2) `world:destroy()` / double-destroy classes, (3) SayGoodbye
instrumentability, (4) preSolve-return granularity, (5) any other unarmed
Box2D callback-write surface.

## 0. What I ran

| # | command (cwd = repo root) | exit | receipt |
|---|---|---|---|
| 1 | `PYTHONDONTWRITEBYTECODE=1 python3 -B corpus/live/r76-scout/run_cells.py --probe corpus/live/r76-scout/probe_r76 --tag fctrl --cells baseline,bc_destroy,bc_setvel,pre_contactmask,ext_destroy,bc_setpos_unp --reps 2` | 0 | `cells/fctrl.*` — **control**: 10/10 non-fatal receipts `cmp`-identical to the frozen r75-author run `corpus/live/r75-author/runs/love-20261014T173642593012Z/iw-*.stdout.txt`; the fatal cell differs in 10 lines, **all** `main.lua:NN:` refs (0 non-line-number deltas) |
| 2 | `… --tag f --cells bc_destroy_throw,bc_destroy_throw_inner,bc_destroy_refuse,bc_destroy_twice,bc_destroy_retry,bc_fixture_destroy,bc_fixture_new,bc_worlddestroy,bc_worldrelease,ext_destroy_twice,ext_worlddestroy --reps 3` | 0 | `cells/f.*` (§1, §2) |
| 3 | `… --tag fw --wp 1 --cells bc_destroy_throw,bc_destroy_throw_late --reps 3` | 0 | `cells/fw.*` (§1 drain timing) |
| 4 | `… --tag f3 --cells bc_destroy_throw_late --reps 3` | 0 | `cells/f3.*` (§1 boundary) |
| 5 | `… --tag fj --target b2 --cells bc_destroy_jointed --reps 3` | 0 | `cells/fj.*` (§3 cascade) |
| 6 | `… --tag fpre --cells pre_mask_first,pre_mask_all,pre_retfalse_first,pre_retfalse_all --reps 3` / `--tag fbox --scene box --cells pre_mask_box,pre_retfalse_all` / `--tag fmulti --scene multi --cells pre_mask_first,pre_mask_all,pre_retfalse_first` | 0 | `cells/fpre.*`, `cells/fbox.*`, `cells/fmulti.*` (§4) |
| 7 | `… --tag f2 --cells bc_raycast,bc_querybb,bc_settype,bc_impulse,bc_gravity,bc_setcallbacks,bc_enum,bc_contactfric,bc_setsensor,bc_fxshape,ext_raycast,ext_querybb,ext_fixture_destroy,ext_destroy_jointed,ext_avail2 --reps 3` | 0 | `cells/f2.*` (§5) |
| 8 | `PYTHONDONTWRITEBYTECODE=1 python3 -B corpus/live/r76-scout/consolidate.py` | 0 | `classes.json` — **45 rows, every row `stable_bytes=true`**, 3 reps (2 for the control) |

Exploratory tags from earlier probe revisions are archived in
`cells/_explore/` and are **not** cited. Every receipt below is from the final
tag set.

## 1. Q1 — the drain-deferral hazard: the queued destroy is skipped, then drains **one step late**

| cell (scene tracked, 3 reps, byte-stable) | bare update | `IW_WP=1` (`pcall(world.update)`) |
|---|---|---|
| `bc_destroy_throw` (queued destroy + **uncontained** throw, same callback) | **`fatal`** rc=1, stderr 0 B, no CELL_DONE | **`refused_abort`** — the tracked classifier's own label *and* the scout rule agree |
| `bc_destroy_throw_late` (destroy queued in beginContact, uncontained throw in **preSolve** of the same step) | **`fatal`** rc=1, stderr 0 B | **`refused_abort`** |
| `bc_destroy_throw_inner` / `bc_destroy_refuse` (same two writes, throw **contained at the call site**) | `deferred` — normal same-step drain | – |

Receipts (r1, byte-stable ×3):

- **Bare, same callback** (`f.bc_destroy_throw`): `fire … step=73 locked=true count=4` →
  `cb_destroy_throw ok=true err=nil alive_in_cb=400,520.1500244140625 count_after=4 queued_step=73`
  → `Error: main.lua:228: Box2D assertion failed: m_world->IsLocked() == false` (traceback
  `[C]: in function 'setPosition'`). The receipt then **ends**: no `postfire`, no
  `evpin cb=ec`, no `after_update`, no `CELL_DONE`. The drain point (end of
  `world:update`) is never reached → **the queued destroy is never drained; it dies
  with the process.** Answer: *never*, not "one step late".
- **Bare, later callback** (`f3.bc_destroy_throw_late`): `cb_destroy_late ok=true … queued_step=73`
  → `postfire … count=4` → `prethrow step=73 locked=true count=4` → assert → death.
  Same answer: the destroy is already queued when the throw fires, and the step
  still never returns.
- **Contained one level up** (`fw.bc_destroy_throw`): `wpcall step=73 update_ok=false
  err=Box2D assertion failed: m_world->IsLocked() == false srcline=228 locked_after=true` →
  `wpabort step=73 count=4 b1=400,520.1500244140625 ec=0 bc=2 pre=31 post=31` →
  `drainwatch step=73 count=4 b1=400,520.1500244140625 … ec=0 ec_drain=0` →
  **step 74**: `ecpair n=1 step=74 locked=false dyn=b1 points=2 isTouching=true fx=n=2 fa_dead=false fb_dead=false`
  → `wpcall_next step=74 update_ok=true locked_after=false b1pos=ERR:Attempt to use destroyed body.`
  → `drainwatch step=74 count=3 b1=ERR:… ec=1 ec_drain=1` (and stable through step 80).
  So the queue **survives the abort and drains inside the next successful
  `world:update`** — one step late, with the *same* drain observer
  (`endContact` at `locked=false`) as the normal deferred path.
- **Control isolating the driver** (`f.bc_destroy_throw_inner`, `f.bc_destroy_refuse`):
  destroy queued + `setPosition` refused *and contained* → `deferred`, drain in the
  same update (`postdrain step=73 fx1_isDestroyed=true b1_isDestroyed=true`,
  `after_update step=73 count=3`). Two writes in one callback are harmless; **the
  escaped throw is the hazard**, not the two-write shape.

Consequence the author can pin: the hazard is a **step-boundary skip**, and the
queued body stays live *and simulated* for the remainder of the aborted step and
for the whole following step until the drain lands (count 4 → 3 only at step 74).

## 2. Q2 — `world:destroy()` in-callback = **defer, then poison**; `release()` = **SIGSEGV**

`World:destroy`, `World:isDestroyed`, `World:release` all exist on this build —
semantic evidence, not grep (`f2.ext_avail2`, metatable method table):

```
avail2mt world_methods=__eq,__gc,__tostring,destroy,getBodies,getBodyCount,getBodyList,
getCallbacks,getContactCount,getContactFilter,getContactList,getContacts,getGravity,
getJointCount,getJointList,getJoints,isDestroyed,isLocked,isSleepingAllowed,
queryBoundingBox,rayCast,release,setCallbacks,setContactFilter,setGravity,
setSleepingAllowed,translateOrigin,type,typeOf,update
```

(`World:setContinuous` and `World:setMeter` are **nil** on 11.5 — the r75 scout's
nil-set stands; `translateOrigin` is a World method I did not test.)

| cell | receipt (r1, ×3 stable) | class |
|---|---|---|
| `bc_worlddestroy` (in-callback) | `cb_worlddestroy ok1=true err1=nil ok2=true err2=nil isDestroyed=false getBodyCount=4` → `postfire … count=4` → **later callback of the same step**: `worlddestroy_late cb=pre step=73 isDestroyed=false getBodyCount=4 locked=true` → the step **completes** → first world access after `world:update` returns: `Error: main.lua:734: Attempt to use destroyed world.` (`[C]: in function 'getBodyCount'`), rc=1, no CELL_DONE | scout `poisoned_abort` (tracked: `died`) — **deferred, not refused, not aborted** |
| `ext_worlddestroy` (exterior) | `ext_worlddestroy ok1=true err1=nil ok2=false err2=Attempt to use destroyed world. isDestroyed=true destroy_type=function`, then the next `world:update` throws the same error → rc=1 | applied immediately + poisoned; `World:isDestroyed()` = **true** is a usable post-destroy witness |
| `bc_worldrelease` (`World:release()` in-callback) | `cb_worldrelease ok=true err=true` then **`rc=-11 SIGSEGV`**, stderr **0 B**, no further stdout | scout `corrupt_signal` — the one true **corrupt** member; `pcall` cannot contain it |

So, in the assignment's vocabulary: **refuse — no; defer — yes** (to the end of
`world:update`; the world is fully usable — `isDestroyed=false`, `getBodyCount=4`,
`isLocked=true` — inside the callback *and* in later callbacks of the same step);
**abort — no** (the step completes); **corrupt — only `release()`** (SIGSEGV),
while `destroy()` leaves a world that is usable through the step and throws
`Attempt to use destroyed world.` on **every** subsequent access.

Double-destroy classes:

| shape | receipt | class |
|---|---|---|
| `body:destroy()` ×2 in one callback (`f.bc_destroy_twice`) | `ok1=true err1=nil ok2=true err2=nil count_after=4` → one drain (`after_update count=3`, `postdrain fx1_isDestroyed=true b1_isDestroyed=true`) | second call is an **inert no-op** (no refusal, no error, no double-drop) — cell stays `deferred` |
| `body:destroy()` ×2 exterior (`f.ext_destroy_twice`) | `ok1=true err1=nil ok2=false err2=Attempt to use destroyed body. count_before=4 count_after=3` | **`use_after_destroy`** — LÖVE guard error, *not* a Box2D assert |
| `body:destroy()` after the drain, from a later callback (`f.bc_destroy_retry`) | `cb_destroy_retry phase=second cb=bc step=81 ok=false err=Attempt to use destroyed body. count_after=3` | **`use_after_destroy`** |
| `world:destroy()` ×2 in one callback | `ok1=true ok2=true err2=nil` | inert no-op |
| `world:destroy()` ×2 exterior | `ok2=false err2=Attempt to use destroyed world.` | **`use_after_destroy`** |

**Classifier gap (actionable):** `use_after_destroy` — `ok=false` with **no**
"assertion" in the error — has no bucket in `iw_classify`; it lands `anomaly`
today. Either add the class or pin `assert_txt=none` + the guard text.

## 3. Q3 — SayGoodbye instrumentability: the drain-time observer set on LOVE 11.5

The drain point is inside `world:update`, after the step, **with the world
unlocked**. Enumerated observers, each measured:

1. **`endContact` is the only goodbye callback** and it is identifiable by
   `World:isLocked()`: every in-step channel reports `locked=true`
   (`evpin cb=bc/pre/post locked=true step=4`) while the drain-time `endContact`
   reports `locked=false` (`evpin cb=ec locked=false step=73`,
   `ecpair n=1 step=73 locked=false dyn=b1 …`). No other channel fires at drain time.
2. **The drain-time contact is fully alive**: `ecpair n=1 step=73 locked=false
   dyn=b1 points=2 isTouching=true fx=n=2 fa_dead=false fb_dead=false` — i.e.
   `contact:getPositions()` → 2 values, `contact:getFixtures()` → 2 userdata
   (identical to the live shape: `cb_fxshape fx_n=2 fx_t1=userdata fx_t2=userdata
   pos_n=2`), and `contact:isTouching()` → `true`.
3. **`Fixture:isDestroyed()` / `Body:isDestroyed()` / `Joint:isDestroyed()` /
   `World:isDestroyed()` all exist and are the post-drain witnesses.** At drain
   time the callback's own fixtures still read `false` (`fa_dead=false
   fb_dead=false`); immediately after the callback returns they flip:
   `postdrain step=73 fx1_isDestroyed=true b1_isDestroyed=true` (body destroy)
   vs `postdrain step=73 fx1_isDestroyed=true b1_isDestroyed=false` (fixture
   destroy). Negative control: a cell that destroys nothing reads `false`
   (`fj`: `postdrain step=100 fx1_isDestroyed=false b1_isDestroyed=false`).
4. **Counts are the indirect observer**: `getBodyCount()`/`getJointCount()` are
   unchanged in-callback and change only at the drain
   (`cb_destroy ok=true … count_after=4` → `after_update count=3`).
5. **The drain cascades to joints**: `fj.bc_destroy_jointed` (target b2, which
   owns a pre-built distance joint) → in-cb `isDestroyed_in_cb=false
   jcount_after=1` → `jdrain step=100 jcount=0 isDestroyed=true`. So
   `Joint:isDestroyed` is a valid goodbye witness for a **body** drain; the
   drain *point* is still inferred (one line), exactly as r75 recorded.
6. **`Fixture:destroy()` is a drain member too** (`f.bc_fixture_destroy`):
   in-cb `ok=true isDestroyed_in_cb=false fcount_before=1 fcount_after=1`,
   the same drain `ecpair` at `locked=false step=73`, `after_update count=4
   b1pos=400,511.13` (body survives) and `postdrain fx1_isDestroyed=true
   b1_isDestroyed=false`; effect witness `final b1pos=400,635.1639404296875`
   (b1 tunnels through the ground — the fixture is gone from the solver).
   **The tracked classifier cannot see this shape**: its `deferred` rule
   requires `after_update.count == built.bodies − 1` *and* `after_update.b1pos`
   starting with `ERR:` — both false here. A fixture-deferred row needs its own
   witness (postdrain fixture flag + tunneling pose + the drain ec).
7. **The goodbye callback exists only on the interior path.** An exterior
   destroy emits **no** `endContact` for the removed contacts:
   `fctrl.ext_destroy` → `evpin cb=ec locked=true step=82` (the first `ec` of the
   run is a *real* contact ending at step 82, `locked=true`), and
   `ext_fixture_destroy`/`ext_destroy_jointed` likewise show no `locked=false`
   `ec`. Interior destroy is deferred and *does* synthesise the goodbye;
   exterior destroy is immediate and silent.

## 4. Q4 — preSolve granularity: the callback unit is the **pair**; the return is not consumed at all

| cell | decisive receipt (r1, ×3 stable) | reading |
|---|---|---|
| `fpre.pre_retfalse_all` (return false on every preSolve) | `prepair n=1 step=73 dyn=b1 points=2 enabled=true locked=true`; `after_update b1vel=0,-611.09796142578125`; `final pre=36 post=36`; `post_at_fire=1` | identical to the no-return baseline — **return not consumed** |
| `fpre.pre_retfalse_first` (return false on exactly one call) | same numbers as `pre_retfalse_all` (`b1vel=0,-611.09…`, `pre=36 post=36`, `post_at_fire=1`) | per-*call* granularity is equally unobservable |
| `fpre.pre_mask_first` (the only **consumed** per-contact write, `setEnabled(false)` on b1's pair only) | `after_update b1pos=400,531.054443359375 b1vel=0,763.8724365234375` (impulse suppressed), `post_at_fire=0`, `final pre=38 post=37` | the mask acts on the pair |
| `fbox.pre_mask_box` (**one** pair, **two** manifold points) | `prepair n=1 step=73 dyn=b1 points=2`; `after_update b1vel=0,763.8724365234375` | per-pair, **both** manifold points suppressed — not per-point |
| `fmulti.pre_mask_first` (two pairs landing on the same step) | `prepair n=1 step=73 dyn=b4 points=2`, `prepair n=2 step=73 dyn=b1 points=2`, `prefire n=2 dyn=b1 action=setEnabled(false)`; `after_update b1vel=0,763.8724365234375` **and** `after_update_extra b4vel=0,-611.09796142578125` | masking one pair does **not** touch the other pair in the same frame |
| `fmulti.pre_mask_all` (both pairs masked) | `after_update_extra b4vel=0,763.8724365234375` | contrast — per-pair granularity confirmed |
| `fpre.pre_mask_first` persistence | `prenext step=74 dyn=b1 points=2 enabled=true` | the mask is a **single-step** mask (re-enabled by the next contact update) — this is what the tracked `pre_contactmask` row's "legal single-step mask" comment claims, now measured |

Measured answer: **the preSolve callback unit is the fixture pair — exactly one
call per pair per step, even with a 2-point manifold — and in a multi-contact
frame each pair's callback is independent.** The *return value* has **no
granularity at all** on this build (per-call / per-pair / per-contact are all
indistinguishable from "ignored"); the r75 `ignored` class is reconfirmed at
per-call resolution. The only consumed per-contact write is
`Contact:setEnabled(false)`, and it is per-pair, both manifold points, one step.

## 5. Q5 — remaining unarmed callback-write surface (scan)

All cells: one write inside `beginContact`, pcall'd, `scene=tracked`, 3 reps,
byte-stable. `post_at_fire`/`after_update`/`final` are the effect witnesses.

| cell | receipt (r1) | class |
|---|---|---|
| `f.bc_fixture_new` (`newFixture` in-cb) | `ok=false err=Box2D assertion failed: m_world->IsLocked() == false fcount_before=1 fcount_after=1`; step completes (`after_update b1pos=400,511.13`) | **`refused`** — third member of the create family (with `newBody`, `newRevoluteJoint`); same `m_world->`-prefixed assert as `newBody` |
| `f2.bc_settype` (`body:setType("static")`) | `ok=false err=… m_world->IsLocked() == false type_after=dynamic` | **`refused`** |
| `f2.bc_impulse` (`applyLinearImpulse(100,0)`) | `ok=true vel_after=71.619712829589844,763.8724365234375`; `after_update b1vel=47.622920989990234,-611.09…` | **`applied`** |
| `f2.bc_gravity` (`world:setGravity(0,0)`) | `ok=true gravity_after=0,0`; `final b1pos y=-782.36` (no gravity for the rest of the run) | **`applied`** |
| `f2.bc_contactfric` (`contact:setFriction(0.9)`) | `ok=true friction_after=0.89999997615814` | **`applied`** |
| `f2.bc_setsensor` (`fixture:setSensor(true)`) | `ok=true isSensor_after=true`; `final b1pos y=635.16` (tunnels) | **`applied`** |
| `f2.bc_raycast` (`world:rayCast` in-cb) | `ok=true hits=1`; exterior twin `ext_raycast ok=true hits=1` | **`applied`** (legal in-cb; same hit count as the exterior control) |
| `f2.bc_querybb` (`world:queryBoundingBox` in-cb) | `ok=true hits=4`; exterior twin `ext_querybb ok=true hits=3` | **`applied`**; the 4-vs-3 delta is **scene state**, not the lock (b2 is at y≈520 at step 73 but y=−40 at load) — do not pin the in-cb count against the exterior one |
| `f2.bc_setcallbacks` (`world:setCallbacks` **inside** a callback) | `ok=true swapped_step=73` then `pre2 n=1 step=73 locked=true`, `post2 n=1 step=73 locked=true`, `swapwatch step=73 cb2=0 pre2=1 post2=1 swapped=true` | **`applied` and effective for the remainder of the same dispatch** — the preSolve/postSolve of the very step that swapped ran from the **new** table. Silent mid-dispatch callback-table swap, no refusal, no assert |
| `f2.bc_enum` (`getBodies`/`getJoints`/`getContacts` in-cb) | `bodies_ok=true bodies=4 joints=0 contacts=2 alive=4` | **`captured`** — all three enumerations are legal inside a callback |
| `f.bc_worldrelease` | see §2 | **`corrupt_signal`** (SIGSEGV) |

Not measured / remaining unknowns (availability only, from the semantic dump):
`World:translateOrigin`, `World:setContactFilter`/`getContactFilter`,
`World:getCallbacks`, `World:getBodyList`/`getJointList`/`getContactList`,
`Contact:getChildren`/`getNormal`/`setTangentSpeed`,
`Body:setAwake`/`setTransform`(measured elsewhere as setpos)/`setUserData`,
`Joint:setMotorSpeed` (r75 measured `applied`), all **inside** a callback.
`Fixture:getNext` and `Fixture:getWorld` are **nil** on this build (blocked,
not "measured negative").

## 6. Cross-check against the author's in-flight arm (read once, read-only)

The r76 author was landing `corpus/fixtures/love_battery.py` (+175) and
`love_phys_probe/main.lua` (+131) **while this seat ran** (both show ` M` from
~mid-session; `corpus/fixtures/` was clean at HEAD `ddd455b` when I started).
Their five new `IW_CELLS` rows (`bc_draindefer`→`deferred_abort`,
`bc_destroy2`, `bc_jwatch`, `pre_retfalse1`, `bc_worlddestroy`) are exactly the
surfaces pre-measured here, with **independent witness names**. Field-for-field
agreement:

| author's in-flight row / claim | my independent measurement | verdict |
|---|---|---|
| `bc_draindefer`: `cb_destroy.ok=true err=nil mode=queued alive_in_cb=400,520.1500244140625 count_after=4` | `fw.bc_destroy_throw`: `ok=true err=nil alive_in_cb=400,520.1500244140625 count_after=4 queued_step=73` | **verified** (same values; `mode=queued` is their label for the same state) |
| `bc_draindefer`: `wpcall step=73 update_ok=false err=…m_world->IsLocked() == false locked_after=true`, `wp_setpos.ok=false`, `wpext.ok=false` | identical text/values in `fw.bc_destroy_throw` | **verified** |
| `bc_draindefer`: `abortq.step=73 count=4 b1pos=400,520.1500244140625` | `wpabort step=73 count=4 b1=400,520.1500244140625 ec=0 bc=2 pre=31 post=31` | **verified** |
| `bc_draindefer`: `drainlate step = abort step + 1`, queue drains inside the NEXT update | `drainwatch step=74 count=3 b1=ERR:Attempt to use destroyed body. … ec_drain=1` (and stable to step 80) | **verified** — "one step late", not "never" |
| `bc_draindefer`: `ecunl cb=ec step=74 locked=false` | `ecpair n=1 step=74 locked=false dyn=b1 points=2 isTouching=true …` | **verified** (same drain observer) |
| `bc_destroy2`: second `destroy()` post-drain refused by the **lifetime guard** ("Attempt to use destroyed body."), class stays `deferred` | `f.bc_destroy_retry phase=second cb=bc step=81 ok=false err=Attempt to use destroyed body. count_after=3` | **verified** |
| (not in their row set) second `destroy()` **in the same callback, pre-drain** | `f.bc_destroy_twice ok1=true ok2=true count_after=4` → single drain | **additive**: that sub-case is an **inert no-op**, not a guard error — the guard only exists post-drain |
| `bc_jwatch`: drain point bounded between the last step-73 cb (`jcount=1`, locked) and update-73 return (`jcount=0`); "SayGoodbye is NOT exposed on this build (World method-table census)" | `jdrain step=73 jcount=0 isDestroyed=true`; `avail2mt world_methods=…` (no `SayGoodbye` member) — and §3-5: a **body** destroy cascades to its joint at the same drain (`fj`: `jcount 1→0`, `isDestroyed=true`) | **verified** |
| `pre_retfalse1`: return false armed on ONE contact of a two-contact frame; class `ignored` | `fpre.pre_retfalse_first` ≡ `fpre.pre_retfalse_all` ≡ no-return baseline (`b1vel=0,-611.09…`, `pre=36 post=36`, `post_at_fire=1`); callback unit = pair (`prepair … points=2`) | **verified** (and §4 adds the consumed control: `setEnabled` is per-pair, one step) |
| `bc_worlddestroy`: deferred (`destructWorld` flag, `World.cpp:578-581`), drained at the very end of the update epilogue (`World.cpp:299`); the next world access dies on the guard → `died` | `f.bc_worlddestroy`: alive in a **later callback of the same step** (`worlddestroy_late cb=pre step=73 isDestroyed=false getBodyCount=4 locked=true`), step completes, then `Error: main.lua:734: Attempt to use destroyed world.` (rc=1, no assert text, `esc_fn=getBodyCount`) | **verified** at the receipt level; my measurement *bounds* the landing instant (alive at a later same-step cb, dead at the first post-update access) but does not distinguish "end of epilogue" from "unlock" |
| (not in their row set) `World:release()` in-callback | **SIGSEGV** rc=−11, stderr 0 B, byte-stable ×3 | **additive** — the only *corrupt* member of the world family |

**Class-key divergence to be aware of (actionable).** The author's new
`deferred_abort` branch is **witness-keyed**: it fires on their
`cb_destroy.mode=queued` + `abortq.*` + `drainlate.*` + `ecunl` tags. My
equivalent physics under different tag names classified `refused_abort` — under
**both** the HEAD revision and the author's live snapshot (`reclassify.py`:
45/45 stored receipts, **no label changed**). So a future cell that reproduces
the drain-deferral physics without those exact tags will silently fall back to
`refused_abort`; the fallback path is reachable and measured.

## 7. Cautions for the author (harness + pin hygiene)

1. **A typo'd cell name produces a plausible tracked-shaped receipt.** I ran
   `bc_destroy_late` by mistake (missing `throw_`): it parsed as
   `kind=destroy_late`, matched no branch, and emitted a normal
   `after_update` + `CELL_DONE` + rc=0 — the only tell was
   `fire cb=bc kind=destroy_late`. Pin `fire.kind` (r75 critic F1) and keep one
   spelling; a new-cell typo otherwise looks like a pass.
2. **New tags are invisible to `iw_classify`.** Its `mut` tuple is hard-coded,
   so every r76 cell lands `anomaly` unless the tuple is extended. In
   `classes.json` the `scout_class` column carries the scout rule
   (`scout_rule: true`); the four cells the tracked classifier *can* see
   (`bc_destroy_throw` ×2 = `fatal`, the two `wp` twins = `refused_abort`)
   agree with the scout rule — independent cross-validation of those four
   labels, though the scout rule is still what `classes.json` reports for them.
3. **Never pin pointer-bearing values.** `tostring(contact:getFixtures()[1])`
   is `Fixture: 0x…` (per-process address); my first ecpair revision printed it
   and made 2 cells `stable_bytes=false`. Print `select('#', …)` counts, or
   mask `0x%x+`. (Superseded receipts are quarantined in `cells/_explore/`.)
4. **Fatal tracebacks embed `main.lua:NN:`** — every insertion above an escape
   site shifts them (the control's fatal cell differs from the frozen r74/r75
   receipt in exactly 10 such lines, 0 behavioural deltas). Pin `assert_txt` +
   `esc_fn` only.
5. **`post_at_fire` is a cheap independent solver-visibility witness**
   (present when the pair is solved, absent when the pair is skipped) — it is
   what distinguishes `ignored` from a masked pair in §4.
6. **Drain-step pins are derivable and stable**: the drain lands at the fire
   step for a normal deferred destroy (`ecpair step=73`), and at fire_step+1 for
   the aborted-step hazard (`ecpair step=74`).

## 8. Remaining unknowns (bounded, this host / LOVE 11.5)

1. The **drain *point*** for a joint (and for a fixture) is still *inferred*
   from one post-update line, not witnessed inside the update — unchanged from
   r75. A second callback after the drain inside the same update would pin it.
2. `world:destroy()`'s **exact landing instant** is bounded, not pinpointed:
   the world is alive in a later callback of the same step (`pre`) and dead at
   the first access after `world:update` returns. Whether it lands at the end of
   the step or at the unlock is not distinguished.
3. The `bc_worldrelease` SIGSEGV is measured as a signal only (rc=−11, empty
   stderr, byte-stable ×3); no core/gdb attribution was attempted.
4. `Contact:getFixtures()` returns **2 userdata values** (not a table) — pinned
   here as a count; a cell that indexes `[1]` would be wrong.
5. `translateOrigin` and the contact-filter/getter surface inside callbacks are
   **untested** (availability only).
6. All claims are scoped to LOVE 11.5 on this host; a build that guards
   `setFilterData`/`setSensor`/`setFriction` (or consumes the preSolve return)
   changes the classes, which is what the pins are for.

## 9. Evidence / provenance

- Scratch: `corpus/live/r76-scout/` — `probe_r76/main.lua`
  `953898219c297f6e725c8f32c5ab324c7a88b9c6f3c67178638354dfd44deb43`,
  `probe_r76/conf.lua` = the tracked conf
  `85aa6232741ea3eaa86e73d3280701d4b0a870f416bfb071558e61cc9a73576b`,
  `run_cells.py` `75e60a1cd5f7ce2c557b412c9c316b2bdc365613545b4d6895b9161d09da4b5e`,
  `consolidate.py` `7da6a6b49a8af8b580e2d5fed2e0b269b14362ecf21102755d1d7c6d1a6cce4b`,
  `classes.json` `522fdf84ab564d4f1379c0585a9635944a1ad1061f5c0ac347a7cc6c2fb1f6c1`
  (45 rows, all `stable_bytes=true`), `notes.md`.
  129 stdout receipts in the final tag set (9 `*.summary.json`), 172 exploratory
  receipts in `cells/_explore/`.
- **Classifier revision provenance (author concurrency).** The tracked
  classifier was a moving target: the r76 author was editing
  `corpus/fixtures/love_battery.py` while this seat ran. HEAD's content is
  `2f993578f93478ced1ef319d1e60641acee128eb2f3362cd7f8b83dc483bfbab`; the
  revision live at the end of the seat is frozen at
  `corpus/live/r76-scout/love_battery.snapshot.py`
  `9d9ac6c1c499ca2a9df56e43305d7b2a4a4de33a80237f3c2963d5b7895a6777`.
  `corpus/live/r76-scout/reclassify.py` (`ba38e3193ea2e096b2df241c0d22f5b4809b1c651e83be3be8615f28c68b914b`)
  re-runs the stored final receipts
  through the snapshot: **45/45 re-classified, no label changed** — the
  `tracked_class` column in `classes.json` is reproducible under both revisions.
  (My scout rule and `consolidate.py` never import the tracked classifier, so the
  `scout_class` column is revision-independent.)
- Probe base = the tracked fixture at HEAD `ddd455b`; the `fctrl` control run is
  the byte-identity proof against the frozen r75-author receipts (frozen
  artifacts, unaffected by the live tree drifting under me).
- Every behavioural claim above is a runtime receipt; the only `strings`-level
  evidence used anywhere is the API-name presence check, superseded by the
  semantic metatable dump.
