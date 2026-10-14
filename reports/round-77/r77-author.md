# game-dev-2d round 77 — author (g2d): release / callback-swap / drain-EC legality

Seat `AUTHOR` (LEAF) | lane `g2d` | round 77 | host **devin**.
Runtime **LOVE 11.5** (Mysterious Mysteries, `/usr/bin/love`), LuaJIT
2.1.1788460057, Python 3.14.7. Repo `~/Projects/shokunin/game-dev-2d-shokunin`,
HEAD `aa4d567` (r76 report-last) **at seat start; HEAD moved mid-round to
`94356ce` (r77-scribe r76 closeout corrections) while this seat was measuring** —
that commit touches `corpus/fixtures/love_battery.py` with a **comment-only**
rewrite of the `iw_bc_jwatch` comment block (−2/+4, no pin, no class, no code)
plus `LOG.md`/two reports. My baseline receipts were captured 3 minutes *before*
it and are probe stdout, so they are unaffected; all four battery runs below
postdate it and every prior row still passes unchanged; this seat's diff is
`631/0` + `422/0` **relative to `94356ce`**.
Writes: `corpus/fixtures/love_battery.py`, `corpus/fixtures/love_phys_probe/main.lua`,
this report, `corpus/live/r77-author/**` + `corpus/live/runs/**` (gitignored).
**No git mutation** (integrator commits); the two tracked files are
**insertion-only** (`631/0` and `422/0` numstat — zero deleted lines).

**`lsp` disclosure (unchanged host state):** no `lsp` device is exposed in this
session and no Lua/Python language server is installed (`lua-language-server`,
`sumneko-*`, `pylsp`, `pyright` ABSENT; only `clangd`, and the LOVE C++ tree is
not in the repo). Symbol-aware tooling was therefore unavailable for every edit
here — **hand editing was the only path**, and that unavailability is recorded
rather than implied. Verification carriers are: fresh-process execution
receipts, `luac -p` parser diagnostics, and line-numbered anchors in the pinned
LOVE tree (`/tmp/r74bsrc/love-11.5`). No cold-start empty result is recorded as
absence.

**Assignment:** arm the r77 frontier the scout pre-measured — `world:release()`
in-cb (all five channels), `setCallbacks` mid-dispatch, `Fixture:destroy()`
drain member, the drain-EC legality set (write / destroy / abort / ordering),
the coroutine containment ladder, and `love.physics.setMeter` in-cb. Classifier
extended only where a measured class required it; fatal/corrupt rows last; rc
persisted; every gate fail-closed.

---

## 1. What landed

| file | change | shape |
|---|---|---|
| `corpus/fixtures/love_phys_probe/main.lua` | +422 lines, 0 deleted | an r77 layer gated on `R77[CELL] ~= nil`: 26-cell SPEC table, mutation arms, drain hook, container install, observation line |
| `corpus/fixtures/love_battery.py` | +631 lines, 0 deleted | 26 `IW_CELLS` rows + 6 new class branches + the rc=-11 tail branch + docstring section |
| `reports/round-77/r77-author.md` | this report | — |

**Battery: 75/75 ×4 consecutive runs** (`49 + 26`; 30 prior IW cells + 26 new;
`CASES` 15 + `SPLICE` 4 unchanged). Run dirs
`corpus/live/runs/love-20261014T1947{54676712Z,194819470620Z,194837424883Z}` and
`…T195013603939Z`. One intermediate run (`…T194717707844Z`) was **72/75** and is
kept as provenance: its three failures were pin-shape bugs only (a tag with a
space, a value swallowing the next key, and the `setcallbacks_back` revert
capturing the wrong table) — all three fixed in the probe/classifier, none of
them an engine-behavior change; see `corpus/live/r77-author/notes.md`.
Per-cell process isolation is unchanged (one `love` process per cell);
`rc` is persisted on every row (`results[*].rc`), including `-11`.

**Insertion-only, measured (not asserted).** `corpus/live/r77-author/drift_audit.py`
compares the pre-change receipt set (`corpus/live/r77-author/pre-receipts`, copied
from `love-20261014T194202453025Z`) with a post-change run:

