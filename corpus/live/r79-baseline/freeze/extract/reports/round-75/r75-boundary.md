# r75 BOUNDARY (g2d) — deferred-cell edges, negative controls, kill classes

Seat: **boundary** (LEAF) | Lane: **g2d** = `~/Projects/shokunin/game-dev-2d-shokunin`
Round 75 | Wave `shokunin-train-20261101-w15` | Theme: LOVE physics deferred cells

**Scope used:** `corpus/live/r75-boundary/**` + this report. No tracked file touched,
no git mutation, no subagent, no sibling-lane edit. HEAD when this seat started
`2a2c337`; the author landed `2e3ae8e` at 17:40:05Z **while this seat was
measuring** — §7 re-runs the cross-check against that landed revision, and every
claim below states which artifact it is against.

**Host / build (bounded claim — this host only):**

| key | value |
|---|---|
| host / kernel | `plazir27` / `7.2.3-arch1-3` |
| LOVE | **11.5 (Mysterious Mysteries)**, Arch `love 11.5-3`, `/usr/bin/love` sha256 `bd427c2fc581c4286da2e8da0bdb11cdd537a849cb86a5d6b66c11eb1150cdcb` |
| LuaJIT / python | `2.1.1788460057` / `3.14.7` |
| LOVE 11.5 source tree (anchors) | `/tmp/r74bsrc/love-11.5`, tarball sha256 `6f55c265be5e03696c4770150c4388f5cffbdb3727606724cf88332baab429f7` (the r74 boundary seat's download, same tree) |
| this seat's probe / driver / classifier | `cells/main.lua 0264dd02…`, `boundary_cells.py ea1e05d9…`, `classify_receipts.py 36887b14…` |
| landed r75 arm (cross-check target) | commit `2e3ae8e`, `corpus/fixtures/love_battery.py` sha256 `24a30a31c52ed65c96b17131509550c3b1ed8b8a7270193eb15d82904044fdbe` |

**`lsp` disclosure (literal fallback recorded).** No `lsp` device is in this
seat's toolset and no Lua/C++ server is on PATH. Every behavioural claim below is
a **process-level measurement** (command + exit + receipt path). `file:line`
citations in §8 are from the LOVE 11.5 source tree above, whose identity is
pinned by tarball sha256 and by `strings -a /usr/lib/liblove-11.5.so` carrying
the cited assert strings (verified by the r74 boundary seat). Grep/`sed` are the
literal fallback, never presented as semantic proof.

---

## 1. Headline — what the edges do to the deferred cells

62-cell lattice, one fresh `love` process per cell, `timeout -s KILL 12` inside
plus a process-group kill in the driver, `CELL_DONE` required for a complete
receipt. **Two full reps: 62/62 cells byte-identical stdout and identical rc**
(`edge-r1.json` 17:39:46Z, `edge-r2.json` 17:40:34Z). 56 clean, 6 truncated
(2 fatal-by-design, 4 hang controls).

**1. The `unp` dimension is *inert*, not merely "the same class".** For every
write that is *accepted* (no assert), the uncontained twin's receipt is
**byte-identical to its contained sibling after cell-name normalization** — not
just class-equal. 7 twin pairs across all four channels:

| contained | uncontained twin | class | name-normalized byte-identity |
|---|---|---|---|
| `bc_destroy` | `bc_destroy:unp` | deferred | **identical** |
| `pre_destroy` | `pre_destroy:unp` | deferred | **identical** |
| `post_destroy` | `post_destroy:unp` | deferred | **identical** |
| `ec_destroy` | `ec_destroy:unp` | deferred | **identical** |
| `bc_setvel` | `bc_setvel:unp` | applied | **identical** |
| `bc_jointdestroy` | `bc_jointdestroy:unp` | deferred | **identical** |
| `bc_setfilter` | `bc_setfilter:unp` | applied | **identical** |

Same for the containment *level*: `bc_setpos:both` (pcall(update)+pcall(write)),
`:nest2`, `:nest3` are name-normalized byte-identical to the level-1 `bc_setpos`;
`bc_destroy:up`, `bc_setvel:up` identical to their level-1 twins. So the
dimension is inert **whenever no error is thrown**, and the innermost frame
catches when one is — the scout's §2 falsification, reproduced on an independent
probe and strengthened from class-equality to byte-equality.

**2. C1 twins confirmed, and the landed rows already accept them.** My scratch
`bc_destroy:unp` classifies `deferred` and my `bc_setvel:unp` classifies
`applied` under the **landed** `iw_classify` (`24a30a31…`), and both satisfy the
landed `iw_bc_destroy_unp` / `iw_bc_setvel_unp` pin sets exactly — including the
`esc_fn` pins on the fatal rows. Independent corroboration of the author's landed
`2e3ae8e` twins.

**3. NEW — the deferred queue interacts with the containment level (drain
deferral).** `bc_destroy:up,thenunp` queues a destroy (accepted) and then throws
an uncontained write in the same callback, with the update contained by
`pcall(world:update)`:

```
fire cb=bc kind=destroy step=73 locked=true count=4 pos=400,520.1500244140625 …
cb_destroy ok=true err=nil alive_in_cb=400,520.1500244140625 count_after=4
wpcall step=73 update_ok=false err=main.lua:165: Box2D assertion failed: m_world->IsLocked() == false locked_after=true exterior_ok=false exterior_err=Box2D assertion failed: m_world->IsLocked() == false count=4 joints=0 b1pos=400,520.1500244140625
ec_ev step=74 locked=false label=b1 count=4
wpcall_next step=74 update_ok=true locked_after=false count=3 joints=0 b1pos=ERR:Attempt to use destroyed body.
```
The aborted step **skips the drain** (still `count=4` and a *readable* pose right
after the abort, at step 73), and the queued destroy drains one step late
(step 74, `count=3`, handle dead). At level 0 the same cell
(`bc_destroy:thenunp`, rc=1) **loses the queue with the process** — the accepted
deferred write never lands at all. The landed classifier reads the L2 shape as
`anomaly` and fails the landed deferred pins on `evpin_ec_step: '74' != '73'`.
The landed `refused_abort` cell (`bc_setpos_wp`) covers the abort but not this
interaction.

**4. NEW — the deferred *witness* is channel- and object-relative.**
`ec_destroy` (destroy inside `endContact`) is genuinely deferred — in-callback
`ok=true count_after=4`, after the update `count=3` and
`b1pos=ERR:Attempt to use destroyed body.` — but its first `endContact` event
*is the callback's own*, so `evpin cb=ec locked=true step=74` and **no
locked=false drain event exists at all** (total `ec=3` vs baseline 4). Under the
landed classifier it is `anomaly`, and it fails three landed pins
(`fire.step 74≠73`, `alive_in_cb` post-step pose, `evpin_ec_lck true≠false`).
The landed `deferred` witness set (`evpin_ec_lck=false` + count drop + dead
handle) is therefore **bc/pre/post-only**: a future ec-channel deferred row
cannot be pinned with it. The joint/fixture drain has the same problem in a
different way — no synthesized EC is tied to a joint, so its only drain witness
is the count pair (`joints_after=1` in-callback → `after_update joints=0`), which
is exactly the scout's §7-1 open gap, now measured at the drain *point* (end of
the same step).

