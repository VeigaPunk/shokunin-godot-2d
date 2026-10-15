# game-dev-2d round 78 — author (g2d): the nested-update damage surface

Seat `AUTHOR` (LEAF) | lane `g2d` | round 78 | wave `shokunin-train-20261101-w18` | host **devin**.
Runtime **LOVE 11.5** (Mysterious Mysteries, `/usr/bin/love`), LuaJIT 2.1.1788460057,
Python 3.14.7. Repo `~/Projects/shokunin/game-dev-2d-shokunin`, HEAD
`d4aaa95` (*r77 report-last: adjudicator ADMIT-corr + ledger*) at seat start and
at seat end (no commit by this seat). Writes: `corpus/fixtures/love_battery.py`,
`corpus/fixtures/love_phys_probe/main.lua`, this report, and
`corpus/live/r78-author/**` (scratch receipts, runner, audits). `conf.lua`
untouched. **No git mutation** (integrator commits); no tracked file outside
those two fixtures was written.

**`lsp` disclosure (unchanged host state):** no `lsp` device is exposed in this
session and no Lua/Python language server is installed (`lua-language-server`,
`sumneko-*`, `pylsp`, `pyright` ABSENT; only `clangd`, and the LOVE C++ tree is
not in this repo). Symbol-aware tooling was therefore unavailable for every edit
here — **hand editing was the only path**, and that unavailability is recorded
rather than implied. Verification carriers: fresh-process execution receipts
(×3 reps per cell, ×4 consecutive full battery runs), `luac -p` parser
diagnostics, and line-numbered anchors in the pinned LOVE tree
(`/tmp/r74bsrc/love-11.5`, re-read not copied). No cold-start empty result is
recorded as absence.

**Assignment (brief):** arm the r78 scout's pre-measured nested-update damage
surface as tracked cells — the lock-clear, the inner-epilogue drain ownership,
the contacting-destroy dispatch escape, the depth-2 drain-EC partition
(SIGSEGV vs refused), the zombie contact handles, and the livelock/convergence
pair. Insertion-only, fatal/corrupt rows last, classifier extended only where a
measured class requires it, every gate fail-closed, rc persisted.

---

## 1. What landed

| file | change | shape |
|---|---|---|
| `corpus/fixtures/love_phys_probe/main.lua` | **+479 / −0** | an r78 layer gated on `R78[CELL] ~= nil`: 17-cell registry, 9 nested/drain/capture acts, the inner-Step bracket observer, the r78 drain hook, the bounded abort emission, the r78 observation line |
| `corpus/fixtures/love_battery.py` | **+560 / −5** | 17 `IW_CELLS` rows (14 + 3 death rows), 7 new class branches, 2 extended existing members, the per-member death-site conjunct, docstring section |
| `reports/round-78/r78-author.md` | this report | — |

