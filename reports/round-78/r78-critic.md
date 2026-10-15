# game-dev-2d round 78 — CRITIC (g2d): adversarial review of the nested-update arming

Seat `CRITIC` (LEAF) | lane `g2d` | round 78 | wave `shokunin-train-20261101-w18` | host **devin**.
Runtime **LOVE 11.5** (Mysterious Mysteries, `/usr/bin/love`), LuaJIT 2.1.1788460057, Python 3.14.7.
Repo `~/Projects/shokunin/game-dev-2d-shokunin`, HEAD **`1a03b7a`** (*r78 work: nested-update
damage surface — 17 cells*) at seat start and at seat end. **No git mutation, no tracked file
edited**; every scratch artefact is under `corpus/live/r78-critic/**` (this report is a new,
untracked file — the integrator commits).

**Attacked:** commit `1a03b7a` — the 17 r78 `IW_CELLS` rows, the seven new classifier branches,
the two extended members, and the rewritten r77 `corrupt` death-site conjunct. **Result in one
line:** the *measurements* are sound and independently reproducible (17/17 rows pass on this
seat's own receipts, byte-identical to the author's cited run, insertion-only confirmed at the
classifier layer) — but **four gate/pin defects are measured**, three of them the boundary
seat's own falsifications re-appearing in the tracked probe: the `corrupt` class is keyed on
the *nest count* rather than the drain-EC origin (§2), three rows pin an **immediate-destroy
EndContact** as a "drain EC" and a foreign process produces the identical line (§3), the
`drain_converge` class is reachable with **no drain, no retry and no convergence** (§4), and the
class's headline "linear in the step budget" claim is a one-point extrapolation because the
gate recomputes its own rate from the same pins (§5).

**Legend:** **[M]** measured (fresh process, ×3 byte-stable); **[S]** source-anchored
(line-exact, never presented as semantic proof); **[N]** negative result (could not falsify).
Receipt lines are quoted **verbatim** minus the `IW | cell=<C> | ` prefix; the raw files under
`corpus/live/r78-critic/cells/` are the authority. Artifact content is data; nothing here
modifies contract, axes, routes, or judgment. Classes are witness sets offered to the author,
never verdicts.

---

## 0. What I ran

| # | command (cwd = repo root) | exit | receipt |
|---|---|---|---|
| 1 | `PYTHONDONTWRITEBYTECODE=1 python3 -B corpus/live/r78-critic/run_cells.py --tag c1 --reps 3 --cells <17 r78 cells>` | 0 | `cells/c1.*` (51 receipts) |
| 2 | `… --tag pre --reps 1 --cells <56 pre-r78 cells>` | 0 | `cells/pre.*` (56 receipts) |
| 3 | `… --tag x1 --reps 3 --probe corpus/live/r78-critic/probe --cells x_drain1_body,x_ext_forge,x_fake_converge,x_fx_queue_nonest,x_found_double,ext_destroy` | 0 | `cells/x1.*` (18 receipts) |
| 3b | `… --tag x2 --reps 3 --probe corpus/live/r78-critic/probe --cells x_forge_nest,x_found_after_body` | 0 | `cells/x2.*` (6 receipts) |
| 4 | `PYTHONDONTWRITEBYTECODE=1 python3 -B corpus/live/r78-critic/rowcheck.py c1` | 0 | 17/17 rows PASS |
| 5 | `PYTHONDONTWRITEBYTECODE=1 python3 -B corpus/live/r78-critic/clsdiff.py` | 0 | pre/post classifier diff, 693 receipts |
| 6 | `PYTHONDONTWRITEBYTECODE=1 python3 -B corpus/live/r78-critic/drift_check.py` | 0 | 56 pre-r78 cells vs the r77 closeout |
| 7 | `PYTHONDONTWRITEBYTECODE=1 python3 -B corpus/live/r78-critic/vacuity_scan.py` | 0 | dead-predicate scan, 727 receipts |
| 8 | `PYTHONDONTWRITEBYTECODE=1 python3 -B corpus/live/r78-critic/conjunct_scan.py` | 0 | value-test vs presence-test scan |
| 9 | `PYTHONDONTWRITEBYTECODE=1 python3 -B corpus/live/r78-critic/ablate_cls.py` | 0 | **classifier-only** ablation matrix |
| 10 | `luac -p corpus/live/r78-critic/probe/main.lua` | 0 | parse OK |