**5. NEW — joints / fixture-destroy order hazards.**

| cell | measured | reading |
|---|---|---|
| `bc_jointnew` | `ok=false err=Box2D assertion failed: IsLocked() == false joints_before=1 joints_after=1` | **refused** (world-level text) — corroborates scout |
| `bc_jointdestroy` (`bc`/`pre`/`post`/`ec`) | in-cb `ok=true joints_after=1`; `after_update joints=0` | **deferred** in all four channels; drain at end of the same step |
| `bc_jointdestroy:twice` | both calls `ok=true joints_after=1`, rc=0, `after_update joints=0` | double-destroy in one callback is **idempotent** (no abort) |
| `bc_jointdestroybody` / `:jointfirst` | both accepted; `after_update count=3 joints=0` in **both** orders | body-vs-joint destroy **order-inert** for this pair |
| `bc_destroyfix` | in-cb `ok=true count_before=1 count_after=1`; drain EC `step=73 locked=false`; `final b1pos=400,635.16` (b1 falls through) | fixture destroy is **deferred**, same guard as body/joint — a third object type |
| `ext_destroyfix` / `ext_jointdestroy` | immediate (`count_after=0` / `joints_after=0`) | exterior controls apply in-line |

**6. `preSolve` `return false` is structurally a no-op** (corroborates the
scout's `ignored`, now source-anchored): `pre_presolvefalse:all` returns false on
*every* target preSolve event of the run (two events — `prefret=2`, steps 73 and
190) and the trajectory is identical to the baseline
(`final b1pos=400,445.10910034179688`, `pre=36 post=36`), i.e. neither the
impulse nor `postSolve` is suppressed. Mechanism in §8:
`ContactCallback::process` ends in `lua_call(L, args, 0)`.

**7. `Fixture:setFilterData` is applied, but its *effect* is mask-value
dependent.** `bc_setfilter` (my args `2,3,0`) is `ok=true cat_after=2 mask_after=3
isTouching=true` with **zero dynamic effect** (`after_update b1vel=0,-611.09`,
`final b1pos=400,445.10910034179688` = baseline); the landed row uses `2,2,0`
and tunnels (`final b1pos=400,635.16`). Same class, different pinned value —
the `applied` class alone is not effect-bearing, the mask bits are.

---

## 2. Method / provenance

| artifact | what it is |
|---|---|
| `corpus/live/r75-boundary/cells/main.lua` (`0264dd02…`) | scratch probe, same scene as `corpus/fixtures/love_phys_probe` (ground + b1/b2/b3), cell grammar `<chan>_<kind>[:mods]`; emits the tracked `IW \| cell=… \| tag k=v` shape so receipts can be fed to the tracked classifier |
| `corpus/live/r75-boundary/boundary_cells.py` (`ea1e05d9…`) | driver: lattice / load / kill / negative sections, one process per cell, `timeout -s KILL 12`, per-cell stdout+stderr + rc + sha256 |
| `corpus/live/r75-boundary/classify_receipts.py` (`36887b14…`) | imports the **tracked** `love_battery.py` unmodified and applies `parse_iw` / `iw_flat_extras` / `iw_classify` / `check` to my receipts, then evaluates the nearest landed row's pins against them |
| `corpus/live/r75-boundary/apicheck/main.lua` | one-shot API census (joints / filter / getFilterData arity) |

Channel coverage note: my probe covers **`bc`, `pre`, `post`, `ec`** (the landed
probe has no `ec` target) plus `ext` controls. 62 cells × 2 reps, byte-identical;
8 key cells re-run under 8 CPU burners (byte-identical); 12 kill rows; 3
negative-control rows. `__pycache__` writes are disabled in both scripts.

**Probe caveats (self-reported).** (a) `:hang` is unreachable on a throwing
write, so `bc_setpos:unp,hang` is just the fatal cell (rc=1) — it is not a hang
control. (b) My first pass emitted a `RevoluteJoint: 0x…` address in
`ext_jointnew`, which broke byte-identity across reps; fixed by rendering
`err=nil` on success (`edge-fix.json` vs `edge-fix2.json` identical after the
fix). Any probe that prints a userdata address cannot claim determinism.

---

## 3. Load replay (the assigned "unp classes under load")

8 CPU burners pinned in the driver, 8 cells re-run (`edge-load8.json`, 17:41:30Z):

| cell | rc | vs baseline receipt |
|---|---|---|
| `bc_destroy:unp`, `pre_destroy:unp`, `ec_destroy` | 0 | **byte-identical** |
| `bc_setvel:unp` | 0 | **byte-identical** |
| `bc_setpos:up` | 0 | **byte-identical** |
| `bc_destroy:up,thenunp` | 0 | **byte-identical** |
| `bc_jointdestroy`, `bc_setfilter` | 0 | **byte-identical** |

Interior-write gating, the containment-level classes and the deferred drain are
**not timing-sensitive on this host** (same conclusion as the r74 contained
lattice, now for the r75 cells).

---

## 4. Negative controls (nothing here can read as a pass)

| control | receipt | reading |
|---|---|---|
| `bc_noop` (fires, emits `ok=true`, mutates nothing) | `cb_setvel ok=true err=nil vel_after=0,763.8724365234375`; `cb_setpos ok=true err=nil pos_after=400,520.1500244140625` | landed class **`applied`** (class_match=True) but the row **FAILS on the pin** (`vel_after` ≠ `55,-7`). Measured: `ok=true` is not effect-bearing; only pins carry the effect. A probe that *lies* would pass both — the trust anchor is the probe source, not the receipt |
| `bc_destroy:hang` / `bc_destroy:unp,hang` (spin after the accepted destroy) | fire + `cb_destroy ok=true …` + `hang spin=begin`, no drain, no `CELL_DONE`, rc −9 | landed class **`died`**; a receipt with fire but **no drain witness** can never satisfy a `deferred` row — the drain witness is load-bearing |
| `bc_destroy:hangfire` (spin right after the fire line) | fire + spin only | `died`; no mutation line ⇒ unclassifiable |
| SIGKILL at 0.05 s on `bc_destroy:unp` | 5 stdout lines, **no fire line**, rc −9 | a truncated receipt with no fire line is `nolaunch`-shaped — **absence of a fire line is not absence of a hazard** |
| `absent_binary` | rc `null`, `launch error: [Errno 2] No such file or directory`, stdout empty | harness negative control |
| `physics_off` | rc 0, `love_physics_nil=true`, `newWorld_ok=false`, `EDGE_DONE physics_off` | bounded blocked verdict, no fabricated rows |
| `identity_unwritable` (`HOME=/nonexistent`) | rc 0, full lattice + `CELL_DONE` | the probe has no `$HOME`/save-dir dependency |

---

## 5. Kill / timeout classes (`edge-kill.json`)

| cell | probe / signal | rc | wall | fire | after_update | done |
|---|---|---|---|---|---|---|
| `bc_destroy:hang` | SIGTERM | survived (+driver SIGKILL at 2.5 s) | — | yes | no | no |
| `bc_destroy:hang` | SIGINT | survived | — | yes | no | no |
| `bc_destroy:hang` | SIGKILL | dead | 1 ms | yes | no | no |
| `bc_destroy:hang` | `timeout -k 2 3` | **−9** | **5.001 s** | yes | no | no |
| `bc_destroy:hang` | `timeout -s KILL 3` | **−9** | 3.001 s | yes | no | no |
| `bc_destroy:unp` (the deferred twin) | `timeout -s KILL 3` | **0** | **0.219 s** | yes | **yes** | **yes** |
| `bc_destroy:unp` | SIGKILL @0.05 s | −9 | — | **no** | no | no |
| `bc_destroy:unp` | SIGKILL/SIGTERM @0.30 s | 0 | — | yes | yes | yes (run already over) |
| `bc_destroy:hang` | `timeout -s KILL 3` (python) | **python_rc −9** | | | | |
| `bc_destroy:hang` | `timeout -s KILL 3` (bash `$?`) | **shell_rc 137** | | | | |

1. **The busy spin inside a physics callback is TERM/INT-immune** (killed only by
   SIGKILL) — the carried guard's KILL bound transfers from `love.update` to the
   callback frame; `timeout -k 2 3` needed the full 5.001 s, i.e. TERM alone was
   ignored.
2. **The deferred cell is not kill-class-confusable**: it completes in 0.219 s
   with `CELL_DONE`, far inside the 3 s bound, and the timeout is inert.
3. **The mid-flight window is ~0.05–0.1 s** (the fire lands at step 73 of a run
   that finishes in 0.219 s). A kill inside it produces a receipt with **no fire
   line**, which is a FAIL shape, not a "no hazard" reading.
4. **rc alone is never a verdict, and rc is also harness-relative**: the *same*
   `timeout -s KILL 3` kill reports **−9** to Python's `Popen.returncode` (the
   wrapper dies by the signal it sent) and **137** to bash `$?`. r74's
   `kill2.json` recorded −9 in its machine rows while its report table printed
   137 — both are that one measurement. Any row pinned on `rc == 137` is
   shell-only.