**Insertion-only is measured, not asserted.** `main.lua` is a pure insertion
(`+479/−0`); the five deleted lines in `love_battery.py` are **all inside
`iw_classify`** and are enumerated in §4.4 (three of them are the r77
`corrupt` death-site conjunct, one is the rc=−11 anomaly message, one is the
`iw_classify` docstring's closing line). No `IW_CELLS` row was moved or edited
— the 17 r78 rows are appended ahead of the process-death tail, and the three
r78 death rows join the tail.

`corpus/live/r78-author/drift_audit.py` compares the pre-change receipt set
(the r77 closeout run `corpus/live/runs/love-20261014T200810918691Z`, HEAD
bytes) against the final run:

```
prior iw receipts compared: 112
  byte-identical:            101
  main.lua:NNN-only diff:    11        (declared unpinned line tokens)
  semantic diff:             0
new receipts (no pre-image): 34        (17 cells x stdout+stderr)
```

The 11 token-only diffs are exactly the receipts that print a probe line
number (`main.lua:NNN` traceback frames and the r75/r76/r77 `srcline=NNN`
field); inserting 479 lines into the probe must move them. Named:
`bc_cowrap_unp`, `bc_coyield`, `bc_draindefer`, `bc_newbody_unp`,
`bc_setpos_unp`, `bc_setpos_wp`, `bc_worlddestroy`, `cowrap_update_yield`,
`ext_worldrelease`, `wp_coyield`, `wp_drain_throw`. `r78wpcall.srcline` is a
probe line number too and is **pinned nowhere**.

**Battery: 92/92 PASS ×4 consecutive on the final revision** — run dirs
`corpus/live/r78-author/runs/love-20261014T21{0544087564Z,0613696721Z,0635061798Z,0943322605Z}`
(15 `CASES` + 4 `SPLICE` + 73 `IW`: 56 prior + 17 r78). The intermediate
revision (before the insertion-only rework) also ran 92/92 three times
(`…T2100{16171220Z,25788543Z,47125716Z}`) and produces **byte-identical r78
receipts** (17/17 compared). One earlier run, `…T205937122136Z`, was **91/92**
and is kept as provenance: its single failure was the first, one-line attempt
at the `corrupt` death-site fix (§4.4) — an author-side gate bug, no engine
behaviour involved.

**Every r78 cell is byte-stable** across those four full runs (`runs_distinct=1`
for all 17) and across ×3 scratch reps (`corpus/live/r78-author/cells/{a1..a6,b1..b3}.*`,
`stable_bytes=true`). `rc` is persisted on every row (`results[*].rc`),
including `-11` and `1`.

**Sibling sanity (unaffected, measured):** pygame battery **80/80 PASS**
(`runs/pygame-20261014T210706706131Z`, final revision) and the Godot-2D battery
`run_battery.py` **88/88 PASS** (`runs/20261014T210716859565Z`, final revision;
both also run once on the intermediate revision). Neither shares a file with
this arm.

---

## 2. The seven classes that landed (and the two extended members)

| class | members | decisive witness set (gate) |
|---|---|---|
| `nested_lockclear` | `n_baseline`, `n_inner_cb`, `n_depth2_seq` | nested update returns `lock_after=false` **and** the inner Step's callback ran `locked=true` with a refused inner write **and** the post-nest write APPLIED (`ok=true err=nil pos_after=1234.5,678.9…`) |
| `inner_drain` | `n_queue_inner_drain` | the drain EC carries `depth=1 in_cb=true locked=false` **and** the nested update returned `lock_after=false` **and** the queued body was alive in-cb but dead after the nest with `count == built.bodies − 1` |
| `dispatch_escape` | `n_destroy_contacting_wp`, `n_destroy_ground_wp`, `n_destroy_fx_wp` (contained, rc=0); `n_destroy_contacting` (uncontained, rc=1) | nested `lock_after=false` **and** `r78wpcall.err` contains `escaped Memoizer` with `srcline=nil`, `locked_after=false` **and** the in-cb destroy `ok=true dead=true` **and** **no** collateral lock refusal (`"assertion" not in wpext.err`) **and** recovery `locked_after=false`; uncontained: rc≠0, `postfire.step` present, the same nested-destroy witness |
| `refused` (r78 member) | `n_depth2_fxdrain` | drain-EC nest with `nest1.ok=false`, `err == "Box2D assertion failed: found"`, `drainec.depth=0 in_cb=false` |
| `contact_invalidated` | `z_drain_use_after` (drain), `z_touch_then_end` (natural end) | the post probe errors `Attempt to use destroyed contact.` on every accessor (`touch/fix_ok/ch_ok/fric_ok/pos_ok` all dead) while the contact's fixtures stay alive (`fxa=false`, `fxa_body=g`) |
| `contact_live_after_abort` | `z_abort_use_after` | the SAME handle reads live at the abort step (`touch/fix_ok/ch_ok/fric_ok/pos_ok` all true, fixtures alive) and is invalidated only after the retry completes (`r78zlate` errors) |
| `livelock` | `livelock_all` | `aborts == drain_n == steps − fire_step + 1` (197 at 200 steps), nothing destroyed, the abort signature (`locked_after=false`, no collateral refusal) |
| `drain_converge` | `livelock_stop2` (abort budget), `livelock_transient` (contact lifetime) | `aborts ≥ 1`, `drain_n ≤ aborts + 1`, `aborts <` the step-budget rate, `count == built.bodies − 1` |
| `corrupt` (r78 member) | `n_depth2_drain`, `n_depth2_drain_wp` | rc=−11, `postfire.step` ABSENT, drain-EC nest at `drainec.n=2 depth=2 in_cb=true`, the depth-2 nest returned `ok=true lock_after=false depth=2 in_cb=true` |

---

## 3. The brief's six arms, measured

### 3.1 Nested lock-clear — `setPosition` applies, `destroy()` executes immediately

`n_baseline` / `n_inner_cb` / `n_depth2_seq` pin `pos_after=1234.5,678.9000244140625`
(the write the lock refused inside the callback applies the moment the nested
Step returns) **and** the inner-Step bracket as the contrast:

```
r78inner cb=pre step=73 locked=true depth=1 dyn=b1
r78inner_write ok=false err=Box2D assertion failed: m_world->IsLocked() == false
r78nest1 ok=true err=nil lock_after=false count=4 depth=1 in_cb=true
r78setpos ok=true err=nil pos_after=1234.5,678.9000244140625
```

The `target_dead mid-callback` witness comes from the destroy arms — inside the
outer callback, after the nest, `r78destroy what=b1 ok=true err=nil dead=true
count=3` (body) / `what=g … dead=true count=3` (static side) / `what=fx …
dead=true fcount_before=1 fcount_after=0 count=4` (fixture). Contrast with the
tracked `deferred` class (`iw_bc_destroy`: `alive_in_cb=400,520.15…`,
`count_after=4`): same call, lock state decides.

`n_depth2_seq` pins that two **sequential** nests are contained, each at
`depth=1` (`r78nest2.depth=1`) — the corruption is the drain-EC nest, not depth
2 as such.

### 3.2 Inner-drain ownership — the inner epilogue drains the outer queue

```
r78queue what=b3 ok=true err=nil dead_in_cb=false count=4
r78drainec n=1 step=73 locked=false depth=1 in_cb=true count=4 dyn=b3
r78destroy what=b3 dead=true count=3 drain_n=1      <- dead BEFORE the outer cb returns
postfire cb=bc step=73 count=3 drain_n=1
final steps=200 count=3 … drain_n=1 aborts=0
```

The drain EC carries `depth=1 in_cb=true` → it was dispatched inside the nested
update's own epilogue while the outer callback was on the stack, and the run
survives to step 200.

### 3.3 Depth-2 from the drain EC — the partition (corrupt vs refused)

Body-drain (`n_depth2_drain`, and its `_wp` twin): **rc=−11, partial receipt,
no CELL_DONE, stderr 0 B**; the last line on the pipe is the depth-2 nest's own
receipt, emitted before the death:

```
r78drainec n=2 step=73 locked=false depth=2 in_cb=true count=4 dyn=b3
r78nest2 ok=true err=nil lock_after=false count=3 depth=2 in_cb=true
```

The `_wp` receipt is **identical modulo the cell name** — a signal is not
containable by `pcall`, which is the point of arming both. Fixture-drain
(`n_depth2_fxdrain`) is the catchable member: `r78nest1 ok=false
err=Box2D assertion failed: found lock_after=false depth=1 in_cb=false`, rc=0,
the run reaches step 200 with `b1pos=400,647.3021240234375`.

**Brief-vs-measurement correction (recorded, not silently smoothed):** the brief
calls the fixture member "REFUSED (ok=false, **Box2D lock assertion**)". The
measured text is `Box2D assertion failed: found` — `b2Body::DestroyFixture`'s
`b2Assert(found)` (`Box2D/Dynamics/b2Body.cpp:241`), not the `IsLocked()` guard
that the r74 `refused` member carries. The class is `refused` (the catchable
Box2D-assertion family) and the text is pinned per row; `iw_classify`'s
docstring now names both members.

### 3.4 Contacting-destroy escape — three sites, two containment levels

Contained (all three, rc=0, recovery to step 200, `aborts=1`):

| cell | destroyed | extra witnesses |
|---|---|---|
| `n_destroy_contacting_wp` | `b1` (the contacting body) | `r78wpext ok=false err=Attempt to use destroyed body.` (lifetime guard, not a lock) ; final `bc=8 ec=6 pre=67 post=67` |
| `n_destroy_ground_wp` | `g` (static side) | **two** drain ECs (`n=2`, `dyn=b3`) ; `r78wpext ok=true pos_after=999,999` (no collateral refusal) ; final `bc=2 ec=2 pre=33 post=33` |
| `n_destroy_fx_wp` | the contacting fixture | `fcount 1→0` in-cb, body alive, `count=4` ; `r78wpext ok=true pos_after=999,999` ; final census unchanged `bc=4 ec=3 pre=36 post=36` |

All three carry the same escape: `r78wpcall n=1 step=73 update_ok=false
err=A fixture has escaped Memoizer! srcline=nil locked_after=false`. That is
**not** the r75/r76 `refused_abort` signature (no assert text on the escape
path, `locked_after=false`, no collateral lock refusal). Uncontained
(`n_destroy_contacting`): rc=1, stderr 0 B, `esc_fn=update`, no CELL_DONE —
a love `Exception` from a contact dispatch, classed `dispatch_escape`, not
`fatal` (the assert text in its stdout belongs to the inner-Step bracket line,
which is why `err_on`/`assert_txt` are unpinned for that row).

### 3.5 Zombie contact handles — two regimes, one control

```
z_drain_use_after   r78zpost touch=ERR:Attempt to use destroyed contact. fix_ok=false ch_ok=false fric_ok=false pos_ok=false
                    r78zpost fxa=false fxb=true fxa_body=g          <- fixtures stay alive
z_abort_use_after   r78zsame touch=true fix_ok=true fa=g fb=b3 ch_ok=true ca=1 cb=1 fric_ok=true pos_ok=true
                    r78zlate touch=ERR:Attempt to use destroyed contact. fix_ok=false
z_touch_then_end    r78zend  touch=ERR:Attempt to use destroyed contact. fix_ok=false fxa=false fxa_body=g
```

The abort unwinds out of `b2ContactManager::Destroy` after the `EndContact`
dispatch and before the unlink, so `Contact::invalidate()` never runs and the
handle stays fully usable for one step; the natural-end and clean-drain
controls show the invalidated regime.

### 3.6 Livelock vs convergence

| cell | steps | drain_n | aborts | final count | shape |
|---|---|---|---|---|---|
| `livelock_all` | 200 | **197** | **197** | 4 (b3 alive) | one drain EC + one abort per subsequent step, last entry AT step 200 |
| `livelock_stop2` | 200 | **3** | 2 | 3 (b3 dead) | abort budget exhausted at entry 3 → the destroy completes there, recovery at step 6 |
| `livelock_transient` | 200 | 1 | 1 | 3 (b1 dead) | the retry finds no touching contact → no drain EC at all → silent completion at step 74 |

The brief's named numbers are confirmed exactly (`drain_n=3` converges;
`drain_n=197=aborts` for the every-entry abort). The pair also pins the bound
*shape*: linear in the caller's step budget with no internal counter
(`livelock_all`), and the contact's lifetime as the real bound
(`livelock_transient`). `ec` inflates with the aborts (199 at 197 aborts) — a
livelocked run must not be read with an `ec ≈ bc` witness set.

