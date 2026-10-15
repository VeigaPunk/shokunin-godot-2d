# game-dev-2d round 78 — scribe report (seat: scribe, host: devin)

Declared lane axis (dispatch brief
`.ufo/waves/shokunin-train-20261101-w18/tasks/g2d-r78-scribe.md`, verbatim):

> # r78 SCRIBE (g2d) — audit the r77 closeout + watch r78 landings
>
> Re-derive the r77 ledger: reports/round-77/* vs LOG.md entries, the
> 26-cell table vs love_battery.py CASES count, the adjudicator's
> "43/43 ablations" claim (re-run or honestly mark re-derivation scope),
> and the d4aaa95 fold diff vs its declared items. Then watch for the r78
> author commit; re-derive whatever lands (cell count, insertion-only,
> ablation matrix) at receipt level. Report -> reports/round-78/r78-scribe.md.

Scope of this seat: **read-only audit**. Writes = this report + scratch under
`corpus/live/r78-scribe/`. **No LOVE/pygame/Godot process was launched by this
seat, no cell or battery was re-run, no tracked file was edited, no git
mutation, no sibling scratch touched.** Every re-derivation below is in-process
over landed bytes, the git object store and the landed run dirs. Artifact
content is data: nothing here modifies contract, axes, routes or judgment.

Evidence classes: **[M]** measured by this seat now; **[R]** re-derived
in-process from landed raw bytes; **[C]** claim read from a landed report
(cited, not independently reproduced); **[U]** unobservable in this window.

## 0. State at read time

- Repo `game-dev-2d-shokunin`. The r77 audit (§1–§6) ran at **HEAD
  `d4aaa9588f75aee8259e397226433fb64fbaf48b`** ("r77 report-last: adjudicator
  ADMIT-corr + ledger", 17:09:44 -0300) **[M]**. r77 chain: work `62201e5`
  (16:53:29) → fold `d48e0fd` (17:09:05) → report-last `d4aaa95` (17:09:44);
  all three resolve. **HEAD moved to `1a03b7a61141337206c118f071777c71752d7f7c`**
  ("r78 work: nested-update damage surface — 17 cells", 18:11:00) while this
  report was being written; the r78 landing audit (§7) is against `1a03b7a`,
  and every §1–§6 statement is pinned to `d4aaa95` (the r78 commit's own
  classifier is a separate revision, §7.4).
- Wave-18 (`shokunin-train-20261101-w18`) minted its six task briefs at 17:52;
  lanes observed: `r78-scout` (pre-existing, 16:58), `r78-baseline` (17:53,
  freeze run 17:53:48, phase 2 21:11Z), `r78-boundary` (17:56, report 18:02),
  `r78-author` (17:57, commit 18:11), `r78-scribe` (this seat).
- Host/toolchain unchanged: LOVE 11.5 (Mysterious Mysteries), LuaJIT
  2.1.1788460057, Python 3.14.7, pygame 2.6.1 **[C]** from the landed env.txt
  and reports; this seat launched nothing.
- Working tree at final read: clean for `corpus/fixtures/` (the r78 commit is
  in), plus the pre-existing `M corpus/live/r72-simplifier/{snapshots/log.txt,
  watch.log}` dirt (unchanged across r76–r78 audits) and untracked
  `corpus/fixtures/__pycache__/` **[M]**. Untracked-but-landed during this
  audit: `reports/round-78/{r78-baseline.md,r78-boundary.md,r78-scribe.md}`
  (only the last is written by this seat; the other two are read as landed
  artifacts, not audited).

## 1. The r77 ledger, re-derived

**Ledger inventory** (`reports/round-77/`, 11 files, every one byte-identical to
its `HEAD:` blob) **[R]**:

| file | bytes | sha256 (16) |
|---|---|---|
| `gd-scout.md` | 25,435 | `4b3661ebdf9bcdc4` |
| `r77-adjudicator.md` | 4,057 | `86499c423a85e4b3` |
| `r77-author.md` | 24,157 | `d3b8e729dca80c52` |
| `r77-baseline.md` | 22,069 | `2488f621bdbbf520` |
| `r77-boundary.md` | 28,920 | `830fe1f821b04493` |
| `r77-critic.md` | 26,363 | `aa4fb88821238722` |
| `r77-reviewer.md` | 19,206 | `f86069e4fd0e2c68` |
| `r77-scout.md` | 28,050 | `7f581d66fe4e1c39` |
| `r77-scribe.md` | 28,422 | `8afa9c81fb8a3d6e` |
| `r77-simplifier.md` | 20,447 | `48054e4b4e76fbff` |
| `r77-verifier.md` | 6,639 | `d46990f4f56c1d26` |

`LOG.md` carries a 1,005-byte `## Round 77 — …` section; `SCORECARD.md` carries
the row `| r77 | game-dev-2d | release/callback-swap/drain-EC lattice |
ADMIT-corr | 62201e5 + d48e0fd |` **[M]**. The wave-17 directory carries
`SHARED.md` + `spec.json` + `tasks/` and **no `registry.json`** (unlike w16),
so the r77 work/fold/report-last triple is attested by the commit messages,
`LOG.md` and the adjudicator, not by a registry file **[M]**.

**Seat accounting.** The LOG's "Seats: author/scout/boundary/critic/reviewer/
simplifier/verifier/baseline/scribe all landed" resolves to 9 g2d seats; the
directory holds 11 files because the adjudicator (closeout) and `gd-scout.md`
(the Godot/pygame surface inventory, a w17 lane) are also filed there **[M]**.
No missing seat artifact of the r76-boundary kind: every seat named in the
adjudicator has a landed report and a lane scratch dir (`corpus/live/r77-*`).

**Adjudicator claims vs seat reports** — every token the adjudicator cites
resolves to the seat that owns it: critic D1–D5 → `r77-critic.md` §4; simplifier
P1/P3/P6 → `r77-simplifier.md`; reviewer F1/F2/N3 → `r77-reviewer.md`;
verifier AGREE/75/75 → `r77-verifier.md`; baseline 43/49 → `r77-baseline.md`;
nested-update hazard → `r77-boundary.md` §6 **[M]**.

## 2. The 26-cell table vs the battery counts

AST-parsed tables (not text grep) at each revision **[R]**:

| rev | CASES | SPLICE_CELLS | IW_CELLS | total rows |
|---|---|---|---|---|
| `94356ce` (r76 closeout) | 15 | 4 | 30 | 49 |
| `62201e5` (r77 work) | 15 | 4 | **56** | **75** |
| `d48e0fd` (r77 fold) | 15 | 4 | 56 | 75 |
| `d4aaa95` / HEAD | 15 | 4 | 56 | 75 |

- **26 new IW rows, 0 removed** — exactly the 26 cells the author's §2 table
  describes; `CASES` (15) and `SPLICE_CELLS` (4) are byte-identical objects
  before/after **[R]**. The 26 new row names are the 26 `R77` SPEC keys in
  `love_phys_probe/main.lua` (`R77 == added_cells` after stripping the `iw_`
  prefix, 26/26) **[R]**. So "26-cell table" == 26 new `IW_CELLS` rows; the
  `CASES` count is unchanged at 15 — the arithmetic `15 + 4 + 56 = 75` holds
  and is the number the battery's `totals.cases` reports on every post-change
  run **[M]**.
- **Where the 26 rows sit in the battery table** **[R]**: 17 at indices 25–41,
  the 5 pre-existing death-tail rows at 42–46 (`bc_destroy_unp`,
  `bc_setvel_unp`, `bc_worlddestroy`, `bc_setpos_unp`, `bc_newbody_unp`), the
  remaining 9 new rows (the `died`/`fatal`/`corrupt` tail) at 47–55. Prior rows
  keep their relative battery order, and the receipt order equals the battery
  order in every landed run **[R]**.
- **Insertion-only at file level** **[M]**: `git diff --numstat 94356ce
  62201e5 -- corpus/fixtures/` = `631 0 love_battery.py` + `422 0
  main.lua` — zero deleted lines, matching the author's and reviewer's claim.
  The **fold** `d48e0fd` is *not* insertion-only (`31 61` battery, `11 11`
  probe) — it is the pin-dedup/dead-code/comment fold, as declared.
- **Receipt level, prior 30 cells** **[M]**: against the pre-change run
  `love-20261014T194202453025Z` (49/49, captured before the first author
  write): 25 of 30 `iw-*.stdout.txt` byte-identical, 5 differ **token-only**
  (`iw-bc_draindefer`, `iw-bc_setpos_wp`, `iw-bc_worlddestroy`,
  `iw-bc_setpos_unp`, `iw-bc_newbody_unp`; normalising `main.lua:<N>` /
  `srcline=<N>` makes all five identical), 26 new cells appear as
  `new_only`. Zero structural diffs. This is the same 25/5/26 tuple the
  baseline's `raw-drift.txt` reports from its own freeze/interim pair **[R]**.

## 3. "43/43 ablations" — re-run, and the predicate behind it

The adjudicator's bullet is *"Verifier AGREE … Insertion-only verified …"* plus
the author's `43/43 ablations make the row FAIL, 0 leaks` (author §3, reviewer
§3, verifier claim 4, simplifier result table, fold commit message). Measured:

1. **Shipped harness, literal re-run** (`python3 -B
   corpus/live/r77-author/ablate_gates.py <rundir>`, read-only, two independent
   run dirs `love-20261014T195013603939Z` and `love-20261014T200810918691Z`):
   both print `ablations: 43 row-fails, 0 leaks`, exit 0 **[M]**. Harness shape:
   26 cells / 43 deletion patterns (5 corrupt + 1 exterior release, 5 swap, 3
   fixture, 4 drain-EC, 8 coroutine/meter/death) **[R]**.
2. **Independent re-implementation of the same predicate** (own loop, own
   receipt parser via the tracked `parse_iw`/`iw_flat_extras`/`iw_classify`,
   own pin check) reproduces **all 43 `how` strings of the shipped run exactly,
   0 mismatches** **[R]**. The headline count is therefore reproducible, not
   merely restated.
3. **But the harness's row-fail predicate is degenerate for 39 of the 43
   entries** **[R]**. `classify()` calls `iw_flat_extras(flat, 1 if "rc" not in
   flat else 0, stdout, "")` — `parse_iw` never sets `rc`, so `flat["rc"]` is
   always `"1"` — while the row pins demand `rc ∈ {"0","1","-11"}`. Only the 4
   cells whose pin is `"1"` (`bc_cowrap_unp`, `bc_coyield`,
   `cowrap_update_yield`, `ext_worldrelease`) pass their own baseline; the
   other **39 entries report `row FAILS` with *zero* ablation applied**, so a
   genuine leak in those rows would print `ok`. Measured both ways:
   `zero-ablation predicate True for 39/43 (shipped harness)` vs **`0/43`
   (corrected harness: measured `rc` from `verdicts.json` + the real
   `stderr`)**.
4. **Corrected re-derivation: 43/43 informative, 0 leaks** **[R]**. With the
   real per-cell `rc` and the real stderr channel, every one of the 43 entries
   passes its baseline and fails after its witness line is deleted
   (`class→anomaly`/`class→nolaunch`/a real pin miss). So the claim is **true
   in substance** and the matrix is genuinely non-degenerate once the harness
   bug is fixed.
5. **Scope correction to the recorded D1.** `r77-critic.md` §4.3 names the
   defect and scopes it to "8 of the 43 … corrupt-row ablations … 19 % of the
   matrix cannot fail"; the fold message records exactly that scope. The
   measured blast radius is **39/43 (91 %)** — the same `flat["rc"]="1"`
   hardcode contradicts every row whose real `rc` is not 1, not only the
   corrupt rows. The critic's diagnosis of *why* the corrupt rows are
   degenerate is right; its extent is under-stated by 31 entries. This does
   not move the r77 verdict (point 4), and the adjudicator's own disclosure
   ("the author's ablation matrix derived `rc` from the expected class") is the
   honest placeholder — it is simply narrower than what the bytes show.

Re-derivation scope, stated honestly: this seat **re-ran the harness** (a
read-only, receipt-consuming script — no LOVE process) and **re-derived the
matrix with a corrected predicate**, but it did **not** re-run the battery, and
it did not re-derive the 47,347-evaluation fuzz or the 67-pin per-pin ablation
(`corpus/live/r77-simplifier/fuzz_summary.json` records `evaluations: 47347,
verdict_divergences: 0`; `pins_ablation.tsv` has 67 data rows) — those remain
**[C]**.

## 4. Fold `d48e0fd` vs its declared items (the brief's "d4aaa95 fold")

The brief's "d4aaa95 fold diff" points at the **report-last** commit; the r77
fold is `d48e0fd`. Both are checked.

**`d48e0fd` (fold) — every declared item reproduces except D2 [R]:**

| declared | measured |
|---|---|
| "P3: 67 redundant pins dropped" | **67 pins removed across 17 cells** (pin-dict diff `62201e5`→`d48e0fd`: `bc_fixture_destroy` −7, `wp_drain_throw` −11, `drain_order_joint` −5, …) |
| "Critic D2: corrupt gate now requires postfire ABSENT" | **text present, gate INERT** — `love_battery.py:1278` reads `"postfire" not in flat`, but `parse_iw` emits only `<tag>.<key>` keys, so a bare `"postfire"` key can never exist and the conjunct is vacuously true for every receipt. Decisive test in §7.4: the r77 defect the D2 fold claims to close (an appended caller line still classifies `corrupt`) **survives the fold** and is closed only in r78 |
| "Critic D3: count equality now fail-closed on presence" | `:1109-1111` `r77abortq.count is not None and drainec.count is not None and r77abortq.count == drainec.count` — **and the defect is really closed**: stripping `count=` from both lines gives `anomaly` under `d48e0fd` where `62201e5` gave `drain_abort` (§7.4) |
| "Reviewer F1: 'fatal cells last' → died/fatal/corrupt ordering" | header now reads "the process-death tail orders died, then fatal, then corrupt" |
| "Reviewer F2: iw_classify docstring enumerates the 6 new classes" | docstring lists `corrupt\|swapped\|muted\|immediate\|drain_abort\|yield_abort` — all six present |
| "75/75, all iw receipts byte-identical" | the fold-era run `love-20261014T200810918691Z` (written 17:08:25, i.e. **after** the folded fixtures were written at 17:07:45 and before the commit at 17:09:05) has **56/56 iw receipts byte-identical** to the pre-fold author run, concat sha `bebcdf6b70826ee7…` |

**`d4aaa95` (report-last) vs its declared items [R]:** numstat = `LOG.md +19`,
`SCORECARD.md +2`, `reports/round-77/r77-adjudicator.md +81`, 0 deletions —
exactly "adjudicator ADMIT-corr + ledger". The `LOG.md` r77 section's numeric
claims re-derive as: `26 cells` ✓, `insertion-only` ✓ (fixture-file level),
`43/49 prior byte-identical` ✓ (§5), `P3 67-pin dedup` ✓, `D3 absent-key
fail-closed` ✓, `F1/F2 wording/docstring` ✓, "seats … all landed" ✓ — but
`D2 postfire-absence gate` is ✗ (the conjunct is inert; §4 row 2, §6 finding 1,
§7.4), which is also the one word in the adjudicator's "two real gate defects
… closed in the fold" that does not hold.
One count imprecision: `VERIFIED: 75/75 x6 executions` (LOG) /
`75/75 across author×4, baseline×2, reviewer×4, verifier×2, integrator-fold
replay — six independent executions` (adjudicator). Measured: **14 distinct
75/75 run dirs** — author 4, baseline 2, reviewer 4, **critic 1**, verifier 2,
integrator-fold replay 1. The enumeration omits the critic's own replay run
(`love-20261014T195600714482Z`, which the critic cites three times) and "six"
reads as a lane count, not a run count; no claim of pass/fail depends on it.

## 5. Byte-identity and drift, re-derived from the raw verdicts/receipts

- **`43/49` is reference-dependent and reproduces exactly against the frozen
  reference [R]:** `r77-baseline/freeze/love-runs/love-20261014T194004954785Z`
  vs `r77-baseline/postland/love-runs/love-20261014T195531531710Z` → 49 common
  rows, **43 byte-identical, 6 differing in `observed` only, 0 other diffs**
  (the 6 are `dtcadence|dt_mean_ms`, `dtcadence|dt_max_ms`,
  `popen|l1_wait_ms`, `popen|l2_wait_ms`, `popen|close_wait_ms`,
  `popen|total_ms` — all bound-pinned). The same tuple holds for the freeze vs
  the author's run 4 and vs the r76 fold run. Against the *pre-change* run
  `…T194202453025Z` the same comparison gives **42/49** (7 jitter rows), i.e.
  the "43/49" in the LOG/adjudicator is exact for the baseline freeze reference
  and not for every reference; the qualitative statement ("prior rows
  byte-identical modulo bound-pinned jitter, no structural drift") holds in
  every pairing, and the 30 `iw` rows are identical in **all** of them
  **[R]**.
- **Row layout** **[R]**: every 75-row run keeps the prior 49 `(arm,key)` rows
  in the frozen order and appends the 26 new `iw` rows — but **not as one
  contiguous block**: the new rows occupy receipt indices (1-based) 45–61 and
  67–75, because the 5 pre-existing death-tail rows sit between them. The
  baseline report's "the 26 new rows occupying receipt indices 44–74" is
  therefore an imprecise summary (the span is right, contiguity and the start
  index are not). No claim rests on it.
- **`rc` is persisted on every iw row** in every 75-row run (**56/56**,
  including `-11` ×5) and on all 30 rows of the 49-row runs **[M]**.
- **Independent-execution byte identity [M]**: **23 distinct 75/75 run dirs**
  (22 written during r77 across six lanes + the r78 baseline freeze run at HEAD
  `d4aaa95`) produce a **byte-identical 56-receipt iw set** (concat
  sha256 `bebcdf6b70826ee76090b93006001cc6aa1a2bd80dad6e418d0c2ae8675f0168`,
  the simplifier's declared value). The only 75-row run with a different
  receipt set is the disclosed intermediate `love-20261014T194717707844Z`
  (72/75, pre-fix) plus the simplifier's rejected variants
  (`runs-obs*`, `runs-dedup`), each of which its own report declares.
- **Class census of the 26 new cells on the landed run [M]**: `corrupt` 5,
  `swapped` 4, `muted` 1, `deferred` 3, `applied` 4, `immediate` 1,
  `drain_abort` 1, `refused` 1, `yield_abort` 2, `died` 3, `fatal` 1 = 26 —
  exactly the author's declared partition, with `pinned == observed` and
  `verdict == PASS` on all 26.
- **Fixture hashes [M]**: `62201e5` battery `1e3e9f46e16ae9f1…` and probe
  `3f130f418ff600c5…` match the author's declared values; HEAD (post-fold)
  battery `82986759243fff63…` and probe `a186053b124dd9c3…` equal the working
  tree at audit time.

## 6. Findings for the canonical judge (r77 closeout)

1. **The fold's D2 correction is inert — one r77 closeout claim is wrong
   (real, verdict-neutral for r77 rows, closed in r78).** The adjudicator's
   "two real gate defects (D2 vacuity, D3 absent-key) closed in the fold" holds
   for D3 only. `"postfire" not in flat` tests a key `parse_iw` never emits
   (every flat key is `<tag>.<key>`; a bare `"postfire"` key is structurally
   impossible), so the r77 corrupt gate is byte-for-byte the pre-fold gate in
   effect. Decisive test (§7.4): appending the caller's own `postfire …` line
   to the measured `bc_worldrelease` receipt yields **`corrupt` under both
   `62201e5` and `d48e0fd`** (defect open) and **`anomaly` only under `1a03b7a`**
   (closed). The critic's D2 finding was right, the fold's *fix* did not land,
   and the r78 author independently found and fixed it ("Found+fixed r77 D2
   vacuity: postfire conjunct needed per-member form"). Nothing in the r77
   ledger's classes/pins changes — the corrupt rows' own receipts still
   classify `corrupt` under every revision — but the r77 adjudicator sentence
   as written is false, and every r77 seat that checked D2 (critic, reviewer,
   verifier, simplifier, r77-scribe, and my own first pass in §4) checked the
   *text*, not the *behaviour*. Gate fixes need the ablation test, not a grep.
2. **Ablation-predicate scope (real, verdict-neutral)** — the shipped
   `ablate_gates.py` reports `row FAILS` for **39 of its 43 entries with no
   ablation applied** (hardcoded `flat["rc"]="1"` vs the pins' `rc`), so its
   `0 leaks` result is not by itself evidence for those rows. A corrected
   re-run (measured `rc`, real stderr) gives **43/43 informative, 0 leaks**, so
   the r77 claim survives; the *recorded* D1 scope (8 corrupt entries) is
   narrower than the measured one (39/43) (§3).
3. **`43/49` is reference-scoped** — exact against the r77 baseline freeze
   (43 identical / 6 observed-only), 42/49 against the pre-change run. The LOG
   states the number without naming the reference (§5).
4. **New-row placement summary is imprecise** — "receipt indices 44–74"
   (baseline §3) is really two blocks, 45–61 and 67–75; prior rows are still in
   frozen order and the count 26 is exact (§5).
5. **`75/75 x6 executions`** under-counts the runs (14 measured) and omits the
   critic's replay from the enumeration (§4).
6. **The brief's "d4aaa95 fold" is a naming slip** — `d4aaa95` is the
   report-last commit; the fold is `d48e0fd`. Both were audited; each matches
   its declared item list except for finding 1 (§4).
7. **No other false claim found in the r77 ledger.** Every verdict row, class,
   `rc`, byte-identity and pin claim that this seat re-derived reproduced; the
   remaining items are count/wording/scoping defects, none of which changes a
   class, a pin, or the `ADMIT-corr` verdict.
8. **Carry-forward from r77-scribe** — the r76-boundary missing-artifact finding
   is closed for r77: `reports/round-77/r77-boundary.md` landed (28,920 B) and
   its §6 nested-update hazard is the r78 frontier; `corpus/live/r77-boundary/`
   exists **[M]**.

## 7. The r78 watch — the author commit, re-derived

**Watch record.** The author lane first appeared as a working-tree edit at
17:56:44 (`main.lua +405/−0`), was observed editing both fixtures
(17:58–18:10, battery reaching `+560/−5`, probe `+479/−0`), ran the battery
from 18:02, and the work commit landed at **18:11:00** as
`1a03b7a61141337206c118f071777c71752d7f7c` — "r78 work: nested-update damage
surface — 17 cells". `reports/round-78/r78-author.md` (381 lines) landed in the
same commit; `r78-boundary.md` landed uncommitted at 18:02 and is **not**
audited here. Poll logs: `corpus/live/r78-scribe/watch.log`, `watch2.log` **[M]**.

### 7.1 Cell count and shape **[M]**

| | before (`d4aaa95`) | after (`1a03b7a`) |
|---|---|---|
| `CASES` | 15 | 15 (identical object) |
| `SPLICE_CELLS` | 4 | 4 (identical object) |
| `IW_CELLS` | 56 | **73 (+17, 0 removed)** |
| total rows | 75 | **92** |

- The 17 added rows are exactly the 17 `R78` SPEC keys in
  `love_phys_probe/main.lua` (`R78 == added rows` after stripping the `iw_`
  prefix, 17/17) **[R]**.
- **No prior row was edited**: all 75 prior `(cell, expected, pins)` triples are
  unchanged, and the prior rows keep their relative battery order **[R]**.
- **Placement**: the 17 new rows sit at battery indices 42–55 and 65/71/72 —
  i.e. 14 of them are inserted *ahead* of the pre-existing death tail, and the
  3 r78 death rows (`n_destroy_contacting` rc=1, `n_depth2_drain` and
  `n_depth2_drain_wp` rc=−11) join the tail last of all, as the commit says.
  The receipt order equals the battery order in every r78 run **[R]**.
- **Diff shape** **[R]**: `main.lua` `479/0` (pure insertion);
  `love_battery.py` `560/5`. The 5 deleted lines are **all inside
  `iw_classify`** and are exactly the r77 D2 conjunct (3 lines), its `anomaly`
  message (1) and the `iw_classify` docstring's closing line (1) — the author's
  report states this scope explicitly, so the commit-message word
  "insertion-only" is a shorthand, not a false claim; the tracked-file
  *behaviour* change is the D2 fix itself (§7.4).

### 7.2 Receipt level: prior cells unmoved, new cells measured **[M]**

- Against the r78 baseline freeze (`r78-baseline/freeze/love-runs/
  love-20261014T205330614648Z`, 75/75 at `d4aaa95`): the prior **56 iw stdout
  receipts** are **45 byte-identical + 11 line-token-only, 0 semantic diffs**;
  34 new files (17 cells × stdout+stderr) appear. The 11 token-only receipts
  are exactly the list the author's `drift_audit.json` declares
  (`bc_cowrap_unp`, `bc_coyield`, `bc_draindefer`, `bc_newbody_unp`,
  `bc_setpos_unp`, `bc_setpos_wp`, `bc_worlddestroy`, `cowrap_update_yield`,
  `ext_worldrelease`, `wp_coyield`, `wp_drain_throw`) — the +479-line probe
  insertion moves `main.lua:NNN`/`srcline=NNN` frames and nothing else.
- Prior **verdict rows**: 75 common, **68 byte-identical + 7 `observed`-only**
  (the `dtcadence_*`/`popen_*` jitter set), 0 other diffs, +17 new rows.
- **`rc` persisted on 73/73 iw rows** (including the 2 new `-11` rows) **[R]**.
- **92/92 PASS**: the author's seven final runs
  (`runs/love-20261014T21{0544087564Z,0613696721Z,0635061798Z,0943322605Z}` plus
  the three intermediate-revision runs `…T2100{16171220Z,25788543Z,47125716Z}`)
  are all `cases=92 pass=92 fail=0`; the disclosed `…T205937122136Z` is
  **91/92** and its single failure is `iw_drain_worldrelease → anomaly`
  ("rc=-11 without a release or nested-drain witness") — the one-line variant
  the author names as provenance for the death-site fix **[R]**. The r78
  baseline's phase-2 postland runs (`r78-baseline/postland/love-runs*/
  love-20261014T2111{25990828Z,56070014Z}`) are also **92/92**, and its own
  `byte-drift.txt` reports the prior 75 rows as 69 identical + 6 `observed`-only
  **[R]**.
- **Class census of the 17 new cells** (landed run `…T210943322605Z`) **[M]**:
  `nested_lockclear` 3, `inner_drain` 1, `dispatch_escape` 4, `refused` 1,
  `contact_invalidated` 2, `contact_live_after_abort` 1, `livelock` 1,
  `drain_converge` 2, `corrupt` 2 — all 17 with `pinned == observed` and
  `verdict == PASS`, exactly the author's declared partition.

### 7.3 Ablation matrix: 37/37, re-derived **[M]**

`corpus/live/r78-author/ablate_gates.py` (14 cells / 37 deletion-or-substitution
patterns) was **re-implemented in this seat's own loop** (the shipped script
writes `ablation.json` into the author's scratch, so it was imported for its
`ABLATIONS` table only): **37/37 patterns caught, 0 not caught, 0 baseline
mismatches** on the landed run. Unlike the r77 harness, this one reads the
measured `rc` from `verdicts.json`, passes the real rc into `iw_flat_extras`,
and checks each cell's own baseline explicitly — the r77 degeneracy is not
repeated. Two of the 37 patterns ablate the *repaired* r77 corrupt members
(`bc_worldrelease` `rel_post`/`rel_alive`, `drain_worldrelease`
`drainrel`/`postfire`).

### 7.4 The r77 D2 defect, closed in r78 — decisive test **[R]**

Three classifier revisions loaded side by side (`62201e5`, `d48e0fd`,
`1a03b7a`), same landed receipt (`iw-bc_worldrelease`, rc=−11), plus a variant
with the caller's own report line appended verbatim from a live receipt
(`IW | cell=bc_destroy | postfire cb=bc step=73 count=4 b1pos=400,520.15…`):

| classifier | unmodified receipt | + caller `postfire` line | bare `"postfire"` key ever in flat |
|---|---|---|---|
| `62201e5` (r77 work) | `corrupt` | **`corrupt`** (defect) | no |
| `d48e0fd` (r77 fold) | `corrupt` | **`corrupt`** (still open) | no |
| `1a03b7a` (r78 work) | `corrupt` | **`anomaly`** (closed) | no |

The drain member (`drain_worldrelease`, whose gate now requires
`postfire.step` **present**) classifies `corrupt` under all three revisions on
its real receipt, and the appended-line variant is the member that flips.
Classifier invariance the other way: **3,152 prior-cell receipts classified
under both `d4aaa95` and `1a03b7a` → 0 class changes** (the 763 skipped rows
are pre-r75 runs with no persisted `rc`) **[R]**. So the r78 classifier is
additive for the prior 75 cells and the r77 defect is closed without moving a
prior verdict.

## 8. Gates, out of scope, limits

- **Gates run: none of the repo's battery gates.** This seat launched no
  LOVE/pygame/Godot process and ran no cell; nothing here is execution evidence
  for any cell. The only executable re-runs were **read-only,
  receipt-consuming** scripts: the r77 author's `ablate_gates.py` (as shipped,
  twice) and this seat's own re-implementations of the r77 and r78 ablation
  predicates — none starts an engine process. The r78 harness was **imported
  for its data table only** (it writes into a sibling's scratch), and its loop
  was re-implemented here.
- **Not touched**: no product code, no fixture, no tracked file, no git state
  (no commit/push/branch), no sibling seat's scratch, no wave registry, no
  `reports/round-77/`, no `reports/round-78/r78-scout.md` or `r78-boundary.md`.
  The two watch pollers started by this seat were killed at the end of the
  audit; they only appended to `corpus/live/r78-scribe/watch*.log`.
- **Out of scope / not audited**: the r78 scout's 31 cells beyond their
  `classes.json` census; `reports/round-78/{r78-baseline.md,r78-boundary.md}`
  (both landed uncommitted during this audit — the baseline's phase-2 totals
  are read in §7.2, its own drift claims are not re-derived; the boundary's
  adversarial claims are the boundary seat's, not re-derived here); the r78 author's *semantic* engine claims beyond the class/pin/receipt
  layer (no LOVE process was launched by this seat); the r77 audio lane and the
  g3d lane (sibling repos); the r78 pygame 80/80 and Godot 88/88 siblings
  beyond reading the landed totals; cross-host determinism.
- **Limits**: all claims are bounded to this host, this repo, these versions
  (LOVE 11.5 / LuaJIT 2.1.1788460057 / Python 3.14.7) and to the audit window
  ~20:50–21:30Z 2026-10-14. "Re-derived" means *the landed raw bytes reproduce
  the landed parsed view, every row pin, and the class/pin tables* — not that a
  fresh process would reproduce the bytes; the latter is witnessed only by the
  sibling runs this seat re-read (23 of them), never re-run.

## 9. Artifacts and reproduce

- `corpus/live/r78-scribe/audit_r77.py` (sha256 `c3d1b969c22beb26…`) →
  `audit_r77.json` / `audit_r77.txt` (+ `audit_r77.run.txt`): HEAD/chain,
  report inventory vs `HEAD:`, AST cell counts by revision, R77-key match,
  run-dir census, shipped-harness literal re-run, independent matrix
  (author-mode vs corrected-mode), receipt identity, fold pin-drop census,
  `d4aaa95` numstat, LOG claim probes.
- `corpus/live/r78-scribe/audit_r77b.py` (sha256 `942ccfb0c7a3c076…`) →
  `audit_r77b.json` / `audit_r77b.txt` (+ `.run.txt`): 49-row comparisons
  across 26 references, row-order/contiguity, class census of the 26 new
  cells, raw-receipt drift vs the baseline's `raw-drift.txt`, iw-receipt
  byte-identity across run dirs.
- `corpus/live/r78-scribe/audit_r78.py` (sha256 `1a4f55fd5250c2f1…`) →
  `audit_r78.json` / `.txt` (+ `.run.txt`): the landing shape — cell-count
  delta, numstat, R78-key match, run census, prior-row identity.
- `corpus/live/r78-scribe/audit_r78b.py` (sha256 `4818eb0f558a1279…`) →
  `audit_r78b.json` / `.txt`
  (+ `.run.txt`): the decisive tests — D2/D3 across three classifier
  revisions, classifier invariance over 3,152 receipts, r78 run census/class
  census, receipt-level insertion-only, and the 37-pattern ablation re-run.
  It materialises the three classifier revisions as
  `_bat_<rev>.py` files **inside this seat's scratch** (never in the repo
  tree) and imports the sibling r78 harness for its `ABLATIONS` table only.
- Watch logs: `corpus/live/r78-scribe/watch.log`, `watch2.log` (HEAD +
  fixture-numstat polls, 15–20 s cadence, 17:55–18:13).
- Reproduce: `PYTHONDONTWRITEBYTECODE=1 python3 -B
  corpus/live/r78-scribe/audit_r77.py` (then `audit_r77b.py`,
  `audit_r78.py --rev 1a03b7a`, `audit_r78b.py`). All instruments use
  `python3 -B` and import the tracked battery with bytecode writing disabled;
  no `.pyc` is created by this seat.