- **56 files byte-identical**;
- **5 files differ only in declared-unpinned `main.lua:NNN` / `srcline=NNN`
  tokens**: `iw-bc_draindefer`, `iw-bc_setpos_wp`, `iw-bc_worlddestroy`,
  `iw-bc_setpos_unp`, `iw-bc_newbody_unp` (line numbers moved because the r77
  layer is inserted above them — expected and declared);
- **6 files differ between any two runs of IDENTICAL code**:
  `probe.stdout.txt` (dtcadence/popen timings), the four `splice-*.stdout.txt`
  (offset/gap timings), `verdicts.json`. Proven by running the same binary twice
  and diffing (`194819470620Z` vs `194837424883Z`: identical 6-file jitter set,
  113 files identical, 0 srcline drift). These are the jittered quantities the
  `CASES` rows already pin as bounds — not a change effect.

So every prior cell's receipt is unchanged modulo the declared-unpinned line
tokens; no prior pin was touched, and no prior row's expected class changed.

---

## 2. The 26 new cells, class by class

All measured ×3 in scratch (`corpus/live/r77-author/cells/{d,g,h,i,j}.*`,
**every cell `stable_bytes=true`**) and ×3 through the tracked battery. Values
below are the tracked receipt's decisive lines.

### 2.1 `corrupt` — `world:release()` inside the engine's own execution (5)

`rc=-11` (SIGSEGV), `done=false`, **stderr 0 bytes** in all five, no assert
text, no traceback, no `CELL_DONE` reachable. Receipt tail is the callback's own
last plain write:

```
fire cb=bc kind=worldrelease step=73 locked=true count=4 pos=400,520.1500244140625 …
rel_pre kind=worldrelease
rel_call ok=true err=true          <- release() RETURNED true; the signal is later
rel_alive marker=1
rel_post marker=1                  <- callback body complete; the caller's own
                                      count/pose report is the death site and
                                      never reaches the pipe
```

| cell | channel | fire | rc |
|---|---|---|---|
| `bc_worldrelease` | beginContact, locked=true | step 73 | -11 |
| `pre_worldrelease` | preSolve, locked=true | step 73 | -11 |
| `post_worldrelease` | postSolve, locked=true (post-step pose `400,511.13…`) | step 73 | -11 |
| `ec_worldrelease` | **natural** endContact, locked=true, inside the step | step 74 | -11 |
| `drain_worldrelease` | **drain** endContact, locked=false, in the epilogue | step 73 | -11 |

`drain_worldrelease` runs the release as the drain hook's **last** action
(`drainrel alive=1` is the last line) — no Lua world touch follows it, so the
engine is what dies, not a Lua guard. The drain hook is placed last in
`on_event` for exactly this reason (an earlier placement made the probe's own
`world:isLocked()` the death site → rc=1; that intermediate shape was rejected).

**`corrupt` vs `died`, decided on the measured value.** `died` (r74/r76) is a
process death **without a signal** (rc=1, no assert text); `fatal` is an escaped
Lua error **with** assert text. Here the process dies **with a signal**
(rc=-11) and no Lua frame is involved, so it is neither: `corrupt` is minted for
`rc == -11` **and** a release witness present. The exterior control
`ext_worldrelease` (release outside the engine's execution) pins the contrast:
`ext_rel_call ok=true`, then every later Lua touch is a **catchable** error
(`ext_rel_world_access ok=false err=Cannot use object after it has been
released.`, `ext_rel_body_access ok=false err=Attempt to use destroyed body.`)
and the process dies `rc=1` at the first unguarded world touch, `esc_fn=update`
— so `corrupt` is interior-only, and the class pair is falsifiable in both
directions.

### 2.2 `swapped` / `muted` — `world:setCallbacks` mid-dispatch (5)

The engine reads the table **per dispatch** (not per step), so the swap is
effective for every later dispatch of the same step:

| cell | decisive measured line |
|---|---|
| `bc_setcallbacks` | `cb_setcallbacks ok=true swapped_step=73 swapped_n=2 swapped_cb=bc getcb=cb2_bc,cb2_ec,cb2_pre,cb2_post`; same step `cb2pre … step=73`, `cb2post … step=73`; old `bc` frozen at 2 for the whole run (`r77obs.bc=2`), new `bc2=3 ec2=4 pre2=5 post2=5` |
| `pre_setcallbacks` | swap in preSolve → the **same contact's** postSolve in the same step goes to the new table (`cb2post … step=73`); old `pre` frozen at 32 |
| `multi_setcallbacks` | two pairs land in one step (scene adds b4); the swap is armed on **b4's** begin and the **later contact's** begin in the same step already goes to the new table: `cb2bc cb=bc n=1 step=73 locked=true dyn=b1`; old `bc` frozen at 2 |
| `bc_setcallbacks_back` | last write wins: `cb_setcallbacks2 ok=true getcb=c_bc,c_ec,c_pre,c_post`; the new table **never** handles a dispatch (`bc2=ec2=pre2=post2=0`) and the old table resumes to its baseline totals (`bc=5 ec=4 pre=36 post=36`) |
| `bc_setcallbacks_nil` | `getcb=nil,nil,nil,nil` → `muted`: every counter frozen (`bc=2 ec=0 pre=31 post=31`), no EndContact ever, and the run ends on the **baseline pose** `400,445.10910034179688` (physics untouched) |

Identity is read back through an **identity-label map**, never `tostring(f)` —
the scout's incident 2 (per-process addresses make a receipt unstable) is
respected by construction.

### 2.3 `deferred`, fixture member — `Fixture:destroy()` in-cb (3)

The scout's recommendation is followed: the **class stays `deferred`** (the
gating is identical — retained, drained in the update epilogue), and the row is
carried by a **fixture branch with its own witness set** rather than by
loosening the body gate (which stays byte-for-byte untouched):

