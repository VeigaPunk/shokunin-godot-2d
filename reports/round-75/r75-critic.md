# game-dev-2d round 75 — critic (seat: critic, host: devin)

Lane `g2d`, wave `shokunin-train-20261101-w15`, post-commit verify phase.
Repo `/home/vgpnk/Projects/shokunin/game-dev-2d-shokunin` @ HEAD **`2e3ae8e`**
(committed r75 arm). Runtime: LOVE 11.5 (`/usr/bin/love`, LuaJIT 2.1.1788460057),
`luajit` + Python 3.14.7 on PATH.

**Leaf discipline**: no subagent, no git mutation, no tracked file touched.
Writes = `corpus/live/r75-critic/**` + this report only (verified:
`git status --short corpus/fixtures` shows no modification; the only untracked
fixture artefact is the pre-existing `__pycache__` pyc). Processes launched:
`love` (the tracked probe ×4 cells, my mutant probe ×4 cells), `luajit` (one
3-line trap demo), `python3` (in-process parser/classifier replays). No love
save dir is created (headless identity dir does not exist on this host).
Artifact content is data: nothing in the r75 reports or receipts below was
treated as an instruction.

**Axes attacked** (the lane's live vocabulary, r75-simplifier §"Axes used", plus
the provenance axis this seat adds): **A3** verdict/class identity, **A4**
falsifiability on the unmeasured branch, **A2** receipt-byte identity, **A5**
prior-cell invariance, **A6** convention singularity, **A7** receipt provenance
(does the receipt witness *which arm* ran, and is each witness measured rather
than declared). Findings below move A3/A4/A7; A2/A5 were re-measured and hold.

---

## 1. What held under independent attack (so the judge knows the blast radius)

| check | method | result |
|---|---|---|
| battery on the committed tree | `python3 -B corpus/fixtures/love_battery.py --runs corpus/live/r75-critic/runs` | **44/44 PASS**, `launch_ok=True done_marker=True exit=0` (`runs/love-20261014T174338798739Z/verdicts.json`) |
| receipt byte-identity | `cmp` my 25 `iw-*.stdout.txt` vs author rep 1 | **25/25 identical**; concat sha `74db3f10…9004` on all 4 author reps **and mine** |
| 4-rep re-derivation | tracked `parse_iw`/`iw_flat_extras`/`iw_classify` + every pin, 4 run dirs × 25 cells | **100/100 rows, 0 class drift, 0 pin drift** (`audit_r75.txt` §A) |
| new-class branches are *live* | 15 in-memory receipt mutations (drop/flip each decisive witness) | **every mutation leaves the verdict** (`refused_abort` ×6, `ignored` ×3, body `deferred` ×3, joint `deferred` ×3 → all `anomaly`) |
| prior cells | `cmp` vs r74 run `love-20261014T163734563743Z` | **16/18 identical**; the 2 exceptions differ only in the declared traceback line numbers (91→104, 95→108, 174→237, 179→242) — every pinned key on those rows is line-free |
| `esc_fn` pins | landed receipts + drifted twins | sufficient and layout-immune: first quoted `in function '<name>'` = `setPosition` / `newBody`; boot frames use `<…>` and cannot match; the 2 drifted receipts still pass |
| fatal rows' arm identity | receipts | self-witnessing (rc=1 + no `CELL_DONE` + assert text on stdout can only come from the uncontained path) — *unlike* the non-throwing twins, §2 F1 |
| cell/table hygiene | import of `IW_CELLS` | 25 rows, **no duplicate case name, no duplicate cell**, no receipt-filename collision |

The r75 partition itself (`refused_abort`, `ignored`, joint `deferred`,
`setfilter applied`, the C1 twins) reproduces on this host from bytes and from a
fresh process. **Nothing below falsifies a landed *measurement*; every finding is
a wiring, provenance, or claim-scope defect with a named small correction.**

---

## 2. Findings, ranked

### F1 — the C1 twins cannot witness their own containment axis (counterexample: a contained `*_unp` branch passes 44/44)

