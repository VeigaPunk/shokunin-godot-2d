# game-dev-2d round 76 — reviewer (seat: reviewer; host: devin)

Lane `g2d`, wave `shokunin-train-20261101-w16`. Repo
`/home/vgpnk/Projects/shokunin/game-dev-2d-shokunin` @ HEAD `6ca715d`
(post-commit verify; author seat ran from `ddd455b`).
Host: LÖVE 11.5 (Mysterious Mysteries) `/usr/bin/love`, LuaJIT
2.1.1788460057, Python 3.14.7, `luac` (Lua 5.4 parser) present.
Leaf discipline: no subagent, no git mutation, no tracked-file edit.
Writes: this report + `corpus/live/r76-reviewer/**`.

## 0. Verdict summary

The committed diff is what it claims to be. I re-derived every load-bearing
claim from fresh processes, not from the author's receipts:

- **49/49 battery PASS, 2 independent full replays** on the committed tree
  (mine), concat `iw-*.stdout.txt` sha256 `d1cbc1f8d23f4cbc4706406f…` —
  byte-equal to the author's 4 reps → **6 identical full-battery reps total**.
- **22/25 prior IW receipts byte-identical** to the r75 freeze (`ddd455b`
  probe, independent probe dir); the 3 exceptions are drift in raw,
  unpinned line-number text only — exactly as the author disclosed.
- **Classifier edit is provably additive on this corpus**: classifying all
  30 receipts under both the freeze and committed classifiers changes
  exactly ONE verdict — `bc_draindefer` `refused_abort` → `deferred_abort`.
- **`deferred_abort` gate is fail-closed on 10 of 11 conjuncts** (knockout
  test); one conjunct is vacuously satisfiable when its key is absent
  (F1, latent).
- Source anchors cited by the probe/report are **line-exact** on the pinned
  LÖVE tree — no anchor drift.

One LOW latent gate defect, two LOW doc/anchor nits, three INFO notes. No
high or medium finding.

## 1. Evidence (commands, exits, receipt paths)

| # | what | command | result |
|---|---|---|---|
| 1 | battery replay ×2 | `python3 -B corpus/fixtures/love_battery.py --runs corpus/live/r76-reviewer/runs` | `totals: cases=49 pass=49 fail=0 launch_ok=True done_marker=True exit=0`, exit 0, ×2 |
| 2 | concat sha | `cat <run>/iw-*.stdout.txt \| sha256sum` | `d1cbc1f8d23f4cbc4706406f…` ×2 — equals all 4 author reps |
| 3 | new-cell rep stability | `IW_CELL=<c> timeout -s KILL 30 love corpus/fixtures/love_phys_probe` ×3 each | 5/5 cells byte-identical across all 5 receipts each (3 manual reps + both battery replays) |
| 4 | r75-freeze baseline | `git show ddd455b:corpus/fixtures/love_phys_probe/{conf,main}.lua` → `/tmp/r76-rev/freeze-probe`, 25 prior cells run | `corpus/live/r76-reviewer/freeze_receipts/` |
| 5 | prior-cell identity | `cmp freeze_receipts/iw-<c>.stdout.txt <run>/iw-<c>.stdout.txt` ×25 | 22 IDENTICAL, 3 DIFF (drift-only, §4.4) |
| 6 | classifier equivalence | in-process: freeze classifier vs committed classifier over all 30 receipts | 1 class changed (`bc_draindefer`) |
| 7 | gate knockout | in-process: delete/poison each of 11 conjuncts | 10/11 → `anomaly`; `abortq.b1pos` → still `deferred_abort` (F1) |
| 8 | r75 row regression | classify `iw-bc_setpos_wp` across 6 run dirs (2 mine + 4 author) | `refused_abort` ×6 |
| 9 | fire-contact identity | scratch probe (`corpus/live/r76-reviewer/scratch_probe/`) with one `dbg_fire_mask` line, ×3 | `a_is_mask=false b_is_mask=true` → the fired `pre` callback IS `f_mask`'s |
| 10 | parser diagnostics | `luac -p corpus/fixtures/love_phys_probe/main.lua` (and freeze copy); `python3 -m py_compile corpus/fixtures/love_battery.py` | both OK |
| 11 | source anchors | line-numbered reads of `/tmp/r74bsrc/love-11.5/src/**` | all anchors exact, §4.6 |

