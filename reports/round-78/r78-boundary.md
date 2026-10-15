# game-dev-2d round 78 — BOUNDARY (g2d): adversarial attack on the nested-update claims

Seat `BOUNDARY`/critic | lane `g2d` | round 78 | wave `shokunin-train-20261101-w18` | host **devin**.
Runtime **LOVE 11.5.0** (Mysterious Mysteries, `/usr/bin/love`), LuaJIT 2.1.1788460057, Python 3.14.7.
Repo `~/Projects/shokunin/game-dev-2d-shokunin`, HEAD **`d4aaa9588f75aee8259e397226433fb64fbaf48b`**
(no git mutation by this seat). **Own LOVE processes, own scratch** under
`corpus/live/r78-boundary/`; `corpus/fixtures/**` was neither read (content), executed,
nor written, and the author's in-flight diff (`love_battery.py`, `love_phys_probe/main.lua`
both `M` in `git status`) was never touched — the one exception is disclosed in §0.

**Attacked:** the five r78-scout claims (a) inner update owns an epilogue drain,
(b) depth-2 via a body-drain EC SIGSEGVs, (c) fixture-drain-EC nesting is refused not
fatal, (d) zombie contacts UAF, (e) every-entry abort livelocks — plus the brief's four
questions. **Result in one line:** (a) **CONFIRMED and sharpened**, (b) **MIS-ATTRIBUTED —
the crash is not depth-gated, it reproduces at depth 1**, (c) confirmed and shown to be
depth-independent, (d) reproduced with a **corrected mechanism**, (e) confirmed but the
bound is **step-deterministic, not wall-clock**, and the gate the scout's own probe uses
is **forgeable three ways** (§4).

**Legend:** **[M]** measured (fresh process, ×3 byte-stable); **[S]** source-anchored
(line-exact in `/tmp/r74bsrc/love-11.5`, never presented as semantic proof); **[I]** inference.
Classes are **witness sets offered to the author**, never verdicts. Receipt lines are quoted
**verbatim** minus the `RB | cell=<C> | ` prefix; `…` marks an elision, and a line quoted in
prose backticks may be partial (the raw files under `cells/` are the authority).

---

## 0. What I ran

| # | command (cwd = repo root) | exit | receipt |
|---|---|---|---|
| 1 | `PYTHONDONTWRITEBYTECODE=1 python3 -B corpus/live/r78-boundary/run_cells.py --tag f1 --reps 3 --timeout 60 --cells baseline,a_inner_real,a_inner_two,a_inner_silent,a_drain_immed,b_drain1,b_drain1_wp,b_drain1_fx,b_drain2_second,c_forge,c_forge_pre,c_forge_ext,d_zombie,d_touch_ctrl,e_live_persist,e_live_400,e_live_transient,e_live_two,e_live_fx2,x_control_destroy` | 0 | `cells/f1.*` |
| 2 | `… --tag f2 --burn 3 --cells e_live_persist,e_live_400,e_live_transient,e_live_two,x_control_destroy,a_inner_real` | 0 | `cells/f2.*` |
| 3 | `… --tag f3 --cells b_drain1_fx_wp,b_drain1_fx,b_drain2_second` | 0 | `cells/f3.*` |
| 4 | `… --tag f4 --cells d_touch_ctrl,d_zombie` | 0 | `cells/f4.*` |
| 5 | `luac -p corpus/live/r78-boundary/probe/main.lua` | 0 | parse OK |

