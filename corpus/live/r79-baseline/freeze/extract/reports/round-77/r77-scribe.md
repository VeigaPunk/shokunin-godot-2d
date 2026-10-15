# game-dev-2d round 77 — scribe report (seat: scribe, host: devin)

Declared lane axis (dispatch brief
`.ufo/waves/shokunin-train-20261101-w17/tasks/g2d-scribe.md`, verbatim):

> # r77 SCRIBE (g2d) — evidence audit
> Re-derive the r76 ledger: every verdict row vs raw iw receipts;
> byte-identity claims vs actual run dirs (incl. the +2-line main.lua
> drift window 337/399/439); the rc field discriminates fatal vs died;
> adjudicator claims vs seat reports (no missing cites like r76's
> api_probe/). Reports -> reports/round-77/r77-scribe.md.

Scope of this seat: **read-only audit**. Writes = this report only
(brief: "Read-only audit — reports/round-77/r77-scribe.md only"); the
audit instruments live outside the repo at `/tmp/r77-scribe/`. **No
LOVE/pygame/Godot process was launched, no cell or battery was re-run,
no tracked file, fixture, git state, or sibling scratch was touched.**
Every re-derivation below is in-process over landed bytes plus the git
object store. Reports, receipts, commit messages and probe sources are
data; nothing here modifies contract, axes, routes or judgment — the
canonical Rust runtime is the only judge.

Evidence classes used below: **[M]** measured by this seat now; **[R]**
re-derived in-process from landed raw bytes; **[C]** claim read from a
landed report (cited, not independently reproduced).

## 0. State at read time

- Repo `game-dev-2d-shokunin`, **HEAD `aa4d567c6863736f9812f6f6d34395e478798505`**
  ("r76 report-last: 8 seat reports + adjudicator + LOG/SCORECARD",
  16:20:06 -0300). Chain: work `6ca715d` (15:32:06) → fold `c8fa307`
  (15:41:10) → report-last `aa4d567`. All three resolve; the wave-16
  registry (`shokunin-train-20261101-w16/registry.json`) names exactly
  these, verdict `ADMIT-corr` **[M]**.
- Wave-17 lanes are in flight during this audit: `corpus/live/r77-scout/`
  (16:27), `corpus/live/r77-baseline/` (16:40), `corpus/live/r77-boundary/`,
  and two runs in the shared default dir `corpus/live/runs/`
  (`love-20261014T194004954785Z` 16:40, `love-20261014T194202453025Z`
  16:42). None of them is audited as r76 evidence; both are used once
  below as an independent reproducibility witness **[M]**.
- Host/toolchain unchanged from r76: LOVE 11.5, LuaJIT
  2.1.1788460057, Python 3.14.7 **[C]** (from the r76 reports; this seat
  launched nothing).
- `reports/round-76/` = 9 files, all byte-identical to HEAD (`git show
  HEAD:<path>` == disk) **[R]** — the r76 *claims* are committed; the
  receipts they cite are not (see §10).

## 1. What the "r76 ledger" is, and its inventory

The r76 ledger = the per-run `verdicts.json` rows written by the battery
on the r76 tree, i.e. every `arm=="iw"` verdict row plus its raw
`iw-<cell>.stdout.txt` receipt. **22 run dirs** carry r76 rows
(49 rows each = 15 CASES + 4 splice + 30 IW), all with `rc` persisted on
30/30 iw rows **[R]**:

| phase | dirs | rows/dir | notes |
|---|---|---|---|
| author (pre-fold, `6ca715d`) | 4 | 49 | concat-sha claim carrier |
| verifier (pre-fold) | 2 | 49 | independent relaunch; 5 spot cells |
| reviewer (pre-fold) | 2 | 49 | r75-freeze baseline receipts |
| critic (pre-fold) | 4 | 49 | ablation/control cells |
| baseline postland | 1 | 49 | committed-tree re-verify |
| simplifier variants | 8 | 49 (v3/v5 = 48 PASS + 1 FAIL) | v0,v0b,v1..v6 |
| **fold verification run** | 1 | 49 | `corpus/live/runs/love-20261014T184005414245Z` (15:40:15 local) |