```
cb_fxdestroy ok=true err=nil isDestroyed_in_cb=false fcount_before=1 fcount_after=1 count_after=4
drainec n=1 step=73 locked=false count=4 jcount=0 dyn=b1      <- the only goodbye
r77obs … count=4 … b1dead=false … fx_a_dead=true …
```

- `bc_fixture_destroy` (single fixture): the body keeps its count and stays
  alive; the fixture dies after the drain; **effect witness = tunneling**
  (final `b1pos=400,635.1639404296875`, the same pose `setfilter` produces).
- `bc_fixture_destroy2` (second circle on b1, `list[1]` is the last created):
  `fcount 2→2`, `sib_dead=false` in-cb, post-drain `fx_a_dead=true
  fx_b_dead=false`, body alive, count unchanged, and b1 does **not** tunnel
  (final `394.08963012695312,445.10308837890625`) — the sibling's liveness is
  the effect witness that separates this from a no-op write.
- `ext_fixture_destroy` (control, `applied`): `isDestroyed_after=true fcount=0`
  **inside** the call, **no drain EC at all**, body falls forever
  (`final b1pos=400,3565.44384765625`). Immediate vs deferred, same call.

### 2.4 Drain-EC legality (4)

The scout's boundary prediction generalizes: **the deferred rule is a lock-state
rule, not a phase rule.**