**93 cited processes** (31 cell-runs × 3 reps), one fresh LOVE process per (cell, rep),
60 s kill bound, **every cell byte-stable across its 3 reps**, stderr 0 B on every cited
receipt (the two fatal-error cells print LOVE's traceback to **stdout**).
Probe `probe/main.lua` sha256 `f9bdeec43b5ec28232251bccf8eb45943a684a64be04e55522c6a08ff94f4529`,
runner `b40d072b…`, `MANIFEST.sha256` 246 hashes. All four tags were run against that one
revision (earlier `smoke*` revisions are kept, **not cited**; notes.md §Pins).

**Scene (mine, not the scout's):** ground + `b1` (bouncing projectile, restitution 0.85) +
`b2` (falling) + `r1,r2,r3` (resting on the ground, persistent touching contacts) + a
non-touching `na/nb` pair (AABB overlap, no shape overlap), **sleeping disabled** so no
contact is skipped by `Collide`'s inactive-body branch [S `b2ContactManager.cpp:139-146`].
`IW`-style cells were not reused; the probe is self-contained and reads no tracked file.
*Disclosure:* three `git show HEAD:<tracked file> | sha256sum|wc -l` invocations hashed the
committed blobs for pinning only (no content read into any decision, no execution, no write).

**Probe-side predicates the receipts lean on.** `locked` = `world:isLocked()`.
`deferred` = was the world locked at the moment of a `destroy()` call (only a deferred call
enters `World::update`'s epilogue drain). `own` = how many of *this probe's deferred and
still-pending* destroys own one of an EndContact's two bodies; `imm` = the same for an
immediate destroy; `cls = drain | immediate | foreign`. `gate` = the r78-scout drain-EC
predicate verbatim: `ev == "ec" and locked() == "false"`.

---

## 1. Verdict table

| # | claim / question | attack | outcome |
|---|---|---|---|
| Q1 | inner drain REAL or observer? | queue-then-nest, queue-after-nest, two-item queue, non-touching target | **REAL and it owns the whole queue** — but its EC is neither necessary nor sufficient (§2) |
| Q2 | does depth-2 reproduce at depth 1? | nest from a **depth-0** (top-level) drain EC; from the 2nd drain EC; fixture twin | **YES — SIGSEGV at depth 1**, twice; depth is not the variable (§3) |
| Q3 | can a forged drain EC pass a gate? | broadphase AABB destroy after a Collide-phase nest; exterior immediate destroy | **YES, two independent forgeries**, one field-identical to a real drain EC (§4) |
| Q4 | livelock bound deterministic or wall-clock? | 3.8× wall-clock burn, 200 vs 400 updates, 2 contacts on target, 2 queued bodies | **step-deterministic**; one attempt per `world:update`; **starves later queued bodies** (§5) |
| a | inner update owns an epilogue drain | §2 | CONFIRMED (+ the EC is not a necessary witness) |
| b | depth-2 via body-drain EC → SIGSEGV | §3 | CONFIRMED as a crash, **REFUTED as depth-2** |
| c | fixture-drain nesting refused not fatal | §3.3 | CONFIRMED, depth-independent, and it is the mechanism control |
| d | zombie contacts UAF | §6 | CONFIRMED, **mechanism corrected** (memoizer, not vptr poisoning) |
| e | every-entry abort livelocks | §5 | CONFIRMED, with a starvation corollary the scout's cells could not see |

---

## 2. Q1 — the inner drain is REAL, and it owns the whole queue

**`a_inner_real`** (queue `r1`, nest one update, queue `r2` after the nest; receipt excerpted,
lines in order) **[M]**:

```
queue  label=r1 ok=true err=nil dead_in_cb=false deferred=true count=8 cc=5 pend=1
ecobs  n=1 step=73 locked=false depth=1 in_cb=true upd=true pend=1 own=1 cls=drain gate=PASS dyn=r1
drainec n=1 step=73 locked=false depth=1 in_cb=true upd=true pend=1 own=1 cls=drain count=8 cc=5 dyn=r1
nested1 ok=true err=nil lock_after=false depth_after=0 count=7 cc=4 pend=0 drain_n=1
queue  label=r2 ok=true err=nil dead_in_cb=true deferred=false count=6 cc=3 pend=0
```

- The queued `r1` is destroyed **inside** the nested `world:update` (`count 8→7` on the
  `nested1` line, i.e. before the outer `world:update` returned), and its EndContact is
  dispatched at **`depth=1 in_cb=true`** — while the outer callback is still on the stack.
  The outer epilogue had nothing left to drain for `r1` **[M]**.
- **`a_inner_two`** (queue both `r1` and `r2`, one nest) drains **both** inside the single
  nested call (two `depth=1` ECs, `count 8→6`, `pend` 2→1→0) and emits **no** EC at the
  outer epilogue **[M]** → the inner invocation consumes and clears the whole queue.
- So the inner drain is not an observer of the outer queue: it is `World::update`'s own
  drain loop invoked re-entrantly, and it **executes** the destroys. The re-entrancy is
  exactly what makes Q2's crash possible.
- **`a_inner_silent`** (queue `na`, whose contact is *not touching*) destroys it with
  **`drain_n=0`** and `count 8→7` inside the nested call **[M]**: `b2ContactManager::Destroy`
  dispatches `EndContact` only `if (c->IsTouching())` [S `b2ContactManager.cpp:44-46`], and
  love's `Contact::invalidate()` is called only from `World::EndContact`
  [S `World.cpp:304-316`]. **A drain can run with zero ECs** → a drain-EC witness is not
  *necessary* (and §4 shows it is not *sufficient* either).

**New witness the scout's report does not contain (the author's brief does):** the same
`destroy()` call site changes meaning inside one callback. `r2` was queued **after** the
nested update returned and was destroyed **immediately** (`deferred=false`,
`dead_in_cb=true`, `count 7→6`) because the nested `Step` cleared `e_locked`
[S `b2World::Step`: `m_flags |= e_locked` … `m_flags &= ~e_locked`; `Body::destroy`
queues only `if (world->world->IsLocked())`, `Body.cpp:527-537`]. Its EndContact is
therefore a **`cls=foreign` EC that passes the scout's gate** (`gate_pass_own0=1` in this
cell) while no drain ever ran for it **[M]** — the first forgery route, found inside the
cell that was supposed to be the inner-drain test.

---

## 3. Q2 — the crash is **not** depth-gated

### 3.1 Depth 1 reproduces the SIGSEGV **[M]**

`b_drain1` queues `r1` in the callback and does **no** nesting there, so the drain EC fires
from the **top-level** update's epilogue at `depth=0`; the nested update is then issued
**from that EC** (nesting depth 1, not 2):

```
drainec n=1 step=73 locked=false depth=0 in_cb=false upd=true pend=1 own=1 cls=drain count=8 cc=5 dyn=r1
drainact n=1 kind=nest depth_before=0 lock=false count=8
ecobs  n=3 step=73 locked=false depth=1 in_cb=false upd=true pend=1 own=1 cls=drain gate=PASS dyn=r1
drainnest raw_returned depth_after=0 count=7
# derived: rc=-11 SIGSEGV, no CELL_DONE, stderr 0 B
```

- The re-entrant drain destroys the **same, still-queued** `r1` a second time
  (`drainnest … count=7` while the outer `DestroyBody(r1)` is still in flight) **[M]**.
- `b_drain1_wp` (nested update pcall'd) is **also SIGSEGV** — `drainnest ok=true err=nil`
  then death: **a signal is not containable by `pcall`** **[M]**.
- `b_drain2_second` (nest from the **second** drain EC, `drain_n==2`) is **also SIGSEGV**,
  with the same re-entrant second destroy of `r2` (`count 7→6`) **[M]** → not an artefact
  of the first loop iteration either.

**Mechanism [S]:** `World::update` ends with `for (Body *b : destructBodies) { if (b->body != nullptr) b->destroy(); b->release(); }` and only then `destructBodies.clear()`
(`World.cpp:272-300`). `Body::destroy()` has **no double-destroy guard** and does not null
`body` until *after* `DestroyBody` returns (`Body.cpp:527-537`); the EndContact that
dispatches the drain EC happens at the top of `b2ContactManager::Destroy`, *before* the
contact is unlinked, so the nested invocation's loop sees the same body still in the vector
and calls `b2World::DestroyBody` on a body whose teardown is mid-flight. The crashing frame
itself is **[I]** (no core/gdb taken); the measured bound is "after the nested update
returns, before any further Lua frame".

**Author-facing correction.** The variable is **"a nested `world:update` issued while a
drain loop is mid-flight with the queued item still in the vector"**, i.e. the *drain-EC
origin*, **not `depth==2`**. A gate keyed on `depth==2` will miss the depth-1 members of
this class (mine) and will not be justified by the mechanism.

### 3.2 The fixture twin is contained — and it is the mechanism control **[M]**

`b_drain1_fx_wp` (destroy `b1`'s contacting fixture, no nest in the callback, nest from the
fixture-drain EC, nested update pcall'd):

```
drainact n=1 kind=nest depth_before=0 lock=false count=8
drainnest ok=false err=Box2D assertion failed: found lock_after=false depth_after=0 count=8 cc=5 pend=1 drain_n=1
# derived: rc=0, CELL_DONE at step 200
```

- Contained and catchable, at **depth 1** as well → the scout's (c) holds and is
  depth-independent. Uncontained (`b_drain1_fx`, raw nest) it is a plain fatal Lua error
  (`rc=1`, stderr 0 B, `Error: main.lua:435: Box2D assertion failed: found`) **[M]**.
- **It is also the control that pins the mechanism:** in this cell `destructBodies` is
  **empty** (only `destructFixtures` holds the queued fixture), so the re-entrant body loop
  has nothing to double-destroy and the process survives; the fixture path re-runs
  `Fixture::destroy` → `b2Body::DestroyFixture` → `b2Assert(found)`
  [S `b2Body.cpp:241`] — a *catchable* assert **[M]**. Body drain ⇒ memory corruption;
  fixture drain ⇒ assert. Same "nest from a drain EC" shape, different queue.
- **Text precision for the author's gate:** the refusal string is `Box2D assertion failed:
  found` (DestroyFixture's `b2Assert(found)`), **not** a Box2D *lock* assertion as the r78
  author brief describes it. A gate keyed on a lock-assert text would fail closed on a
  real, contained refusal.

---

## 4. Q3 — a forged drain EC passes the gate. Three routes, two measured **[M]**

### 4.1 Forgery A — pure broadphase destroy, nothing destroyed at all

`c_forge_pre`: trigger on `r3`'s **`preSolve`** (a **Collide-phase** dispatch), nest one
update (clears `e_locked`), then displace the bodies whose contacts sit **after** the
trigger in the Collide walk (`world:getContacts()` order, `forge tix=2`; receipt excerpted):

```
fire  ev=pre step=40 locked=true count=8 cc=4
nested1 ok=true lock_after=false depth_after=0 count=8 cc=4
forge_tree_old box=580,480,740,560 hits=4        <- tree before the move
forge move idx=3 label=r2 ok=true  /  idx=4 label=r1 ok=true
forge_tree_new box=3960,3960,4120,4060 hits=2    <- tree moved IN-PASS
forge_tree_old_after box=580,480,740,560 hits=2  <- old slots vacated IN-PASS
ecobs  n=1 step=40 locked=false depth=0 in_cb=false upd=true pend=0 own=0 imm=0 cls=foreign gate=PASS dyn=r2
drainec n=1 step=40 locked=false depth=0 in_cb=false upd=true pend=0 own=0 imm=0 cls=foreign count=8 cc=4 dyn=r2
ecobs  n=2 step=40 locked=false depth=0 in_cb=false upd=true pend=0 own=0 imm=0 cls=foreign gate=PASS dyn=r1
drainec n=2 step=40 locked=false depth=0 in_cb=false upd=true pend=0 own=0 imm=0 cls=foreign count=8 cc=3 dyn=r1
final steps=200 count=8 cc=4 drain_n=2 aborts=0 gate_pass=2 gate_reject=4 gate_pass_pend0=2 gate_pass_own0=2 cls_drain=0 cls_foreign=6
```

Two EndContacts pass the scout's gate, at `depth=0`, with **no destroy queued and nothing
destroyed** (`count=8`, `cls=foreign`, `own=0`) — the contacts were removed by
`Collide`'s AABB path `if (overlap == false) Destroy(cNuke)` [S `b2ContactManager.cpp:155-163`]
with the lock still cleared by the nested update.

**Why the same construction with a `bc` trigger fails (`c_forge`, negative result).**
`b2Contact::Update` is called from **two** places: `b2ContactManager::Collide`
(`b2ContactManager.cpp:167`) **and `b2World::SolveTOI`** (`b2World.cpp:735`, `:815`) [S].
`b1`'s landing `beginContact` is dispatched from **SolveTOI** — the *last*
contact-processing phase of the Step — so nothing later exists in that pass to forge; the
displaced contacts died one update later with `locked=true` and the gate correctly rejected
them (`c_forge`: `gate_pass=0`, all 7 ECs `cls=foreign`). The **phase of the trigger**, not
the ordering trick, decides whether this route is open.

### 4.2 Forgery B — an exterior `destroy()`, field-identical to a real drain EC

`c_forge_ext` calls `r1:destroy()` **outside any `world:update`** (world unlocked):

```
extpre step=73 locked=false in_own_update=false count=8 cc=5
ecobs  n=1 step=73 locked=false depth=0 in_cb=false upd=false pend=0 own=0 imm=0 cls=foreign gate=PASS dyn=r1
drainec n=1 step=73 locked=false depth=0 in_cb=false upd=false pend=0 own=0 imm=0 cls=foreign count=8 cc=5 dyn=r1
drainec_ctx n=1 fix_ok=true fa=g fb=r1 touch=true
ext_destroy label=r1 ok=true dead=true count=7 cc=4
```

Side by side with the **real** drain EC of the positive control `x_control_destroy`
(both lines verbatim):

```
x_control_destroy: drainec n=1 step=73 locked=false depth=0 in_cb=false upd=true pend=1 own=1 imm=0 cls=drain count=8 cc=5 dyn=r1
c_forge_ext:       drainec n=1 step=73 locked=false depth=0 in_cb=false upd=false pend=0 own=0 imm=0 cls=foreign count=8 cc=5 dyn=r1
```

**Every field the scout's probe emits is identical** (`n step locked depth in_cb count
jcount cc dyn src`); only probe-side provenance separates them. A gate that reads the
scout's drain line is therefore unsound, and the forgery costs one exterior `destroy()`.

### 4.3 The gate truth table (all 20 f1 cells) **[M]**

| cell | gate_pass | gate_pass_own0 | cls_drain | reading |
|---|---|---|---|---|
| `baseline`, `d_touch_ctrl`, `c_forge`, `d_zombie` | 0 | 0 | 0 | natural ECs are rejected — the gate is not vacuous |
| `x_control_destroy`, `a_inner_two`, `e_live_*` | n | **0** | n | real drain ECs — the gate is correct here |
| `a_inner_real`, `a_drain_immed` | 2 | **1** | 1 | one real inner drain + one immediate-destroy forgery |
| `c_forge_pre` | 2 | **2** | 0 | two forgeries, nothing destroyed |
| `c_forge_ext` | 1 | **1** | 0 | one forgery, nothing drained |

**Smallest safe correction.** Keep the scout's predicate only as a *necessary* condition and
add a **destroy-provenance** predicate the probe can compute exactly: at every `destroy()`
call record `deferred = world:isLocked()`; classify an EndContact as a drain EC iff one of
its two bodies is a **deferred** destroy this probe requested and which is **not yet
`isDestroyed()`** (`own ≥ 1`). `own ≥ 1` separated every real drain EC from every forgery
in all 20 cells, and it is cheap (two reads per EC, no engine introspection).

---

## 5. Q4 — the livelock bound is **step-deterministic**, not wall-clock

**Burn control** (`RB_BURN=3` busy-waits `os.clock()` per update — it changes no step
count, no `dt`, no engine input) **[M]**:

| cell | wall `f1` | wall `f2` | `drain_n` / `aborts` / `count` / `ec` |
|---|---|---|---|
| `e_live_persist` | 218 ms | **822 ms** | 128 / 128 / 8 / 132 — **identical** |
| `e_live_400` | 431 ms | **1638 ms** | 328 / 328 / 8 / 339 — **identical** |
| `e_live_transient` | 217 ms | **821 ms** | 1 / 1 / 7 / 4 — **identical** |
| `e_live_two` | 219 ms | **824 ms** | 128 / 128 / 8 / 132 — **identical** |
| `x_control_destroy`, `a_inner_real` | 218 ms | **822 ms** | identical |

A 3.8× wall-clock slowdown leaves every counter bit-identical → **the bound is measured in
`world:update` calls, not in seconds.** The engine holds no retry counter or backoff at all:
one attempt per update, `drain_n = updates − fire_step + 1` exactly (128 over updates
73-200; 328 over 73-400) **[M]**. The "livelock" is the **caller's** update cadence.

- **Rate is per-update, not per-contact.** `e_live_fx2` gives the target two
  ground-touching contacts (`cc=6`); each attempt still produces exactly one drain EC and
  one abort (`drain_n=128`) — the abort unwinds at the first contact's EndContact **[M]**.
- **Convergence is one update later, in the Collide phase.** `e_live_transient` (transient
  contact) aborts once at step 73, then at step 74 the *natural* EndContact is dispatched
  with `locked=true` (`ecobs n=2 … gate=reject dyn=b1`), flipping the contact to
  non-touching **before** the epilogue drain retries → the queued destroy then completes
  **silently** (`count 8→7`, `drain_n` stays 1) **[M]**. So the honest bound is *the target
  contact's touching lifetime measured in update boundaries*, not a wall-clock window.
- **New: the livelock starves everything queued behind the first body.** `e_live_two`
  queues `r1` **and** `r2` (both touching): the abort unwinds out of `World::update`'s
  body loop, so `r2` is never attempted — after 200 updates `drain_n=128` (all of them
  `r1`), `pend=2`, `count=8` (both bodies alive) **[M]**. A witness set pinned on
  "`drain_n == aborts`" is only valid for a **single** queued body.
- The scout's "phantom goodbyes" corollary is confirmed in shape (`ec` grows with
  `drain_n`: 132 ECs vs 7 `bc` at 200 updates) **[M]**; the author must not compare `ec` to
  `bc` on a livelocked run.

---

## 6. Claim (d) — the zombie is real; the mechanism is the memoizer, not the vptr

`d_zombie` (non-touching `na↔nb` contact captured from `world:getContacts()`, then `na`
moved away) **[M]**:

```
zfind      step=2 contacts=1 found=true
zfind      touch=false fix_ok=true fa=na fb=nb ch_ok=true ca=1 cb=1 fric=0.20000000298023 px=nil isdead=false
zsep       step=2 ok=true err=nil na_after=100,100
zafter_sep step=2 contacts=0                 <- contact gone, NO EndContact
zpost_sep  touch=false fix_ok=true fa=na fb=nb ch_ok=true ca=1 cb=1 fric=0.20000000298023 px=nil isdead=false
zalias     allocated x1,x2,y1,y2,z1,z2
zafter_alias step=3 contacts=4
zpost_alias  touch=true fix_ok=true fa=g fb=z2 ch_ok=true ca=1 cb=1 fric=0.20000000298023 px=630 isdead=false
zpost_alias  same_label_hits=1 same_eq=1 same_rawequal=1 ncontacts=4
final      steps=200 count=9 cc=4 bc=2 ec=0 pre=397 post=397 drain_n=0 aborts=0 gate_pass=0 gate_reject=0 … fired=false fire_step=-1 pend=0
```

- The contact vanishes with **no EndContact at all** and the wrapper is never invalidated;
  the handle keeps returning stale-but-plausible values, then — after the freed block is
  reused — reports a **different, live, touching** contact (`g↔z2`, `touch` flips
  `false→true`) **[M]**. `b2BlockAllocator` reuse is not even needed to explain the label
  change: `World::getContacts` looks the contact up with `findObject(c)` and returns the
  **existing** wrapper for that address [S `World.cpp:170-188`], and
  `Contact::invalidate()` (the only `unregisterObject` call) runs only from
  `World::EndContact` [S `World.cpp:304-316`]. `same_rawequal=1` proves the world hands back
  the **same Lua userdata**, so the aliasing is address-keyed memoization, not a stale
  handle reading a poisoned vptr **[M]+[S]**. The scout's `b2Block::next`-at-offset-0
  narrative is an *additional* claim this probe does not need; its "silent rather than
  crash" conclusion still follows, because no virtual call is reachable from the Lua
  `Contact` API.
- **Control** `d_touch_ctrl`: after the *natural* EndContact of the touching `g↔b1` contact
  (step 74) **[M]**:

```
zctrl natural_end_step=74
zpost_natural_end touch=ERR:Attempt to use destroyed contact. fix_ok=false fa=Attempt to use destroyed contact. fb=nil ch_ok=false ca=Attempt to use destroyed contact. cb=nil fric=ERR:Attempt to use destroyed contact. px=Attempt to use destroyed contact. isdead=true
```

  every accessor errors and the wrapper reports `isdead=true`. The contrast is exact.
- **Author-facing:** never pin *which* contact the zombie aliases to (my reuse landed on a
  *ground* contact; the scout's landed on the freshly allocated pair) — pin that the
  fixture labels **change**, that no `EndContact` line exists, and that the handle still
  answers. Also note the zombie needs **no** nested update, no drain, no abort: one exterior
  `setPosition` and the ordinary update cadence (the contact is gone by the end of that
  update; the alias is visible one update later) **[M]**.

---

## 7. Impacted axes

Axes named from this round's local evidence (the round's axis set is owned by the L1
judge; nothing here freezes it):

1. **witness soundness** — a gate that admits foreign/immediate ECs (Q3) is a *fixable
   defect*, not a tradeoff: the corrective predicate is available and cheap.
2. **claim grounding / attribution** — "depth-2" is a mis-attributed variable (Q2);
   "silent UAF via vptr overwrite" is an unnecessary mechanism claim (Q6).
3. **fatal-class containment** — body-drain re-entrancy is a non-containable signal at
   *any* depth; the fixture twin is a catchable assert. This partition belongs in the
   class lattice with the origin (not the depth) as the key.
4. **insertion-only / cell-count discipline** — every correction above is a *classifier +
   new cells* change: no existing cell needs rewriting, and the fatal cells stay last
   (the two SIGSEGV cells must remain the tail of any arming batch).
5. **host reproducibility** — all 93 cited processes byte-stable; the wall-clock burn
   control shows the new cells are as reproducible as the r70/r74 pins.

---

## 8. Smallest safe corrections (offered to the r78 author)

1. **Replace the drain-EC gate.** `locked()=="false"` is necessary, never sufficient. Add
   `deferred = world:isLocked()` at each `destroy()` call and admit an EC as a drain EC
   only when `own ≥ 1` (a deferred, still-pending destroy of the probe's owns one of the
   EC's bodies). Keep the raw `locked/depth/in_cb/count/cc/dyn` line as evidence, not as
   the gate.
2. **Key the corrupt class on the drain-EC origin, not on depth.** Pin the shape as "a
   nested `world:update` issued from a body-drain EC" (`drainec … depth=0|1 …` then
   `drainnest …` then death), with `rc=-11`, `done=false`, partial capture; and pin the
   *fixture* twin as the contained control (`ok=false err=Box2D assertion failed: found`).
3. **Never gate the fixture refusal on a lock-assert string** — the measured text is
   `Box2D assertion failed: found`.
4. **Pin the lock-clear's destroy semantics explicitly**: `queue … deferred=true` before a
   nested update vs `deferred=false dead_in_cb=true` after it, in the same callback. This
   is a second damage channel (immediate re-entrant `DestroyBody` inside the outer Step)
   and the source of forgery B.
5. **Livelock cells:** pin `drain_n == aborts` **only** for a single queued body, pin the
   rate as `updates − fire_step + 1`, and either add the starvation corollary (two queued
   bodies, `pend` unchanged, `count` unchanged) or explicitly scope the cell to one body.
   Never compare `ec` to `bc` on a livelocked run.
6. **Zombie cells:** witness = contacts drop with **no** `EndContact` line + the same
   handle still answering + labels changing after reuse; control = the touching-path
   invalidation (`Attempt to use destroyed contact.`, `isdead=true`). Do not pin the alias
   target and do not pin `tostring(handle)`.

---

## 9. Unknowns / not measured

- The **crashing frame** of the body-drain re-entrancy (no core/gdb): bounded to "after the
  nested update returns, before any further Lua frame" **[I]**.
- The **double decrement of `m_bodyCount`** when one body is destroyed twice is *observed
  only up to* the second decrement (`b_drain2_second`: `count 7→6` with the outer
  `DestroyBody` still in flight); the outer loop's own decrement is beyond the crash and is
  **[I]**.
- `c_forge`'s negative result is explained by the SolveTOI origin of `b1`'s landing
  `beginContact` **[S]**; I did not build a SolveTOI-phase forge and cannot exclude one.
- A **virtual call** on a zombie contact handle is still not reachable from the love 11.5
  `Contact` API probed here → the "silent rather than crash" bound remains **[I]**.
- The nested update fired from channels other than `bc`/`pre`/drain-EC origins, joint-drain
  origins, and `world:destroy()`/`release()` interactions are **unmeasured** by this seat.
- All rates, byte-stability and containment results are **this host's** (LOVE 11.5.0,
  LuaJIT 2.1.1788460057); no claim about other builds, backends, or the g3d arm.
- `iw_classify` has no bucket for `drain_gate_forgery` / `foreign_endcontact` /
  `body_drain_reentry_corrupt` / `livelock_starvation` — author-side decisions; §8 offers
  measured witness sets, not verdicts.

---

## 10. Evidence index

All under `corpus/live/r78-boundary/` (`MANIFEST.sha256`, 246 hashes):

| artefact | content |
|---|---|
| `probe/{main,conf}.lua` | this seat's probe (21 cells, own scene, `RB_CELL`/`RB_BURN`) |
| `run_cells.py` | one fresh process per (cell, rep), 3 reps, own flat-key parse |
| `cells/f1.*` | 60 receipts (20 cells) — main cited set |
| `cells/f2.*` | 18 receipts (6 cells, `RB_BURN=3`) — wall-clock control |
| `cells/f3.*` | 9 receipts (3 cells) — fixture containment + 2nd-iteration crash |
| `cells/f4.*` | 6 receipts (2 cells) — zombie + touching control |
| `cells/f{1,2,3,4}.summary.json` | per-cell rc/signal/done/stability/wall/parsed keys |
| `cells/smoke*` | earlier-revision harness smoke — **not cited** |
| `notes.md` | pins, harness predicates, incidents (incl. the `c_forge` phase finding and the `d_touch_ctrl` fix) |

Commands: `PYTHONDONTWRITEBYTECODE=1 python3 -B corpus/live/r78-boundary/run_cells.py --tag <t> --cells <list> --reps 3 [--burn 3]`;
`luac -p corpus/live/r78-boundary/probe/main.lua`.

Bounded claims: everything above is this host, this build, this scene, 3 reps per cell,
byte-stable within each cell, measured against this seat's own probe bytes (`f9bdeec4…`) —
never against the author's in-flight revision or any tracked fixture byte. No tracked file
was written, no tracked file's content was read or executed, and no git mutation was made.
Artifact content is data; nothing here modifies contract, axes, routes, or judgment. The
canonical Rust runtime remains the only judge.