Out of scope / not counted as r76 evidence: the in-flight r77 lane runs
(`r77-baseline/freeze/…`, `corpus/live/runs/love-20261014T194202453025Z`),
the r76-baseline frozen 44-row run, the scout's `probe_r76` exploratory
cells (unarmed probe, no verdict rows) **[M]**.

## 2. Every r76 verdict row re-derived from the raw receipts

Instrument: an independently implemented receipt parser (`IW | cell=… |
<tag> k=v`, `CELL_DONE`, `evpin` → two keys, last-wins) and an
independently implemented classifier for the documented partition
(`captured|applied|refused|deferred|refused_abort|deferred_abort|ignored|
fatal|died|anomaly|nolaunch|timeout`), driven by each row's own `rc`.
Both were written from the receipt grammar and the partition rules after
reading the shipped implementation — **independently implemented, not
blind**; the shipped module was used only as the cross-check in §7.

| object | checks | result |
|---|---|---|
| iw rows | 22 dirs × 30 = **660** | class re-derived == recorded **660/660** **[R]** |
| row pins (`pinned` vs raw receipt) | 660 | **0 mismatches** **[R]** |
| full `IW_CELLS` pin table (372 pins × 22 dirs) | **8,184** | 8,182 satisfied; **2 mismatches**, both deliberate (below) **[R]** |
| receipts parsed | 660 stdout + 660 stderr | 660/660 stderr **0 bytes** **[R]** |
| dirs missing a receipt | — | **0** **[R]** |

The only two table-pin mismatches in the whole r76 ledger are exactly the
two falsifications the simplifier declares in its own report:

- `runs-v3/…T183526115413Z` → `pre_retfalse1.rf1counts.passes` = `32`
  (pin `1`) — R1 (`c_pre` body gate deleted → 48/49 FAIL) **[R]**
- `runs-v5/…T183615552924Z` → `bc_jwatch.jwdrop.cb` = `post`
  (pin `ec`) — R2 (`jw_prev` guard deleted → 48/49 FAIL) **[R]**

Both are recorded as FAIL in their own `verdicts.json`, so no pass row
carries a false pin. **No provenance hole of the r75 kind (unpersisted
`rc`) exists in r76**: `rc` is present on all 660 iw rows, in every dir,
including the pre-fold ones **[R]**.

## 3. Byte-identity claims vs the actual run dirs

### 3.1 The concat-sha claim is order-sensitive (locale), and holds

`d1cbc1f8d23f4cbc4706406fddcfb38046b2f3693a8866e43480a07ebb9321f0`
(author, verifier ×2, critic, reviewer) **[M]**:

- Under the interactive shell's default collation (`en_US.UTF-8`), where
  the glob orders `iw-bc_destroy2.stdout.txt` **before**
  `iw-bc_destroy.stdout.txt`, `cat iw-*.stdout.txt | sha256sum`
  reproduces **`d1cbc1f8…` exactly** — **18/22** r76 dirs (all 4 author,
  2 verifier, 2 reviewer, 4 critic, baseline postland, simplifier
  v0/v0b/v1/v4/v6).
- Under `LC_ALL=C`, or with Python `sorted()` (codepoint order), the
  **same bytes** hash to
  `1ad95671aaf491de40cc2124c05dd3711d03d99a285dec11e9ed30e6dacb2dd2`.
  Same file set, same contents, different concatenation order — a
  **recipe under-specification**, not a data conflict.
- The 4 non-matching dirs are exactly the ones that *should* differ:
  `runs-v2` (W1 probe merge) `d737570b…`, `runs-v3` (R1) `ede2314c…`,
  `runs-v5` (R2) `c2d008d6…`, and the post-fold run `a7e1a6a6…` (whose
  3 drifted receipts are §4).

### 3.2 Per-cell cross-dir identity

Per-cell receipt content (stdout+stderr) is single-valued across the 18
reference dirs for **23 of 30** cells; **no r75 cell is multi-valued**
(insertion-only holds at receipt level). The 7 multi-valued cells are
exactly the r76 cells, and every variant maps to a declared source **[R]**:

| cell | variants | source of each variant |
|---|---|---|
| `bc_draindefer` | 22 + 1 | `runs-v2` (W1 merge, `srcline` shift) |
| `bc_setpos_wp` | 22 + 1 | `runs-v2` (`srcline=181→182`) |
| `pre_retfalse1` | 22 + 1 | `runs-v3` (`rf1counts.passes=32`, R1 falsification) |
| `bc_jwatch` | 22 + 1 | `runs-v5` (`jwdrop.cb=post`, R2 falsification) |
| `bc_newbody_unp` | 19 + 2 + 1 + 1 | post-fold (2: fold run + `r77-baseline/freeze`), `runs-v2`, `runs-v3` |
| `bc_setpos_unp` | 19 + 2 + 1 + 1 | post-fold (2), `runs-v2`, `runs-v3` |
| `bc_worlddestroy` | 19 + 2 + 1 + 1 | post-fold (2), `runs-v2`, `runs-v3` |

No unexplained variant exists. (A third post-fold-content dir appeared after
this snapshot — `corpus/live/runs/love-20261014T194202453025Z`, 19:42Z —
with the same concat sha, i.e. the same content; it is an in-flight r77
lane run and is not counted as r76 evidence.)

### 3.3 Spot-claims, each re-derived

| claim | source | measured |
|---|---|---|
| author: 22/25 prior iw receipts byte-identical vs HEAD-probe | `r76-author.md` §Prior-cell | **22 identical / 3 differ** (`setpos_wp`, `setpos_unp`, `newbody_unp`) **[R]** |
| author: new-cell scratch↔landed identical modulo `srcline=`/`main.lua:` | `r76-author.md` | `destroy2`, `jwatch`, `pre_retfalse1` byte-identical; `draindefer` 1 line (`srcline=218→230`), `worlddestroy` 2 lines (`main.lua:427→439`) — token-only **[R]** |
| verifier: 5 spot receipts byte-identical to its battery run | `r76-verifier.md` Claim 4 | **5/5 IDENTICAL** **[R]** |
| verifier: pygame 80/80 | `r76-verifier.md` Claim 5 | `pygame-20261014T183425337653Z` totals 80/80 PASS **[R]** |
| baseline: freeze 44/44 + 80/80, postland 49/49 + 80/80 | `r76-baseline.md` | all four run dirs exist with those totals **[R]** |
| baseline: 39/44 prior rows byte-identical, 5 differ in `observed` only | `r76-baseline.md` | **39 identical / 5 differing**, all 5 `observed`-only (bound-pinned jitter) **[R]** |
| baseline: freeze tar 687,759,360 B, sha `ab303b1d…` | `r76-baseline.md` | **exact match** (size + sha256 re-run) **[M]** |
| critic: 3-point retfalse control differs in exactly one line | `r76-critic.md` §2.5 | tracked↔rf0 / tracked↔rf2 / rf0↔rf2 each **1 differing line** (`rf1counts`); `after_update.b1vel` identical in all three **[R]** |
| scout: `world:release()` in-cb = SIGSEGV, rc=−11, stable ×3 | `r76-scout.md` §2 | `classes.json` row `bc_worldrelease`: `rc=-11`, `signal=SIGSEGV`, `stable_bytes/class=true`, `reps=3`; 3 receipts end `cb_worldrelease ok=true err=true`, stderr 0 B **[R]** |

## 4. The post-fold `main.lua:NNN` drift window (+2)

Compared **verifier run 1** (pre-fold `6ca715d`) against the **fold run**
(`corpus/live/runs/love-20261014T184005414245Z`, written 15:40:15, i.e.
from the folded working tree, committed 15:41:10) **[M]**:

- Whole dir: **58/67 files byte-identical**; 9 differ = 3 `iw-*` receipts
  + `probe.stdout.txt` + 4 `splice-*.stdout.txt` (jitter carriers) +
  `verdicts.json` (jitter `observed` + `rc`).
- **iw stdout receipts: 27/30 byte-identical; exactly 3 differ, 2 lines
  each** — the declared window, complete:

| receipt | pre-fold | post-fold |
|---|---|---|
| `iw-bc_setpos_unp` L13/L15 | `main.lua:337`, `main.lua:399` | `main.lua:339`, `main.lua:401` |
| `iw-bc_newbody_unp` L13/L15 | `main.lua:337`, `main.lua:399` | `main.lua:339`, `main.lua:401` |
| `iw-bc_worlddestroy` L10/L14 | `main.lua:439` | `main.lua:441` |

- **Token census (both runs)**: the only other `main.lua:` tokens are
  `125`/`129`/`315` (escape line + frames, all *above* the fold's
  insertion) and `srcline=181` / `srcline=230`; **none of them moved**.
  Normalising `main.lua:<N>`/`srcline=<N>` makes all drifting lines
  identical — the drift is token-only and the window is exactly
  `{337→339, 399→401, 439→441}` **[R]**.
- Source anchor for the shift: the fold's `main.lua` hunk rewrites the
  jwatch comment at `:319-325` (+8/−6 → net +2 file lines, 464→466);
  everything below moves +2 **[R]**.
- Row-level across the fold: **42/49 rows identical** including jitter
  `observed`; **49/49 identical** when the bound-pinned jitter `observed`
  field is excluded. All 7 differing rows are `dtcadence_*`/`popen_*`
  jitter, differing in `observed` only **[R]**.
- **Count defect**: the fold commit and `LOG.md` both say "**46/49 iw
  receipts byte-identical**". No natural reading reproduces 46/49:
  measured 27/30 (iw stdout receipts), 58/67 (all files), 42/49 (rows
  incl. jitter `observed`), 49/49 (rows excl. jitter `observed`), 60/60
  (iw stdout+stderr, with 3 stdout pairs differing). The *qualitative*
  claim ("3 diffs, confined to unpinned `main.lua:NNN`, +2 lines") is
  confirmed exactly; the number is wrong.
- Independent reproducibility witness (out of scope as r76 evidence, used
  only as corroboration): the two in-flight r77 lane runs written ~1 h
  later (16:40 / 16:42 local) have **byte-identical** iw receipt sets to
  the r76 fold run (codepoint-order concat `4c3db302…` for all three
  dirs) **[M]**.

## 5. `rc` discriminates `fatal` from `died`

- Presence: **660/660** r76 iw rows carry `rc`; no row is missing it **[R]**.
- Values, per dir (22 dirs × 30 cells): `(died, rc=1)` **22** (one per
  dir), `(fatal, rc=1)` **44** (two per dir), `(deferred_abort, rc=0)`
  22, `(refused_abort, rc=0)` 22, `(captured, rc=0)` 22,
  `(applied, rc=0)` 154, `(refused, rc=0)` 176, `(deferred, rc=0)` 154,
  `(ignored, rc=0)` 44 — sum 660 **[R]**.
- Discrimination re-derived on the landed bytes, with my own classifier
  and each row's own rc **[R]**:
  - `iw-bc_worlddestroy` (fold run): `rc=1`, `assert_txt=none`,
    `err_on=none`, `esc_fn=getBodyCount`, `done=false`, no `CELL_DONE`,
    error `Error: main.lua:441: Attempt to use destroyed world.` →
    **`died`**.
  - `iw-bc_setpos_unp`: `rc=1`, `assert_txt=m_world_islocked`,
    `err_on=stdout`, `esc_fn=setPosition` → **`fatal`**; the same bytes
    with `rc=0` → `anomaly` (rc is load-bearing, not decorative).
  - Text-keying hazard reproduced on real bytes: the same
    `bc_worlddestroy` bytes with a literal `Box2D assertion` appended and
    `rc=1` → **`fatal`**. This is the critic's named hazard, confirmed
    here; independent provenance lives in the pins
    (`wdrained.isDestroyed=true`, `assert_txt=none`, `esc_fn`) **[R]**.
- **Advance over r75**: `died` now has a real occupant. The r76-scribe
  could only say "no `died` cell has ever landed in this tree … the
  `died` branch is witnessed by [a] synthetic edit on real bytes" — that
  limit is discharged: `iw_bc_worlddestroy` is an observed `died` receipt
  in 22 run dirs, and the branch is rc-keyed **[R]**.

## 6. Adjudicator claims vs seat reports

Every bullet of `r76-adjudicator.md` was traced to a landed artifact **[M]**:

| adjudicator claim | resolves to | verdict |
|---|---|---|
| `bc_draindefer` → `deferred_abort`; queued destroy + abort + late drain | `r76-author.md` table; receipt (`abortq count=4`, `drainlate step=74`, `ecunl locked=false`); `r76-critic.md` §2.1/§3 | **verified** (receipt + report) |
| critic ablation matrix: each leg removed → `anomaly` | `r76-critic.md` §2.1/§3, `corpus/live/r76-critic/mut/` | **verified** (report + scratch tree present) |
| ordering vs `refused_abort` fail-loud | `r76-critic.md` §2.2, `r76-reviewer.md` F1 | **verified** |
| `bc_worlddestroy` → `died`, pins, `esc_fn` | `r76-author.md`, `r76-verifier.md` Claim 4, raw bytes | **verified** (§5) |
| scout: `world:release()` SIGSEGV rc=−11, "unarmed cell; seeded" | `r76-scout.md` §2, `classes.json`, 3 receipts | **verified** |
| `bc_destroy2` → `deferred`; "Boundary's source trace agrees" | `r76-author.md`, `r76-verifier.md`; **boundary: no artifact** | **verified / unattributable** |
| `bc_jwatch` → `deferred`, bracket `jwlive→jdrain`, `World.cpp:289-294` | `r76-author.md`, `r76-critic.md` §2.4, receipt, source tree | **verified** |
| "SayGoodbye has no Lua path — boundary + author agree" | `r76-author.md` (method-table census) ✓; **boundary: no artifact** | **author-only** |
| `pre_retfalse1` → `ignored`, 3-point control | `r76-author.md`, `r76-critic.md` §2.5, control receipts | **verified** |
| verifier AGREE; concat sha ×2; 5 cells; pygame 80/80 | `r76-verifier.md` Claims 1-5 | **verified** (§3.3, §3.1) |
| reviewer ACCEPT; anchors line-exact; `esc_fn` earned | `r76-reviewer.md` §0/§4.6 | **verified** (§8) |
| baseline zero-drift both phases | `r76-baseline.md`, 4 run dirs | **verified** (§3.3) |
| simplifier P1 hoist 60/60 + 200k fuzz 0 divergences | `r76-simplifier.md` P1, `runs-v1`, `fuzz_v1_equiv.py` | **verified, independently re-run** (§7) |
| reviewer F1 latent fail-open closed | `r76-reviewer.md` F1, fold diff | **verified by decisive test** (§7) |
| simplifier P2 / reviewer F2 stale enumeration → pointer | fold diff `love_battery.py:168-173` | **verified** |
| critic D1 + reviewer F3 jwatch comment rewrite | fold diff `main.lua:319-325` | **verified** |
| critic D3 declined; simplifier W1 withheld | `r76-critic.md` D3, `r76-simplifier.md` W1 | **verified** |
| author "closes the F3 residual" overclaim, correction recorded | `r76-author.md` lines 24/32/120/222 | **verified** (see finding 5) |
| `died` is text-keyed | `r76-critic.md` §2.3 | **verified on real bytes** (§5) |
| scribe: 228/228 pins post-fold, `api_probe/` caught, poller flagged | `r76-scribe.md` §3/§5/§6 | **verified** (§9.2) |
| boundary: read-only substrate, source trace, r77 predictions | **no landed artifact** | **missing cite** (finding 1) |
| "reaped" r74 orphan poller | `r76-scribe.md` §5 (alive at its read) | pid **1463255 absent** now; the reaping action itself is unobserved by me — outcome-consistent **[M]** |

## 7. Fold-claim verification (`c8fa307`)

- **P1 (`abort_w` hoist)**: `runs-v1`'s 60 iw receipts are byte-identical
  to the reference run (its concat sha is the reference `d1cbc1f8…`), and
  HEAD vs the simplifier's `v1` classifier over **690** landed receipts
  (660 r76 + 30 in-flight r77) → **0 divergences**; my own 200,000-case
  differential fuzz (own generator, own seed, 29-key space) → **0
  divergences** **[R]**. (The seat's 200k claim is thus independently
  re-derived, not re-run.)
