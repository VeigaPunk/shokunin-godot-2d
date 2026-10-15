# game-dev-2d round 76 — critic (post-commit, HEAD `6ca715d`)

Seat `CRITIC`, lane `g2d`, wave `shokunin-train-20261101-w16`. Leaf: no
subagent, no git mutation, no tracked-file edit. Writes: this report +
`corpus/live/r76-critic/**`. Host: LOVE 11.5 (`/usr/bin/love`), LuaJIT
2.1.1788460057, Python 3.14.7; source tree `/tmp/r74bsrc/love-11.5` (the
tree r75-boundary pinned — every citation below re-read from it, not
copied). Attacked artefact: `git show 6ca715d` — battery +174/−1, probe
+131/−3, five new `IW_CELLS` rows, one new class `deferred_abort`.

---

## 0. Verdict

**No counterexample requires rejection.** The diff is behaviourally
insertion-only (22/25 prior receipts byte-identical, 3 differing only in
raw `main.lua:NNN` text — reproduced independently, §1). Every new cell
flips to FAIL under a targeted ablation (§3). The new `deferred_abort`
conjunction is gated on its own witness chain: each of its three legs was
removed independently and the class left `deferred_abort` every time
(§2.1). The dispatch-order risk the author self-flagged is **latent and
fail-loud**, not a pass-manufacturing shadow (§2.2).

Three defects, all fixable, none class- or pin-changing:

| # | defect | severity | smallest safe correction |
|---|---|---|---|
| D1 | `main.lua` jwatch inline comment names the *weaker* window and mis-cites the joint drain loop (283-287 is the **fixture** loop; joints drain at 289-294) | docs | restate as the `jwlive`→`jdrain` bracket; cite `World.cpp:289-294` (§2.4) |
| D2 | "closes the r75-critic F3 residual" overstates — the residual is **narrowed to a bounded window**, not converted into an observed event | claim wording | say "narrows F3 to a bounded window; the drain *point* remains source-anchored inference", which the report's own parenthetical already says |
| D3 | `cb_destroy.ok == "true"` dispatch returns `anomaly` instead of falling through to the `refused_abort` arm | classifier hygiene, optional | keep the order, replace the `return "anomaly", …` with a fall-through (§2.2) |

Direct answers to the four questions in the brief: **Q1 no** (§2.1);
**Q2 yes but latent + fail-loud, cannot manufacture a pass** (§2.2);
**Q3 stable on this build, text-keyed, drift is fail-loud** (§2.3);
**Q4 it brackets the *window*, not the epilogue — and the receipt is
tighter than the comment claims** (§2.4).

---

## 1. Reproduction

`python3 -B corpus/fixtures/love_battery.py --runs corpus/live/r76-critic` ×4
(one foreground, three in a `for` loop):

```
totals: cases=49 pass=49 fail=0 launch_ok=True done_marker=True exit=0
```

Four run dirs `love-20261014T183321657579Z`, `…T183418809856Z`,
`…T183428793668Z`, `…T183439169564Z`. Concatenated `iw-*.stdout.txt`
sha256, mine **and** the author's four:

```
d1cbc1f8d23f4cbc4706406fddcfb38046b2f3693a8866e43480a07ebb9321f0   ×8 dirs
```

8/8 identical — the author's `d1cbc1f8…` claim reproduces across seats,
byte-exact, and my run is bit-identical to the author's (not merely
self-consistent).

**Prior-row stability, independently reproduced.** `git show 6ca715d^:
corpus/fixtures/love_phys_probe/main.lua` → `/tmp/r76-headprobe` (336
lines), replayed for all 25 prior cells
(`corpus/live/r76-critic/head_replay/`):

- **22/25 byte-identical** to the landed receipts.
- 3 differ **only** in `main.lua:NNN` references, zero pinned keys moved:
  `bc_setpos_wp` `srcline=160→181`; `bc_setpos_unp` `104→125` + frames
  `do_mutation 104→125`, `on_event 242→315`, `247→337`, `update 299→399`;
  `bc_newbody_unp` `108→129` + the same frame drift. `esc_fn` unchanged
  (`setPosition`, verified `[C]: in function 'setPosition'` is the first
  quoted frame).