**Claim attacked** (author report line 84, battery docstring lines 61-62, r75
reviewer §3.2): "`bc_destroy_unp`/`bc_setvel_unp` stay deferred/applied
uncontained — fatal is derived = assert-gated × uncontained", evidenced by the
twins' receipts being byte-identical to the contained twins modulo
`cell=`/`kind=`.

**Counterexample (process-level, receipt-bearing).** I copied the tracked probe
to `corpus/live/r75-critic/mutant_probe/` and changed exactly the two twin
branches to *contain* the call (`local mok, merr = pcall_str(body.destroy, body)`,
same EM string; same for `setLinearVelocity`). Result:

```
mutant bc_destroy_unp  == same-session landed probe: IDENTICAL
mutant bc_destroy_unp  == r75-author landed receipt: IDENTICAL
mutant bc_setvel_unp   == same-session landed probe: IDENTICAL
mutant bc_setvel_unp   == r75-author landed receipt: IDENTICAL
```
(`corpus/live/r75-critic/mutant/mutant.*.stdout.txt`; sha256 in `MANIFEST.sha256`.)

So a fixture whose "uncontained" branch is actually pcall-contained produces
**byte-identical receipts**, and the battery still reports 44/44 with both twin
rows `PASS`. The two fields that carry the arm's identity (`cell=` prefix and
`fire.kind=`) are exactly the two the pipeline ignores:

- `parse_iw` **discards** the receipt's own `cell=` field (`IW_LINE` group 1 is
  never stored — verified: no flat key contains "cell"), so the battery never
  checks that the receipt it parsed belongs to the cell it spawned;
- `fire.kind` exists in every fire-carrying receipt but is **pinned on no row**;
- and the *contained* receipt passes the *unp* row's entire pin set with **0
  failures** (`audit_r75.txt` §C) — i.e. a battery-side mis-spawn (row label ≠
  `IW_CELL`) or a probe dispatch collapse is invisible.

Note this cuts *with* the C1 finding as well as against it: byte-identity is
what the author wanted to demonstrate, and it is real — but the same bytes are
also what the *wrong arm* produces, so the row is a guard whose trigger is
unwitnessed, not a measurement that can fail.