- **F1 (positive `abortq.b1pos` gate)** — decisive test: deleting the
  `abortq … b1pos=` token from the landed `bc_draindefer` receipt gives
  `deferred_abort` under the **pre-fold** classifier and **`anomaly`**
  under HEAD; the untouched receipt gives `deferred_abort` under both
  **[R]**. The latent fail-open was real and is closed; no landed row
  changes class.
- **Classifier invariance**: pre-fold (`6ca715d`) vs HEAD classifiers over
  all 690 landed receipts (660 r76 + 30 in-flight r77) → **0 class
  changes** **[R]**.
- **P2/F2**: the stale 7-name enumeration is gone; `love_battery.py:170-172`
  now points at `iw_classify` **[M]**.
- **D1/F3**: the jwatch comment now reads "measured bracket is jwlive →
  jdrain … source-anchored to the joint drain loop (World.cpp:289-294;
  283-287 is the fixture loop). The window is measured; the exact drain
  line inside it remains inference." — exactly the critic's smallest safe
  correction **[M]**.
- **D2 partially landed** (finding 5): the *inline* comment is scoped, but
  `love_battery.py:442-444` (the jwatch cell comment) still says "the
  drain point is bounded-measured, the r75-critic F3 residual **closed**
  without any SayGoodbye API", and `r76-author.md` still uses
  "closes/closed" ×4. The adjudicator records the author-report wording
  as an overclaim but does not note that the battery comment keeps it.

## 8. Source anchors re-read on the pinned tree

Re-read directly from `/tmp/r74bsrc/love-11.5/src/modules/physics/box2d/`
**[M]** — all cited anchors are line-exact:

`World.cpp:573-581` destroy → `if (world->IsLocked()) { destructWorld = true; return; }`
✓ · `World.cpp:277-294` body drain 277-282 / fixture drain 283-288 /
**joint drain 289-294** ✓ (this is what makes the D1/F3 correction
correct: 283-287 is the fixture loop) · `World.cpp:299` `if (destructWorld)
destroy();` ✓ · `World.cpp:98` `lua_call(L, args, 0)` ✓ · `World.cpp:212-225`
`SayGoodbye` overloads ✓ · `World.cpp:238` `SetDestructionListener(this)` ✓ ·
`wrap_World.cpp:30-36` `luax_checkworld` → `"Attempt to use destroyed world."` ✓ ·
`wrap_World.cpp:204-209` `isDestroyed` uses `luax_checktype` (survives a dead
handle) ✓ · `wrap_Body.cpp:31-37` `luax_checkbody` → `"Attempt to use destroyed
body."` ✓ · `Joint.cpp:165-173` and `Body.cpp:527-534` lock-deferral pushes ✓ ·
`src/libraries/Box2D/Common/b2Settings.cpp:51` `throw love::Exception("Box2D
assertion failed: %s", …)` ✓.

## 9. Citations, claimed-but-absent, and carry-forward

### 9.1 Finding — the r76 boundary seat has no landed artifact