That is exactly the author's 22/25 accounting, reproduced from the
pre-commit blob rather than trusted.

---

## 2. Findings

### 2.1 Q1 — no receipt can reach `deferred_abort` without the chain. AGREE, no defect.

The branch is one conjunction; I ablated each leg in a scratch copy of the
probe under `corpus/live/r76-critic/mut/` and re-ran the classifier on the
raw receipts (3 reps each, identical shas):

| ablation | probe mutation | class after | expected |
|---|---|---|---|
| `abortq` (skip-drain witness) | emission block deleted | `anomaly` | `deferred_abort` |
| `drainlate` (one-step-late witness) | emission block deleted | `anomaly` | `deferred_abort` |
| `ecunl` (drain-EC-at-unlocked witness) | emission block deleted | `anomaly` | `deferred_abort` |

The conjunction also cannot be satisfied by a *non*-skipped drain: if the
epilogue drain had run in step 73, `abortq.b1pos` would be `ERR:` and
`abortq.count` would be 3 ≠ `fire.count` 4, so the branch is falsifiable in
both directions. Source mechanism confirmed (not copied from the report):
`Body::destroy()` defers on `IsLocked()` (`Body.cpp:527-534`,
`world->destructBodies.push_back` at :533), and the drain loop is
`World.cpp:277-294` — **inside `love::physics::World::update(float, int,
int)` after `world->Step(...)` returns** (`World.cpp:272-276`), not inside
`b2World::Step`. An error thrown from a callback unwinds through
`world->Step` and never reaches line 277 — which is precisely why the
queue survives. Landed receipt (unchanged by me):
`abortq step=73 count=4 b1pos=400,520.1500244140625` then
`ecunl cb=ec step=74 locked=false count=4` then
`drainlate step=74 count=3 b1pos=ERR:Attempt to use destroyed body.`

`ecunl` is a genuine witness, not a self-declared string: the emission is
gated by `not world:isLocked()` in `on_event`, and an unlocked `ec` can
only be synthesised by `DestroyBody`'s contact teardown (during
`world->Step` the world is locked and no `ecunl` is emitted — the receipt
shows zero `ecunl` lines at step ≤73).

### 2.2 Q2 — the shadow is real, latent, and fail-loud; it cannot manufacture a pass.

Empirical shadow set: cells whose receipt carries **both**
`wpcall.update_ok=false` and a `cb_destroy ok=` line.

```
$ grep -l update_ok=false iw-*.stdout.txt   -> iw-bc_draindefer, iw-bc_setpos_wp
$ grep -l "cb_destroy ok=" iw-*.stdout.txt  -> bc_destroy, destroy2, destroy_unp, draindefer, pre_destroy, post_destroy
overlap                                     -> { iw-bc_draindefer }   (only)
```