---

## 4. Classifier

### 4.1 New branches and precedence

Seven new branches are inserted **after** the r77 branches and **before** the
pre-r77 gates (`wpcall.update_ok`, `cb_retfalse`, the `mut` scan), so no r78
receipt can satisfy an earlier gate and no prior receipt can reach an r78 branch
(structurally impossible: the `r78*` tags do not exist in pre-r78 receipts — the
56 prior rows classify exactly as before, measured by the 92/92 runs and the
drift audit). Two precedences are documented in the code rather than left
incidental: `inner_drain` before `nested_lockclear` (a cell can show both; the
drain ownership is the more specific shape), and the zombie branch before the
livelock branch (both carry an abort count).

Two branches are **extended existing members**, gated on the r78-only keys:

- `refused` gains the fixture-drain nested-update member (§3.3);
- `corrupt` gains the depth-2 body-drain member — its witness set is disjoint
  from the release member's and each is required in full.

### 4.2 Fail-closed, measured

`corpus/live/r78-author/ablate_gates.py` deletes each decisive line (or flips a
negative conjunct) from the measured receipt and re-runs **the battery's own row
gate** (class + every pinned key): **37/37 ablations make the row FAIL, 0 leaks,
0 absent tags, 0 base mismatches.** The two layers are both load-bearing: e.g.
dropping `r78drainec` from `livelock_all` leaves the class at `livelock` but
fails the row on `r78drainec.n: key missing`; dropping `r78nest2` flips
`n_depth2_drain` to `anomaly`; flipping the "no collateral lock refusal"
conjunct on `n_destroy_contacting_wp` (`wpext.err` → the IsLocked assert) flips
it to `anomaly`.

