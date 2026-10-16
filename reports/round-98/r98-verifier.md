# r98 verifier — independent non-author verification of `9d421fb2`

**VERDICT: VERIFIED (with findings).** The committed r98 landing
`9d421fb2c0577488cf6f34399c123d81a91a067b` (*r98 author: canvas/draw-flush
lattice (32 rows, 426->458)*) clears this seat's gate. On a fresh
`git archive 9d421fb2` checkout — **125,220/125,220 tree entries byte-identical
to the commit** — my own full battery run is **470/470 PASS** (463 `CASES` +
7 meta rows; 0 FAIL), all 32 r98 rows green, the r98 floor gate `True`, all
three new allowlist entries live-matched with `dead_in_run=false`, and the
**conflict-resolution union is complete**: every one of the 431 pre-existing
r97 tuples survives with an identical literal value (2 tuple *segments*
reflowed, values unchanged), +32 r98 tuples, 0 lost, 0 duplicated. Every r98
cell re-derives from the raw receipts (27 whole-line / 3 prefix / 2 contiguous
substring, exactly as declared), 683 signature-token mutations all reject, and
an in-harness mutant battery (dead allowlist entry + one-token signature
mutation) fails exactly as designed. Findings F1–F7 are documentation /
pre-existing-harness observations with no byte defect; the load-bearing one is
**F1: the author's counts describe the r96-based worktree, not the landed
merge** — the landed tree runs **470** rows, not the "458" the commit message
and report headline claim.

