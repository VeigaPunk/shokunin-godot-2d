# r99 critic — adversarial review of committed `254e79dd` (21-row audio lattice claimed; 22 tuples landed; the landed bytes had never been measured)

Seat `CRITIC` (g2d lane r99) | host **devin** | Godot
`4.7.2.stable.arch_linux.ed1daf0bf` (`/usr/bin/godot`, `--headless`, Dummy audio
driver, 60 tps, `RendererDummy`), Python 3.14.7.
Reviewed commit **`254e79dd`** (`r99 author: headless audio lattice (21 rows,
+150/-0), green 447/447`, parent **`9d421fb2`** = r98 author). Lane HEAD at
session start **`2dcbb6f6`** (r100 author); HEAD at report time **`9ede7c50`**
(`r97-r100 integration fix: dedupe crash sentinel CASES rows`). The reviewed
landing is a **single-parent commit**, not a merge commit: the three-way
resolution happened in the landing step, between the author's worktree (built on
r96 `89f85ed8`) and main (r98 `9d421fb2`).
**No tracked write, no commit.** Seat-owned artifacts: `corpus/live/r99-critic/**`
(`struct/`, `mutants/`, `runs/`, `manifest.sha256`) and this report.

**Commit sha verified: `254e79dd81202b2f25b3064681c96d95a37ccdfe`** — all
harness-derived evidence below comes from a fresh `git archive` checkout of that
sha (`corpus/live/r99-critic/struct/landed_run_battery.py`,
sha256 `fd2ed16c934ed251ae86bde64ece2b134db8c5652a0795a8e8724bf9437eeae8`).

## Verdict: **PASS-with-findings**

The landed tree passes the full battery **on its own bytes** — 492 rows, 492
PASS, 0 FAIL, all 48 gate discriminations true (§2.1) — and the r99 block's 21
rows, its one `expected_errors` entry and its floor gate are live, covered and
falsifiable (§2.2–§2.4). Two findings stand:

* **F1 (HIGH, provenance/record)** — the landing's evidence chain describes a
  **different file** than the one committed. The report names
  `run_battery.py` = `71d38d9…` as "the shipped" file; the landed blob is
  `fd2ed16…`. `71d38d9` is the author's pre-merge worktree file (440 CASES,
  missing the whole r97 and r98 blocks); `fd2ed16` is 485 CASES. The landed
  bytes were never run by any battery (no run dir exists for them), so the
  commit's "green 447/447" is evidence for an artifact that is not in the
  commit. §2.1 supplies the missing measurement.
* **F2 (MEDIUM, splice defect)** — the three-way resolution inserted **22**
  tuples where the round claims 21: `crash_spontaneous_sigabrt` is duplicated
  (CASES indices 459 and 481). The harness has no uniqueness invariant, so the
  duplicate is absorbed silently, runs the SIGABRT probe twice, and inflates
  the allowlist census by one row. Benign today only because the two tuples are
  byte-identical. Already repaired on main by `9ede7c50` (§3.3).

Neither finding is a red gate: no axis of the round's *claims* (the 21 rows'
pins, the single allowlist entry, the gate) is falsified. F1 is a record
correction with a one-line fix in the report/commit message; F2 needed a
one-line deletion, which has landed.

---

## 0. What I ran

| # | batch | scope | result |
|---|---|---|---|
| 1 | structural census (AST) | landed blob `fd2ed16`, parent `df4563c8`, author worktree `71d38d9`, r100 `2dcbb6f6`, repair `9ede7c50` | §1, §2.5, §3 |
| 2 | **full battery, landed bytes** | fresh `git archive 254e79dd` checkout → `python3 corpus/fixtures/run_battery.py` | **492 rows, 492 PASS, 0 FAIL, verdict PASS** |
| 3 | harness mutant `deadentry` | landed file + one never-emitted allowlist entry under the r99 prefix (`r99_audio_bus_peak`); full battery | **FAIL, 492 rows, exactly 1 FAIL (`probe_error_clause_surface`), exactly 1 false discrimination (`r99_expected_errors_all_matched`)** |
| 4 | pin-mutant re-classification | the landed run's own captured output × 21 single-token signature mutants, production `classify_process` (segment sha256 `749fa060…`) | **21/21 shipped accept, 21/21 mutants reject** |
| 5 | harness mutant `pins` | landed file + the same 21 single-token pin mutations; full battery | **FAIL, 492 rows, exactly the 21 r99 rows FAIL, every other row and all 48 discriminations PASS** |