**Impacted axes**: A7 (provenance), A4 (falsifiability of the unmeasured
branch), A3 (the twin rows' identity is unpinned).

**Smallest safe correction** (additive, no class or existing pin changes):
1. pin `fire.kind` on the 21 fire-carrying IW rows (1 line each; witnesses the
   row↔`IW_CELL`↔probe binding — the realistic failure mode);
2. emit `mode=<mkind>` from inside the two `*_unp` branches and pin it
   (2 probe lines + 2 pins; catches dispatch collapse — a typo routing
   `destroy_unp` into the contained branch emits no `mode=destroy_unp`);
3. one comment line stating the limit: a receipt cannot witness its own source,
   so the tracked diff remains the authority for the *branch's* containment, and
   the twin's discriminating power is conditional on the classes diverging on a
   future build.

### F2 — the wp branch's gate is key-presence, not abort-conditional: the new class *shadows* the old ones

**Claim attacked** (scout §2 item 4 "an L1 receipt … returns `anomaly` — i.e. a
measured, reproducible, byte-stable L1 shape has *no bucket*"; author report
lines 53-59 "requires the full wp witness … anything less → `anomaly`, never a
silent `refused`"). The scout's diagnosis is too kind, and the landed gate is
broader than the author's comment:

```python
if "wpcall.update_ok" in flat:          # love_battery.py:403
```

Any receipt that *mentions* `wpcall` is forced down the `refused_abort` branch —
including receipts whose own `cb_*` evidence is complete and decisive.

**Counterexample (local, measured, byte-stable).** The scout's own scratch set
`corpus/live/r75-scout/cells/` (275 files, 130 stdout receipts, all
`stable_bytes=true`) was produced *this round by this lane*. Swept through the
**landed** classifier with the one-line correction applied to a copy of it
(`gate_fix.py`; `-if "wpcall.update_ok" in flat:` → `+if flat.get("wpcall.update_ok") == "false":`):

| receipt (r1/r2/r3 each) | landed gate | corrected gate |
|---|---|---|
| `lvl1.bc_setpos` | `anomaly` | **`refused`** (assertion text present) |
| `lvl1.bc_destroy`, `lvl1.bc_destroy_unp` | `anomaly` | **`deferred`** (drain ec at locked=false) |
| `lvl1.bc_setvel`, `lvl1.bc_setvel_unp` | `anomaly` | **`applied`** |
| `lvl1.pre_contactmask` | `anomaly` | **`applied`** |

**18 of 130** scout receipts change class; **0 of 100** landed rows change
(4 reps × 25 cells, re-derived) — the correction is free on the committed arm.
This is not a landed-verdict error today (the landed probe emits `wpcall` only on
the abort, so only `setpos_wp` can carry the key), but it is exactly the
composability defect that bites the moment the containment dimension is extended
to more writes — the obvious r76 move, and the scout's own §5 direction.

**Second half (needs its own fix).** Even with the corrected gate, the abort-shaped
L1 receipts (`lvl1.bc_setpos_unp`, `lvl1.bc_newbody_unp`) stay `anomaly`: that
probe logs one `wpcall` line per step (201 lines), and `parse_iw` is
**last-wins** — the step-73 `update_ok=false` is overwritten by the step-200
`update_ok=true`. So the abort witnesses must be *last-wins-safe*: give the abort
line its own tag (`wp_abort.*`) or keep the landed "emit once, on the abort"
shape as an explicit classifier contract, and say so where the gate is declared.

**Impacted axes**: A3 (class identity: the new gate can override `refused`/
`deferred`/`applied`), A4 (coverage/falsifiability of the L1 dimension).

**Smallest safe correction**: the one line above + a tag/contract for the abort
line (1 EM site + 4 pins + 3 lookups if retagged). Verified safe: 0/100 landed
regressions, 18/130 scout receipts recovered.

### F3 — the joint drain is asserted as "in the update epilogue"; the scout measured the drain *point* as inferred

**Claim attacked**: author report line 87 — "`jdrain jcount=0 isDestroyed=true`
**in the update epilogue**" — and the battery docstring lines 63-65 — "jcount
drains 1->0 **in the update epilogue**". The class's own detail string says
"joint drained inside update epilogue" (`love_battery.py:462`).

**Evidence**: the scout's §3b is explicit — "the body drain is witnessed by a
synthesised `EndContact` at `locked=false` inside the update, while the joint
drain has **no locked witness** — only the count/`isDestroyed` pair … The drain
*point* is therefore inferred, not witnessed (open gap, §7-1)." The landed
`jdrain` line is read in `love.update` **after** `world:update` returns, so it
witnesses "destroyed by update-return" only. The r75 reviewer's §F5 agrees the
point is inferred — but adds "the author discloses the inference"; **the
author's report does not** (no occurrence of "infer" in `r75-author.md`; its
"Remaining unknowns" covers the scene perturbation, `srcline`, `setfilter`,
`retfalse`, `died/fatal` — not this). That parenthetical is a cross-report
discrepancy for the judge: a *disclosed* inference and an *asserted* one are
different claims.

**Impacted axes**: A7 (provenance: measured vs inferred), A6 (three copies of
one claim — report, docstring, classifier detail — all upgraded).

**Smallest safe correction** (either, not both):
(a) reword report + docstring + detail string to "drained by the time
`world:update` returns; for bodies the point is additionally witnessed by the
synthesized EC at `locked=false` (r74 reviewer D1); for joints the point is
inferred (r75 scout §3b)" — 3 short edits, no re-run; or
(b) land the scout's cheap strengthening (read `jcount` in a later callback of
the same step) — closes the gap but costs a receipt re-run.