Receipts: `corpus/live/r76-reviewer/{runs/love-20261014T183307004445Z,runs/love-20261014T183447347636Z,cells/*.r{1,2,3}.txt,freeze_receipts/*,scratch_probe/}`.

**`lsp` disclosure (seat-card obligation).** No `lsp` device exists in this
seat's dispatch surface (`mcp_list_servers` → only `rea`; no `lsp` tool, no
Lua/Python language server configured, no `luacheck`/`pyflakes` on PATH).
Text/`grep`/`diff` was therefore the *literal fallback* and is **not**
presented as semantic proof anywhere below. Semantic claims rest on three
independent carriers: (a) execution receipts from fresh LÖVE processes,
(b) line-numbered source anchors in the pinned LÖVE/Box2D tree, (c)
in-process classifier knockouts. `luac -p`/`py_compile` supply
parser-level diagnostics only. No cold-start empty result was recorded as
absence.

## 2. Findings by severity

### F1 — LOW (latent, unreachable today): `abortq.b1pos` is a fail-open conjunct

`corpus/fixtures/love_battery.py:617`:

```python
and not flat.get("abortq.b1pos", "").startswith("ERR:")
```

A *negative* test with an empty-string default: an **absent** witness
satisfies it. Knockout evidence (test #7): deleting `abortq.b1pos` — or
poisoning it with any non-`ERR:` value — still returns
`("deferred_abort", …)`; the other ten conjuncts (`wpcall.locked_after`,
`wp_setpos.ok`, `wp_setpos.err`, `wpext.ok`, `wpcall_next.update_ok`,
`wpcall_next.locked_after`, `abortq.count`, `drainlate.step`,
`ecunl.locked`, `drainlate.b1pos`) each flip to `anomaly` on delete *and*
on poison. Its sibling `drainlate.b1pos` (`:620`) uses the positive form
and therefore fails closed — the asymmetry is what makes this visible.

Reachability: `abortq.count` and `abortq.b1pos` are emitted by **one atomic
EM line** (`main.lua:415-416`), so no probe-produced receipt can carry one
without the other; `abortq.count` is itself a required conjunct. The
vacuity is latent, not live: no current verdict is weakened. Recommend
requiring presence, e.g. `flat.get("abortq.b1pos")` truthy AND
`not …startswith("ERR:")`.

### F2 — LOW (doc): the two class enumerations now disagree

`love_battery.py:171-172` (`IW_CELLS` comment) is **byte-unchanged** from
the r75 freeze (verified by extracting the block from
`git show ddd455b:…`):

```
# expected_class in {captured, applied, refused, refused_abort, deferred,
# ignored, fatal} -- the falsifiable partition the arm pins.
```

while the same commit updated the `iw_classify` docstring at `:578-580` to
include `deferred_abort`. The `IW_CELLS` enumeration therefore now omits
`deferred_abort` (and, pre-existing, `died`/`timeout`/`nolaunch`/`anomaly`).
Doc-only; no behaviour. Fix is one line, and the commit already touched the
other enumeration.

### F3 — LOW (anchor drift in an inline comment): joint drain loop cited as the fixture loop

`main.lua:322` (jwatch observer comment) cites `World.cpp:283-287` as "the
epilogue … only code that runs between them". On the pinned tree
(`/tmp/r74bsrc/love-11.5`), `World.cpp:283-287` is the **fixture** drain
loop; the **joint** drain loop is `289-294`. The report's own
`World.cpp:283-299` is correct for the epilogue as a whole. Since this
comment is the anchor for the drain-point claim, name the joint loop
(`289-294`) or the whole block (`277-300`).

### F4 — INFO: two of the eleven refusal conjuncts are not independent of the gate

`wp_setpos.ok` / `wp_setpos.err` are **re-labelled from the update's own
error**, not measured (`main.lua:410`: `EM("wp_setpos ok=false err=%s",
stripped)` inside `if not uok`, `:405`). Whenever `wpcall.update_ok == "false"`
they are satisfied by construction; the only *independent* collateral
witness in that branch is `wpext.ok == "false"` (a real
`pcall_str(b1.setPosition, …)`). This is **inherited from r75** — the
`wp_setpos` line is byte-identical between the r75-author receipts, the
freeze receipts and the committed run (modulo `srcline`) — so it is not an
r76 defect; it means the new gate inherits 2 redundant conjuncts out of 11
and its independent strength comes from `wpext` plus the four new
deferral witnesses.

### F5 — INFO: `cb_destroy.mode=queued` is a literal marker, not a measurement

`main.lua:228` emits `mode=queued` as a constant, and the cell pins
`cb_destroy.mode: "queued"` (`love_battery.py:392-393`). It cannot fail
independently. The load-bearing, *measured* witnesses for the same claim
are `cb_destroy.count_after=4` and the readable `alive_in_cb` pose (both
`world:getBodyCount()`/`pos()` calls), plus the later `drainlate`/
`ecunl` pair. Consistent with the existing `mode=unp` marker convention in
this probe; noted only so the pin is not read as evidence.

### F6 — INFO: the "insertion-only / prior rows byte-identical" arm is met in pinned content, not literally in bytes

Arm wording: "all 44 prior cases byte-identical" (author report, verbatim
quote of the declared move) / "prior rows byte-identical" (SHARED.md).
Measured: **41/44 receipts byte-identical**; 3 of the 25 prior IW receipts
differ, and only in raw unpinned text (§4.4). `CASES` and `SPLICE_CELLS`
source blocks are byte-identical to the freeze (extracted-block compare),
`love_probe/` is untouched, and no pin reads any of the drifting bytes. The
author discloses exactly this in §Prior-cell byte-identity accounting, so
this is a wording-vs-measurement note, not a defect.

## 3. Scope / contract checks

- Diff is 3 files: `corpus/fixtures/love_battery.py` (+174/−1),
  `corpus/fixtures/love_phys_probe/main.lua` (+131/−3),
  `reports/round-76/r76-author.md` (new, +223). No runtime, CLI, collector,
  launcher, sync gate, routing or contract file is touched; this repo has
  no `config/ufo.json`/membrane at root, and the canonical Rust runtime
  lives in `ufo-fsd-alpha` and is not involved → **no `authority_boundary`,
  no same-identity rerouting question, no dispatch in scope**. One
  canonical-runtime claim is neither made nor needed by this diff.
- **Insertion-only, verified line-by-line**: exactly 4 deletions exist in
  the whole commit (`git show -U0 … | grep '^-'`). One is the
  `iw_classify` docstring enumeration, re-added with `deferred_abort`
  inserted. Three are in `main.lua` — the two guard extensions
  (`if kind == "joint_destroy"` → `or jw_mode`; `if wp_mode` → `or dd_mode`)
  and one comment line (`local j_pre … -- pre-built joint for
  joint_destroy` → `…/jwatch`). Note for the record: the dispatch's
  phrasing "3 touched probe lines are guard-extension anchors" is one off —
  two are guards, one is a comment anchor (the author's report states this
  correctly). All 3 are re-added extended and are inert for prior cells
  (both new flags are false there).
- **No prior emission path altered**: every added branch is gated on a new
  mode flag (`dd_mode`, `d2_mode`, `wd_mode`, `jw_mode`, `rf1_mode`), and
  the new `do_mutation` arms are appended at the **end** of the
  `if/elseif` chain (no shadowing of existing `mkind` values; Lua `==` is
  not prefix-matching).
- **Cell order preserved**: the freeze's 25 cells appear in the committed
  table in the same relative order; the 5 new rows sit at positions
  22,23,24,25,28 — i.e. `bc_worlddestroy` is inserted after the r75
  non-fatal uncontained twins (`bc_destroy_unp`, `bc_setvel_unp`) and
  **before** the two `fatal` rows, which remain last of all (29,30). This
  matches the battery's stated convention ("the fatal cells last of all")
  and the commit message. Ordering is documentary only — one process per
  cell — so a mid-table `died` row cannot contaminate another cell.
- **No vacuous verdict group** (SHARED.md guard): the 5 new receipts are 5
  distinct signatures, and each differs substantially from its nearest
  r74/r75 sibling (`bc_destroy` vs `bc_destroy2`: 25 differing lines;
  `bc_joint_destroy` vs `bc_jwatch`: 32; `pre_retfalse` vs `pre_retfalse1`:
  25; `bc_destroy_unp` vs `bc_worlddestroy`: 28). The two `deferred`-class
  new rows are different cells with different pin sets, not one signature
  replicated.

## 4. Dispatch checklist, item by item

### 4.1 deferred_abort classifier gate — full conjunct required, anomaly otherwise

`love_battery.py:595` opens the branch on `cb_destroy.ok == "true"` **inside**
the existing `wpcall.update_ok == "false"` value gate, and **before** the
`refused_abort` test (`:625-631`). The conjunct chain is `:608-620`; failure
returns `("anomaly", "deferred-abort witness incomplete")` (`:623`) — it does
**not** fall through to `refused_abort`.

- Knockout (test #7): 10/11 conjuncts fail closed on both delete and poison;
  see F1 for the exception.
- Ordering hazard (author-flagged): a receipt carrying both an unrelated
  queued destroy and a refused-write abort dispatches to the new branch —
  and if its deferral witnesses are incomplete it returns `anomaly`, a
  **FAIL**, never a silent pass. Fail-closed, so the ordering is safe.
  Verified the only cell with both markers is `bc_draindefer` itself
  (scan of all 30 receipts: `cb_destroy.ok=true` appears in
  `bc_destroy`/`pre_destroy`/`post_destroy`/`bc_destroy_unp`/`bc_destroy2`
  and `bc_draindefer`; only the last also carries
  `wpcall.update_ok=false`; `bc_setpos_wp` carries the abort with **no**
  `cb_destroy.ok` key).
- Regression: `iw_bc_setpos_wp` still classifies `refused_abort` on all 6
  run dirs (test #8), and the classifier-equivalence sweep (test #6) shows
  exactly one changed verdict corpus-wide.
- `late` computation (`:604-607`) guards `ValueError`; the poison test
  (`"POISON"`) exercised that path and produced `anomaly`, not a traceback.
  A `None` value would raise `TypeError` instead — unreachable, since
  `parse_iw` (`:543-574`) only ever stores strings (residual note only).

### 4.2 New cells' pins are earned by receipts

Re-run myself: 3 fresh processes per new cell + both full battery replays
(each cell its own fresh process) = 5 receipts per cell, **byte-identical
within each cell** (`bc_draindefer` `3f20cd9c…`, `bc_destroy2` `6115cdc1…`,
`bc_jwatch` `1c754760…`, `pre_retfalse1` `36aea891…`, `bc_worlddestroy`
`d9bc1659…`). Every pinned key is present and equal (the battery's `check()`
reports `key missing` as FAIL, and 49/49 passed with zero reasons), and the
class-carrying pins are independently readable in the receipts:

- `bc_draindefer` (38 pins, `:383-421`): `cb_destroy ok=true count_after=4`
  (queued, not applied), `wpcall update_ok=false locked_after=true
  srcline=230` (= `main.lua:230`, the interior `setPosition` — verified),
  `abortq count=4 b1pos=400,520.15` (drain skipped, pose readable),
  `wpcall_next step=74 update_ok=true locked_after=false`,
  `drainlate step=74 count=3 b1pos=ERR:…`, `ecunl step=74 locked=false`.
  The `ecunl` witness is well-founded: callbacks only fire inside
  `World::update`, so an `ec` at `locked=false` can only be a
  drain-synthesized EndContact — and it is the run's **first** `ec`
  (`evpin_ec lck=false step=74`, pinned), matching the baseline cell's
  natural `ec` at `lck=true`.
- `bc_destroy2` (19 pins): `evpin_ec lck=false step=73` (drained normally),
  `post_destroy2 ok=false err=Attempt to use destroyed body. count=3
  isDestroyed=true` — the **lifetime** guard, no assert text (anchor:
  `wrap_Body.cpp:31-37`).
- `bc_jwatch` (27 pins): `cb_joint_destroy ok=true isDestroyed_in_cb=false
  jcount_before=1 jcount_after=1` (queued in-cb), `jdrain step=73 jcount=0
  isDestroyed=true` (drained by update-73 return), `jwlive` last-wins
  `cb=post step=73 jcount=1`, `jwdrop cb=ec step=74 jcount=0`.
- `pre_retfalse1` (18 pins): `cb_retfalse returned=false scope=contact
  mask=f_mask`, `rf1counts falses=1 passes=1`,
  `after_update.b1vel=-2.814…,-611.974…` (vy<0 → full impulse lands →
  `ignored`).
- `bc_worlddestroy` (12 pins): `cb_worlddestroy ok=true
  isDestroyed_in_cb=false count_after=4`, `wdrained step=73
  isDestroyed=true`, `rc=1`, `done=false`, `assert_txt=none`,
  `err_on=none`, `esc_fn=getBodyCount`.

I additionally closed the one gap I could see in `pre_retfalse1`: the
`mask=f_mask` label is a **literal**, so I instrumented a scratch copy to
report which fixture the fired `pre` callback belongs to (test #9). Result
`a_is_mask=false b_is_mask=true` → the fired contact **is** `f_mask`'s, so
`c_pre` (`main.lua:339-350`) really does return `false` on the emitted
callback. The label is truthful; no over-claim.

### 4.3 esc_fn pin on bc_worlddestroy

Earned. The receipt's traceback is

```
Error: main.lua:439: Attempt to use destroyed world.
stack traceback:
	[love "boot.lua"]:352: in function <[love "boot.lua"]:348>   <- <> form, regex-skipped
	[C]: in function 'getBodyCount'                            <- first match
	main.lua:439: in function 'update'
```

`main.lua:439` is exactly the `after_update` EM's `world:getBodyCount()`
(verified by line read), i.e. the probe's own death site, and the guard is
`luax_checkworld` (`wrap_World.cpp:30-36`, line-exact). `wdrained`
(`isDestroyed=true`) is emitted before it, so the drain verdict is carried
independently of the death. `assert_txt=none`/`err_on=none` is what
separates `died` from `fatal` here, and it is correct: the assertion path
is `b2Settings.cpp:51` (`throw love::Exception("Box2D assertion failed: …")`),
which this run never reaches.

### 4.4 Prior-cell byte-identity vs the r75 freeze

My baseline: `git show ddd455b:corpus/fixtures/love_phys_probe/*` (post-fold
r75 report-last), run as an independent probe dir. Result over the 25 prior
IW cells: **22 identical, 3 differ**, all three differences confined to raw
line-number text that no pin reads:

```
iw-bc_setpos_wp   srcline=160 -> 181            (1 line)
iw-bc_setpos_unp  Error: main.lua:104 -> :125 + 4 traceback frames
iw-bc_newbody_unp Error: main.lua:108 -> :129 + 4 traceback frames
```

`stderr` for all 25 is byte-identical; `esc_fn`, `rc`, assert bytes and every
pinned key are unchanged. `CASES` and `SPLICE_CELLS` blocks compare
byte-identical; `love_probe/` is untouched.

I also validated the author's **baseline choice**, which is the non-obvious
part: the r75-author run dirs are pre-fold, and comparing against them would
have produced 5 false drifts — each of the 4 r75 run dirs differs from the
post-fold freeze in exactly
`bc_setpos_wp`, `bc_setpos_unp`, `bc_newbody_unp`, `bc_destroy_unp`,
`bc_setvel_unp` (20/25 match). The author's statement "all r75 run dirs
predate the folds" is confirmed, and `ddd455b` is the right reference.

### 4.5 Author-flagged risks

- **Trajectory pin sensitivity** (`pre_retfalse1.final.b1pos`,
  `bc_jwatch.final.bc/ec/pre/post` + `after_update.b1pos`): verified
  bit-identical over 6 independent run dirs on this host. The "sensitive to
  solver drift on other builds" half is a bounded warning I cannot falsify
  here — but it is **fail-loud**: those pins are checked by the battery, so
  drift is a FAIL, and **none of them feeds the class decision** (the
  class-carrying pins are step-local: `after_update.b1vel`/`b1pos`,
  `rf1counts`, `cb_retfalse.returned`). No silent-pass path.
- **cb-order dependence** (`jwlive.cb=post`, `jwdrop.cb=ec`): stable ×6
  here; `jwlive` is last-wins by construction. A build with different
  callback order would fail the *pin* loudly while the *bound* (jcount 1
  through the last step-73 callback → 0 at update-73 return) still holds —
  the disposition the author records is correct. Note the probe's inline
  comment states the looser bound (last step-73 cb → first step-74 cb);
  the report and the `jdrain` line give the tighter, receipt-supported one.
- **Dispatch ordering**: verified, §3.
- **SayGoodbye absence**: the census is real and line-exact — the
  `w_World_functions` table (`wrap_World.cpp:229-256`) lists exactly the 24
  entries the author enumerates, with no destruction-listener hook, and the
  internal `World::SayGoodbye` overloads (`World.cpp:212-225`) only
  invalidate wrapper objects. "No other code drains in that window" remains
  a source-anchored inference, correctly marked as such.

### 4.6 Source anchors — line-exact, verified against the pinned tree

`/tmp/r74bsrc/love-11.5` (the r75-boundary tree): `World::destroy` lock →
`destructWorld = true; return;` at **578-581** ✓; `World::update` epilogue —
body drain 277-282, fixture drain 283-288, joint drain **289-294**,
`destructBodies/Fixtures/Joints.clear()` 295-297, `if (destructWorld)
destroy();` at **299-300** ✓; `Joint::destroyJoint` deferral
(`IsLocked()` → `destructJoints.push_back`) `Joint.cpp:165-173` ✓ — this is
what makes the jwatch bound engine-anchored rather than merely inferred;
`luax_checkbody` `wrap_Body.cpp:31-37` ✓; `luax_checkworld`
`wrap_World.cpp:30-36` ✓; `w_World_isDestroyed` uses `luax_checktype`, not
`luax_checkworld` (`wrap_World.cpp:204-209`) ✓ — which is why
`wdrained`/`post_destroy2.isDestroyed` survive a dead handle while
`getBodyCount` does not; `World.cpp:98 lua_call(L, args, 0)` ✓ (the
preSolve return is not consumed — the r75 anchor underpinning
`pre_retfalse1`'s `ignored`); `b2Settings.cpp:51` assertion throw ✓.

## 5. Residual risk and verification gaps

1. **F1's vacuity** is latent; if a future receipt producer ever emits
   `abortq.count` and `abortq.b1pos` on separate lines, the pose conjunct
   stops carrying evidence. One-line fix.
2. **Trajectory pins are host/build-scoped by construction.** The bounded
   claim I can support is: deterministic on this host, LÖVE 11.5,
   LuaJIT 2.1.1788460057, 6 independent run dirs. Cross-build stability is
   untested and untestable here.
3. **The `deferred_abort` class rests on one cell** (one armed shape, one
   process family). The gate is fail-closed, but the class has no second,
   independently-shaped witness (e.g. a queued *joint* destroy + abort).
   Not a defect — a frontier note for the next round.
4. **`ecunl` is dd_mode-only and un-tagged in the classifier**: the gate
   requires `ecunl.locked == "false"` but the classifier cannot distinguish
   a drain-synthesized EC from any other `locked=false` EC. On this build
   that equivalence is forced (callbacks only fire inside `World::update`,
   and the natural ECs pin at `locked=true`), so it holds — but it is a
   probe-side property the classifier inherits rather than verifies.
5. **`died` is a coarse class**: its discrimination is carried entirely by
   pins (`rc`, `done`, `assert_txt`, `err_on`, `esc_fn`, `wdrained`). A
   different crash shape that happened to match those pins would pass; the
   `esc_fn` pin is what makes that unlikely.
6. **Working-tree state** (not mine, left untouched): `M
   corpus/live/r72-simplifier/snapshots/log.txt` and `…/watch.log`
   (mtimes 12:35 / 11:57 local, before this seat's first run at 15:32),
   pre-existing untracked `corpus/live/r73-*`, `corpus/live/integrator-r7*-*`,
   and `corpus/fixtures/__pycache__/run_battery.cpython-314.pyc` (13:05).
   My scratch instrumentation created and then removed one untracked file,
   `corpus/fixtures/__pycache__/love_battery.cpython-314.pyc`; the directory
   is back to its pre-session contents, and no tracked file was modified
   (`git status` shows no fixture/report changes from this seat).
7. **Not verified by me** (out of this seat's reach, stated so it is not
   read as verified): cross-host/cross-build determinism; the claim that
   LOVE exposes no other destruction-notification surface beyond the
   method-table census (census verified; exhaustiveness of the census
   argument is the author's).

## 6. Recommendation

**No blocking finding.** The diff is insertion-only in the pinned-content
sense it claims, the new class is earned and fail-closed, prior-cell
identity is exactly as accounted, and every new pin is backed by a receipt I
reproduced myself in fresh processes. F1 (one-line conjunct hardening) and
F2/F3 (doc/anchor nits) are worth folding in the next pass; none of them
changes a current verdict. This is a seat recommendation, not an admission
— the canonical runtime remains the sole judge.