**Load/host caveat (honest, load-bearing for batch 2).** The host was **never
idle**: loadavg 16.2 (10.2–16.2 range) on 32 cores with **22 concurrent
`godot` processes** at batch 2's start and 37 later in the session (mostly other
lanes' batteries — r97-verifier, r97-simplifier, r98-scribe, r98-reviewer,
r99-scribe, r100-critic, r100-reviewer, r100-verifier, r100 integration,
`…/tmp/r98-mutant-full`; the 37 includes this seat's two mutant batteries).
Batch 2 ran entirely under that contention and still returned 492/492, so its
green is not an idle-host artifact. No row in batch 2 measured nothing; every
row carries a fresh-process receipt (`actual_exit`, `signature`, captured merged
output).

**Scratch-path caveat.** `/tmp` is a shared tmpfs at 80 % with a per-user write
failure (`EDQUOT` on a 1-byte write, reproduced twice). Archive-tree runs
therefore live in **fresh `git archive` checkouts under
`/home/vgpnk/tmp/g2d/`** (`landing-r99/`, `mut-deadentry/`), out of the lane
repo, not literally under `/tmp`. Nothing was staged or committed.

---

## 1. Findings (ranked)

### F1 — HIGH (provenance / evidence chain) · the landed artifact is **not** the artifact the round measured, and it was never measured

Three files, three digests, one report:

| object | sha256 | bytes | CASES | gates | r97/r98 rows |
|---|---|---|---|---|---|
| **landed blob** `254e79dd:corpus/fixtures/run_battery.py` | `fd2ed16c934ed251ae86bde64ece2b134db8c5652a0795a8e8724bf9437eeae8` | 489 915 | **485** | 48 | present |
| report's "shipped `run_battery.py`" | `71d38d91871a14667da955263e1695cc5392d6e99d3fca399098dc2d988b7829` | 465 444 | **440** | 46 | **absent** |
| commit parent `9d421fb2` | `df4563c8ec1f22c31ea1c60fc10817fabeec20ae29b376d8ab4579f891bac973` | 477 774 | 463 | 47 | present |

`71d38d9` is byte-for-byte the **author's worktree file**
(`/home/vgpnk/Projects/shokunin/game-dev-2d-shokunin-wt-r99/corpus/fixtures/run_battery.py`)
— the file runs A/B/C and the smoke pass were taken on. Its gates dict has no
`r97_`/`r98_expected_errors_all_matched`, and its `expected_errors` dict is
missing the three r97/r98 entries; the landed blob has all of them.

Consequences, each verified, not inferred:

1. **The round's row arithmetic describes the wrong tree.** The report says
   "CASES 419 → 440 (+21); results 426 → 447 (+21)" and "insertion-only
   `+150 / −0`". The commit's own numstat is **`151 2`** for `run_battery.py`
   (2 deletions), and the landed CASES count went **463 → 485**. The report's
   `419`/`440` are the author's r96-based worktree (419 = r96 CASES).