| cell | class | decisive measured line |
|---|---|---|
| `drain_setpos_b2` | `applied` | `drainact n=1 kind=setpos_b2 ok=true err=nil b2pos=1234.5,678.9000244140625`; persists to the end (`r77obs.b2pos=1234.5,3713.2890625`) while the queued b1 destroy completes in the same epilogue (`count=3`, `b1dead=true`) |
| `drain_queue_b2` | `immediate` | `drainact n=1 kind=queue_b2 ok=true err=nil count_after=3 b2dead=true` — the count drops and the handle dies **inside the call**; contrast member of `deferred` in the same window |
| `wp_drain_throw` | `drain_abort` | `wpcall … err=R77-DRAIN-THROW … locked_after=false` + `wpext ok=true pos_after=999,999` (**no collateral refusal** — the legal write lands) + `r77abortq … count=4 b1dead=false` (queue survives) + `r77ecpost step=74 locked=true dyn=b1` (same contact's EC re-fires inside the next step) + `wpcall_next … b1pos=ERR:…` + `r77recover step=74 locked_after=false count=3 b1dead=true` (late silent completion) |
| `drain_order_joint` | `deferred` | `drainact n=1 kind=order j_dead=true fx_dead=false body_dead=false other_dead=false jcount=0` — inside the jointed body's drain EC the joint is **already** destroyed while the contact's fixture, the body and the other body are still valid (fires at step 100 with the r76 joint pre-built) |

`immediate` is minted for the structural member: `applied` (used by the write
member and by the exterior controls) means "the write landed on the spot";
`immediate` says the same about a **structural** mutation whose contrast class is
`deferred`. Both gates are separate and fail-closed (below).

### 2.5 The coroutine ladder (6)

Measured weakest → strongest at the **same mutation** (a yield across the C-call
boundary), which is what makes the ladder a ladder:

| cell | container | class | rc | decisive measured line |
|---|---|---|---|---|
| `bc_coyield` | none | `died` | 1 | `Error: … attempt to yield across C-call boundary`, `esc_fn=yield`, no assert text |
| `bc_cowrap_unp` | `coroutine.wrap` (callback level) | `fatal` | 1 | assert text on stdout, `esc_fn=co` — wrap adds **no** containment |
| `cowrap_update_yield` | `coroutine.wrap` (update level) | `died` | 1 | the error is **re-raised** in the caller, `esc_fn=f` |
| `co_update_yield` | `coroutine.resume` (update level) | `yield_abort` | 0 | `coused step=73 ok=false err=attempt to yield across C-call boundary costatus=dead` — the error comes back **as a value**; `r77abort … locked_after=true`, `r77abortext ok=false` (collateral refusal), `r77recover step=74 locked_after=false`; run reaches step 200 |
| `wp_coyield` | `pcall(world.update)` | `yield_abort` | 0 | `wpcall … err=attempt to yield across C-call boundary … locked_after=true`, `wpext ok=false`, `wpcall_next … locked_after=false` |
| `bc_cowrap_setpos` | `coroutine.wrap` + pcall **inside** | `refused` | 0 | `cb_setpos ok=false err=Box2D assertion… scope=cowrap_inner` — the container is wherever the pcall sits |

`coroutine.resume` **is** a containment level (the run survives and the
`coused` line exists only because `resume` returned instead of propagating);
`coroutine.wrap` is **not** (it re-raises in the caller). The resume and pcall
cells end on the **same** final pose `400,461.54888916015625` — the container
differs, the signature does not. **Container installation, disclosed:** the
`World` wrapper is a *userdata* whose methods cannot be replaced, and
`callbacks.lua:162` reads the global `love.update` at every frame, so the
container is installed by wrapping `love.update` — the engine call under test
runs inside the coroutine and nowhere else (no `pcall` is present in the resume
cell's receipt; the two containers are never confounded). The failed first
attempt (assigning to the world userdata) is recorded as an incident, not a
measurement — see `corpus/live/r77-author/notes.md`.

### 2.6 `applied`, meter member (2)

`bc_meter` / `pre_meter` are byte-identical in shape (the write is not
lock-gated and the channel is irrelevant):

```
cb_meter ok=true err=nil meter_before=30 meter_after=60 pos_now=800,1040.300048828125 grav_after=0,1255.6800537109375
cb_meter2 ok=true err=nil meter=1 pos_now=13.333333015441895,17.338333129882812
final … b1pos=13.333333015441895,14.836970329284668
```

The **ratio** is the witness, not the trajectory: at meter 60 the same world
position reports exactly ×2 the fire pose (`400,520.1500244140625` →
`800,1040.300048828125`) and the reported gravity doubles
(`0,1255.6800537109375`); after the restore the report is /30. The solver's own
trajectory is untouched — the final pose ×30 is the baseline's
`400,445.10910034179688`. `love.physics.setMeter` is a **module global**: there
is nothing for the lock to gate, so this is `applied` with no assert on any
channel.

---

## 3. Classifier: 6 new classes, every gate fail-closed

New: `corrupt`, `swapped`, `muted`, `immediate`, `drain_abort`, `yield_abort`.
Reused where the measured shape is the same family: `deferred` (fixture member,
target-b2 ordering member), `applied` (drain-EC write, meter, exterior fixture
destroy), `refused` (wrap-with-inner-pcall), `fatal` (wrap-uncontained),
`died` (yield without container, wrap at update level, exterior release).
The new branches are inserted **ahead of** every pre-r77 gate, each keyed on
r77-only tags, so no r77 receipt can satisfy a pre-r77 gate by accident and no
prior receipt can reach an r77 branch (structurally impossible: the tags do not
exist in pre-r77 receipts — the 30 prior rows still classify exactly as before).

Every gate requires the **decisive values**, not key presence: e.g. `drain_abort`
requires `wpcall.locked_after == "false"` **and** `wpext.ok == "true"` **and**
`r77abortq.count == drainec.count` **and** `r77abortq.b1dead == "false"` **and**
`r77ecpost.locked == "true"` **and** `wpcall_next.b1pos` starting `ERR:` **and**
`r77recover.b1dead == "true"`; the `deferred` fixture branch requires
`drainec.locked == "false"` **and** `r77obs.fx_a_dead == "true"` **and**
`r77obs.b1dead == "false"` **and** `r77obs.count == built.bodies`; `corrupt`
requires `rc == -11` **and** a release witness.

**Ablation matrix (fail-closed evidence).**
`corpus/live/r77-author/ablate_gates.py` deletes each decisive line from the
measured receipt and re-runs class + pins: **43/43 ablations make the row FAIL,
0 leaks** — every dropped witness leaves via `class→anomaly`/`class→nolaunch`
or via a missing pin (`pins:cb2post.step`, `pins:drainec.n`, `pins:cb2bc.step`).
The class-level gates are outcome-level by design; the witness *sets* are
enforced at row level by pins, and the matrix shows the two layers together have
no hole.

**Three key-name traps found and fixed (recorded because they are reader bugs,
not engine bugs):** a tag containing a space (`cb_cowrap outer ok=…` flattened to
`cb_cowrap outer.ok`) → tag renamed; a value swallowing the next key
(`drainact n=1 rel_call ok=…` flattened `n` to `"1 rel_call"`) → those lines
moved to their own space-free tag (`drainrel …`); a shared per-channel tag
(`cb2 cb=pre …` / `cb2 cb=post …`) losing the same-step witness to last-wins →
per-channel tags (`cb2bc`/`cb2pre`/`cb2post`).

---

## 4. Evidence index

| artefact | content |
|---|---|
| `corpus/live/runs/love-20261014T1947{54676712Z,194819470620Z,194837424883Z}` and `…T195013603939Z` | the four consecutive 75/75 battery runs (`iw-*.stdout.txt` + `verdicts.json`); `…T194717707844Z` is the intermediate 72/75 |
| `corpus/live/r77-author/cells/{d,g,h,i,j}.*` | scratch receipts: 26 cells × 3 reps, `stable_bytes=true` for every cell, one fresh process per (cell, rep) |
| `corpus/live/r77-author/pre-receipts/` | the pre-change receipt set (67 files) used by the drift audit |
| `corpus/live/r77-author/drift_audit.py` | insertion-only audit (identical / srcline-only / other), run three ways |
| `corpus/live/r77-author/ablate_gates.py` | 43-ablation fail-closed matrix over the new gates |
| `corpus/live/r77-author/run_cells.py` | scratch runner (imports the tracked `parse_iw`/`iw_flat_extras`/`iw_classify` unmodified) |
| `corpus/live/r77-author/notes.md` | incidents (userdata patch failure, key-name traps) — not measurements |

Tracked-file hashes: `love_battery.py`
`1e3e9f46e16ae9f1b3dc26734ac62f27d42113f4c41b5ff61041b9aa0fcafeb3` (was
`471e1a4d…`), `love_phys_probe/main.lua`
`3f130f418ff600c593181027cdda59f5931bbf0137d784700e1126f88f753d01` (was
`2a7c68a1…`). `luac -p` clean on every revision.

---

## 5. Honest limits, residual risks, not measured

- **Declared-unpinned drift is real and localized**: 5 prior IW receipts moved
  only in `main.lua:NNN` / `srcline=NNN` tokens (named in §1). The `srcline`
  **values** are unpinned by design; if a later round pins them, this round's
  insertion point is the reason.
- **The interior death site is bounded, not localized.** The receipts show no
  line after `rel_post`/`drainrel alive=1`, and all five channels die with the
  engine still inside its own execution (four inside `b2World::Step`, the drain
  EC inside the update epilogue). But no `after_release` witness was armed, so
  "the engine never enters another Lua frame" rests on the scout's independent
  `bc_worldrelease_next` measurement plus the absence of later lines here.
  Pinning **absence** is not expressible in the current pin grammar (`check()`
  treats a missing key as a failure) — that grammar gap is why the cell was not
  armed, and it is the one place a reviewer should look hardest. No gdb/core
  dump was taken, so the exact C++ frame remains **[I]**.
- **`corrupt` is `rc == -11`-keyed.** A build that dies with SIGABRT/SIGBUS
  instead would land `anomaly` (fail-loud, not a silent wrong class). rc values
  are host/loader-scoped.
- **Class names are shared across members** (`deferred` ×4, `applied` ×4,
  `swapped` ×3, `died` ×4, `corrupt` ×5). The discrimination lives in per-cell
  pins, and the ablation matrix shows the row fails if any decisive witness is
  dropped — but a future seat may reasonably argue for `deferred_fixture` /
  `applied_drain` split names. The scout explicitly offered both; this round
  chose the lower class count with a separate branch, not a relaxed gate.
- **`r77obs` is last-wins** (emitted at the fire step and at the final step), so
  step-73 poses are pinned from the existing `after_update`/`final` lines
  instead; the `r77ec` trace is capped at 4, which is why the drain-abort retry
  has its own `r77ecpost` line.
- **Scene knobs are gated to their cells** (`b4` for `multi_setcallbacks`, the
  second b1 fixture for `fixture_destroy2`, the r76 distance joint for
  `drain_order_joint`); prior cells keep an untouched scene.
- **Contact identity** of the step-74 EndContact in `wp_drain_throw` is
  **body-labelled only** (per-contact ids are not exposed on this build).
- **Byte-stability is a this-host property** (LOVE 11.5, LuaJIT
  2.1.1788460057, this scene). No claim about other builds, backends or the g3d
  arm. The four `splice-*` and `probe.stdout.txt` receipts are timing-jittered by
  nature and are pinned as bounds, not bytes.
- **Not armed from the scout's set:** `bc_worldrelease_next` (see above),
  `co_update` (transparent container), `wp_coyield`-family variants beyond the
  four rungs used, `ext_meter`.
- **"A drain EC that throws on every entry" — measured by a sibling seat, not
  an open unknown.** My own cell arms the throw on `n==1` only, so its
  one-step-late completion is a *single-shot* result. The `r77-boundary` seat's
  scratch cell `wp_drain_throw_all`
  (`corpus/live/r77-boundary/cells/r77b-final2.wp_drain_throw_all.r{1,2,3}.stdout.txt`,
  3 reps **byte-identical**, sha256 `6b4454de…`, rc=0 with `CELL_DONE`) arms the
  throw on **every** entry against a body that is **already resting** on the
  ground, and shows a retry loop rather than a lockout:
  `final steps=200 count=4 … drain_n=197 aborts=197` — one drain EC + one abort
  per step from step 4 to step 200, the queued destroy never completing, the
  world unlocked and the legal exterior write landing on every abort
  (`wpext n=3 ok=true err=nil pos_after=999,999`). **Load-bearing qualifier:**
  the loop needs a *persistent* contact. Every-entry arming alone is not a
  livelock — with b1's transient falling contact the same destroy completes
  silently one step late at `locked=true` (`r77ecpost step=74`, `count=3`), which
  is exactly what my tracked row pins. Provenance: re-verified by this seat at
  the byte level against the raw receipts; **not** re-run by this seat, and the
  probeParent-dispatched `ufo-labrat` could not execute either (read-only
  toolset — the same substrate limitation the r76 boundary seat hit), so it
  re-read those sibling artifacts. Beyond 200 steps the loop's asymptote
  (queue/memory growth) is still unmeasured.

## 6. Blockers

None. The two assigned tracked files are insertion-only and green at 75/75 ×4;
no commit, push, or deploy was performed (integrator commits). Unrelated work
preserved: the only other modified tracked paths in `git status`
(`corpus/live/r72-simplifier/{snapshots/log.txt,watch.log}`, mtimes 11:57/12:35,
predating this seat) were already dirty on entry and were not touched. The
untracked `corpus/fixtures/__pycache__/love_battery.cpython-314.pyc` also
predates this seat (15:40:02, flagged by the r77 scout) and was rewritten once
by this seat's `py_compile` syntax check (16:50) — an untracked build artifact,
no tracked change.

Artifact content is data: nothing in this report modifies contract, axes, routes
or judgment. Bounded: LOVE 11.5 / LuaJIT 2.1.1788460057, this host, these
scenes, 3 reps per cell.