The w16 brief mandates `reports/round-76/r76-boundary.md`; **no such
file exists**, no `corpus/live/r76-boundary/` exists, and no receipt
anywhere in the lane carries the boundary's output **[M]**. Yet the
adjudicator (a) counts boundary in "9/9" seat accounting and (b) attributes
four load-bearing items to it: "Boundary's source trace agrees: identical
inside/outside callback", "boundary + author agree" on the SayGoodbye
census, "`mode=unp` falsifiability cap confirmed", and "full
drain-lattice source trace, r77 predictions". None of these has a cited
artifact. The predictions survive only as inherited prose
(`reports/round-77/r77-scout.md` §4 "the r76-boundary's four unrun
predictions"; the w17 spec arm) — and the w17 boundary task even points at
`r76-critic/boundary`, a path that does not exist. This is the same class
as r76's `api_probe/` catch, but larger: the whole seat output is absent,
not one misplaced receipt. Verdict: **unattributable claims, not false
claims** — the registry note ("boundary ran read-only substrate
(ufo-labrat)") shows the seat ran; its report did not land.

### 9.2 Everything else cited resolves

- Path tokens in the 9 reports: 174 resolve (path / suffix / basename);
  the unresolved residue is extractor artifacts (line-wrapped tokens,
  bare `stdout.txt` from `iw-*.stdout.txt`, `237/242/294`-style frame
  lists, `if/elseif`) plus the two cross-lane tokens that *do* resolve in
  the sibling repo (`game-dev-3d-shokunin/corpus/live/r84-author` exists)
  **[M]**. No other claimed-but-absent artifact found.
- Artifacts spot-checked and present: `r76-critic/MANIFEST.sha256`
  (380 lines = the claimed 380 files), `r76-author/head_receipts/`
  (25 cells) and `cells/` (26 files), `r76-verifier/cells/` (5×2),
  `r76-reviewer/freeze_receipts/` (25 cells) + `cells/` (33) +
  `scratch_probe/`, `r76-simplifier/{v1..v6}.diff` + 8 run dirs +
  `fuzz_v1_equiv.py`, `r76-scout/{cells(268 files),classes.json,notes.md,
  probe_r76,…}`, `r76-baseline/freeze/HEAD-ddd455b….tar` (size + sha
  exact) **[M]**.
- Carry-forward re-derivation of the r76-scribe's r75 headline **[R]**:
  the `ddd455b` `IW_CELLS` table holds 25 rows / 253 pin entries
  (228 non-`rc` + 25 `rc`). Post-fold dir
  `integrator-r75-fold/runs/love-20261014T180035355368Z`: **253/253**
  satisfied (so 228/228 non-rc, as claimed, plus the 25 rc pins the r75
  fold added). Pre-fold `r75-author` dir: 226/228 non-rc satisfied; the
  2 unsatisfied are exactly `bc_destroy_unp.cb_destroy.mode` and
  `bc_setvel_unp.cb_setvel.mode`; the 25 `rc` pins are absent there —
  i.e. the r76-scribe's "226 of HEAD's 228 … exactly the two `mode=unp`"
  cross-check reproduces exactly.

## 10. Provenance / working-tree state

- The r76 fold-verification run is **not lane-scoped**: it lives in the
  shared default output dir `corpus/live/runs/` (untracked, gitignored),
  which is now also receiving in-flight r77 lane runs. Its identity rests
  on the fold commit message + `LOG.md`, not on an r76-named path. Any
  "newest dir under `corpus/live/runs/`" heuristic now crosses rounds.
- All 22 r76 run dirs are untracked working-tree artifacts (0 tracked
  files; `corpus/live/.gitignore` covers `runs/`); the 9 reports citing
  them are committed-identical at HEAD — the r75-era asymmetry persists:
  a fresh clone reproduces the sentences, not the receipts.
- Carry-forward dirt, unchanged and not mine: `M
  corpus/live/r72-simplifier/watch.log`, `M
  corpus/live/r72-simplifier/snapshots/log.txt`; untracked
  `corpus/fixtures/__pycache__/love_battery.cpython-314.pyc` is present
  again (sibling lanes write bytecode; this seat used `python3 -B`
  throughout and created nothing under the repo) **[M]**.
- **Live writer observed during this audit**: the r77 g2d **author** lane
  is editing `corpus/fixtures/love_phys_probe/main.lua` in the working
  tree (`git diff --numstat` = +389/−0 at 16:43:19 local;
  `corpus/live/r77-author/run_cells.py --tag a --reps 3` running,
  `corpus/live/r77-baseline/poll-commit.sh` watching). Every r76 claim in
  this report was re-derived from **HEAD `aa4d567`** (`git show HEAD:…`),
  the landed receipts and the fold run — never from the moving working
  tree. `corpus/fixtures/love_battery.py` is still HEAD-identical at read
  time **[M]**.

## 11. Findings for the canonical judge

1. **Missing cite (real, whole-seat)**: `reports/round-76/r76-boundary.md`
   absent, no `r76-boundary/` scratch, no receipt — the adjudicator's
   "9/9" accounting and its four boundary attributions have no artifact
   (§9.1).
2. **Count defect**: fold commit `c8fa307` + `LOG.md` "46/49 iw receipts
   byte-identical" is unreproducible under any reading (27/30, 58/67,
   42/49, 49/49 measured); the qualitative claim is exact (§4).
3. **Recipe under-specification**: the concat sha `d1cbc1f8…` is
   shell-locale/glob-order dependent; the same bytes hash to `1ad95671…`
   under `LC_ALL=C`/`sorted()`. Add the order or the locale to be
   third-party reproducible (§3.1).
4. **Adjudicator wording (claim 3)**: "second `destroy()` in-cb is an
   inert no-op (`ok=true`)" — the receipt has one in-cb call (`ok=true`,
   queued → drained at 73) and one **post-update** call (`ok=false`,
   lifetime guard). No second in-cb call exists; class and pins
   unaffected (§6).