2. **The landed tree carries 44 rows the round never executed.** The author's
   run C (`…/wt-r99/corpus/live/runs/20261016T090222167156Z/verdicts.json`,
   447 rows = 440 CASES + 7 meta rows, **zero duplicate case rows**) has **no
   result row** for any of the 12 `stree_lattice_*`, 15 `r98_canvas_*`, 16
   `r98b_*` and the `r98c_flush` row that the landed blob contains (44 = 12
   r97 + 32 r98). Those 44 rows — and the r97/r98 allowlist entries and gates
   they carry — were measured for the first time in batch 2 (§2.1). The parent's
   463 rows decompose exactly as 419 r96-era + 32 r98 + 12 r97, which is where
   the report's `419` comes from.
3. **No run exists for the landed bytes.** No `corpus/live/runs/**` directory
   anywhere in the lane repo or the author worktree is newer than the r99
   commit. The committed `corpus/fixtures/__pycache__/run_battery.cpython-314.pyc`
   is the bytecode of the **landed** file (its embedded `src_size` = 489 915
   matches `fd2ed16`, and not the 465 444-byte worktree file), so the merged
   file was *imported/compiled* ~10 s before the commit — but the battery that
   produced the 447-row evidence never saw it. "Bytes were re-hashed
   immediately before and after the run" is true of `71d38d9`, not of the
   landed blob: the author's own `fixture_sha256.txt` **and**
   `fixture_sha256_pre_run_C.txt` both record `71d38d9` for
   `corpus/fixtures/run_battery.py`. The merge therefore happened **after** the
   round's hashing and after its last battery run.