### 4.3 Classifier changes beyond new branches (all in `iw_classify`)

The only edits to pre-existing classifier code are the five deleted lines
enumerated below. They are **predicate corrections the new members required**,
not behaviour changes for any prior row (measured: 92/92, drift audit, ablation).

### 4.4 The five deleted lines (exhaustive)

1–3. The r77 `corrupt` branch's condition

```python
        if ("fire.step" in flat and "postfire" not in flat
                and ("rel_alive.marker" in flat
                     or "drainrel.alive" in flat)):
```

is replaced by the **per-member** death-site form

```python
        if ("fire.step" in flat
                and (("rel_post.marker" in flat and "postfire.step" not in flat)
                     or ("drainrel.alive" in flat and "postfire.step" in flat))):
```

**Why (found defect):** the r77 fold's D2 conjunct `"postfire" not in flat`
tested a key `parse_iw` never emits — every flat key is `<tag>.<key>` — so it
was **vacuously true for every receipt**; and it cannot simply be tightened,
because the drain-release member dies **after** `postfire` (the callback
completes, then the epilogue hook releases). The per-member form is
non-vacuous and ablation-verified: deleting `rel_post` or `postfire` now flips
the respective row to `anomaly` (both ablated). This is a prior-round gate
defect this seat found and closed; it is the reason the intermediate run was
91/92 (the one-line variant broke `iw_drain_worldrelease`, kept as provenance).