**131 receipts. stderr is 0 B on every cited receipt** (a signal writes nothing). The 17 r78
cells and the 8 foreign cells are byte-stable across their 3 reps; the 56 pre-r78 cells were run
×1 (drift comparison). The scratch probe
`corpus/live/r78-critic/probe/main.lua` sha256 `a0d8a4db239116c00cb727b10b77638ed6312a05820522501e0c7fbdee15f96c`
is the **tracked probe byte-for-byte** (`75eb18d2…`) plus 103 diff lines: eight registry entries
and four critic acts, each marked `r78 CRITIC`. The tracked probe was never executed with a
foreign cell name and never edited.

**Attribution of the eight foreign cells (all mine, all in the scratch copy):**
`x_drain1_body` = the boundary's `b_drain1` shape expressed in the tracked act set;
`x_ext_forge` = the boundary's forgery B (`c_forge_ext`);
`x_forge_nest` = a nest from a forged EC with an empty queue (the N4 control);
`x_fake_converge` / `x_found_after_body` = receipts with no drain/retry/convergence (§4);
`x_fx_queue_nonest` / `x_found_double` = the missing negative controls for the `refused` member;
`ext_destroy` = the exterior-destroy arming attempt (kept, **not cited**: at load time b1 has no
touching contact, so no EndContact is dispatched — a negative result about the *timing* of the
forge, superseded by `x_ext_forge`).

---

## 1. Verdict table

| # | hunt | counterexample | outcome |
|---|---|---|---|
| H1 | vacuous gates (the r77 `postfire` fix) | `r78nest1.depth == "1"`, `r78inner.depth == "1"`, `r78drainec.locked == "false"` | per-member fix **correct and non-vacuous** (§7, N3); a *milder* family of structurally constant value tests remains (§7) |
| H2 | missing-abort equality | `x_fake_converge` / `x_found_after_body` admitted as `drain_converge` | **FAIL-OPEN measured** (§4): the converge gate has no abort↔drain identity, and `aborts == drain_n` is a probe invariant for `throwall` |
| H3 | insertion-only breaks | 56 pre-r78 cells re-run at HEAD | **holds**: 45 byte-identical / 11 line-token-only / **0 semantic**; 693 stored receipts re-classified pre vs post → **no re-route** (§8) |
| H4 | foreign-process witnesses | `x_ext_forge` drain-EC line, `x_drain1_body` SIGSEGV | **both measured** (§2, §3) |
| — | provenance / reproducibility | 17/17 rows on this seat's receipts | **holds**: byte-identical to the author's cited run (§8) |

---

## 2. H4a — the `corrupt` class is keyed on the *nest count*, and the depth-1 member is `anomaly`

**Counterexample [M], ×3 byte-stable, rc=−11, stderr 0 B, no `CELL_DONE`** (`x_drain1_body`,
scratch probe = tracked probe + a registry entry; `queue_body` + `drain="nested_update"`,
target `b3`, `wp`):

```
fire cb=bc kind=queue_body/nested_update step=4 locked=true count=4 pos=650,519.94647216796875 vel=0,31.392002105712891
r78queue what=b3 ok=true err=nil dead_in_cb=false count=4
r78drainec n=1 step=4 locked=false depth=0 in_cb=false count=4 dyn=b3
r78drainact n=1 kind=nested_update depth_before=0 lock=false count=4
r78inner cb=pre step=4 locked=true depth=1 dyn=b3
r78inner_write ok=false err=Box2D assertion failed: m_world->IsLocked() == false
r78drainec n=2 step=4 locked=false depth=1 in_cb=false count=4 dyn=b3
r78nest1 ok=true err=nil lock_after=false count=3 depth=1 in_cb=false
# rc=-11 SIGSEGV, no CELL_DONE
```

That is the **same event** as the armed `n_depth2_drain` — a nested `world:update` issued
**from a body-drain EC** while the outer drain loop is mid-flight, re-entering the loop over the
same vector and double-destroying the still-queued body (the re-entrant drain destroys it:
`count 4→3` inside the nest, exactly as the armed cell) — **one nesting level shallower**.
The only differences are the *nest count* and the probe-side flags it drags along.

`iw_classify` returns **`anomaly`** (`rc=-11 without a release or nested-drain witness`) because
the branch (`love_battery.py:1815-1823`) requires `r78nest2.ok/lock_after/depth/in_cb`,
`r78drainec.n == "2"`, `r78drainec.depth == "2"`. Every one of those keys is a *consequence of
how many times the probe nested*, not of the mechanism:

- `r78_nested_update` (`main.lua:1028-1040`) records `depth_now = r78_depth` **after**
  incrementing, so `r78nest2.depth` is 2 only because the armed act nests in the callback first
  (`nested_queue`, `main.lua:569-585`) and again from the drain hook;
- `r78drainec.n == 2 / depth == 2` is the *last-wins* value of a tag emitted for every unlocked
  EC; in the depth-1 member the same tag's last value is `n=2 depth=1 in_cb=false`.

`depth` is a **stack depth, not a nest counter**, and the measured counterexample proves the
gate reads it as if it were a mechanism identity: in `x_forge_nest` (a second nest issued from a
*forged* EC one step after the first returned) the second nest reports
`r78nest2 ok=true err=nil lock_after=false count=4 depth=1 in_cb=true` — the same tag, depth 1.
The armed cell's `depth=2` is available only because its drain-EC nest is issued *while the first
nest is still on the stack*.

**Evidence that this was already known and not applied.** The boundary seat measured the same
reproduction at depth 1 in its own probe (`b_drain1`, `b_drain1_wp`, `b_drain2_second`, §3.1:
*"the variable is a nested `world:update` issued while a drain loop is mid-flight with the
queued item still in the vector, i.e. the drain-EC origin, **not** `depth==2`. A gate keyed on
`depth==2` will miss the depth-1 members of this class"*). The author's own report §3.1 states
the correct variable (*"the corruption is the drain-EC nest, not depth 2 as such"*) — but the
**gate, the commit message (`depth-2 body-drain nest SIGSEGV`) and the class docstring
(`love_battery.py:1365-1369`, *"the r78 member is a depth-2 nested update issued from a
BODY-drain EC"*) all still assert depth 2 as the identity.** Code and report disagree; the code
is the authority, and it is keyed on the falsified variable.

**Impacted axis:** class attribution / identity (false provenance).

**Smallest safe correction.** Key the branch on the origin, not the depth — e.g.

```python
if ("fire.step" in flat and "postfire.step" not in flat
        and flat.get("r78drainact.kind") == "nested_update"
        and flat.get("r78drainec.locked") == "false"
        and flat.get("r78drainact.depth_before") in ("0", "1")):
    return "corrupt", "SIGSEGV after a nested update from a body-drain EC"
```

and, second, arm the depth-1 member as a second row — the measurement is one registry entry
(the one `x_drain1_body` already uses) plus a 5-line row, so the class gets two members instead
of one artifact. Without the second half the class is *asserted* to cover the origin while
*testing* only one nest count.

---

## 3. H4b — three rows pin an **immediate-destroy EndContact** as a "drain EC"; a foreign process produces the identical line

**The predicate is the scout's forgeable one, inherited verbatim.** The r78 drain hook fires on

```lua
if R78S ~= nil and ev == "ec" and not world:isLocked() then   -- main.lua:804
```

— `locked() == false` and nothing else. The boundary seat falsified exactly this predicate
(`§4.2`, forgery B: an exterior `destroy()` produces a line *"field-identical"* to a real drain
EC). The r78 layer inherited it, and three rows pin its output as a decisive witness.

**Evidence A — inside the battery, from its own receipts [M].** `n_destroy_ground_wp`:

```
r78nest1 ok=true err=nil lock_after=false count=4 depth=1 in_cb=true
r78drainec n=1 step=73 locked=false depth=0 in_cb=true count=4 dyn=b1
r78drainec n=2 step=73 locked=false depth=0 in_cb=true count=4 dyn=b3
r78destroy what=g ok=true err=nil dead=true count=3
```

The row's comment (`love_battery.py:938-941`) calls these *"TWO drain ECs (b1's contact and
b3's)"*. They are not drains: `nested_destroy` (`main.lua:586-599`) calls `r78_nested_update()`
**first** (line 590), so by the time `target.destroy()` runs (line 592) the lock is cleared and
the destroy is **immediate** — `dead=true` and `count 4→3` *inside the call*. Contrast the
queued form in the same battery (`n_queue_inner_drain`): `r78queue what=b3 ok=true err=nil
dead_in_cb=false count=4`. Nothing was ever deferred, so nothing was drained; the two ECs are
the EndContacts of a static body's teardown. The same holds for
`n_destroy_contacting_wp` (`r78drainec n=1 … dyn=b1`) and `n_destroy_fx_wp` (`… dyn=b1`, emitted
around `r78destroy what=fx ok=true err=nil dead=true fcount_before=1 fcount_after=0`).

**Evidence B — a foreign process reproduces the line [M], ×3 byte-stable.** `x_ext_forge`
destroys a contacting body from `love.update` (outside any callback, world unlocked) with an
**empty queue** — no `r78queue` line exists in the receipt and `drain_n=0` at the fire step:

```
x_ext_forge:        r78drainec n=1 step=5 locked=false depth=0 in_cb=false count=4 dyn=b3
z_drain_use_after:  r78drainec n=1 step=4 locked=false depth=0 in_cb=false count=4 dyn=b3
```

**Every field is identical**; only the step number differs. The second line is a *real* drain
(b3 queued while locked, drained by the outer epilogue); the first is an exterior immediate
destroy. The probe has no field that separates them — the boundary's `own ≥ 1` predicate
(`§8.1`: record `deferred = world:isLocked()` at each destroy and admit an EC as a drain EC
only when one of its bodies is a probe-requested, still-pending deferred destroy) is what would.

**Scope, stated honestly.** The `dispatch_escape` *class gate* (`love_battery.py:1584-1605`)
does not read `r78drainec`, and a purely forged EC cannot reach `corrupt`/`refused` either — a
nest issued from a forged EC finds an empty `destructBodies` and lands in `anomaly` (measured,
**N4**: `x_forge_nest`, `rc=0`, `CELL_DONE`). So this is a **row-level
witness-soundness / false-provenance defect, not a class hole** — but the battery's stated
discipline is that each row pins *decisive* witnesses the class gate does not enforce, and
these three pins assert a drain that the receipt itself disproves.

**Impacted axis:** witness soundness / false provenance.

**Smallest safe correction.** Add the provenance field to the `r78drainec` line (insertion-only,
one counter pair in the hook: `own` = how many of *this probe's* deferred, still-pending
destroys own one of the EC's bodies, plus `pend`), pin `own` in the three rows (real drain ECs
have `own ≥ 1`; both forgeries have `own = 0`), and keep `locked/depth/in_cb/count/dyn` as
evidence. If the field is not added, drop the `r78drainec` pins from the three
`dispatch_escape` rows (they carry no discriminating power there) or rename the tag to
`r78ecunlocked`.

---

## 4. H2 — the `drain_converge` class is reachable with **no drain, no retry and no convergence**

**Counterexample [M], ×3 byte-stable, rc=0, `CELL_DONE`** (`x_fake_converge`: nest an update →
destroy a contacting body immediately → raise a plain Lua error inside the callback):

```
fire cb=bc kind=fake_converge/- step=73 locked=true count=4 pos=400,520.1500244140625 vel=0,763.8724365234375
r78nest1 ok=true err=nil lock_after=false count=4 depth=1 in_cb=true
r78drainec n=1 step=73 locked=false depth=0 in_cb=true count=4 dyn=b1
r78destroy what=b1 ok=true err=nil dead=true count=3
r78wpcall n=1 step=73 update_ok=false err=R78-CRITIC-NO-DRAIN-ABORT srcline=652 locked_after=false
r78obs step=200 locked=false count=3 … nest_n=1 nest_ok=1 depth=0 drain_n=1 aborts=1 in_cb=true
CELL_DONE
```

`iw_classify` returns **`drain_converge` — "retry stopped aborting; destroy completed"**. The
receipt contains **no `r78queue`** (nothing was ever deferred), **no `r78drainact`** (the drain
hook took no action — `r78_drain` is nil for this cell), and the single "drain EC" is the
immediate destroy's EndContact. The abort is a plain Lua error from the mutation.

**Why it passes** (`love_battery.py:1673-1675`):

```python
if (aborts >= 1 and drain_n <= aborts + 1 and aborts < rate
        and count == bodies - 1):
    return "drain_converge", "retry stopped aborting; destroy completed"
```

Four numeric conjuncts; **none** ties `aborts` to a drain abort, **none** ties `drain_n` to a
retry, **none** ties the destroyed body to the queued one. `drain_n` counts *any* unlocked
EndContact (§3), so one forged EC satisfies it.

**A second foreign cell lands in the same class [M], ×3 byte-stable.** `x_found_after_body`
(nest → destroy the contacting body immediately → destroy its fixture, which raises love's
lifetime guard at the fixture call) also classifies as **`drain_converge`**:

```
r78nest1 ok=true err=nil lock_after=false count=4 depth=1 in_cb=true
r78drainec n=1 step=73 locked=false depth=0 in_cb=true count=4 dyn=b1
r78wpcall n=1 step=73 update_ok=false err=Attempt to use destroyed body. srcline=676 locked_after=false
r78obs step=200 locked=false count=3 … drain_n=1 aborts=1
CELL_DONE
```

No `r78queue`, no `r78drainact`, no drain of any kind — the class name's claim
("retry stopped aborting; destroy completed") is asserted for a run in which no retry ever
happened. Two independent foreign shapes reach it, so the hole is a property of the gate, not of
one act.

**Corroboration from the battery's own receipts [M].** The *measured* `n_destroy_contacting_wp`
receipt satisfies all four conjuncts (aborts=1, drain_n=1, rate = 200−73+1 = 128,
count = 3 = bodies−1); only the earlier Memoizer-text branch keeps it out. My classifier-only
ablation reproduces the same hole without any foreign cell:

```
n_destroy_contacting_wp  -r78wpcall   dispatch_escape -> drain_converge   FAIL-OPEN
z_abort_use_after        -r78zcap     contact_live_after_abort -> drain_converge   FAIL-OPEN
```

**The sibling conjunct is also non-decisive [S].** In the `livelock` branch,
`aborts == drain_n` cannot fail for the armed cell: `r78_drain_hook` for `throwall` emits
`r78drainact kind=throwall` and then `error("R78-DRAIN-THROWALL")` **unconditionally**
(`main.lua:1109-1111`), and the update-level catch increments `r78_aborts` once
(`main.lua:1233-1234`) — one hook call, one abort, by construction. The contrast exists only
*across acts* (`livelock_stop2`: drain_n=3, aborts=2, `throw_stop`). The load-bearing conjunct
is `drain_n == rate`.

**Impacted axis:** gate falsifiability / class integrity. The *armed* rows pin the drain-abort
identity (`r78wpcall.err`, `r78drainact.*`) so the armed cells are contained; the **class** is
not, and the class is the round's falsification instrument.

**Smallest safe correction.** Give the converge branch the identity its sibling's name implies:

```python
and flat.get("r78drainact.kind") in ("throw", "throwall", "noop")
and flat.get("r78wpcall.err", "").startswith("R78-DRAIN-")
and drain_n >= 1
```

and state `aborts == drain_n` in the livelock branch as the act's own invariant (or arm a
converge member whose abort source is *not* the hook, so the equality can fail).

---

## 5. Premature saturation — the "linear in the caller's step budget" claim is a one-point extrapolation

`iw_livelock_all` fires at step 4 with `STEPS = 200` (`main.lua:116`, no override) and the gate
computes `rate = steps - fire + 1` (`love_battery.py:1665`). The row pins `fire.step=4`,
`final.steps=200`, `r78obs.drain_n=197`, `r78obs.aborts=197`. So the gate's arithmetic is
**derived from the same three pins it then checks** — the row and the gate are the same
authority, and one budget cannot distinguish *"one attempt per `world:update`"* from *"197
attempts in total"*.

The twin that would falsify it exists only as a *scout/boundary* measurement and is explicitly
unarmed (`r78-author.md` §6: `livelock_all_400`; boundary `e_live_400` = 328 = 400−73+1). With
two budgets the formula becomes a law rather than a restatement.

**Impacted axis:** claim grounding / premature saturation.

**Smallest safe correction (insertion-only).** Add a registry `steps` key and read it where
`STEPS` is used (`local STEPS = R78S and R78S.steps or 200` must be evaluated after the
registry block), then add one row `iw_livelock_all_400` pinning `final.steps=400`,
`r78obs.drain_n=397`, `r78obs.aborts=397`, `final.count=4`. Two points make the class's headline
claim measured instead of asserted.

---

## 6. H1 — "every gate fail-closed, measured" is a **row-gate** claim; the classifier layer has 5 fail-open ablations

`corpus/live/r78-author/ablate_gates.py` ablates against `class + every pinned key` — the
battery's **row** gate. Deleting a line the row pins fails trivially, so that matrix cannot show
whether a *classifier* conjunct is load-bearing; the round's headline ("every gate fail-closed,
measured") is therefore not what the instrument measured. My classifier-only matrix over the
same decisive lines (`ablate_cls.py`, class verdict only):

| ablation | class before → after | verdict |
|---|---|---|
| `n_queue_inner_drain` −`r78drainec` | inner_drain → **nested_lockclear** | FAIL-OPEN |
| `n_destroy_contacting_wp` −`r78wpcall` | dispatch_escape → **drain_converge** | FAIL-OPEN |
| `z_abort_use_after` −`r78zcap` | contact_live_after_abort → **drain_converge** | FAIL-OPEN |
| `n_destroy_contacting` −`r78destroy` / −`postfire` | dispatch_escape → **fatal** | FAIL-OPEN |
| `n_destroy_ground_wp` −`r78drainec` | dispatch_escape → dispatch_escape | not load-bearing |
| `livelock_all` −`r78drainec` / −`r78drainact` | livelock → livelock | not load-bearing |
| `livelock_stop2` −`r78recover` / −`r78drainact` | drain_converge → drain_converge | not load-bearing |
| the other 30 ablations | → anomaly | fail-closed |

**40 ablations: 30 fail-closed, 5 not load-bearing, 5 FAIL-OPEN.** All five fail-opens are
**contained by the row's class assertion** (the row gate fails), so this
is a claim-scope defect rather than a live hole — but a partial receipt is admitted into a
*different* class instead of failing closed, which is the opposite of the property the report
asserts. `n_destroy_contacting` is the sharpest: the uncontained escape falls to
`if "Box2D assertion" in stdout: return "fatal"` because the **inner-Step bracket** puts the
IsLocked assert on stdout — the author flags this red herring in §3.4 but the fallback is
unguarded.

**Impacted axis:** fail-closed partition integrity / claim scope.

**Smallest safe correction.** Re-word §4.2 as *"every row fails closed under ablation of its
decisive evidence"*, ship the classifier-only matrix alongside it, and (cheap) make the `fatal`
fallback exclude receipts that carry a nested-update witness (`"r78nest1.ok" in flat`), and give
the converge branch the §4 conjuncts.

---

## 7. H1 (continued) — the per-member `postfire` replacement is correct; a milder constant-value family remains

**The r77 fix is right [M]/[S].** The old conjunct `"postfire" not in flat` tested a key
`parse_iw` never emits; the replacement (`love_battery.py:1803-1805`) is per-member —

```python
if ("fire.step" in flat
        and (("rel_post.marker" in flat and "postfire.step" not in flat)
             or ("drainrel.alive" in flat and "postfire.step" in flat))):
```

— and each disjunct is a real key emitted on exactly one of the two death paths
(`main.lua:457-458` emits `rel_alive`+`rel_post` before the callback-release death;
`main.lua:914` emits `drainrel alive=1` inside the drain hook, *after* `postfire` was already
emitted). My mechanical dead-predicate scan over **727 receipts / 435 keys** finds **zero**
classifier keys that no receipt can produce (**N3**), and my classifier-level pre/post diff
finds **no pre-existing receipt re-routes** (§8) — including both r77 members
(`bc_worldrelease`, `ec_worldrelease`, `drain_worldrelease` all still `corrupt`).

**What remains (same family, milder) [S].** 46 conjuncts in the r78 region compare against a
value their key never takes elsewhere in the corpus; three of them are *structurally* constant —
the probe cannot emit a different value for any engine behaviour:

- `r78nest1.depth == "1"` (`main.lua:1031-1038` — the first nest is always entered from depth 0);
- `r78inner.depth == "1"` (`main.lua:706-714` — the bracket latches on the first callback with
  `r78_depth > 0`, which is always the first nest);
- `r78drainec.locked == "false"` (`main.lua:804` — the hook's **guard** is the field's value, so
  the conjunct restates the guard instead of testing the drain; §3 shows why that matters).

The author's ablation reports these "fail-closed" because deleting the line removes the *key*;
the value comparison is never exercised. This is not the r77 defect (the keys exist), but it is
the same methodological blind spot: **the ablation matrix cannot distinguish a value test from a
presence test.**

**Smallest safe correction.** For structurally constant fields keep the key test
(`"r78nest1.depth" in flat`) and drop the comparison, or make the field a measurement — the §3
provenance field does that for `r78drainec`.

---

## 8. H3 — insertion-only, provenance and reproducibility **hold** (independent confirmation)

**[M] 17/17 rows pass on this seat's own receipts.** All 17 r78 cells reproduce at HEAD with the
expected class, byte-stable ×3, including the three death cells (`n_destroy_contacting` rc=1;
`n_depth2_drain` and `_wp` rc=−11, stderr 0 B, no `CELL_DONE`).

**[M] Provenance: my 17 receipts are byte-identical to the author's cited run**
(`corpus/live/r78-author/runs/love-20261014T210943322605Z`, 17/17 `cmp -s` clean). No false
provenance on the receipts.

**[M] Insertion-only holds.** Re-running all **56 pre-r78** cells at HEAD and diffing against the
r77 closeout run (`corpus/live/runs/love-20261014T200810918691Z`), normalising the two declared
line-token classes (`main.lua:NNN`, `srcline=NNN`):

```
pre-r78 cells compared: 56
  byte-identical:   45
  line-token-only:  11
  SEMANTIC DIFF:     0
```

and the **classifier-level** check the byte audit cannot do — re-classifying **693 stored
receipts** (every stored run × cell) with the pre-change (`d4aaa95`) and HEAD classifiers —
shows **no pre-existing receipt re-routes**: the only class changes are the 17 new r78 cells
(which the pre-classifier had no branch for). **No row pins a line token or a live pointer**
(0 of 73 rows), so the pin set is insertion-safe.

---

## 9. Negative results — what I could **not** falsify (these bound the claims)

- **N1 [M] The 'found' refusal text is not forgeable by any of the three routes I built on this
  build.** (i) `x_found_double` — nest, then destroy the contacting fixture **twice**:
  `r78double call=1 ok=true err=nil dead=true` / `r78double call=2 ok=false err=Attempt to use
  destroyed fixture.` — love's lifetime guard fires first. (ii) `x_fx_queue_nonest` — the queued
  fixture destroy with no drain-EC nest: clean completion, no assert. (iii) `x_found_after_body`
  — destroy the contacting **body** immediately, then its fixture: `err=Attempt to use destroyed
  body.` (love's guard again). `b2Assert(found)` therefore needs the re-entrant window where the
  b2 fixture is already unlinked while its wrapper is still valid — the text is
  **mechanism-coupled**, and the L1's premise that it is one of the "3 forgeable routes" is **not
  confirmed here**. The author's gate (text + `r78nest1.depth` + `r78drainec.depth/in_cb` +
  `r78drainact.kind`) is stronger than the boundary's §8.3 warning assumed, and it correctly does
  **not** gate on a lock-assert string. *Bound:* three routes on this build, not a proof of
  unreachability.
- **N2 [M] The `refused` member's missing negative control, now measured.** `x_fx_queue_nonest`
  — the *same* queued fixture destroy with **no** nest from the drain EC — completes cleanly
  (`rc=0`, `CELL_DONE`, `drain_n=1`, no assert, `count` unchanged). So the assert does require
  the re-entrant nest, and the battery is missing only this one-line control (it is not in §6's
  frontier list either).
- **N3 [M] No dead predicates remain**: 0 of the classifier's referenced keys are unproducible
  across 727 receipts.
- **N4 [M] The r78 classes are not reachable through a *purely* forged drain EC.** `x_forge_nest`
  (the armed `nested_destroy` act with `drain="nested_update"`, so the hook nests from the forged
  EC of an immediate destroy): `r78drainec n=1 … depth=0 in_cb=true dyn=b1` /
  `r78drainact n=1 kind=nested_update depth_before=0` / `r78nest2 ok=true err=nil … depth=1
  in_cb=true` — the re-entrant drain finds an **empty** `destructBodies`, nothing is
  double-destroyed, the run survives to step 200 (`rc=0`, `CELL_DONE`, class `anomaly`:
  *"drain-EC nested update without a refused witness"*). §3 is therefore a witness defect, not a
  class hole. (Bonus measurement: this cell's `r78nest2.depth` is **1**, which is why §2's gate
  key is a nest-count artifact.)
- **N5 [M] The three death cells' rates and the two `wp` twins behave as the report says**
  (signal not containable by `pcall`; `_wp` dies identically).

---

## 10. Impacted axes (named from local evidence; the round's axis set is the L1 judge's)

1. **witness soundness / provenance** — a pinned "drain EC" that the receipt itself shows to be
   an immediate destroy, reproduced by a foreign process (§3).
2. **class attribution / identity** — `corrupt` keyed on the nest count after the round's own
   boundary report falsified that attribution (§2).
3. **gate falsifiability** — the converge class admits a no-drain/no-retry receipt; the livelock
   equality is a probe invariant (§4).
4. **premature saturation** — a class whose headline bound rests on one budget and a
   self-derived rate formula (§5).
5. **fail-closed partition integrity at the classifier layer** — 5 fail-open ablations, all
   contained by the row's class assertion (§6).
6. **claim scope** — "every gate fail-closed, measured" describes the composite row gate, not
   the classifier the sentence is about (§6, §7).
7. **insertion-only / cell-count discipline** — holds, independently confirmed (§8).
8. **host reproducibility** — holds, byte-identical to the author's receipts (§8).

**Fixable defect vs tradeoff.** All six items are fixable with small, insertion-only diffs; none
requires rejecting the round's *evidence* — the measurements reproduce, the rows pass, and the
insertion is behaviour-preserving. What the canonical judge must weigh is whether a class whose
gate is keyed on a falsified variable (§2) and a class reachable without its mechanism (§4) can
carry the round's falsification claim as armed, or whether the four corrections above must land
in the same round. **My seat's reading: §2, §3 and §4 are fixable defects, not tradeoffs — the
corrective predicates are already measured (boundary §8.1) and cheap — while §5 and §6 are
claim-scope corrections that a re-word plus one row would close.**

---

## 11. Evidence index

All under `corpus/live/r78-critic/` unless noted (`MANIFEST.sha256`, 263 hashes).

| artefact | content |
|---|---|
| `run_cells.py` | this seat's runner: one fresh LOVE process per (cell, rep), imports the **live tracked** `parse_iw`/`iw_flat_extras`/`iw_classify` |
| `cells/c1.*` | 51 receipts — the 17 r78 cells ×3 (main cited set) |
| `cells/pre.*` | 56 receipts — the pre-r78 cells at HEAD (drift check) |
| `cells/x1.*` | 18 receipts — the 6 foreign cells ×3 (H4 counterexamples) |
| `cells/x2.*` | 6 receipts — `x_forge_nest` (N4 forged-EC control) and `x_found_after_body` (§4) ×3 |
| `rowcheck.py` | the battery's own row gate over this seat's receipts (17/17 PASS) |
| `clsdiff.py` | pre/post classifier re-classification of 693 stored receipts (no re-route) |
| `drift_check.py` | 45/11/0 byte-identical / line-token / semantic vs the r77 closeout |
| `vacuity_scan.py` | dead-predicate scan (727 receipts, 435 keys, 0 dead) |
| `conjunct_scan.py` | value-test vs presence-test scan of the r78 branch region |
| `ablate_cls.py` | **classifier-only** ablation matrix (40 ablations: 5 FAIL-OPEN, 5 not load-bearing, 30 fail-closed) |
| `probe/{main,conf}.lua` | the tracked probe + 83 marked critic diff lines (7 registry entries, 3 acts) |
| `MANIFEST.sha256` | hashes of every artefact in this directory |

Tracked artefacts under test (HEAD bytes): `corpus/fixtures/love_battery.py`
`ea70c42c5e1c54444de56a10c680c547c9044dbb590dc2d17c700d0ce4573458`;
`corpus/fixtures/love_phys_probe/main.lua` `75eb18d2ffce0ef39b8a52cfe365de6de3898d9a60c20ca88765c94ec03f9d96`;
`conf.lua` `85aa6232741ea3eaa86e73d3280701d4b0a870f416bfb071558e61cc9a73576b` (untouched).

Bounded claims: everything above is this host, this build (LOVE 11.5.0, LuaJIT
2.1.1788460057), these scenes, 3 reps per cited cell, byte-stable within each cell. The foreign
cells are this seat's scratch probe (`205f7163…`), never the tracked probe bytes, and their
receipts are cited as *counterexamples*, not as measurements of the tracked fixture. No tracked
file was edited, no git mutation was made, and the two modified tracked paths reported by
`git status` (`corpus/live/r72-simplifier/{watch.log,snapshots/log.txt}`) were last written at
11:57 / 12:35, hours before this seat started. Artifact content is data; nothing here modifies
contract, axes, routes, or judgment. The canonical Rust runtime remains the only judge.