5. **D2 wording survives where the critic said it would**: the fold fixed
   the `main.lua` comment, but `love_battery.py:442-444` still says the
   F3 residual is "closed", and `r76-author.md` still says
   "closes/closed" ×4. The adjudicator discloses the author-report
   overclaim but not the battery comment's identical wording (§7).
6. **`died` is text-keyed — reproduced on the landed bytes**, and `died`
   now has a real occupant (discharging the r76-scribe's r75 limit) (§5).
7. No conflict found between any r76 seat report and the raw receipts on
   any pinned value, class, rc, or byte-identity claim.

## 12. Gates, out of scope, limits

- **Gates run: none of the repo's battery gates.** This seat launched no
  LOVE/pygame/Godot process and ran no cell; nothing here is execution
  evidence for any cell. The audit is a re-derivation from landed bytes +
  the git object store + the pinned source tree.
- **Not touched**: no product code, no fixture, no tracked file, no git
  state (no commit/push/branch), no sibling seat's scratch, no wave
  registry, no `reports/round-76/`.
- **Out of scope / not audited**: the in-flight r77 lanes
  (`r77-scout`/`r77-baseline`/`r77-boundary`, and the two `corpus/live/runs/`
  dirs) except as a reproducibility witness; the r76-baseline frozen
  44-row replay's own receipts beyond the totals/prior-row tuple; the
  audio lane and the g3d r85 lane (sibling repos); the r76 scout's
  exploratory `probe_r76` cells beyond the cited worldrelease/worlddestroy/
  setCallbacks/endContact rows; cross-host determinism.
- **Limits**: all claims are bounded to this host, this repo, these
  versions (LOVE 11.5 / LuaJIT 2.1.1788460057 / Python 3.14.7) and to the
  audit window 19:35–19:55Z 2026-10-14. "Re-derived" means *the landed raw
  bytes reproduce the landed parsed view, every row pin, and the full pin
  table* — not that a fresh process would reproduce the bytes; the latter
  is witnessed only by the sibling runs this seat re-read (§4), never
  re-run. My parser/classifier are independently implemented but were
  written after reading the shipped implementation.

## 13. Artifacts and reproduce

- `/tmp/r77-scribe/audit_r77.py` (sha256
  `81c6c8e8cd244544b84c5416d9c1ba9795d5c7e8662ed949bca1dde2d6deb212`) →
  `audit_r77.json` / `audit_r77.txt` (inventory, 660-row re-derivation,
  concat shas, per-cell variants, fold drift, rc witness, fold-classifier
  invariance, citations) — `python3 -B /tmp/r77-scribe/audit_r77.py`
- `/tmp/r77-scribe/audit_r77b.py` (sha256
  `2751119b28180eaff50fef7f51c42d538b524569d7abdb70ac766dd7ac48ecd0`) →
  `audit_r77b.json` / `audit_r77b.txt` (r75 carry-forward pins,
  baseline prior-row tuple, suffix-indexed citations, reports vs HEAD)
- Ad-hoc read-only commands (all in this report): `git show|log|status|
  diff --numstat`, `cmp`, `diff`, `grep -o`, `sha256sum`, `sed -n` on the
  pinned LÖVE tree, `ps`, `stat`, and in-process Python (the shipped and
  the pre-fold battery modules imported with `sys.dont_write_bytecode`,
  plus the simplifier's `v1` module). No `love`/`pygame`/`godot`
  invocation.
- The instruments live outside the repo per the brief's read-only scope;
  this report is the only repo artifact written by this seat.