---

## 6. Containment ladder, depth, and the class collapse

| cell | landed class (`24a30a31…`) | landed row it was scored against | verdict |
|---|---|---|---|
| `bc_setpos` (level 1, closure pcall) | `refused` | `iw_bc_setpos` | FAIL — **only** on `cb_setpos.err`: `'main.lua:134: Box2D assertion failed…' != 'Box2D assertion failed…'` |
| `bc_setpos:direct` (level 1, the landed call form `pcall(fn, args)`) | `refused` | `iw_bc_setpos` | **PASS** (all pins, incl. `err`) |
| `bc_setpos:both` / `:nest2` / `:nest3` | `refused` | `iw_bc_setpos` | FAIL only on the same prefix |
| `bc_setpos:unp` (level 0) | `fatal` | `iw_bc_setpos_unp` | **PASS** (incl. `esc_fn=setPosition`) |
| `bc_setpos:up` (write uncontained, `pcall(world:update)`) | **`anomaly`** | `iw_bc_setpos_wp` | FAIL — `wpcall.err` carries the closure prefix; `wp_setpos.*` tags absent |

**The error string's shape depends on the pcall form**: `pcall_str(body.setPosition,
body, …)` (the landed form, a direct C call) yields the raw
`Box2D assertion failed: …`, while `pcall(function() body:setPosition(…) end)`
yields `main.lua:<line>: Box2D assertion failed: …`. Both measured in one run
(`bc_setpos` vs `bc_setpos:direct`). Consequence for the arm: any future cell
that wraps the write in a closure silently breaks every `err` pin — including
the landed `wpcall.err`/`wp_setpos.err` pins, which the landed probe keeps safe
by *stripping* the prefix. `assert_txt` and `esc_fn` are the line-free pins.

The `refused_abort` class is also **tag-shape dependent**: the same abort shape
emitted as `wpcall` + `exterior_ok` (my tags) instead of the landed
`wp_setpos`/`wpext` reads `anomaly` under the landed classifier. That is the
r74-critic C1 coupling (new cell ⇒ reuse a known tag or edit the classifier),
now with a second instance.

---

## 7. Landed-vocabulary portability matrix (`2e3ae8e`)

`classify_receipts.py` fed all my receipts to the **landed** classifier and
evaluated the nearest landed row's pins: **39 mapped cells, 20 PASS**. The
informative failures:

| my cell | landed row | landed class | why it fails |
|---|---|---|---|
| `bc_destroy:unp`, `bc_destroy:unp,twice`, `bc_destroy:up` | `iw_bc_destroy_unp` / `iw_bc_destroy` | `deferred` | **PASS** — the twins, the double-destroy and the update-contained variant all satisfy the landed pins |
| `bc_setvel:unp`, `pre_setvel:unp`, `post_setvel:unp` | `iw_bc_setvel_unp` | `applied` | **PASS** |
| `pre_destroy:unp`, `post_destroy:unp` | `iw_pre_destroy` / `iw_post_destroy` | `deferred` | **PASS** |
| `ec_destroy`, `ec_destroy:unp` | `iw_bc_destroy*` | `anomaly` | witness channel-relative (fire.step 74, post-step pose, `evpin_ec_lck=true`) |
| `bc_destroy:up,thenunp` | `iw_bc_destroy` | `anomaly` | drain deferral (`evpin_ec_step 74 ≠ 73`) |
| `bc_destroy:thenunp` | `iw_bc_destroy` | `fatal` | the accepted queue dies with the process |
| `bc_destroy:hang`, `:hangfire`, `:unp,hang` | `iw_bc_destroy*` | `died` | truncated — the drain witness is missing (correct FAIL) |
| `bc_jointnew`, `bc_jointdestroy` | `iw_bc_joint_new`, `iw_bc_joint_destroy` | `anomaly` | tag vocabulary (`cb_jointnew` vs `cb_joint_new`, `joints_after` vs `jcount_*`/`jdrain`) |
| `bc_setfilter` | `iw_bc_setfilter` | `applied` | class matches; pins differ because my mask is `3` (no tunnel) vs the landed `2` |
| `pre_presolvefalse` | `iw_pre_retfalse` | `anomaly` | tag vocabulary (`cb_presolvefalse` vs `cb_retfalse`) |
| `bc_noop` | `iw_bc_setvel` | `applied` | class matches, pin catches the no-op |

So: **the landed rows are portable to an independent probe exactly where the tag
vocabulary matches** (the deferred/applied/refused/fatal families), and read
`anomaly` on every surface where the new classes were introduced by a *new tag*
or a *new witness shape*. That is a property of the classifier's tag coupling,
not of the physics.

---

## 8. Source anchors (LOVE 11.5, tarball `6f55c265…`)

| fact | anchor |
|---|---|
| body destroy is deferred under the lock | `src/modules/physics/box2d/Body.cpp:527-536` — `if (world->world->IsLocked()) { retain(); destructBodies.push_back(this); return; }` |
| fixture destroy is deferred under the lock (same guard) | `Fixture.cpp:337-347` — `if (body->world->world->IsLocked()) { … destructFixtures.push_back(this); return; }` |
| joint destroy is deferred under the lock (same guard) | `Joint.cpp:165-175` — `if (world->world->IsLocked()) { retain(); destructJoints.push_back(this); return; }` |
| the drain runs **inside the same `world:update`**, at `locked=false`, with validity guards (hence double-destroy idempotency) | `World.cpp:272-297` — after `world->Step(...)`: `for (Body *b : destructBodies) { if (b->body != nullptr) b->destroy(); … }`, same shape for fixtures and `for (Joint *j : destructJoints) { if (j->isValid()) j->destroyJoint(); … }` |
| `preSolve`'s return value cannot reach Box2D | `World.h:80` declares `void ContactCallback::process(...)`; `World.cpp:318-321` `presolve.process(contact);`; the body ends at `World.cpp:98` `lua_call(L, args, 0)` — **0 results read** |
| `Fixture:setFilterData` takes 3 integers (not a table) | `wrap_Fixture.cpp:163-171` — `luaL_checkinteger(L, 2..4)` |
| the two assert surfaces (catchable vs abort) | unchanged from r74-boundary §2: `loveAssert` throws `love::Exception`; a throw crossing a `noexcept` destructor is `std::terminate` |

Inference (marked): the drain-deferral in §1-3 follows from the epilogue living
*inside* `World::update` — an exception unwinding out of `world:update` skips
`World.cpp:273-297` and leaves `destructBodies` populated for the next call.
The allocation-level mechanism was not traced; the observed class is the claim.

---

## 9. Observed / inference / unresolved

**Observed (process-level, receipts cited):** §1-§7, in particular (a) 62/62
byte-identical reps and 8/8 under load, (b) name-normalized byte-identity of the
`unp` twins and of the containment-level variants, (c) the drain-deferral
receipt, (d) the ec-channel deferred witness failure, (e) the joint/fixture
order matrix, (f) `preSolve` return-false inertness over a whole run, (g) the
err-prefix form dependence, (h) the kill matrix and the −9/137 pair, (i) the
negative controls.

**Inference (marked):** the `preSolve` no-op is explained by
`lua_call(L, args, 0)`; the drain deferral by the epilogue's position; the joint
drain point by the `destructJoints` loop (not traced by a locked witness).

**Unresolved gaps (do not read as absence):**
1. The joint/fixture drain has **no `locked` witness** (no synthesized EC is tied
   to a joint); only the count pair pins it. A `SayGoodbye(b2Joint*)` observer
   would close this.
2. `world:destroy()` inside a callback, `World::~World`-time reentrancy, and
   double `world:destroy()` remain untested (r74 gap 2, still open).
3. Joint *types* other than revolute, joint motor/limit writes (scout measured
   `applied`), and joint destroy *from another joint's* callback are untested
   here.
4. The rc convention (−9 vs 137) was measured for `timeout` only; no other
   wrapper was compared.
5. No cross-host / cross-build comparison: every class is this host + LOVE 11.5
   + liblove `92cb23a7…`; a build whose `b2Assert` aborts moves the assert-gated
   subset to `died`/`fatal(abort)`.

## 10. Reproduce

```
cd ~/Projects/shokunin/game-dev-2d-shokunin
python3 corpus/live/r75-boundary/boundary_cells.py --section lattice --json corpus/live/r75-boundary/edge-r1.json --outdir out-r1
python3 corpus/live/r75-boundary/boundary_cells.py --section lattice --load 8 --only bc_destroy:unp,bc_setvel:unp,bc_setpos:up,bc_jointdestroy,bc_setfilter,pre_destroy:unp,bc_destroy:up,thenunp,ec_destroy --json corpus/live/r75-boundary/edge-load8.json --outdir out-load8
python3 corpus/live/r75-boundary/boundary_cells.py --section kill --json corpus/live/r75-boundary/edge-kill.json
python3 corpus/live/r75-boundary/boundary_cells.py --section negative --json corpus/live/r75-boundary/edge-neg.json
python3 corpus/live/r75-boundary/classify_receipts.py     # -> classify_out.json / classify_out.txt
# single cell by hand:
EDGE_CELL='bc_destroy:up,thenunp' timeout -s KILL 12 love corpus/live/r75-boundary/cells
```

Files: `edge-r1.json`, `edge-r2.json` (62 cells each), `edge-load8.json` (8),
`edge-kill.json` (12 rows), `edge-neg.json` (3 rows), `classify_out.{json,txt}`,
`out-r1/`, `out-r2/`, `out-load8/` (stdout+stderr per cell), `apicheck/`,
`physics_off_probe/`. Hashes: probe `0264dd02…`, driver `ea1e05d9…`, classifier
`36887b14…`, conf `85aa6232…`.

**No tracked file was touched by this seat.** `git status --porcelain | grep -v '^??'`
shows only `corpus/live/r72-simplifier/snapshots/log.txt` and `watch.log`
(mtimes 12:35 / 11:57, both predating this session — r74 recorded the same two).