Seat `VERIFIER` (g2d lane `r98-verifier`, independent non-author) | host
**devin** | Godot `4.7.2.stable.arch_linux.ed1daf0bf` (`/usr/bin/godot`,
`--headless`, 60 tps default), Python 3.14.7, `timeout 2700` on each battery
run. Target commit: **`9d421fb2c0577488cf6f34399c123d81a91a067b`**. Lane repo
HEAD has since advanced (r99, r100, an integration dedupe, an r97
adjudication; `2ac38451` at the time of writing) — the assigned r98 commit is
an ancestor of all of them; §7 proves the r98 bytes carry forward unchanged.
Receipts:
`corpus/live/r98-verifier/` (untracked). Author report
`reports/round-98/r98-author.md`; scout/boundary evidence under
`corpus/live/r98-scout/`, `corpus/live/r98-boundary/` (corroboration only —
every load-bearing number below is re-derived on this seat's own runs).

**`lsp` disclosure.** No `lsp` device in this session and no GDScript/Python
language server on this host (unchanged lane state r89–r98); symbol-aware
operations were **unavailable for every file in scope**. No symbol work was
required: this pass makes **zero edits** (verification only — no rename, no
definition change, no code action), so the fallback is static reads plus
fresh-process execution, and the recorded unavailability costs nothing here.

**Frozen probeParent disclosure.** Exactly one read-only `ufo-labrat` (L2,
agent `3ec7e49d`) was dispatched with one bounded four-clause hypothesis over
the committed bytes × this seat's `run1` verdicts: (a) 32/32 r98 rows
PASS/exit 0/error null with the committed signature present — **CONFIRMED**;
(b) the emitted-line form census is exactly 27 equal / 3 prefix / 2 mid-line
with 0 outside forms — **CONFIRMED**; (c) all three r98 allowlist entries
censused with `dead_in_run=false`, `matched_lines` 1/2/6, gate `true`, every
observed `ERROR:` line byte-claimed — **CONFIRMED**; (d) no committed signature
occurs as a literal in the fixture its row launches (all four fixtures
format-build their PASS line) — **CONFIRMED, 0 hits**. Advisory only; it wrote
nothing and launched nothing.

**Host caveat (must be read with every row below).** `/tmp` on this host is a
16 GB tmpfs with a **1,048,576-inode cap already at 97 %** (1,015,699 inodes
used, **32,877 free**); the r98 tree is 125,220 files, so the contract's
"fresh `git archive` checkout under `/tmp`" is **impossible on this host right
now** (`tar: … Cannot write: Disk quota exceeded` on the first entry;
`dd` of 200 MB also failed). The archive was therefore extracted to a fresh
checkout on the root filesystem — `/home/vgpnk/Projects/shokunin/tmp/
r98-verify-full` (740 GB free) — same commit, same `git archive` provenance,
byte-pinned in §1. Concurrent lanes ran throughout (loadavg **9.0 → 14.6**
during run 1; **5.6 → 8.2** during run 2, with **ten** sibling
`run_battery.py` runs visible in `ps` at the same time); no row flaked. One
consequence of that pressure is disclosed in §5.1: the first mutant attempt was
reaped mid-run when its owning tool session exited, and was relaunched detached.

---

## 1. Method — whole-commit pin, not a fixtures-only slice

- `git archive 9d421fb2 | tar -x -C …/r98-verify-full` (fresh dir, no `.git`).
- **Blob identity**: every `git ls-tree -r 9d421fb2` entry hashed as a git blob
  against the extracted bytes — **125,220/125,220 match, 0 mismatches,
  0 missing** (125,152 regular blobs + 68 symlinks verified by link-text
  hashing; modes `100644`×125,051 / `100755`×101 / `120000`×68). Receipt:
  `artifacts/blob-identity-9d421fb2.json`, probe `probes/blob_identity.py`.
- **Fixture pins** (sha256, computed here) match the author report table
  exactly: `canvas_lattice.gd` `866480a1…94f0` (791 lines),
  `r98b_attack.gd` `2e71c715…a2f8` (822), `r98b_rksenum.gd` `7bb51902…f76a`
  (68), `r98c_flush.gd` `c038f748…932e` (272) — the four claimed byte-copies
  are byte-copies. `run_battery.py` `df4563c8…c973` (5,046 lines).
- **Commit scope** (`git diff --name-status f67094bb 9d421fb2`): exactly 6
  paths — the 4 new fixtures, the harness, the author report. Nothing else.
- Row/flag shapes (AST over the committed harness): 32 rows, `expected_exit`
  0/32, flags `--arm=…` (plus `--var=…` on the five `latch` rows), 15 launches
  of `canvas_lattice.gd`, 15 of `r98b_attack.gd`, 1 of `r98b_rksenum.gd`
  (no flags — no arm dispatch), 1 of `r98c_flush.gd`. Every declared arm
  appears as a literal in its fixture's `match` dispatch and all four fixtures
  end with a loud `_fail("unknown_arm")`-shaped fallback (rksenum has no
  dispatch at all) — a silent `_:`-fallback row is impossible. All four new
  fixtures exist and **only** r98 rows reference them (no orphan fixture, no
  cross-round leakage).

## 2. Merged-bytes integrity — the union is complete (the headline check)

The landing was a worktree merge: the author's branch was cut from **r96**
(`89f85ed8`, `CASES` = **419**) and landed onto **r97** (`f67094bb`,
`CASES` = **431**), so the r98 block had to be unioned with a block the author's
branch never contained. Proof by AST tuple-value comparison
(`probes/union_proof.py`, `artifacts/union-proof.json`):

| edge | CASES | added | lost | value-changed | segment-changed | dup names | shared order |
|---|---|---|---|---|---|---|---|
| `89f85ed8 → f67094bb` (r97's own edge) | 419 → 431 | +12 | **0** | **0** | 0 | 0 | identical |
| `f67094bb → 9d421fb2` (this landing) | 431 → **463** | **+32** | **0** | **0** | **2** (reflow only) | 0 | identical |

- The 32 additions are **contiguous** at child indices **427–458**, anchored
  between `stree_lattice_scene_probe` and `crash_spontaneous_sigabrt` — the
  four-row crash/descendant tail (`crash_spontaneous_sigabrt`,
  `crash_self_sigkill`, `descendant_pipe_detached_control`,
  `descendant_pipe_forged_signature_release`) keeps its order, so
  `descendant_pipe_detached_control`'s sleep-8 gap stays adjacent to the meta
  probes exactly as the author declared.
- The two "segment-changed" rows are the merge reflow, and the reflow is
  **value-neutral**: `stree_lattice_scene_probe` gained a trailing `#`-comment
  on its closing line, and `crash_spontaneous_sigabrt` was joined onto the
  previous physical line (`… bounded=1'),    ("crash_spontaneous_sigabrt", …`).
  `ast.literal_eval` of both tuples is identical to the parent's — no r97
  signature byte changed. (This is why `git diff --numstat` is `150 2`, not the
  `150 0` the author report records — see **F1**.)
- `expected_errors`: 75 → **78** entries, `+3 / −0 / 0 changed` — exactly
  `r98_canvas_clip`, `r98_canvas_draw_refusal`, `r98b_clipmatrix`. Floor gates:
  r97's `r97_expected_errors_all_matched` survives and `r98_expected_errors_all_matched`
  is added (13 round gates total in the committed harness).
- Duplicate-signature census over all 463 rows: 456 distinct signatures, 6
  duplicate groups — **all six pre-existing** (`negative_overlap`/`negative_signal`,
  the three camera-limit rows, the two `button_activation_*` rows, the two
  `r95b_order_celloff_*` rows, and the two crash / two descendant pairs).
  **No r98 row reuses another row's signature.**

## 3. Battery on the pinned tree — my run

`cd /home/vgpnk/Projects/shokunin/tmp/r98-verify-full && timeout 2700 python3
corpus/fixtures/run_battery.py` (default runs dir inside the archived tree, so
the lane repo's own receipts are untouched).

| rep | run dir | verdict | rows | r98 rows | r98 gate | dead entries |
|---|---|---|---|---|---|---|
| **run1** (committed bytes) | `runs/20261016T092213219927Z/` | **PASS** | **470/470** | **32/32 PASS** | **True** | **0** |

Wall clock 09:22:13Z → 09:29:45Z (≈7 m 30 s); log
`artifacts/run1-tree.log`, receipts `run1-tree/verdicts.json`. All 13 round
gates are `True`; `census.dead_entry_count = 0`; every surface discrimination
`true`. The three r98 allowlist entries are live-matched in-run —
`r98_canvas_clip` 1 line, `r98_canvas_draw_refusal` 2, `r98b_clipmatrix` 6 —
with `bare_classification_rejects = true` for each (the allowlist is doing real
work: without it those rows reject) and **every observed `ERROR:` line byte-equal
to its committed entry** (0 unclaimed lines).

**Author-number reconciliation (the F1 root cause).** The author's "458/458 ×2"
is the *branch* count: `419 + 32 = 451` CASES, `+7` meta = **458** — computed
on a base that never saw r97. The landed merge runs `431 + 32 = 463` CASES,
**470** results rows. Both are green; only the arithmetic referent is stale.
The commit message's "CASES 419->451" is the same artefact.

## 4. Cell re-derivation — 32/32 from raw receipts

`probes/rederive.py` (production `classify_process` AST-extracted from the
committed harness, not re-implemented) over `run1-tree/verdicts.json` →
`artifacts/rederive-run1.json`:

- **32/32** rows: `verdict == PASS`, `actual_exit == 0`, `error is None`,
  committed signature present in the merged captured output, production
  classifier `True`.
- **Form census re-derived: 27 whole-line / 3 prefix / 2 contiguous substring**
  — the author's declared 27/3/2 exactly, with the declared cut points:
  `r98_canvas_queue` cuts before ` events_tail=` (tail =
  `q@pf0|d@pf0|d@pf1|d@pf2|d@pf6|d@pf8|d@pf10|d@pf12`),
  `r98b_qflush_same_frame` cuts before ` coalesce_draws=` (12 further keys
  dropped), `r98b_qorder_tree` cuts before ` stagger=` (9 further keys
  dropped). The two substring rows are exactly `r98b_qflush_suppress`
  (`hide_ticksep_n=1 hidden_across_tick_n=0 show_after_tick_n=1`, mid-line of
  the same `qflush` emission the head row prefixes) and `r98b_qorder_flat`
  (`flat=CBACBA`, which occurs on 2 lines — the `R98B qorder` diagnostic and
  the PASS line's tail; the harness's substring semantics accepts either).
- Every dropped tail key is a **tick-phase / scheduling observable** the
  author declared unpinnable, and every kept key is either a boolean or a small
  integer — the declared "pin the law, not the host's scheduler" discipline
  holds on the emitted bytes.
- The 4 r98 fixtures build their PASS lines with `print("PASS …" % […])` from
  measured state; **no committed signature occurs as a literal in the fixture
  a row launches** (labrat clause (d), 0 hits) — the rows cannot pass by
  echoing a constant.
- `r98c_flush` (the one row with no frozen-probe provenance) deserves the
  extra note: its keys are all computed — `draws` is counted inside `_draw()`,
  ticks from `Engine.get_physics_frames()`, per-process-frame draw counts from
  a histogram keyed on `Engine.get_process_frames()`, and every wait loop is
  bounded by a 240-frame guard that flips `bounded=0`. The 80 ms
  `OS.delay_msec` process-step block is the in-process equivalent of the
  boundary's `--frame-delay`, which the row cannot pass as a launch flag.

## 5. Mutation / negative controls — the gate bites

- **In-signature token mutations: 683 generated across the 32 rows
  (bool flips, int ±1, float last-digit, last-letter, key renames), re-classified
  with the production classifier against the captured bytes — 683/683 reject,
  0 accepted, 0 gaps** (`artifacts/rederive-run1.json → mutations`).
- **Global axes, all 32 rows**: rc flip 32/32 reject · injected unrelated
  `ERROR:` 32/32 · `SCRIPT ERROR:` 32/32 · `Parse Error:` 32/32 ·
  **signature-line deletion 32/32 reject** · tail junk appended after the
  signature admitted 29/32 — the documented `signature in output` substring
  semantics, measured not assumed (the 3 that reject it are the allowlist rows,
  whose bare classification already rejects on the unclaimed `ERROR:` lines).
- **Harness property measured, not assumed (F4)**: passing an *empty*
  signature is admitted 32/32 (`"" in output` is trivially true) — see F4.
- **Mutant battery run (in-harness negative control)**: a second fresh
  `git archive 9d421fb2` checkout with exactly two patches to the committed
  harness (`probes/patch_mutant.py`, verified `diff` = 2 hunks: a **dead
  `expected_errors` entry** for `r98_canvas_zorder`, and a **one-token
  signature mutation** `r98b_gskew … gs_local=0.0258 → 0.0259`). Result in §5.1.

### 5.1 Mutant run result — FAIL, and only by design

Run dir `20261016T094759770183Z` (mutant tree), 470 rows executed:

- Exactly **2 non-PASS rows**: `r98b_gskew` — the mutated pin (the fixture
  emitted the *same* bytes as run 1, `gs_local=0.0258`, while the pin asked for
  `0.0259`) — and `probe_error_clause_surface`, whose **only** false
  discrimination is `r98_expected_errors_all_matched`; the other twelve round
  gates stay `True`, so the failure is localised to the injected dead entry.
- `census.dead_entry_count = 1`: the injected `r98_canvas_zorder` entry with
  `matched_lines = 0`, `dead_in_run = true` — a dead allowlist entry cannot
  pass silently, which is exactly what the r98 floor gate exists to prevent.
- **31/32 r98 rows still PASS** and 468/470 rows overall — the FAIL is caused
  by the two injections, not by collateral damage.
- Run-free cross-check of the same predicate (`probes/gate_recompose.py`, which
  re-composes the committed harness's own `surface_allowed_error` / `entry_shape`
  helpers and the committed predicate expression over run 1's captured outputs):
  gate **`True`** with the committed allowlists (census 75 rows) and **`False`**
  with the injected dead entry (census 76 rows, dead entry named).
- **Disclosure**: the first mutant attempt was **reaped at row 287** when the
  tool session that owned it exited — the log ends mid-run with no traceback and
  the process was gone (`pgrep` empty). It was relaunched detached
  (`setsid nohup timeout 2400 …`) and completed all 470 rows; only the second
  run is reported.

## 6. Cross-run stability — run1 vs run2 on identical fixture bytes

`probes/stability.py` → `artifacts/stability-run1-run2.json`, over the same 32
rows (run 2 uses the mutant *harness* but byte-identical *fixtures*):

- **32/32** rows: committed pin present in both runs, verdict PASS, exit 0.
- **30/32 captured outputs byte-identical.** The two that differ are the
  `qorder` pair (`r98b_qorder_tree`, `r98b_qorder_flat` — one shared launch,
  14 lines each, same line count) and they differ **only in the `stagger_off=`
  field**, on both the `R98B` diagnostic line and the PASS line's tail — one of
  the keys the author declared tick-phase-dependent and deliberately left
  outside the pins. `stagger=`, `stag_groups=`, `stagoff_groups=`, `tree=`,
  `rev=` did **not** move.
- **31/32 pinned lines byte-identical**; the exception is `r98b_qorder_tree`,
  whose *pinned prefix* is identical — the differing bytes sit entirely in the
  dropped `stagger_off=` tail. `r98b_qorder_flat`'s pinned substring
  (`flat=CBACBA`) is identical in both runs.
- `r98b_gskew`'s **emitted** PASS line is byte-identical across both runs
  (measured directly), so run 2's FAIL is attributable to the mutated pin alone.
- Consequence: the declared "unpinnable key" list is **empirically
  corroborated** — under two full runs at different host load (loadavg 9–15 vs
  5.6–7.2) the only bytes that moved are outside the pins, and every pinned byte
  held. That is the discipline the r98 encoding decisions claim, measured.

## 7. Carry-forward — the r98 bytes survive every later landing

- AST tuple comparison `9d421fb2 → 254e79dd → 2dcbb6f6 → 2ac38451` (the lane
  HEAD at the time of writing): **0 rows lost, 0 tuple values changed**; the 32
  r98 rows are present and **value-identical 32/32** in all of them. The later
  landings include r99 (+21 CASES), r100 (+27) and the integration commit
  `9ede7c50` ("dedupe crash sentinel CASES rows, 509/509 unique") — that dedupe
  touched **no** r98 row, which is exactly the kind of downstream edit this
  check exists to catch.
- The four r98 fixtures are **byte-identical in HEAD** (sha256 recomputed from
  `git show 2ac38451:…` equals §1's pins: `866480a1…`, `2e71c715…`,
  `7bb51902…`, `c038f748…`). So nothing in this pass is invalidated by the
  later landings, and the r98 rows are not silently rewritten downstream.

## 8. Findings

**F1 (documentation, load-bearing).** The author report and commit message
describe the **r96-based worktree**, not the landed merge: `CASES 419->451`
(landed `431 → 463`), `426 -> 458` results rows (landed **470**), `git diff
--numstat = 150 0` (landed `150 2`), "All 149 added lines" (landed 150
insertions; the report's own breakdown 123+17+10 already sums to 150). The
landed *bytes* are correct and green — the union is complete (§2) and my run is
470/470 (§3) — but any downstream reader who trusts "458" is reading a branch
number. Recommend the adjudicator record the landed counts.

**F2 (documentation).** The report's allowlist census reads "matched 2/1/6
lines respectively" for `clip`/`draw_refusal`/`clipmatrix`; measured (and
independently confirmed by the labrat) it is **1/2/6** — a transposition. The
report's own code comment has the per-arm counts right (`clip` 1/run,
`draw_refusal` 2/run, `clipmatrix` 6/run).

**F3 (coverage note, not a defect).** 2 of the 32 rows re-pin a disjoint slice
of a line another row already pins: `r98b_qflush_suppress` shares its launch
with `r98b_qflush_same_frame`, and `r98b_qorder_flat` with `r98b_qorder_tree`
(32 rows = 30 distinct `(fixture, flags)` launches). Both pins are disjoint and
both are load-bearing under §5's mutation sweep; the only consequence is that
those two rows are not independent *measurements* of each other.

**F4 (pre-existing harness property).** `classify_process` admits an empty
signature (`"" in output`), measured 32/32. No row in the tree is exposed —
all 475 signature strings are non-blank, the shortest being this round's
`flat=CBACBA` (11 chars) — but a future row with a blank signature would be
vacuously green. Not introduced by r98; worth a guard in a later round.

**F5 (pre-existing repo hygiene).** `corpus/fixtures/__pycache__/
run_battery.cpython-314.pyc` is tracked and **stale** (its header records
source size 215,328 vs the committed 477,774; blob `13319b13…` is identical in
r97 and r98, so r98 did not touch it, and r99/r100 churned it). Harmless: the
battery runs as `__main__`, and Python invalidates a stale cache by
mtime+size — but it is noise in a "byte-verified" tree.

**F6 (naming nit).** `r98c_flush`'s `multitick_frames_ge2` predicate is
`multitick_frames >= 1` (at least one process frame carrying ≥2 ticks); the key
name can be misread as "count ≥ 2". The regime claim is independently witnessed
by `draws_gt_frames=1`, `draws_eq_ticks=1`, `max_draws_per_pf_ge2=1`.

**F7 (host caveat).** `/tmp` inode exhaustion forced the archive checkout off
`/tmp` (§ Host caveat); runs happened under loadavg 9–15 with concurrent lanes.
Both are declared, not hidden: the run measured everything it claims to.

## 9. What this seat does not claim

- No judgement of whether the r98 *laws* are the right laws — this seat checks
  that the committed bytes measure what they say they measure, and that the
  pins are load-bearing. Law semantics belong to the adjudicator.
- No claim about rows outside the r98 scope beyond "they stayed green in my two
  full runs".
- No commit, no push, no repo-state mutation: `git status --untracked-files=no`
  in the lane repo is **empty** before and after this pass; receipts are
  untracked files under `corpus/live/r98-verifier/` and this report.

**Gate: VERIFIED** — commit `9d421fb2c0577488cf6f34399c123d81a91a067b`,
470/470 PASS on the pinned tree, union complete, 32/32 cells re-derived,
683/683 mutations rejected, the mutant control FAILing exactly and only where
injected, allowlist live-matched, carry-forward intact. Findings F1–F7 are
documentation and pre-existing-harness observations; none of them is a byte
defect in the r98 landing. Two things a reader should carry forward: the landed
tree is a **470-row** battery (not 458 — F1), and the only cross-run variance
observed anywhere in the 32 new cells sits in a key the author deliberately
left unpinned (§6).
