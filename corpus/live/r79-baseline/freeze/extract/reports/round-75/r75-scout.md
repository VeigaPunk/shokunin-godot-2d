# game-dev-2d round 75 — scout (g2d): pre-measurement of the deferred cells

Seat: scout (LEAF) | Lane: g2d | Round: 75 | Wave `shokunin-train-20261101-w15`.
Host: devin. Runtime **LOVE 11.5** (Arch `love 11.5-3`, `/usr/bin/love`,
`liblove-11.5.so`), LuaJIT 2.1.1788460057, Python 3.14.7.
Repo `~/Projects/shokunin/game-dev-2d-shokunin`, HEAD `2a2c337` when this seat
started (fixture tree clean there).
**No git mutation, no subagent, no tracked file touched** — scratch
`corpus/live/r75-scout/` + this report only.

Assignment: pre-measure, *before* the author pins them, (1) the real classes of
`bc_destroy_unp`/`bc_setvel_unp`, (2) the pcall-containment-level partition,
(3) joint-callback behaviour availability under LOVE 11.5. Falsify the predicted
classes honestly.

**`lsp` disclosure:** no `lsp` device is exposed in this session, and no
Lua/Python language server is installed (`lua-language-server`, `sumneko-…`,
`pylsp`, `pyright`, `jedi-language-server` all ABSENT; only `clangd` exists, and
LOVE's C++ source is not on disk — no `/usr/include/love*`, no `/usr/share/love`).
`grep`/`strings` are used below as **literal** evidence only (string presence in
the installed `.so`), never as semantic proof; every behavioural claim is a
runtime receipt.

## 0. What I ran

| # | command (cwd = repo root) | exit | receipt |
|---|---|---|---|
| 1 | `PYTHONDONTWRITEBYTECODE=1 python3 -B corpus/live/r75-scout/run_cells.py --probe corpus/live/r75-scout/probe_level --tag ctrl --cells baseline,bc_destroy,bc_setvel,pre_contactmask,ext_destroy,bc_setpos_unp --reps 2` | 0 | `cells/ctrl.*` — 12/12 receipts **byte-identical** to the frozen r74 author run `corpus/live/r74-author/runs/love-20261014T163734563743Z/iw-*.stdout.txt` |
| 2 | same runner, `--tag ctrl2` (post-patch control) | 0 | `cells/ctrl2.*` — same byte-identity (fatal receipt differs only in the probe line number inside `Error: main.lua:NN:`) |
| 3 | `… --tag unp0 --cells bc_destroy_unp,bc_setvel_unp,bc_setactive_unp --reps 3` | 0 | `cells/unp0.*` (§1) |
| 4 | `… --tag lvl1 --wp 1 --cells bc_setpos_unp,bc_newbody_unp,bc_setactive_unp,bc_destroy_unp,bc_setvel_unp,bc_setpos,bc_destroy,bc_setvel,pre_contactmask --reps 3` | 0 | `cells/lvl1.*` (§2) |
| 5 | `… --tag pre75 --cells bc_setfilter --reps 3` | 0 | `cells/pre75.bc_setfilter.*` (§4) |
| 6 | `… --probe …/probe_joint --tag j0..j9 --cells <joint/filter/retfalse/avail surface> --reps 2-3` | 0 | `cells/j*.*` (§3, §4) |
| 7 | `PYTHONDONTWRITEBYTECODE=1 python3 -B corpus/live/r75-scout/consolidate.py` | 0 | `classes.json` — 51 rows, 25 scout-rule-labelled, every row `stable_bytes=true` |
| 8 | `strings -a /usr/lib/liblove-11.5.so \| grep -E …` | 0 | literal string presence only: `m_world->IsLocked() == false` (14128), `p == entry->data` (14479), `newRevoluteJoint`/`newWeldJoint`/`setFilterData`/… all present |

Every cell in every run: **byte-identical stdout across reps** (3 reps where
fatal/near-fatal cells are involved). `classes.json` is the machine-readable
table; this report is its reading.

## 1. The deferred cells' real classes — prediction confirmed, and *stronger*

Predicted: `bc_destroy_unp` -> deferred, `bc_setvel_unp` -> applied. Measured
(`probe_level`, `IW_WP` unset, 3 reps, byte-stable; class = the **tracked**
`iw_classify`):

| cell | rc | CELL_DONE | class | decisive receipt fields |
|---|---|---|---|---|
| `bc_destroy_unp` | 0 | yes | **deferred** | `cb_destroy ok=true err=nil alive_in_cb=400,520.1500244140625 count_after=4`; `evpin ec locked=false step=73`; `after_update count=3 b1pos=ERR:Attempt to use destroyed body.` |
| `bc_setvel_unp` | 0 | yes | **applied** | `cb_setvel ok=true err=nil vel_after=55,-7`; `after_update b1pos=400.78515625,519.7547607421875 b1vel=55,-7` |
| `bc_setactive_unp` (bonus, the boundary twin) | 1 | no | **fatal** | `Error: … Box2D assertion failed: m_world->IsLocked() == false`, `esc_fn=setActive`, stderr **0 bytes** |

The prediction is confirmed, and the inertness of the containment dimension for
these two classes is not merely "same class" but **same bytes**: after
normalising the `cell=` field, `unp0.bc_destroy_unp.r1.stdout.txt` differs from
the landed `iw-bc_destroy.stdout.txt` in **one line only** — `kind=destroy` ->
`kind=destroy_unp` inside the fire line (identical for `setvel`). So
`fatal ⟺ assert-gated write × uncontained` is now measured at the receipt-byte
level, not inferred, and `setActive` is confirmed as the third assert-gated
class (fatal twin `esc_fn=setActive`).

Encoding note for the author (C1 correction 2): the uncontained cells emit the
**landed** `cb_destroy`/`cb_setvel` tags, so the tracked classifier's hard-coded
tag list needs no edit — proven by these rows classifying `deferred`/`applied`
under the unmodified `iw_classify`. `ok=true`/`err=nil` on an uncontained cell
are encoded by **reachability** (the line only prints if the call returned), not
by a pcall result; that is sound but should be stated in the probe comment.

## 2. Containment-level partition (critic C3) — level grid, and one falsification

Three levels, same scene, same write: **L0** no pcall (landed `*_unp`),
**L1** `pcall(world.update, world, dt)` only (`IW_WP=1`), **L2** pcall inside the
callback (the landed arm). `lvl1` receipts, 3 reps, byte-stable:

| cell | level | class (tracked) | `wpcall.update_ok` | `wpcall.locked_after` | `after_update.b1vel` | `wpcall_next` |
|---|---|---|---|---|---|---|
| `bc_setpos_unp` | L1 | **`anomaly`** (no class exists) | false | true | `0,763.8724365234375` (no impulse) | `step=74 update_ok=true locked_after=false b1pos=400,509.53021240234375` |
| `bc_newbody_unp` | L1 | `anomaly` | false | true | `0,763.8724365234375` | same |
| `bc_setactive_unp` | L1 | `anomaly` | false | true | `0,763.8724365234375` | same |
| `bc_destroy_unp` | L1 | **deferred** | true | false | `ERR:…` | n/a |
| `bc_setvel_unp` | L1 | **applied** | true | false | `55,-7` | n/a |
| `bc_setpos` (contained) | L2 | refused | true | false | `0,-611.09796142578125` (impulse) | n/a |
| `bc_destroy` (contained) | L2 | deferred | true | false | `ERR:…` | n/a |
| `bc_setvel` (contained) | L2 | applied | true | false | `55,-7` | n/a |
| `pre_contactmask` (contained) | L2 | applied | true | false | `0,763.8724365234375` | n/a |

Observed facts, all from the receipts:

1. **L1 shape for assert-gated writes**: the write is still refused (position
   unchanged) **and the step aborts** — `after_update` at the fire step shows the
   pre-integration pose `400,520.1500244140625` and the un-consumed contact
   velocity `0,763.8724365234375`, versus `400,511.13113403320312` /
   `0,-611.09796142578125` for the L2 twin. The world is **transiently locked**:
   a legal exterior `b1:setPosition(999,999)` attempted on the aborted step is
   refused with `Box2D assertion failed: m_world->IsLocked() == false` and
   `pos_after=400,520.1500244140625` (unchanged). Recovery is at the next
   update: `wpcall_next step=74 update_ok=true locked_after=false b1pos=400,509.53021240234375`.
   Callback counts shift: `final … bc=5 ec=4 pre=37 post=37` (L1) vs
   `pre=36 post=36` (L2 twin). This reproduces r74-critic C3's `m_wp` receipt
   value-for-value (including `400,509.53021240234375`) from an independent
   probe.
2. **Falsification (the load-bearing one): the level dimension is inert for the
   non-throwing classes.** `bc_destroy_unp` and `bc_setvel_unp` classify
   `deferred`/`applied` at L1 exactly as at L0 — there is no error to catch, so
   moving the boundary up changes nothing (`wpcall.update_ok=true` on every
   step). `pre_contactmask` likewise stays `applied`. So the partition is
   2-dimensional but **sparse**: only assert-gated writes have an L1 shape.
   Prediction "containment level changes the class" is true only for the
   assert-gated subset.
3. **Innermost boundary wins.** With both levels present (contained kind under
   `IW_WP=1`) the callback-level pcall catches first: `update_ok=true`, class
   unchanged, receipt identical to the landed one except for the added `wpcall`
   lines. There is no "double containment" third shape.
4. **Classifier gap (actionable).** Under the landed `iw_classify` an L1 receipt
   that does not emit a `cb_*` mutation line returns **`anomaly`** ("CELL_DONE
   but no mutation line") — i.e. a measured, reproducible, byte-stable L1 shape
   has *no bucket*. If the L1 cell instead re-emits the landed tag
   (`cb_setpos ok=false …`) the same receipt classifies **`refused`** — which is
   exactly the C3 collision (an aborted step passing as a plain refusal).
   Correction options, both cheap: (a) a new class (`refused_abort`) keyed on
   `wpcall.update_ok=false` + `wpcall.locked_after=true` + `wpcall_next.update_ok=true`;
   or (b) pins only, with the class left as the L2 one and the abort carried by
   pins. (a) is the honest one; my `post_at_fire`-style witnesses are not needed
   for it.
5. **Receipt-shape caution.** My scratch probe emitted one `wpcall` line per
   step (200 lines/cell); that bloats the receipt and pushes unrelated pins far
   apart. The author's in-flight probe emits the `wpcall`/`wpcall_next` witnesses
   only on the abort and the recovery step — the right shape; this scout's
   §2 numbers were re-checked against that shape (see §5).

## 3. Joint-callback surface under LOVE 11.5 — availability first, then gating

### 3a. Availability (measured `type()`, `probe_joint` `avail_physics` / `bc_contactapi`, byte-stable ×2)

Present on this build: `love.physics.newRevoluteJoint | newPrismaticJoint |
newDistanceJoint | newWeldJoint | newFrictionJoint | newRopeJoint | newMotorJoint
| newGearJoint | newPulleyJoint`; `World:getJointCount | getJoints |
setContactFilter | queryBoundingBox | rayCast | isLocked`; `Body:getJointList |
getContactList | setTransform | applyForce | applyLinearImpulse | setAwake |
setType`; `Fixture:setFilterData | getFilterData | setCategory | getCategory |
setMask | getMask | setGroupIndex | getGroupIndex | setSensor | setDensity |
rayCast`; `Joint:destroy | setMotorSpeed | setMotorEnabled | setMaxMotorTorque |
setLimits | getReactionForce | getBodies | getType | setUserData`; `Contact:setEnabled
| isEnabled | isTouching | setFriction | setRestitution | getNormal | getPositions
| getFixtures | getChildren | getTangentSpeed | setTangentSpeed`.

**Absent (nil) — record as blocked, never "measured negative"**:
`Fixture:isTouching`, `Joint:setCollideConnected`, `Contact:getNormalImpulses`.
The last one is the reason the postSolve impulse cannot be read back from the
contact on this build; the impulse witness must come from the body velocity.

`Fixture:getMask()` is **not** a usable readback witness on this build:
`filterpre category=1 mask=nil group=0 mask_n=0` (returns **zero** values before
any filter write) while after `setMask(4)` it returns one value (`4`). Use
`getFilterData()`, which returns **3** values (`1, 65535, 0` at load).

`Fixture:setFilterData` signature on this build is **three numbers**
(`setFilterData(2,4,0)` -> ok, readback `2,4,0`); the table form errors
`bad argument #2 to '?' (number expected, got table)` — a plain Lua argument
error, i.e. **not** a `refused` shape (it classifies `anomaly`). `setCategory` /
`setMask` / `setGroupIndex` all work.

### 3b. Gating (all cells byte-stable across reps; scout-rule labels, flagged `scout_rule` in `classes.json`)

| cell | write | class | decisive receipt fields |
|---|---|---|---|
| `bc_jointcreate` | `newRevoluteJoint` in beginContact, pcall'd | **refused** | `ok=false err=Box2D assertion failed: IsLocked() == false` (**world-level** text, no `m_world->` prefix), `jcount_after=1`, step completes (`after_update b1vel=0,-611.09796142578125`) |
| `bc_jointcreate_unp` | same, uncontained | **fatal** | rc=1, `CELL_DONE` absent, `Error: … Box2D assertion failed: IsLocked() == false`, **`esc_fn=newRevoluteJoint`**, stderr 0 bytes |
| `bc_jointdestroy` | `joint:destroy()` in beginContact, pcall'd | **deferred** | in-callback `ok=true err=nil jtype_after=revolute isDestroyed_in_cb=false jcount_after=1`; after the update `joints=0`; `jdrain step=73 jcount=0 isDestroyed=true` |
| `ext_jointcreate` | joint create outside any callback | **applied** | `ok=true jtype=revolute jcount_after=2` |
| `ext_jointdestroy` | joint destroy outside any callback | **applied** | `ok=true err=nil jcount_after=0` (immediate) |
| `bc_jointsetmotor` | `setMotorSpeed(-9)` in beginContact | **applied** | `ok=true err=nil motor_after=-9` |
| `bc_jointsetlimits` | `setLimits(-0.5,0.5)` in beginContact | **applied** | `ok=true err=nil limits_after=-0.5` (`getLimits` returns 2 values; only the first is printed — pin both or neither) |
| `pre_filterdata` | `setFilterData(2,4,0)` in preSolve | **applied** | `ok=true err=nil category_after=2 mask_after=4 group_after=0`; effect witness `final b1pos=400,635.1639404296875` (y>540: b1 tunnels through the ground) |
| `pre_filterdata_tbl` | table form | **api_error** (not refused) | `ok=false err=bad argument #2 to '?' (number expected, got table)`, no Box2D assert |
| `pre_retfalse` / `bc_retfalse` | Lua `return false` from preSolve / beginContact | **ignored** | `retfalse cb=pre step=73 returned=false` **and** the full impulse lands: `after_update b1vel=0,-611.09796142578125`, `post_at_fire post_count=1` |
| `pre_contactmask` (in-scene control) | `contact:setEnabled(false)` in preSolve | **applied** | `isEnabled_after=false isTouching=true`; impulse suppressed `after_update b1vel=0,763.8724365234375`; **no `post_at_fire` line at all** (the disabled contact is skipped by the solver) |

So the joint surface gives one new member of each existing class (refused,
deferred, applied) plus one new death twin, and the joint-destroy deferral is
**not** the same shape as body-destroy deferral: the body drain is witnessed by
a synthesised `EndContact` at `locked=false` inside the update, while the joint
drain has **no locked witness** — only the count/`isDestroyed` pair
(`false`/`1` in-callback -> `true`/`0` after the update). The drain *point* is
therefore inferred, not witnessed (open gap, §7-1).

**Return-false is measured-absent as a mechanism**: `preSolve`'s Lua return is
not consumed on this build (Box2D's `PreSolve` is void and LOVE 11.5 does not
translate the return), whereas `contact:setEnabled(false)` is consumed. Two
independent witnesses in the same probe/scene: the impulse (`b1vel` −611.09 vs
+763.87) and the presence/absence of the `post_at_fire` line (postSolve runs for
a solved contact, is skipped for a disabled one). Any cell whose whole content is
"the return value gates the contact" is **blocked** on this build.

## 4. Cross-check against the author's in-flight arm (read once, read-only)

The author was landing `corpus/fixtures/love_battery.py` (+ the probe) while this
seat ran. Every r75 pin I can independently reach was re-measured; the table is
agreement, with the two `not-independently-verified` items named.

| author's row / pin | my independent measurement | verdict |
|---|---|---|
| `bc_setpos_wp` class `refused_abort`; `wpcall.step=73`, `update_ok=false`, `locked_after=true` | identical | **verified** |
| `wpcall.err` / `wp_setpos.err` = `Box2D assertion failed: m_world->IsLocked() == false` (prefix stripped) | raw text carries the probe line prefix (`main.lua:96:`); stripped form matches | **verified** (strip is required — an unstripped pin can never match) |
| `wp_setpos.ok=false`, `wp_setpos.pos_after=400,520.1500244140625` (collateral legal exterior write refused while locked) | `wpcall exterior_setpos ok=false err=Box2D assertion failed: m_world->IsLocked() == false pos_after=400,520.1500244140625` | **verified** |
| `wpcall_next.step=74`, `update_ok=true`, `locked_after=false`, `b1pos=400,509.53021240234375` | identical | **verified** |
| `final.pre=37`, `final.post=37` on the wp row | `final … bc=5 ec=4 pre=37 post=37` | **verified** |
| `bc_setfilter` class `applied`; `ok=true`, `err=nil`, `filter_after=2,2,0`, `after_update.b1vel=0,-611.09796142578125`, `final.b1pos=400,635.1639404296875`, `final.bc=4`, `final.ec=3` | reproduced in the tracked scene with the author's exact args (`pre75.bc_setfilter`) — every pinned key byte-equal | **verified** |
| `bc_joint_destroy` class `deferred`; `isDestroyed_in_cb=false`, `jcount_before=1`, `jcount_after=1`, `jdrain.step=73`, `jdrain.jcount=0`, `jdrain.isDestroyed=true` | identical (my twin: pre-built revolute joint, same in-callback/after-update pair) | **verified** |
| `bc_joint_new` class `refused`, world-level `IsLocked() == false`, `jcount_before=0`, `jcount_after=0` | same class + same assert text on the `newRevoluteJoint` twin (`jcount` differs only because my scene pre-builds a joint) | **verified** (class/assert), counts scene-specific |
| `bc_destroy_unp` deferred / `bc_setvel_unp` applied + all pinned keys | byte-identical to the landed contained twins modulo the `kind=` label | **verified** |
| `pre_retfalse` class `ignored`, `cb_retfalse.returned=false`, `after_update.b1vel=0,-611.09796142578125` | identical (my scene returns false only on the fire contact; the author's returns false for every contact) | **verified** |
| `pre_retfalse` `final.pre=36`, `final.post=36` | my joint-scene receipt shows the joint-scene counts (`pre=5 post=5`), so this pin is not reachable from my probe; it is consistent with "no effect on the contact history" | **not independently verified** (scene-specific) |
| `esc_fn` pins `setPosition` / `newBody` on the two landed unp rows, rule = first `in function '<name>'` frame | receipts carry three `[C]:` frames (`setPosition`, `update`, `xpcall`); the boot frames use `<…>` and never match, so first-quoted-wins is the correct rule and yields exactly `setPosition` / `newBody` | **verified** |

Two cautions that follow from the measurements, not from the author's text:

- **Never pin the raw `Error:` line.** It embeds the probe file's line number
  (`Error: main.lua:96: …`); my one inserted branch moved it from 91 to 96 while
  behaviour was unchanged. `assert_txt` + `esc_fn` (line-free) are the safe pins,
  which is what the landed rows do. The author's `srcline=` field is fine as an
  unpinned diagnostic — pinning it couples the row to the probe file's layout.
- **Keep new tag/key names dot-free.** `parse_iw`'s tag/`k=v` split is literal:
  a dotted key (`api physics.newBody=function`) parses as tag `api physics.` and
  key `physics..newBody`. Harmless for my availability dump, but it silently
  mangles dotted pins.

## 5. Optional strengthenings (cheap, additive, none required)

1. `post_at_fire post_count=<n>` at the fire step: an independent
   solver-visibility witness that distinguishes `ignored` from `applied`-with-mask
   (present for a solved contact, absent when `setEnabled(false)` skipped it).
   Measured working in `probe_joint`.
2. `isDestroyed_in_cb` + a joint-count read in a *later* callback of the same
   step would pin the joint drain *point* (currently inferred; §7-1).
3. `getLimits` returns two values — if the limits cell is pinned, pin the pair or
   a single explicit component, not `limits_after` (which silently shows only the
   first).

## 6. Evidence / provenance

- Scratch: `corpus/live/r75-scout/` — `probe_level/main.lua`
  `1f3ecf9b4ee10a129bbdfeef1b4ba8b669b651e69f0cc3d2a5ca5e3685423ef3`,
  `probe_joint/main.lua`
  `8a6f615695f36ab43e4155083d27b6543c19468e641ef8d1b67618b90853f278`,
  `probe_level/conf.lua` = `probe_joint/conf.lua` = the tracked conf
  `85aa6232741ea3eaa86e73d3280701d4b0a870f416bfb071558e61cc9a73576b`,
  `run_cells.py` `b178657ef27a58d33c304b36e3bf36db29a3e943f053b4113b1716b5934a9ab9`,
  `consolidate.py` `dade855b4750cbe6f6204eeaa8f500df90f29c640481ead5fb36cac509319cbb`,
  `classes.json` `124813a59cef252ab2b72d48f1c34fd5f19c7efa5b018dd34230b4cf00e7ba49`,
  `notes.md`. 275 files in `cells/` (130 stdout receipts, 15 run summaries).
- Controls are frozen artifacts: the landed r74 run
  `corpus/live/r74-author/runs/love-20261014T163734563743Z/` (its `iw-*` receipts
  are identical across all four of the author's run dirs, verified).
- Tracked fixture as read by this seat's `probe_level` copy:
  `corpus/fixtures/love_phys_probe/main.lua` `2c0ac378…` at copy time (== HEAD
  `2a2c337`); at report time the author's in-flight version is `c80e2ba3…`
  (`git status` ` M`), i.e. the working tree moved under this seat — expected, and
  why the controls are the frozen r74 receipts.
- Reproduce: `PYTHONDONTWRITEBYTECODE=1 python3 -B corpus/live/r75-scout/run_cells.py
  --probe corpus/live/r75-scout/probe_level --tag <t> --cells <c,…> --reps 3`
  (add `--wp 1` for the L1 level), then `python3 -B
  corpus/live/r75-scout/consolidate.py`.
- This seat's only additions are `corpus/live/r75-scout/` and
  `reports/round-75/r75-scout.md`; `git status` shows no tracked file modified by
  it (the two `corpus/live/r72-simplifier/*` modifications predate the session).

## 7. Bounded claims / remaining unknowns

- All claims are for **this host**: LOVE 11.5 (`Mysterious Mysteries`, Arch
  `love 11.5-3`), LuaJIT 2.1.1788460057. The exact poses
  (`400,520.1500244140625`, `400,511.13113403320312`, `400,509.53021240234375`,
  fire step 73, callback counts) are this-build values; the **classes and the
  level-relative shapes** are the load-bearing assertions.
- **Not measured / open:**
  1. the joint-destroy drain *point* (no locked witness exists for it — inferred
     from the count/`isDestroyed` pair, unlike the body-destroy drain which has a
     synthesised `EndContact` at `locked=false`);
  2. L1 shape for classes other than the five sampled writes (e.g. a joint or
     filter write escaping to the update level) — `bc_jointcreate`/`setfilter`
     were only measured at L2;
  3. whether the L1 abort's transient lock affects a *later* callback in the same
     step (my collateral witness is the post-abort exterior write, not an
     in-step callback read);
  4. `pre_retfalse` with an unconditional `return false` for every contact (the
     author's shape) was not re-run here — only the fire-contact-only variant;
  5. whether a Lua-level `error()` thrown from a callback has the same L1 shape
     (r74-boundary measured `update_ok=false` for it; not re-measured here);
  6. the `getMask()` zero-return-at-load behaviour's mechanism (observed
     fact; the cache-vs-read explanation is inference and was not traced).