4. **The same misdescription is in the commit subject** ("21 rows, +150/-0,
   green 447/447") — the landed insertion is 22 tuples, `151/2`, and green for
   a file that is not in the commit.

*Smallest safe correction (record only, no code change required by this seat):*
the r99 report's digest line, numstat line and CASES/rows arithmetic should be
restated against `fd2ed16` / 485 CASES / 492 rows, and the green claim replaced
by the landed-bytes measurement in §2.1. The mechanism fix is upstream: the
landing step must re-measure the *merged* file (one battery run) before the
commit, or land the author's tree on top of main instead of splicing.

### F2 — MEDIUM (splice defect, silently absorbed) · the merge inserted a duplicated CASES row

Structural proof (AST over both trees, `struct/structural_census.txt`):

* parent `9d421fb2`: CASES = 463, **no duplicate names**.
* landed `254e79dd`: CASES = 485; `landed[:460] + landed[482:] == parent`
  **tuple-for-tuple** (every pre-existing row, signature and flag preserved);
  the inserted block is **22** tuples at index 460 —
  `['r99_audio_census' … 'r99b_finfree_played']` (21, the round's rows) **plus
  `crash_spontaneous_sigabrt`**.
* the parent's own `crash_spontaneous_sigabrt` survives on the **same physical
  line** as the `r98c_flush` row (line 1403 — a splice the r98 landing had
  already left there), and the r99 comment header was appended to that same
  line; the inserted copy is on line 1535. Net: **`crash_spontaneous_sigabrt`
  ×2**, `crash_self_sigkill` ×1, `descendant_pipe_detached_control` ×1.

Why it is invisible to the harness (checked in the landed source, not assumed):

* `CASES` is iterated with `for case in CASES:` — every tuple yields a result
  row, so the battery now runs the SIGABRT probe **twice** (both PASS) and the
  battery is **492 rows**, not the claimed 447.
* there is **no uniqueness gate** over case names anywhere in the gates dict
  (48 discriminations: allowlist floors, census consistency, classifier
  consistency, prior-row stability anchors — none counts rows or names).
* `crash_records = {r["case"]: r for r in results …}` is a **last-wins dict
  comprehension**, so the duplicate collapses there; both copies are identical
  tuples and both PASS, so the meta row `probe_spontaneous_crash_classification`
  is unaffected *today*. A future divergence between the two copies would be
  caught only by the two rows failing independently.
* the duplicate also reaches the **census**: batch 2's census carries
  `rows_with_expected_errors = 76` with `crash_spontaneous_sigabrt` appearing
  **twice** (75 unique names), i.e. the duplicate inflates the allowlist census
  by one row and dilutes the meaning of that count. `dead_entry_count = 0` and
  the gate still evaluates over all entries, so no verdict moves.

*Smallest safe correction:* delete one of the two `crash_spontaneous_sigabrt`
tuples (either copy — they are byte-identical) and re-run the battery once on
the corrected bytes; row count returns to 491 = 484 CASES + 7 meta. **This has
already landed on main**: `9ede7c50` (§3.3). No action is required from this
round beyond recording it.

*Cross-seat custody:* the repair commit attributes the same splice class to
**r98-critic F1** ("crash_spontaneous_sigabrt appeared x3 and crash_self_sigkill
x2 after serial union landings"). This seat reached the same conclusion
independently from the r99 landing and pins the lineage one step earlier: the
r98 landing had already glued `crash_spontaneous_sigabrt` onto the end of the
`r98c_flush` row line (parent line 1403), and the r99 union landing appended the
r99 comment header to that same line while also inserting the author's copy of
the crash pair — hence ×2 at `254e79dd` and ×3 at `2dcbb6f6`.

### F3 — INFO (cross-round, not this round's artifact) · the same splice class reached r100

The r100 landing (`2dcbb6f6`) inherited F2 and compounded it: CASES = 512 with
`crash_spontaneous_sigabrt` **×3** and `crash_self_sigkill` **×2** (indices
459/481/508 and 482/509). Recorded here only because it shows F2 is a *merge
shape*, not a one-off, and because it changes the repair target: the deletion
must be applied on top of HEAD, not on `254e79dd`. It is now repaired at
`9ede7c50` for both rounds.

### F4 — INFO (report precision) · the round's receipts are untracked, so F1 could not be caught from the commit

The report cites `corpus/live/r99-author/**` (battery logs A/B/C,
`battery_runs_ABC.json`, `smoke/`, `bus_reps/`, `fixture_sha256*.txt`) as its
evidence. None of it is in the commit; it lives only in the author's worktree
(`…-wt-r99/corpus/live/r99-author/`, `??` untracked). The house pattern tracks
the scout/boundary probes and reports under `corpus/live/` while run trees stay
ignored (`corpus/live/.gitignore`: `runs*/`, `**/__pycache__/`), so this is not
a violation — but it means the commit alone cannot be audited, and the digest
mismatch in F1 was only visible by reading the worktree. Naming the evidence
file *by path and digest* inside the report (as the r95 critic did) would have
made F1 self-evident at commit time.

---

## 2. What survived (positive verifications)

### 2.1 Full battery on the landed bytes — 492/492, first measurement of this artifact

`git archive 254e79dd` → fresh checkout → `python3 corpus/fixtures/run_battery.py`
(`landing-r99/corpus/live/runs/20261016T092236662915Z/verdicts.json`):

* **492 rows, 492 PASS, 0 FAIL**, battery verdict **PASS**, `EXIT=0`.
  (492 = 485 CASES + 7 meta rows; the 447-row figure in the report is not this
  tree.)
* **all 21 r99 rows PASS** on the landed bytes.
* **all 48 discriminations true**, including `r97_expected_errors_all_matched`,
  `r98_expected_errors_all_matched`, `r99_expected_errors_all_matched` — i.e.
  the three r97/r98 allowlist entries and the r99 entry are all **live**, and
  `dead_entry_count = 0` with `dead_entries = []` over 76 census rows.
* the duplicate is visible exactly as predicted: `{'crash_spontaneous_sigabrt': 2}`
  in the result rows **and** twice in the census.

### 2.2 The r99 allowlist entry is live, not dead

`r99_audio_gen` census record: `entry = 'ERROR: Condition "active" is true.'`,
`shape = exact`, **`matched_lines = 2`**, `dead_in_run = false`. The two refused
`clear_buffer()` calls fire on the landed bytes, twice per receipt, as the
report claims — the "only stderr in the whole block" claim holds at this launch
shape.

### 2.3 The r99 gate is correctly scoped and non-vacuous

`r99_expected_errors_all_matched` is a discrimination of the
`probe_error_clause_surface` meta row and covers
`r99_audio_*` / `r99b_*` — exactly the prefix set that contains the round's only
allowlist entry, so a dead r99 entry cannot pass silently (r79-critic C2 shape).
It is non-vacuous on this tree because the census it quantifies over is
non-empty (76 rows) and contains the r99 entry.

### 2.4 Mutation battery — the r99 rows and the r99 gate are falsifiable, end-to-end

* **Pin mutants (batch 5, full battery).** The landed file with **21 single-token
  mutations**, one per r99 row (e.g. `first=0.002902494` → `first=0.00290249x`,
  `played_gt_02=true` → `played_gt_02=trux`, `enable_input=false max_fps=0
  tps=60` → `…tps=61`). Structural pre-check: 21 tuples changed, all 485 case
  names unchanged. Result: **battery FAIL, 492 rows, exactly those 21 rows
  FAIL**, every other row PASS, **all 48 discriminations still true**,
  `dead_entry_count = 0`. So the round's rows are real falsifiers, and a wrong
  engine reading lands on the row that owns the pin — not on the gate.
* **Pin-mutant re-classification (batch 4).** The same 21 mutations applied to
  batch 2's own captured output through the **production** `classify_process`
  (AST-extracted from the landed file; segment sha256
  `749fa0607e7707e614c1ab157a6f8e756dfc2f460746e6d218e6734ad8fa72c3`, the same
  segment the author's report pins): **shipped signatures accepted 21/21,
  mutated signatures rejected 21/21.** No row is an echo pin.
* **Dead-allowlist mutant, isolated (batch 3, full battery).** The landed file
  plus **one never-emitted** allowlist entry under the r99 prefix
  (`'r99_audio_bus_peak': ('ERROR: dead-entry mutant: never emitted by any
  arm',)`), leaving `r99_audio_gen`'s own entry intact and every row's stdout
  untouched. The dead entry is deliberately **verdict-inert for its own row**
  (`r99_audio_bus_peak` still PASSes — its stderr is clean), so **only** the
  floor gate can catch it. Result:

  * battery verdict **FAIL**; 492 rows; **exactly one FAIL row** =
    `probe_error_clause_surface`;
  * **exactly one false discrimination** of 48:
    `r99_expected_errors_all_matched` — every other discrimination, including
    `census_bare_classifier_consistent`, `census_allowlisted_reproduces_verdicts`
    and the r97/r98 floors, stays true;
  * `dead_entry_count = 1`, `dead_entries = [{'case': 'r99_audio_bus_peak',
    'entry': 'ERROR: dead-entry mutant: never emitted by any arm', 'shape':
    'exact'}]`; `rows_with_expected_errors` 76 → 77;
  * `r99_audio_gen`'s own entry is unaffected: `matched_lines = 2`,
    `dead_in_run = false`.

  So the r99 gate is **load-bearing, non-vacuous and precisely scoped**: a dead
  entry anywhere under `r99_audio_*` / `r99b_*` turns the battery red and names
  itself in the census, while no other discrimination moves.

### 2.5 Merge hygiene that survived

* **No silent rewrite of pre-existing rows.** `landed[:460] + landed[482:]`
  equals the parent **tuple-for-tuple** (names, fixtures, flags, expected
  exits, signatures). The r97 (12) and r98 (32) rows are byte-identical to the
  r98 landing.
* **The two dict surfaces moved by exactly one key each.**
  `expected_errors`: +1 (`r99_audio_gen`), nothing removed, no value changed
  (79 vs parent 78). Gates: +1 (`r99_expected_errors_all_matched`), nothing
  removed, no body changed (48 vs parent 47). Every gate key is unique in both
  trees (a duplicate gate key would silently shadow an earlier one — none).
* **Fixture provenance holds.** `corpus/fixtures/audio_lattice.gd` =
  `165571c410d506f14915326fd0806e9ff01e5056631620f565c9a7836a920baf` (773 L) and
  `corpus/fixtures/r99b_modes.gd` =
  `b680e6f297b7534d02a3bdc33337961062f9f0a79393b2a48798308785d38624` (453 L) are
  **byte-identical** to the frozen probes in
  `corpus/live/r99-scout/probes/audio_lattice.gd` and
  `corpus/live/r99-boundary/probes/r99b_modes.gd`. The byte-copy claim is true.
* **Every allowlist entry is keyed to a real CASES row.** All 79 keys resolve to
  a name in the landed `CASES` (none orphaned); the four empty-tuple entries
  (`export_preset_missing`, the three `slider_adjust_repeat_right_*restore*`
  rows) are inert by construction and are listed as
  `allowlists_outside_expected_errors`, not censused.
* **The landed file parses and runs.** `ast.parse` clean; the battery executes
  it end-to-end.

---

## 3. Provenance and cross-round notes

### 3.1 The reviewed bytes

Every harness-derived claim above is pinned to a **frozen `git archive` checkout
of `254e79dd`** (`landing-r99/`, `struct/landed_run_battery.py`, sha256
`fd2ed16…`), not to the lane worktree, which carries other lanes' churn. The
lane worktree's only tracked modification during this session was
`corpus/fixtures/__pycache__/run_battery.cpython-314.pyc` (regenerated by the
r100 landing; `corpus/fixtures/__pycache__/` has been tracked since r69
`ec2cda6a` and is ignored only under `corpus/live/`).

### 3.2 Why the two dict surfaces were the merge's risk — and were clean

The dispatch flagged "three-way merge resolution touched `expected_errors` +
gate dict". Both were checked by AST against the parent, key by key: **+1 entry,
+1 gate, zero value/body churn, zero key collisions, zero orphaned keys.** The
merge's actual defect was in `CASES`, one line above the region it was told
about (F2) — the dict surfaces are the visible part of a splice that also
duplicated a row.

### 3.3 The post-landing repair (`9ede7c50`) is correct and minimal

`9ede7c50` (`r97-r100 integration fix: dedupe crash sentinel CASES rows
(509/509 unique)`, parent `2dcbb6f6`) drops **exactly** `crash_spontaneous_sigabrt`
×2 and `crash_self_sigkill` ×1 from its parent: 512 → 509 CASES, no duplicates,
`expected_errors` identical (82), gates identical (49), **all 21 r99 rows still
present**, `r99_audio_gen`'s entry unchanged. So F2's repair is verified
structurally at HEAD. The repair's own claim is "509/509 unique", not green —
the corrected tree has not been battery-measured in this seat's session (out of
this round's scope; the r100/integration lane owns that measurement).

---

## 4. What this seat did **not** do

* No commit, no `git add`, no write to any tracked file; no mutation of the
  lane worktree, the author worktree, or any other lane's artifacts.
* No battery run at HEAD (`9ede7c50`) or at `2dcbb6f6` — both are other rounds'
  artifacts; only their structure was read.
* No claim about the r99 rows under `--fixed-fps` / `--max-fps` modes, or about
  the folded keys (`block_jumps_ge6`, `fin_same_frame`, `period_is_block`
  ownership) — those are the boundary's and reviewer's surfaces, and the report
  discloses them honestly. This seat re-ran nothing at other launch shapes, so
  it asserts nothing there.
* No claim that the duplicate was harmless *in general*: it is harmless here
  because the two tuples are byte-identical, which is a coincidence of this
  merge, not an invariant the harness enforces.

---

*Evidence bundle:* `corpus/live/r99-critic/` — `struct/` (landed, parent,
author-worktree sources + `structural_census.txt`), `mutants/` (both mutant
harnesses), `runs/` (baseline + mutant `verdicts.json` and logs),
`manifest.sha256`.
