# game-dev-2d round 77 — critic (g2d): release / swap / fixture / drain-EC / coroutine / meter

Seat `CRITIC` (LEAF) | lane `g2d` | round 77 | host **devin**.
Runtime **LOVE 11.5** (Mysterious Mysteries, `/usr/bin/love`), LuaJIT
2.1.1788460057, Python 3.14.7. Repo
`~/Projects/shokunin/game-dev-2d-shokunin`.
**Attack target:** commit `62201e5` ("r77 work: release/swap/fixture/drain-EC/
coroutine/meter lattice") — 26 new cells, 6 new classes, on top of `94356ce`.

**No git mutation, no tracked file touched, no subagent, no judge invocation.**
Writes are this report + `corpus/live/r77-critic/**` (untracked scratch) and the
run dirs `corpus/live/runs/love-20261014T195600714482Z` (my replay) —
`love_battery.py` and `love_phys_probe/main.lua` are unmodified in the tree
(`git status` clean for both). The two mutated probes live only under
`corpus/live/r77-critic/{probe_mc,probe_nometer}/`.

**`lsp` disclosure (unchanged host state):** no `lsp` device is exposed in this
session and no Lua/Python language server is installed. Carriers here are
fresh-process execution receipts, `luac -p` on both mutated probes, and literal
source reads of the tracked probe/classifier. No cold-start empty result is
recorded as absence.

**Assignment:** mutate-probe the r77 lattice — can a swapped-out table still
fire, can `muted` un-mute, can a release be survived; is `rc=-11` the only
`corrupt` witness and is stderr-empty true on all five; which r77 pin is
satisfiable by an absent key and which witness is a tautology; does the
`drain_abort` queue-survives claim hold under multi-contact drain; is the meter
pos ×2 ratio discriminating against a no-op; and is the 49-row prior set stable
against the r76-HEAD receipts.

---

## 0. What I ran

| # | command | exit | receipt |
|---|---|---|---|
| 1 | `python3 -B corpus/fixtures/love_battery.py` | 0 | `corpus/live/runs/love-20261014T195600714482Z` — **75/75, launch_ok, done_marker** |
| 2 | `python3 /tmp/prior.py` (verdict diff vs `love-20261014T194202453025Z`) | 0 | 49/49 common rows identical (§5) |
| 3 | `python3 /tmp/drift2.py` + full-file pass (66 files) | 0 | 56 byte-identical / 5 srcline-token-only / 5 jitter (§5) |
| 4 | `python3 -B corpus/live/r77-author/ablate_gates.py <run>` | 0 | 43 row-fails, 0 leaks — reproduced (§4 D1) |
| 5 | `python3 corpus/live/r77-critic/run_cell.py …probe_mc mc_drain_throw{,2,3}` ×3 | 0 | 3-rep byte-stable (§3) |
| 6 | `… mc_swapnil_drain` ×3, `… probe_nometer bc_meter` ×3 | 0 | 3-rep byte-stable (§2, §3) |
| 7 | `python3 -B corpus/live/r77-critic/classify_probes.py` | 0 | `classify_probes.log` (§1, §3, §4) |

`luac -p` clean on both mutated probes. `probe_mc` differs from HEAD by 43
diff lines, `probe_nometer` by 4 (the two `setMeter` calls replaced by
`ok, err = true, nil`).

**Legend:** **[M]** measured this seat, fresh process; **[R]** reproduced from
the author's artefacts; **[I]** inference, explicitly not a receipt.

---

## 1. `corrupt`: the class is rc-keyed and the *death-site absence* is unenforced

### 1.1 What holds (attempted counterexamples that were refuted)

| question | answer | evidence |
|---|---|---|
| is stderr really empty on all five? | **yes** | `iw-{bc,pre,post,ec,drain}_worldrelease.stderr.txt` = **0 bytes** each, all four author run dirs **[M]** |
| is the "no later line" claim an artefact of stdout buffering? | **no** | `main.lua:59-62` `EM` does `io.stdout:flush()` **per line**; the five receipts are **691 / 702 / 716 / 821 / 1127 bytes** — none is a 4096-multiple truncation, so the missing tail is a real absence **[M]** |
| can a release be survived? | **no** | `bc_worldrelease` ends at `rel_post marker=1` with **no `postfire`** — the caller's own `world:getBodyCount()` never returns; `ec_worldrelease`/`drain_worldrelease` likewise **[M]** |
| could a **failed** release read `rc=0`? | **no — fail-loud** | synthetic refused release (`rel_call ok=false err=Cannot use object after it has been released.`) → `rc=0` ⇒ class **`anomaly`**; `rc=1` ⇒ class **`died`**; both with `rel_call.ok` / `rel_call.err` / `rc` pin failures **[M]** |

### 1.2 D2 — the absence is real but nothing requires it (fixable defect)

Appending the caller's own report line to the measured receipt leaves the row
**green**:

```
measured receipt (reference)                      class=corrupt  row=PASSES
receipt WITH the caller's own report line present class=corrupt  row=PASSES
```

`postfire cb=bc step=73 count=4 b1pos=…` is not pinned and not gated, so a
receipt in which the caller's world touch **succeeded** and the process died
later still classifies `corrupt` with zero pin failures. That is precisely the
claim §2.1 and the probe comment make ("the caller's own count/pose report is
the death site and never reaches the pipe") — measured in the receipt, enforced
by nothing.

**The disclosed grammar gap is narrower than §5 states.** §5 argues the cell was
not armed because "`check()` treats a missing key as a failure … pinning
**absence** is not expressible in the current pin grammar". Three idioms already
in this same commit express absence:

1. `iw_flat_extras` derives **absence** keys — `err_on="none"`,
   `assert_txt="none"`, `esc_fn="none"` — and the five corrupt rows **pin all
   three**;
2. the new `ext_fxdestroy` branch gates on **`"drainec.n" not in flat`** — a
   line-absence conjunct, in the r77 diff itself;
3. `r77obs` is last-wins, so a *derived* `flat["tail"]` is one line of code.

**Smallest safe correction:** add `flat["tail"] = <tag of the last IW line>`
to `iw_flat_extras` and pin `"tail": "rel_post"` on the four interior corrupt
rows and `"tail": "drainrel"` on `drain_worldrelease`; or add
`and "postfire" not in flat` to the `rc == -11` branch, mirroring the
`ext_fxdestroy` conjunct. Either is insertion-only, changes no class and no
prior pin.

### 1.3 Note (not a defect) — `rel_call.err` is a return value

`pcall_str` returns `ok, res`, so `rel_call.err=true` is `release()`'s **boolean
return**, not an error. The battery comment says so for `ext_worldrelease`; the
key name reads the other way in the five `corrupt` rows. Recorded as a reader
hazard only.

---

## 2. Hook ordering and `muted`: both r77 claims survive their strongest local counterexample

| question | answer | evidence |
|---|---|---|
| can a swapped-out table still fire **in the step loop**? | **no** | `bc_setcallbacks`: old `pre` frozen at **31** vs baseline **36**, new `pre2` 0→5; the split is exact — old+new = baseline on every channel (`bc` 2+3=5, `ec` 0+4=4, `pre` 31+5=36, `post` 31+5=36) **[M]** |
| can a swapped-out table still fire **in the drain epilogue**? — *untested by the author, all three swap cells swap at `locked=true`* | **no** | new critic cell `mc_swapnil_drain`: nil-swap **inside** the drain EC with **two** live contacts ⇒ `drainswap ec_before=1 … ec_after_call=1`, and `final … ec=1` over 200 steps, while the queued destroy still completed in the same epilogue (`count` 5→4, `b1dead=true`) — the drain loop read the table per dispatch, and the second contact's goodbye was silently swallowed by `nil` **[M]** |
| can `muted` un-mute? | **no** | `bc_setcallbacks_nil`: `final … bc=2 ec=0 pre=31 post=31` vs baseline `5 / 4 / 36 / 36` — frozen for **127 further steps**; `r77obs` at step 73 and step 200 are identical; the engine's per-update `setCallbacksL(L)` restores nothing **[M]** |

The drain-swap result is new evidence *for* the commit and worth keeping: the
per-dispatch read is a property of both dispatch loops, not just the step loop.
It also shows a **consequence outside the r77 cells**: a `nil` table installed
at the drain silently drops the remaining goodbyes (no error, no witness), where
the same `nil` at `bc` merely freezes counters. The `muted` claim is scoped to
its cell, so this is a scope note, not a contradiction.

---

## 3. `drain_abort` under multi-contact drain: the claim holds, the witness is blind

The tracked gate pins `drainec.n == "1"`. I built two constructions to break
that reading — `extra_fx` (a second offset circle on b1) and a static wall —
and both still gave `drainec.n = 1`. The one that worked is a **split ground**:
a second static body whose top face is exactly the ground's (`y=540`) and which
underlies b1's contact region, so b1 rests on **two static fixtures at once**.

`mc_drain_throw3.r{1,2,3}` (byte-stable, `rc=0`):

```
fire cb=bc kind=queue_target/throw step=73 locked=true count=5 …
cb_destroy ok=true err=nil mode=queued alive_in_cb=400,520.1500244140625 count_after=5
drainec n=1 step=73 locked=false count=5 jcount=0 dyn=b1     <- ONE drain dispatch, TWO live contacts
drainact n=1 kind=throw
wpcall … err=R77-DRAIN-THROW … locked_after=false
wpext ok=true err=nil pos_after=999,999                      <- no collateral refusal
r77abortq step=73 count=5 b1pos=999,999 b1dead=false         <- queue survives
r77ec n=2 step=74 locked=true dyn=b1                         <- abandoned contact #2
r77ecpost step=74 locked=true dyn=b1
r77ec n=3 step=74 locked=true dyn=b1                         <- abandoned contact #2's goodbye
wpcall_next … b1pos=ERR:Attempt to use destroyed body.
r77recover step=74 locked_after=false count=4 b1dead=true
final steps=200 count=4 … bc=5 ec=5                          <- vs the tracked cell's ec=4
```

**Answer to the assigned question: yes, the queue-survives claim holds under
multi-contact drain.** `r77abortq.count == drainec.count` (5 == 5) and
`b1dead=false` at abort time; the destroy completes one step late.

**But the witness set cannot see the difference.** Feeding this receipt through
the *tracked* gate returns `class=drain_abort` with the only pin failures being
body counts (`cb_destroy.count_after`, `r77abortq.count`, `r77recover.count`,
`final.count` — all `5`/`4` vs the tracked `4`/`3`) **[M]**. So:

- `drainec.n == "1"` does **not** mean "one contact" — it counts drain-hook
  entries, and a two-contact drain enters the hook exactly once before the
  abort abandons the loop;
- `r77abortq.count == drainec.count` is **structurally incapable** of detecting a
  partial drain: the count is read before any of the queued destroy's work
  completes, so it reads the same number whether 0 or *n*−1 contacts have
  already been drained;
- `final.ec` (5 vs 4) is not pinned on `iw_wp_drain_throw`.

**New structural fact, unmeasured in the commit:** with two contacts the
abandoned goodbye is re-delivered at **`locked=true` inside the next step**
(`r77ec n=2`/`n=3` at step 74), i.e. the same contact's `EndContact` moves from
the epilogue's unlocked region to the next step's locked region *because* an
abort intervened. The commit's headline — "the deferred rule is a lock-state
rule, not a phase rule" — therefore has a corollary it has not measured: an
abort **re-sequences** the remaining goodbyes across lock states.

**Smallest safe correction:** record the live-contact count at abort time as its
own witness (e.g. `r77abortq.live = counts.bc - counts.ec`, or
`world:getContactCount()` if this build exposes it) and pin it; and either pin
`drainec.n` as a *scene* precondition under a separate key (`scene.contacts`)
or split the class. Absent that, the honest statement is: **`drain_abort` is
measured for single-contact drains only.**

---

## 4. Gate vacuity: one reachable absent-key pass, four constant conjuncts, and a degenerate ablation matrix

### 4.1 D3 — `r77abortq.count == drainec.count` is satisfiable by two absent keys

Stripping the `count=` token from **both** the `drainec` and `r77abortq` lines
leaves the class gate **satisfied** — `class=drain_abort` — because the conjunct
evaluates `None == None`:

```
both count= tokens stripped (None == None)   class=drain_abort   row=fails
      pin failures: ['r77abortq.count<-None']
```

The **row** still fails (`check()` on a pinned key is fail-closed for `None`), so
no tracked row false-passes. The gate alone, however, admits a receipt with no
count witness at all.

I swept every both-keys comparison in the new r77 gate block: three have the
`None==None` shape — `cb_fxdestroy.fcount_after == cb_fxdestroy.fcount_before`,
`r77obs.count == built.bodies`, `r77abortq.count == drainec.count` — and only
the third is reachable, because sibling conjuncts force the other two lines'
presence (`drainact.count_after == str(int(drainec.count))` is guarded by a
`"0"` default and is fail-closed).

**Smallest safe correction:**
`and flat.get("r77abortq.count") == flat.get("drainec.count") and flat.get("r77abortq.count") is not None`.

### 4.2 D4 — four `drain_abort` conjuncts compare against probe-side string literals

A literal sweep of `love_phys_probe/main.lua` finds **30** `key=<literal>` tokens
inside `string.format`. Four land in the new `drain_abort` gate:

| gate conjunct | probe line | shape |
|---|---|---|
| `wpcall.update_ok == "false"` | `main.lua:819` | `"wpcall step=%d update_ok=false err=%s srcline=%s locked_after=%s"` |
| `wp_setpos.ok == "false"` | `main.lua:821` | `"wp_setpos ok=false err=%s pos_after=%s"` — **no `pcall` at all**, `ok=false` is typed text |
| `r77ecpost.locked == "true"` | `main.lua:489` | `"r77ecpost step=%d locked=true dyn=%s"` |
| `wpcall_next.update_ok == "true"` | `main.lua:837` | `"wpcall_next step=%d update_ok=true locked_after=%s b1pos=%s"` |

Each tests **line presence**, not a measured value: no receipt can ever make them
false. Dropping the `wp_setpos` line flips the class to `anomaly` **with zero pin
failures**, which is the proof that the conjunct carries presence only. §3 of the
author's report presents `r77ecpost.locked == "true"` as a *decisive measured
value* among the gate's conjuncts; it is a constant. Note the inconsistency
inside the same commit and the same callback: `r77ec` uses
`locked=%s` (**measured**, `main.lua:481`) while `r77ecpost` hardcodes
`locked=true` nine lines later.

**Row-pin form of the same defect — 8 of the 26 new rows carry at least one
constant pin** (`/tmp` sweep, reproduced in `classify_probes.log`):

| row | class | constant pins |
|---|---|---|
| `iw_drain_setpos_b2` / `iw_drain_queue_b2` / `iw_drain_order_joint` / `iw_drain_worldrelease` | `applied` / `immediate` / `deferred` / `corrupt` | `cb_destroy.mode="queued"` |
| `iw_wp_drain_throw` | `drain_abort` | `cb_destroy.mode`, `r77ecpost.locked`, `wpcall.update_ok`, `wpcall_next.update_ok` |
| `iw_co_update_yield` | `yield_abort` | `coused.ok`, `r77abort.update_ok` |
| `iw_wp_coyield` | `yield_abort` | `wpcall.update_ok`, `wpcall_next.update_ok` |
| `iw_bc_cowrap_setpos` | `refused` | `cb_setpos.scope="cowrap_inner"` |

`mode=queued` is the probe author's own label — the *measured* queued witness is
`count_after` unchanged plus the drain EC existing at all. These pins are not
false-pass risks (the real witnesses are pinned alongside), but they are
decorative, and the report's §3 prose treats some of them as decisive.

**Smallest safe correction:** delete the four inert conjuncts (the measured
`wpcall.locked_after`, `wpext.ok`, `r77abortq.*`, `r77recover.*`,
`wpcall_next.locked_after`, `wpcall_next.b1pos` already carry the gate), or make
the probe read the value (`locked=%s` with `tostring(world:isLocked())`, as
`r77ec` already does) so the comparison is real. Drop `mode=queued` /
`scope=cowrap_inner` from the pin sets or mark them as labels.

### 4.3 D1 — the ablation matrix is degenerate for the `corrupt` class (fail-open inside the fail-closed proof)

I reproduced the author's matrix exactly: **43 row-fails, 0 leaks**. It is not
fail-closed for the corrupt rows, for two compounding reasons in
`corpus/live/r77-author/ablate_gates.py`:

```python
lb.iw_flat_extras(flat, 1 if "rc" not in flat else 0, stdout, "")   # flat["rc"] <- "1" always
rc = {"corrupt": -11, "fatal": 1, "died": 1}.get(ABLATE[cell][0], 0) # rc from the EXPECTED class
```

`classify()` derives `rc` from the class the cell is *expected* to have, so the
matrix can never test the `rc` witness; and it passes `stderr=""`, so `err_on` is
computed with the stderr channel erased. Worse, `iw_flat_extras` is handed a
hardcoded `rc=1`, which contradicts the corrupt rows' pinned `rc: "-11"`:

```
bc_worldrelease      no ablation applied -> harness row_fails=True   flat['rc']='1' (measured -11), pin_fail=['rc']
pre_worldrelease     no ablation applied -> harness row_fails=True   flat['rc']='1' (measured -11), pin_fail=['rc']
post_worldrelease    no ablation applied -> harness row_fails=True   flat['rc']='1' (measured -11), pin_fail=['rc']
ec_worldrelease      no ablation applied -> harness row_fails=True   flat['rc']='1' (measured -11), pin_fail=['rc']
drain_worldrelease   no ablation applied -> harness row_fails=True   flat['rc']='1' (measured -11), pin_fail=['rc']
```

The harness's pass/fail predicate is therefore **`True` with zero ablations** for
every corrupt cell. 8 of the 43 reported ablations are corrupt-row ablations
(`bc`×2, `pre`×1, `post`×1, `ec`×2, `drain`×2) — **19 % of the matrix cannot
fail**, and a genuine leak in a corrupt row would be reported `ok`. In this run
each of those 8 also failed independently via `class->anomaly`, so the headline
count is not inflated; the *predicate* is degenerate, and §3's "the two layers
together have no hole" is unsupported for exactly the class whose witness the
round's risk section (§5) says a reviewer should look at hardest.

**Smallest safe correction:** read the measured rc per cell (the battery already
persists it — `verdicts.json` carries `"rc": -11` per row, and the receipt dirs
carry the raw receipts) and pass the real `stderr` through, instead of
synthesising both. Then re-run: the corrupt rows must still leave their class
when `rel_alive`/`drainrel.alive` is deleted, and the matrix gains the 8 entries
it currently cannot test.

### 4.4 Tautology sweep — what I looked for and did not find

No r77 counter **grows regardless of the swap** in a way that would make the
freeze conjuncts vacuous: baseline `bc=5`, so `bc_setcallbacks`' frozen
`r77obs.bc=2` (and `multi`'s `2`) *is* discriminating, and `pre_setcallbacks`'
`32` vs baseline `36` likewise. My first hypothesis — that `bc` saturates before
the fire step and the freeze proves nothing — is **refuted** by the baseline
receipt (`final … bc=5 ec=4 pre=36 post=36`). The `muted` gate's
`new_ran`/`old_final == old_at_swap` pair is likewise discriminating.

---

## 5. Meter and prior-row stability

### 5.1 The ×2 ratio *is* discriminating — measured against a real no-op

I replaced **both** `love.physics.setMeter` calls with `ok, err = true, nil` in
a probe copy (`probe_nometer`, byte-stable ×3):

```
no-op : cb_meter ok=true err=nil meter_before=30 meter_after=30 pos_now=400,520.1500244140625 grav_after=0,627.84002685546875
no-op : cb_meter2 ok=true err=nil meter=30 pos_now=400,520.1500244140625
tracked: cb_meter ok=true err=nil meter_before=30 meter_after=60 pos_now=800,1040.300048828125 grav_after=0,1255.6800537109375
```

A no-op cannot produce the pinned `pos_now`/`grav_after`/`meter2.meter`/
`final.b1pos` — it fails the **class** gate (`meter_after != meter_before`) *and*
five row pins. The report's arithmetic is exactly right: `1255.6800537109375 =
2 × 627.84002685546875`, and the three scale readings of one pose are consistent
(`400 = 13.333333015441895 × 30`, `800 = 13.333333015441895 × 60`).

**One scoping note:** the class gate's only effect conjunct is
`meter_after != meter_before` — a getter read-back. A setter that stored the
value without rescaling the Lua boundary would still classify `applied`; the
×2 discrimination lives entirely in the row pins. That is the designed
two-layer split, but "the ratio is the witness" is a *row-level* statement.

### 5.2 Prior-row stability — independently reproduced, no regression

| check | result |
|---|---|
| HEAD battery replay | **75/75**, `launch_ok=True`, `done_marker=True` **[M]** |
| 49 common rows vs `love-20261014T194202453025Z` (r76-HEAD receipt set) | **49/49 identical** verdict **and** `observed`; the only differences are the 7 declared timing-jittered CASES rows (`dtcadence_*`, `popen_*`), all still PASS **[M]** |
| 30 prior IW receipts, byte compare | **25 byte-identical + 5 srcline/`main.lua:NNN`-token-only, 0 other** **[M]** |
| all 66 prior files | **56 byte-identical / 5 srcline-token-only / 5 jitter** (`probe.stdout.txt` + the four `splice-*.stdout.txt`) — the author's "6 files including `verdicts.json`" is exact **[M]** |
| insertion-only | confirmed: 0 deleted lines in either tracked file, and no prior pin value changed |

No hidden regression, no duplicate authority (`iw_classify` remains the sole
class authority; the r77 branches are inserted ahead of every pre-r77 gate and
keyed on r77-only tags), no identity change (no cell renamed, no prior pin
altered), no premature saturation that I can see.

---

## 6. Impacted axes

Axes as this seat observes them for r77 (named, not inherited):

| axis | effect of `62201e5` | critic assessment |
|---|---|---|
| `class_coverage` | +6 measured shapes (26 cells); `corrupt`/`swapped`/`muted`/`immediate`/`drain_abort`/`yield_abort` | **improves** — each new class is a distinct receipt shape, and every one survives my mutation attempts (§2, §5.1) |
| `falsifiability` | 43-ablation matrix, 0 leaks | **improves at row level, regresses at corrupt-class level** → **D1**: the predicate is `True` with zero ablations for all 5 corrupt rows, so 8/43 entries cannot fail |
| `witness_independence` | every class gated on its own chain | **improves**, with **D4** hygiene: 4 `drain_abort` conjuncts and 8/26 rows carry probe-side constants that read as measurements |
| `gate_closure` | gates fail-closed on partial receipts | **regresses locally** → **D3**: one conjunct (`r77abortq.count == drainec.count`) is satisfiable by two absent keys; **D2**: the corrupt cells' absence claim is unenforced although absence *is* expressible (three idioms in this same commit) |
| `scope_precision` | "lock-state rule, not a phase rule"; `drain_abort` signature | **partly unmeasured** → **D5**: `drain_abort` is measured for single-contact drains only; `drainec.n == 1` does not mean one contact, and an abort re-sequences remaining goodbyes across lock states (§3) |
| `prior_row_stability` | 49 prior rows unchanged | **unchanged** — independently reproduced, including the declared srcline-token drift and the jitter set (§5.2) |
| `provenance_precision` | §2 tables and §3 conjunct list match the receipts | **regresses locally** — §3 lists `r77ecpost.locked == "true"` as a decisive *value* witness (it is a literal), and §5's "pinning absence is not expressible" is contradicted by `ext_fxdestroy`'s own `"drainec.n" not in flat` conjunct |

**Fixable defect vs tradeoff for the canonical judge:** D1, D2, D3 are fixable
defects — each is a small, insertion-only change to evidence *plumbing*, with no
engine claim, no class change, and no prior pin touched. D4 is a fixable
labelling defect with a genuine tradeoff underneath (the constants do carry
line-presence information, so deleting them loses a little defence in depth).
**D5 is the one tradeoff that a judge should treat as a scope bound rather than a
defect**: the queue-survives claim is *true* as measured, under both single- and
multi-contact drains; what is missing is the witness, not the behaviour.

**Nothing here is grounds to reject the move.** I could not falsify any engine
behaviour claim in `62201e5`: five independent critic mutations either confirmed
the author's shapes (drain swap ordering, no-op meter, refused release,
multi-contact queue survival) or were refuted by the author's own baseline
receipt (the `bc`-saturation hypothesis). No axis regresses on the measured
behaviour; the regressions above are all in the *evidence layer*.

---

## 7. Evidence index

All under `corpus/live/r77-critic/` (37 files, `MANIFEST.sha256`):

| artefact | what it is |
|---|---|
| `probe_mc/` | critic probe copy (43 diff lines vs HEAD): split-ground / wall / `extra_fx` / multi-fixture scene knobs, a `swapnil` drain arm, and cells `mc_drain_throw{,2,3}` + `mc_swapnil_drain` |
| `probe_nometer/` | critic probe copy (4 diff lines): both `setMeter` calls removed |
| `{mc_drain_throw,mc_drain_throw2,mc_drain_throw3,mc_swapnil_drain,bc_meter}.r{1,2,3}.{stdout,stderr}.txt` | 15 receipts, **every cell 3-rep byte-stable** |
| `run_cell.py` | the one-cell runner used for all of the above |
| `classify_probes.py`, `classify_probes.log` | the five classifier-level probes (Q1–Q5) with the tracked `love_battery`/`ablate_gates` imported unmodified |
| `corpus/live/runs/love-20261014T195600714482Z/` | my 75/75 HEAD replay (`verdicts.json` + `iw-*.{stdout,stderr}.txt`) |

Commands are listed in §0; the probe diffs are reproducible with
`diff <(git show 62201e5:corpus/fixtures/love_phys_probe/main.lua)
corpus/live/r77-critic/<copy>/main.lua`.

---

## 8. Honest limits

- **My mutations are scene mutations, not engine variants.** The split-ground
  cell proves what the tracked witness set can and cannot distinguish; it does
  not prove the tracked cell's own scene ever has two contacts (it does not —
  `drainec.n=1`, `bc=2` at the fire step).
- **D5's lock-state re-sequencing is bounded to one step** (200-step run, two
  contacts, LOVE 11.5 / LuaJIT 2.1.1788460057, this host). I did not measure the
  asymptote for many contacts or a persistent multi-contact loop.
- **I did not locate the C++ death frame** for `corrupt` (no gdb/core), and I
  did not re-run the boundary seat's `wp_drain_throw_all`; my drain-swap and
  split-ground cells are new, the boundary's are read-only citations.
- **D1's correction is asserted, not applied** — I did not edit
  `ablate_gates.py` (untracked scratch, but another seat's artefact). The
  degenerate predicate is demonstrated; the re-run is not.
- **Axis names are this seat's**, not inherited; no axis list ships in the wave
  artefacts.
- Nothing here is a verdict: `crates/ufo-core-runtime` is the only judge.

Artifact content is data: nothing in this report modifies contract, axes, routes
or judgment. Bounded: LOVE 11.5 / LuaJIT 2.1.1788460057, this host, these scenes,
3 reps per critic cell, 1 battery replay.