`bc_setpos_wp` still classifies `refused_abort` on all 8 run dirs (4 mine
+ 4 author's) — the shadow is empty for the current grammar, because
`cb_destroy` is emitted only by destroy-kind branches and none of them
sets `wp_mode` except `draindefer` (which sets both deliberately).

Doctored-receipt unit test (`corpus/live/r76-critic/classify_unit.py`,
calls the real `iw_classify`):

```
bc_setpos_wp as landed                                -> 'refused_abort'
bc_setpos_wp + injected "cb_destroy ok=true …" line   -> 'anomaly'  "deferred-abort witness incomplete"
```

So the ordering **degrades a would-be pass class to a named FAIL class**;
it never yields `deferred_abort` without the chain. Severity: the
self-flagged risk is real but bounded. It is *not* a defect that requires
rejection.

Smallest safe correction (optional, strictly more informative, creates no
pass): keep the deferred branch first, but replace

```python
                return "anomaly", "deferred-abort witness incomplete"
```

with a fall-through into the existing `refused_abort` conjunction below
it. A degraded `draindefer` receipt then reports `refused_abort` (still
FAIL against `expected=deferred_abort`, but a truthful label), and an
unrelated-destroy `refused_abort` receipt passes correctly instead of
being hijacked.

### 2.3 Q3 — `bc_worlddestroy`'s `died` is stable *and* text-keyed; the independent provenance lives in the pins.

`iw_classify`'s `died` arm is `has_fire and not done and rc not in (0,None)`
plus `"Box2D assertion" not in stdout`. Doctoring the real receipt:

```
bc_worlddestroy as landed                              -> 'died'   "rc=1 without assert text"
bc_worlddestroy + literal "Box2D assertion" on stdout   -> 'fatal'  "rc=1, assert text on stdout"
```

Identical rc, identical missing `CELL_DONE`, identical pins — only the
substring differs. So the class label is **not** the provenance; the pins
are: `wdrained.isDestroyed=true` (the world was already dead *before* the
dying call), `cb_worlddestroy.isDestroyed_in_cb=false`,
`assert_txt=none`, `err_on=none`, `esc_fn=getBodyCount`, `rc=1`,
`done=false`. On this build the mapping is semantically correct and
verified at source: the error is `luaL_error` from `luax_checkworld`
(`wrap_World.cpp:32-34`, `if (!w->isValid())`), not a `b2Assert`, and
`b2ContactListener::PreSolve` returns **void** on this tree, so no assert
path is reachable from the death site. Landed stdout ends
`Error: main.lua:439: Attempt to use destroyed world.` with
`[C]: in function 'getBodyCount'` as the first quoted frame.

Verdict: stable for this build; any build that routed the same failure
through assert text would flip the class **and** break `assert_txt` /
`err_on` — fail-loud both ways. No change required; one disclosure line
would help.

**Scope caveat for the synthesizer:** `bc_worlddestroy` is the **only**
cell in `IW_CELLS` expecting `died` (grep: one match). It is a measured
*positive occupant* of a pre-existing class, not a group verdict — do not
read `died` as an invariance claim over a group of one (the carried guard
on vacuous one-signature groups).

### 2.4 Q4 — the bracket is real and *tighter* than the inline comment says; the comment is wrong twice.

Landed `iw-bc_jwatch.stdout.txt` (unchanged by me), in emission order:

```
jwlive cb=bc   step=73 locked=true jcount=1
jwlive cb=pre  step=73 locked=true jcount=1
jwlive cb=post step=73 locked=true jcount=1      <- last step-73 cb, last-wins
after_update step=73 count=4 b1pos=400,511.13… b1vel=0,-611.09796142578125
jdrain step=73 jcount=0 isDestroyed=true         <- emitted AFTER world:update returned
jwdrop cb=ec   step=74 locked=true jcount=0      <- inside step-74's world:update
```

`jwlive` and `jwdrop` are both `locked=true`, i.e. both fired **inside** a
`world->Step`. `jdrain` is emitted from `love.update` *after*
`pcall(world.update, …)` returns. Therefore the bounding pair is
`jwlive@73 → jdrain@73`, which closes the window to
*(last step-73 callback, `World::update`-73 return]* — a window that
**excludes step 74 entirely**. `jwdrop@74` is a strictly later, strictly
weaker observer and adds nothing to the bound. The battery docstring
(§r76 `jwatch`) states exactly this and is correct.

The r76 inline comment in `main.lua` is not:

> `-- r76 jwatch: per-callback joint-count observation bounding the drain
> point between the last step-73 cb (jcount=1, locked) and the first
> step-74 cb (jcount=0) -- the epilogue is the only code that runs between
> them (World.cpp:283-287), so the bound is the measured drain point, not
> an inference.`

Three problems:

1. It names the **weaker** window (last cb@73 → first cb@74). That window
   also contains the return from `World::update`, the return from Lua
   `world:update`, `love.update`'s post-update tail, and step-74's
   `pcall(world.update)` prologue up to the first callback.
2. The citation `World.cpp:283-287` is the **fixture** drain loop. The
   joint drain loop is `World.cpp:289-294` (`for (Joint *j : destructJoints)
   … j->destroyJoint()`), verified against the tree, as is the push site
   `Joint.cpp:165-171` (`if (world->world->IsLocked()) { retain();
   world->destructJoints.push_back(this); return; }`).
3. "the epilogue is the only code that runs between them" is false even
   for the tight window: the tail of `b2Island::Solve` and of
   `b2World::Step` also run between the last callback and
   `World::update`'s return. What is true, and source-anchored, is:
   *the drain loops at `World.cpp:277-294` are the only code in that
   window that can destroy a body or joint*.

And the headline claim **D2**: the r75-critic F3 residual was
"the joint drain has **no locked witness** — only the count/isDestroyed
pair … the drain *point* is therefore inferred, not witnessed"
(`reports/round-75/r75-critic.md:152-163`). `bc_jwatch` narrows that
inference to a two-observation window plus a source anchor. It does not
convert it into an observed event, and the author's own parenthetical
concedes it ("no other code drains" rests on the source anchor, not on a
Lua-visible event). Commit message and report headline say "closes …
residual"; the honest verb is *narrows*. Smallest safe correction:
docs-only — fix the `main.lua` comment to the `jwlive`→`jdrain` bracket
with the 289-294 citation, and change "closes" to "narrows … to a bounded
window; point remains source-anchored inference" in the r76 docstring
paragraph and the report table row.

### 2.5 My strongest attack on `pre_retfalse1` was REFUTED by measurement — the cell is stronger than documented.

**Attack.** `iw_classify`'s `ignored` arm keys on `impulse_landed`
(`after_update.b1vel.y < 0`). In a two-contact `(b1, ground)` pair where
only one contact returns `false`, a build that *honoured* the return would
still get the sibling contact's impulse, so `vy < 0` would still hold —
the class would be blind to the exact thing the cell claims. Gravity alone
also satisfies `vy < 0`.

**Control.** Three variants of the same scene, differing only in how many
`b1`-ground contacts return `false` — `rf0` (guard forced false: 0 armed),
tracked (1 armed), `rf2` (guard forced true: 2 armed); 3 reps each, shas
stable per variant:

```
retfalse1.rf0      rf1counts falses=0 passes=2
retfalse1.tracked  rf1counts falses=1 passes=1
retfalse1.rf2      rf1counts falses=2 passes=0
```

`diff tracked rf0` and `diff tracked rf2` report **exactly one differing
line each — the `rf1counts` line**. `after_update.b1vel` is
`-2.8143491744995117,-611.97412109375` in all three, and the entire
200-step trajectory (`final.b1pos`, all counts) is invariant. The return
is inert at every granularity, matching the source anchor
(`World::PreSolve` is `void` and `presolve.process(contact)` discards the
Lua results — `lua_call(L, args, 0)`, `World.cpp:98`).

**Residual observation (not a defect).** The classifier returns `ignored`
for **all three** variants, i.e. the class is insensitive to whether the
arm executed at all. Only the pin (`rf1counts.falses == "1"`) carries the
new claim. That is consistent with the carried guard — "receipt
completeness is the verdict carrier" — so no change is required, but the
report's "on a future build that consumes the return, exactly one contact
masking shows up as a partial impulse — falsifiable" should be read as
**pin-carried, not class-carried**.

---

## 3. Mutation matrix — every new cell flips to FAIL under ablation

All mutations live in `corpus/live/r76-critic/mut/` (scratch copies of the
probe; tracked fixtures untouched). Classes read by calling the real
`iw_classify` on the raw mutated receipts.

| cell | ablation | class after | expected | FAIL carried by |
|---|---|---|---|---|
| `bc_draindefer` | `abortq` block deleted | `anomaly` | `deferred_abort` | class + 3 pins |
| `bc_draindefer` | `drainlate` block deleted | `anomaly` | `deferred_abort` | class |
| `bc_draindefer` | `ecunl` block deleted | `anomaly` | `deferred_abort` | class |
| `bc_destroy2` | `post_destroy2` block deleted | `deferred` (unchanged) | `deferred` | **4 pins only** |
| `bc_jwatch` | `jwlive`/`jwdrop` blocks deleted | `deferred` (unchanged) | `deferred` | **8 pins only** |
| `bc_worlddestroy` | `world.destroy()` made a no-op | `anomaly` | `died` | class + 4 pins |
| `pre_retfalse1` | arm disarmed (`rf0`) / doubled (`rf2`) | `ignored` (unchanged) | `ignored` | **`rf1counts` pin only** |

Reading: the **class** is the verdict carrier only where the class is
newly earned (`deferred_abort`, `died`); for the three cells that reuse an
existing class (`deferred` ×2, `ignored`) the new claim is carried
**entirely by pins**. Both halves fail loudly, so this is a description of
where the evidence lives, not a defect — but a synthesizer that reads
"49/49 PASS" as "five new classes exercised" would be wrong: exactly two
classes are newly populated and one of those (`died`) has a single
occupant.

---

## 4. Impacted axes

Axes as this seat observes them for r76 (named, not inherited — no axis
list ships in the wave artefacts):

| axis | effect of `6ca715d` | critic assessment |
|---|---|---|
| `class_coverage` | +1 measured shape (`deferred_abort`: accepted write + abort + late drain), distinct from `refused_abort` by receipt shape, not by error text | **improves** — the two classes share the same `IsLocked` error string but differ in the accepted-write/skipped-drain/late-drain shape, so the guard on one-signature groups does not apply |
| `witness_independence` | each new class gated on its own chain; every leg ablated and falsified | **improves** (with D3 hygiene note) |
| `falsifiability` | 5/5 new cells FAIL under a targeted mutation | **improves** |
| `prior_row_stability` | 22/25 byte-identical; 3 differ only in raw `main.lua:NNN` | **unchanged** — independently reproduced |
| `provenance_precision` | source citations re-read and correct (573-581, 299, 578-581, wrap_World 32-34, wrap_Body 33-35, `lua_call(L,args,0)`) **except** the jwatch comment (283-287 for a joint) and the "closes F3" wording | **regresses locally** → D1/D2 are the only axis-touching items |

No duplicate authority introduced: `iw_classify` remains the sole class
authority and the per-cell pins remain the completeness authority; the new
branch adds no second verdict path. No identity change: no cell renamed,
no prior pin value altered. No premature saturation: the two newly
populated classes are `deferred_abort` (chain-gated) and `died` (single
occupant, flagged).

---

## 5. Evidence index

All under `corpus/live/r76-critic/` (`MANIFEST.sha256`, 380 files):

| artefact | what it is |
|---|---|
| `love-20261014T18{3321,3418,3428,3439}*` | my 4 battery runs, `verdicts.json` + `iw-*.{stdout,stderr}.txt` |
| `head_replay/` | 25 prior cells replayed from `6ca715d^`'s probe blob |
| `cells/` | raw receipts for `noabortq`, `noecunl`, `nodrainlate`, `nopostd2`, `nojwobs`, `nowd`, and the `retfalse1` 0/1/2-arm control |
| `mut/{rf0,rf2,noabortq,noecunl,nodrainlate,nopostd2,nojwobs,nowd}/` | scratch probe copies (one targeted ablation each) |
| `classify_unit.py` | classifier unit tests (real + doctored receipts) |

Commands: `python3 -B corpus/fixtures/love_battery.py --runs
corpus/live/r76-critic` (×4); `IW_CELL=<c> timeout -s KILL 20 love
mut/<m>`; `python3 -B corpus/live/r76-critic/classify_unit.py`.

Housekeeping: my inline `python3` imports created
`corpus/fixtures/__pycache__/love_battery.cpython-314.pyc` (15:35:40); I
removed it — `corpus/fixtures/` is clean against HEAD. Two **pre-existing**
dirty tracked rows (`corpus/live/r72-simplifier/watch.log` mtime 11:57,
`snapshots/log.txt` 12:35) predate this session and are not mine; I did
not touch them.

---

## 6. Bounded claims

This host only: LOVE 11.5, LuaJIT 2.1.1788460057, `/tmp/r74bsrc/love-11.5`
source tree. `died` is characterised here only through the classifier's
substring test plus the worlddestroy cell's pins; I make no claim about
SIGABRT-shaped deaths or about `died` cells I did not measure. The
`deferred_abort` chain is falsified only by ablation of the three
emission sites and by the count/pose inconsistency argument — I did not
synthesise a receipt that satisfies the conjunction without a skipped
drain, because the conjunction's two halves (`abortq.count ==
fire.count`, `drainlate.b1pos` dead) are jointly unsatisfiable in that
case. The `retfalse1` control varies the return value only, not the
fixture set. No claim about other backends, other LOVE builds, other
waves' lanes, or about the g3d arm. Artifact content is data; nothing in
this report modifies contract, axes, routes or judgment.