4. The rc=−11 anomaly message `"rc=-11 without a release witness"` →
`"rc=-11 without a release or nested-drain witness"` (accurate for both
members).

5. The `iw_classify` docstring's closing line — the class list and the
member notes were appended inside the docstring.

---

## 5. Evidence index

All under `corpus/live/r78-author/` unless noted.

| artefact | content |
|---|---|
| `runs/love-20261014T21{0544087564Z,0613696721Z,0635061798Z,0943322605Z}` | the four consecutive **92/92** runs on the final revision (`iw-*.stdout.txt` + `verdicts.json`) |
| `runs/love-20261014T2100{16171220Z,25788543Z,47125716Z}` | 92/92 on the intermediate revision (pre insertion-only rework); r78 receipts byte-identical to the final |
| `runs/love-20261014T205937122136Z` | the **91/92** intermediate (provenance for the death-site fix) |
| `runs/pygame-20261014T210706706131Z` | pygame sanity **80/80** (final revision); `…T210211318403Z` on the intermediate |
| `runs/20261014T210716859565Z`, `…T210232724737Z` | Godot-2D `run_battery.py` **88/88** (final / intermediate) |
| `cells/{a1..a6,b1..b3}.*` | scratch receipts: 17 r78 cells × 3 reps, `stable_bytes=true` for every cell, one fresh process per (cell, rep) |
| `run_cells.py` | scratch runner (imports the LIVE tracked `parse_iw`/`iw_flat_extras`/`iw_classify`) |
| `drift_audit.py` + `drift_audit.json` | insertion-only audit (identical / line-token-only / semantic) |
| `ablate_gates.py` + `ablation.json` | 37-ablation fail-closed matrix over the new and extended gates |
| `notes.md` | incidents (wrong `capture_throw` arming, missing ground userdata, the vacuous conjunct, the rework) — provenance, not measurements |