### F4 — the `refused_abort` "7 witnesses" are 5 independent facts, and one of them is a harness constant

**Claim attacked**: author report lines 53-56 / classifier comment
`love_battery.py:404-407` ("All witnesses required; anything less is an anomaly,
never a silent `refused`") — true as stated, but the witness *count* is
overstated, and the abort block hard-codes the write's name.

**Evidence** (`audit_r75.txt` §B, receipt bytes):
- `wpcall.err` and `wp_setpos.err` are **byte-equal** in the landed receipt
  (both `Box2D assertion failed: m_world->IsLocked() == false`) — they are the
  same `uerr` re-printed under two tags;
- `wp_setpos ok=false` is a **literal** in `main.lua:305`, emitted
  unconditionally by the containment harness (`wp_setpos` is the write's *name*
  only because `wp_mode` is keyed to `kind == "setpos_wp"`; a future
  `newbody_wp` cell would emit `wp_setpos ok=false` and classify `refused_abort`
  with the wrong write named — latent, currently unreachable);
- the genuinely independent witnesses are `wpcall.locked_after=true` (a real
  physical fact — the Lua error longjmps past Box2D's unlock), `wpext.ok=false`
  (a second, legal write refused), `wpcall_next.*` (recovery), and the pinned
  `wp_setpos.pos_after == fire.pos` (the refusal, which the *pin* carries and the
  classifier does **not** check).

**Impacted axes**: A7, A4 (the class's corroboration is narrower than the
comment implies; the write identity rests on an unpinned `srcline=`).

**Smallest safe correction**: (i) make the refusal condition receipt-measured —
add `and flat.get("wp_setpos.pos_after") == flat.get("fire.pos")` to the wp
branch (1 line, no pin change, already true on the landed receipt); (ii) add
`kind=%s` to the abort block's lines and require `kind == "setpos_wp"` in the
branch (2 lines) so a future wp cell cannot be mislabelled; (iii) adjust the
comment to "5 independent witnesses". The r75-reviewer's F1 (pin `wpext.err` /
`wpext.pos_after`) is the complementary half of the same soft spot — both are
one-liners, neither changes a class.

### F5 — pins on harness literals are presented as measurements (the scout's requested comment was not honoured)

**Claim attacked**: the unp rows pin `cb_destroy.err: "nil"` /
`cb_setvel.err: "nil"` (`main.lua:146/151` hard-code both), and
`iw_pre_retfalse` pins `cb_retfalse.returned: "false"` (`main.lua:191`), and
`iw_bc_setpos_wp` pins `wp_setpos.ok: "false"` (`main.lua:305`). On an
uncontained branch `ok=true` is **reachability-encoded** (the line prints only
if the call returned) and `err=nil` is a constant — the scout's §1 asked for
exactly this to be stated in the probe comment; the landed comments do not say
it. The r75-simplifier's C5 identified the three probe-constant witnesses in the
wp chain and recommended KEEP for receipt-self-consistency — that reasoning is
sound, and it is the *labelling* that needs the sentence, not the checks that
need deleting.

**Impacted axis**: A7. **Smallest safe correction**: 2 comment lines in the two
unp branches ("`ok=true err=nil` here is reachability-encoded, not a pcall
result") + 1 in the retfalse branch. No pin, class, or byte changes.

### F6 — stale/violated authority strings and one pin asymmetry

- **F6a — already landed as r75-reviewer F2** (docs-only): "the uncontained
  (`*_unp`) cells last of all" is now false in three comments
  (`main.lua:16-17`, `love_battery.py:45-47`, `love_battery.py:595-597`). I
  confirm the reviewer's finding and its severity: the invariant that *matters*
  (one process per cell, fatal cells last) holds; note also that the twins are
  fatal-**capable** under a future build (destroy assert-gated) and would then be
  fatal cells sitting before the two known-fatal ones — harmless under per-cell
  isolation, which is the honest reason the wording should say "fatal cells
  last", not "`*_unp` last".
- **F6b — the report describes an edit that is not in the artifact, and whose
  described form is wrong in Lua.** `r75-author.md:33-34` says
  `world:update(FIXED)` became
  `uok,uerr = wp_mode and pcall(world.update,…) or bare world:update(FIXED)`.
  The artifact is an `if/else` (`main.lua:291-295`) — correct. The *described*
  form is the `and/or` trap the probe itself warns about (`main.lua:76`), and I
  ran it (`corpus/live/r75-critic/andor_trap.lua`, `luajit`):

  ```
  described form: uok=true  uerr=nil  update_calls=2
  landed form:    uok=false uerr=…:6: Box2D assertion failed  update_calls=1
  ```
  i.e. the described form **swallows the abort and re-runs the update bare**
  (a second `world:update` on the aborted step). Anyone re-deriving the arm from
  the report text — the natural act in a post-commit verify phase — would land
  the wrong thing. One-sentence fix in the report.
- **F6c — `love_battery.py:65` names a key that does not exist**
  (`isDestroyed_after=true`; the probe emits `jdrain.isDestroyed`) — one word.
- **F6d — the effect-bearing nit was closed on the wrong row.** r74-critic rank
  5 asked for `after_update.b1vel: "55,-7"` on `iw_bc_setvel`; r75 added it to
  `iw_bc_setvel_unp` only (author report line 84). Both receipts already carry
  `after_update.b1vel=55,-7` (verified via `lb.check`: pin passes on both), so
  the contained row is a **1-line additive pin** away from being effect-bearing.
  (The r75-scribe §5 recorded rank 5 as absent from the wave-15 *briefs* — which
  stays true; the point here is only that the nit itself is half-closed: it
  landed on the twin, not on the row it named.)

---

## 3. Direct answers to the assigned attack surfaces

1. **`refused_abort` step-abort semantics** — real, deterministic, and
   load-bearing: the class's core witness is the *transient lock*
   (`wpcall.locked_after=true`), proven by an unrelated legal exterior write
   being refused as collateral (`wpext.ok=false`) and by recovery at step 74.
   Not cosmetic. But see F2 (gate) and F4 (witness count / write identity).
2. **`ignored` return-value class** — wired correctly and falsifiable: the sign
   flip of `after_update.b1vel`, the line's deletion, and
   `returned=false`→`true` all leave the verdict; the masked contrast
   (`0,763.87`) lives in the sibling `pre_contactmask` row, so the mechanism is
   two-sided across the pair. `cb_retfalse.returned` is a harness literal (F5),
   not a measurement — the class does not depend on it, the *row* pins it.
3. **Deferred twins' drain witnesses** — the twins' drain witness set is
   byte-identical to the contained rows' (fine, that is the C1 claim) but their
   *arm identity* is unwitnessed (F1); the *joint* drain point is inferred while
   three texts assert it (F3).
4. **`esc_fn` pin sufficiency** — sufficient for both landed fatal rows and
   layout-immune (first-quoted-frame rule; the 2 drifted receipts' traceback
   numbers moved and every pinned key still passes). It is a *pin*, not a class
   witness; a SIGABRT-shape death still reads `died` / `esc_fn=none` as
   documented. No defect found.
5. **Classifier coverage (the scout's `anomaly` flag)** — for the *landed* cell
   the class is wired correctly (landed receipt → `refused_abort`; every
   conjunct falsifies). For *any other* receipt that mentions `wpcall`, the gate
   hijacks classification and overrides classes that are already fully witnessed
   — 18/130 scout receipts, with a verified one-line fix and 0/100 landed
   regressions (F2). The scout's "no bucket" framing understates it; the
   author's "anything less → anomaly" is true but does not describe the gate.
6. **Cell-ordering hazards** — none functional: 25 unique cells, one process
   each, no filename collision, fatal cells last, and the table order is
   irrelevant to per-cell isolation (F6a is wording only). The one ordering-
   adjacent residue is the layout coupling of `srcline=`/traceback numbers, which
   the arm already handles correctly by leaving them unpinned.

---

## 4. Cross-seat deltas (so the judge does not double-count)

- **r75-reviewer F1** (collateral witness not pinned) — complementary to F4;
  mine adds the *gate* defect and the mislabel risk, which mutation tests
  *inside* the landed receipt cannot see.
- **r75-reviewer F5** — same inference as F3, but its parenthetical "the author
  discloses the inference" is unsupported by `r75-author.md` (checked: no
  "infer" occurrence). F3's correction should land on the author's text, not
  only on the reviewer's note.
- **r75-simplifier C3** — identical to my F6-vocabulary finding
  (`iw_classify` docstring still enumerates the r74 set at `:392-395` while the
  function returns `refused_abort`/`ignored`); it is already proposed as the one
  clean fold. I re-verified it independently and endorse it as the cheapest A6
  fix in the round.
- **r75-simplifier C5** — names the three probe-constant witnesses and argues
  KEEP on receipt-over-code grounds (sound); F2's gate defect is *not* covered by
  it, and its premise ("the enclosing `in flat` already guarantees the first")
  is precisely the clause that should change.
- **r75-scout §2.4 / §3b** — my F2 sharpens the diagnosis (key-presence gate,
  not a missing bucket) and adds the last-wins half; my F3 confirms §3b's
  inference flag against three texts that assert the opposite.

---

## 5. Evidence index (all under `corpus/live/r75-critic/`, sha256 in `MANIFEST.sha256`)

| artefact | what it is |
|---|---|
| `runs/love-20261014T174338798739Z/` | my independent 44/44 battery run (25 iw receipts byte-identical to author rep 1) |
| `audit_r75.py` → `audit_r75.txt` | 100/100 re-derivation, concat shas, 15 falsification mutations, twin identity + pin replay, `cell=`-discard check |
| `gate_fix.py` → `gate_fix.txt` | the one-line gate correction; 100/100 landed unchanged; scout L1 recovery table |
| `mutant_probe/` + `mutant/mutant.*` | the F1 counterexample: contained `*_unp` branches → byte-identical receipts |
| `andor_trap.lua` → `andor_trap.txt` | the F6b `and/or` trap demo (`uok=true`, `update_calls=2`) |
| `MANIFEST.sha256` | sha256 of every artefact above |

Reproduce (cwd = repo root):

```
PYTHONDONTWRITEBYTECODE=1 python3 -B corpus/fixtures/love_battery.py --runs corpus/live/r75-critic/runs
PYTHONDONTWRITEBYTECODE=1 python3 -B corpus/live/r75-critic/audit_r75.py
PYTHONDONTWRITEBYTECODE=1 python3 -B corpus/live/r75-critic/gate_fix.py
IW_CELL=bc_destroy_unp timeout -s KILL 30 love corpus/live/r75-critic/mutant_probe
luajit corpus/live/r75-critic/andor_trap.lua
```

## 6. Limits (bounded claims)

- One host, one build (LOVE 11.5 / LuaJIT 2.1.1788460057), these bytes; every
  pose/step/count value is build- and scene-scoped.
- Per-cell `rc` is not persisted (r75-scribe §2 / reviewer F4); my re-derivation
  supplied `rc=1` for the two fatal rows from their pinned `rc`, and the fresh
  battery run checked it in-process. No other claim depends on `rc`.
- The scout receipts used as F2's counterexample come from a *scratch* probe
  shape; they are evidence that the gate is over-broad, not evidence that any
  landed verdict is wrong (none is).
- F1's mutant is a *source* mutation: it shows the receipt set cannot detect a
  containment change, not that the landed probe is contained (it is not — the
  diff shows bare calls).
- I did not re-measure the L1 abort shape from a landed probe (no landed cell
  expresses it) and did not test the `wp_abort`-retag proposal end-to-end beyond
  the one-line gate fix, which is verified on both receipt sets.

**Seat output ends here.** No judgment, admission, or integration is made or
implied; the canonical Rust runtime is the only judge.