Tracked-file hashes (HEAD bytes → this seat's bytes):

| file | HEAD | now |
|---|---|---|
| `corpus/fixtures/love_battery.py` | `82986759243fff639696095c61933eab135b8f325f8d46223e4fc86c8540221b` | `ea70c42c5e1c54444de56a10c680c547c9044dbb590dc2d17c700d0ce4573458` |
| `corpus/fixtures/love_phys_probe/main.lua` | `a186053b124dd9c3191381948dedf26138979f1d1901481057812cdfc4802925` | `75eb18d2ffce0ef39b8a52cfe365de6de3898d9a60c20ca88765c94ec03f9d96` |
| `corpus/fixtures/love_phys_probe/conf.lua` | `85aa6232741ea3eaa86e73d3280701d4b0a870f416bfb071558e61cc9a73576b` | unchanged |

`luac -p` clean on every revision; `python3 -c "ast.parse(...)"` clean.

---

## 6. Deliberately NOT armed (scope boundary, named)

The scout measured 31 cells; the brief's arm list is six bullets. These remain
scout-measured and **unarmed** — listed so the next round inherits them as
frontier, not as gaps:

- the drain-bracket cells (`bracket_body`, `bracket_fixture`,
  `bracket_two_contacts`) — §3 of the scout report; a joint + observer layer
  the brief did not assign;
- the exterior release/destroy lattices (`rel_lattice_load`,
  `rel_lattice_post`, `dz_lattice_load`) — §4; the r77 arm already pins the
  exterior-release `died` control;
- the **non-touching zombie hole** (`z_nontouch`, `z_nontouch_alias`) — §5.1,
  the scout's silent-UAF + block-reuse finding. It needs a step-driven scene
  protocol (contact scan at step 2, separation, aliased reallocation at step 3)
  that no bullet in the brief assigns;
- `n_noop` (the "a no-write nest is not a no-op" control: +14 px, +2 pre/post),
  `x_destroy_b1_post` (the census control), `livelock_all_400`, and the
  uncontained ground/fixture escape twins (`n_destroy_ground`,
  `n_destroy_fx`).

---

## 7. Honest limits, residual risks, blockers

- **No independent reproduction by another seat.** The r78 scout's delegated
  labrat had no execution tool and returned NOT-RUN for all three hypotheses;
  every number here is this seat's own fresh-process measurement (×3 reps, ×3
  consecutive full runs, byte-stable).
- **The crashing frame of the depth-2 SIGSEGV is still inferred, not observed**
  (no core/gdb): the measured bound is "the depth-2 nested update returns and
  its receipt is flushed, then the process dies before any further Lua frame".
  The re-entrant `destructBodies.clear()` while the outer drain loop iterates is
  source-anchored inference (`World.cpp:272-300`).
- **`assert_txt` / `err_on` are non-decisive for r78 rows** (the inner-Step
  bracket legitimately puts `Box2D assertion failed: m_world->IsLocked() ==
  false` on stdout in every nested cell), so they are unpinned for those rows;
  the r78 escape/death rows are witnessed by their own keys plus `esc_fn`.
- **`r78wpcall.srcline` is a probe line number** and is pinned nowhere — same
  class as the 11 declared-unpinned `main.lua:NNN` drifts.
- **Receipt size:** `livelock_all` emits one `r78drainec` line per entry
  (~197 lines; ~400 lines total) by design — the per-entry `step` is the rate
  witness. The abort lines are bounded to the first two plus a running count.
- **Unmeasured here:** virtual-call UAF on a zombie contact handle (not
  reachable through the love 11.5 `Contact` API surface); nested updates in
  channels other than `beginContact` (the r78 cells fire on `bc` only); nesting
  deeper than 2 from a drain EC; why the contained escape inflates the solver
  census (`pre/post 67` vs the exterior control's 35 — measured, mechanism
  open); the non-touching hole under a GC'd world.
- **Bounded:** LOVE 11.5, LuaJIT 2.1.1788460057, this host, these scenes; no
  claim about other builds, backends, or the g3d arm.
- **Blockers: none.** No resume/continuity preflight was needed (no resume
  mutation was made); no commit, push, or deploy was performed; the arm leaves
  the shipping decision to the operator/integrator.
