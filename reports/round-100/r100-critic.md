# r100 critic — adversarial review of the r100 capstone landing `2dcbb6f6` (25 GUI/input rows), plus the integration repairs that followed it

Seat `CRITIC` (g2d lane r100, capstone) | host **devin** | Godot
`4.7.2.stable.arch_linux.ed1daf0bf` (`/usr/bin/godot`, `--headless`,
`RendererDummy`, 64×64 root viewport, 60 tps), Python 3.14.7.

Reviewed commits:

* **`2dcbb6f6`** — the r100 capstone landing under review (the task's named
  target; lane HEAD at session start). Harness blob under test:
  `corpus/fixtures/run_battery.py` sha256
  `86a1aef86b36f70758a47bacd323879e9f76aa5a101bdb4b60e0a176fdeadc90`.
* **`9ede7c50`** — `r97-r100 integration fix: dedupe crash sentinel CASES rows
  (509/509 unique)`; harness blob sha256
  `35233c8b2edbd45c5a6f37fb3293613017657b8ab4a96ff94bb4967bf081c35c`.
* Lane HEAD at report time **`f02ee348`**; `git diff 9ede7c50..HEAD --
  corpus/fixtures/run_battery.py` is **empty**, so the run reported in §0 row 3
  is a measurement of the harness bytes that are live at HEAD. The two commits
  between them (`619ad7e0` pyc refresh, the r97/r98 adjudications) touch no
  harness byte.

Every harness check ran on a fresh `git archive <rev>` extraction, never on the
mutable worktree. **No tracked write, no commit, no delegated probe** (no
`probeParent` dispatch; every check is direct shell / fresh-process evidence).

**Scratch-path caveat (honest, load-bearing).** `/tmp` is a shared 16 GB tmpfs
that sat at 80–100 % all session with real `EDQUOT` write failures (reproduced:
a 111 MB `cp -a` failed mid-copy, and one battery run died inside
`shutil.copytree` with `Disk quota exceeded`). My archive trees therefore live
under **`/var/tmp/r100-critic/`**, outside the lane repo, not literally under
`/tmp`. Two runs launched inside `/tmp` were additionally **reaped mid-run** by
the host/session (no traceback, no verdict file) and are **not** counted as
evidence; only runs that reached a `verdicts.json` are.

**Load caveat.** The host was never idle: loadavg **11–15 on 32 cores**, with
4–8 concurrent foreign batteries (r97/r98/r99/r100 sibling lanes) and 17–37
foreign `godot` processes for the whole session. Every run below returned under
that contention, so none of these verdicts is an idle-host artifact.

**Prior art in this wave (read before filing).** `r98-critic` F1,
`r99-critic` F1/F2/F3, `r100-reviewer` F1–F6, `r100-verifier` F1/F1b/F2/F3/R1–R4
and `r100-simplifier` F1–F6 already cover the duplicate CASES rows, the
claim-fidelity mismatch and the `.pyc` record. This report **confirms** those
with its own measurements and files only what they do not contain (F1, F2 below,
plus the mode matrix, the four-round union check and the drop-mutant experiment).

---

## Verdict: **PASS-with-findings**

The lattice is sound and now measured on its own bytes: all 25 rows pin whole
measured lines, they reproduce byte-identically across two full runs and across
five launch modes, the three allowlist entries are live, the floor gate is
load-bearing, and the four fixtures are byte-copies of the frozen probes. The
landed *content* is faithful — a four-round union check finds **0 lost rows and
0 mangled tuples**.

Two findings are mine and are not on the record elsewhere:

* **F1 (MEDIUM, harness ceiling)** — no invariant anywhere in the harness can
  see a CASES row that is duplicated, dropped or renamed, and the
  `*_expected_errors_all_matched` family is vacuously true for an *absent*
  prefix. Measured, not argued: a drop-mutant that removes all 25 r100 rows
  while leaving their allowlist entries and gate in place still runs the battery
  to **green** (§2.10). This is the mechanism that let the splice artifact ride
  three consecutive landings to green.
* **F2 (MEDIUM, discrimination gap)** — the two `r100b_seq_*` rows pin exactly
  one line each of a 14-cell replay; a forged extra output line inside the
  replay leaves both rows PASS, and 3 of the replay's 4 measured divergences
  from the fresh-process pins are unconstrained by the row.

The duplicate rows in `2dcbb6f6` and the record/hygiene items are **already
filed and already repaired** upstream; this report verifies the repairs rather
than re-litigating them (§1 F3–F5).

---

## 0. What I ran

| # | batch | scope | result |
|---|---|---|---|
| 1 | **full battery, landed bytes** `2dcbb6f6` | fresh `git archive` → `python3 corpus/fixtures/run_battery.py`; run dir `tree/corpus/live/runs/20261016T093802973190Z/verdicts.json` | **519 rows, 519 PASS, 0 FAIL, verdict PASS** |
| 2 | **full battery, landed bytes** `2dcbb6f6`, second run | run dir `tree2/corpus/live/runs/20261016T094648175394Z/verdicts.json` | **519 rows, 519 PASS, 0 FAIL, verdict PASS** (§2.9) |
| 3 | **full battery, repaired harness** `9ede7c50` (= harness bytes live at HEAD `f02ee348`) | run dir `treeH/corpus/live/runs/20261016T093933406641Z/verdicts.json` | **516 rows, 516 PASS, 0 FAIL, verdict PASS** |
| 4 | **dead-allowlist mutant battery** (fixture side) | `2dcbb6f6` + one fixture edit: `r100_gui.gd:752` `img = tex.get_image()` → `pass` — the printed `r1 img_null=1` line is unchanged | **FAIL**, sole failing row `probe_error_clause_surface`, sole false gate `r100_expected_errors_all_matched`; the render row itself stays **PASS** (§2.4) |
| 5 | **drop-mutant battery** (harness side) | `9ede7c50` with **all 25 r100 CASES tuples deleted** (allowlist entries + gate left in place; 484 CASES, 0 r100 names) | **PASS** — 491 rows, 491 PASS, `r100_expected_errors_all_matched: True` over zero rows, 0 false gates (§2.10) |
| 6 | **launch-mode matrix** | 9 pinned arms × 5 engine modes (`quiet`, `--fixed-fps 30/120/1`, `--single-threaded-scene`) = 45 fresh processes, classified against the landed pins | **45/45 byte-identical** (§2.5) |
| 7 | **pin mutants** | `m_clip` (far sink x 80→70), `m_focus` (initial `grab_focus()` removed), `m_seq` (forged extra line inside the replay's hover cell) | clip **FAIL**, focus **FAIL**, both seq rows **PASS** (§2.3, F2) |
| 8 | **structural / provenance** | AST CASES census of `2dcbb6f6`, `9ede7c50`, r96/r97 commits and the r98/r99/r100 author files; four-round union diff; dict-key census; fixture↔frozen-probe digests; author manifest verify | §1, §2.2, §2.6 |
| 9 | **cross-artifact byte check** | my run-1 captures for the 25 r100 rows vs the author's manifest-verified fresh-process smoke receipts (`wt-r100`; `sha256sum -c` 275/275 OK) | **25/25 byte-identical** (§2.7) |

---

## 1. Findings

### F1 — MEDIUM (harness ceiling, **new**) · a duplicated, dropped or renamed CASES row is invisible to every gate, and the all-matched family is vacuous for an absent prefix

`2dcbb6f6` executed **512 CASES rows for 509 distinct names** and was green.
Nothing in the harness can see the difference: `for case in CASES: execute(*case)`
is the only consumer of the tuple list, there is **no count or uniqueness
assertion** in `main()` (its only three `assert`s are the causal-fixture anchor,
the export-output-dir-empty precondition and the seeded-mutant marker — none of
them about CASES), and the final payload carries no row count. The blindness
is symmetric:

```python
"r100_expected_errors_all_matched": all(
    not e["dead_in_run"]
    for r in census_rows
    if r["case"].startswith(("r100_gui_", "r100b_"))
    for e in r["entries"]),
```

`all()` over an **empty** generator is `True`. Drop or rename the whole r100
block and the gate still passes, the census simply carries no r100 rows, and the
battery stays green — the "named-by-round / covers-round-prefixes" shape
(r87–r99) is a floor *for rows that ran*, never an existence proof.

**Measured, not argued (§2.10).** A drop-mutant harness with all 25 r100 tuples
removed — their three `expected_errors` entries and the r100 gate left exactly
as landed — runs the full battery to **green**, with the r100 gate reporting
`True` over zero rows. That is the same blind spot that let the union-merge
splice artifact ride `9d421fb2` → `254e79dd` → `2dcbb6f6` to green and be caught
only by human-seat critics (`r98-critic` F1, `r99-critic` F2/F3,
`r100-reviewer` F1, `r100-verifier` F1, `r100-simplifier` F1/F3).

**Smallest safe correction.** One structural gate in `sf_discriminations` (it is
already evaluated on every battery run):

```python
"cases_integrity": (
    len([c[0] for c in CASES]) == len({c[0] for c in CASES})
    and all(sum(1 for c in CASES if c[0].startswith(p)) > 0
            for p in ("r100_gui_", "r100b_"))),
```

i.e. unique names **plus** a non-empty existence check per named-by-round
prefix. It would have failed `254e79dd` and `2dcbb6f6` at their own commits.
`r100-verifier` F1b proposes the same control *outside* the harness (a verifier-lane
AST check); putting it in the harness makes it fail the offending commit instead
of relying on a later seat to notice.

### F2 — MEDIUM (discrimination gap, **new**) · each `r100b_seq_*` row pins one line of a 14-cell replay; the other divergences are unconstrained

`r100b_seq_clean` pins the `cursor` cell (`c0=(30.0, 14.0) …`) and
`r100b_seq_noclean` the `hover` cell (`h0=P …`). Each row's captured output is
23 lines (the fixture replays all 14 cells in one process). Measured on the
landed bytes:

* the replay reproduces **10/14** cells byte-identically to their fresh-process
  pins; **4 diverge** — `cursor`, `touch`, `subvp` (`cursor_root=(20.0, …)` vs
  `(0.0, …)`) and `warp` (`cursor=(20.0, …)` vs `(0.0, …)`). The row pins the
  first of them only, so the contamination it is evidence *for* in
  `touch`/`subvp`/`warp` is not constrained by any row;
* mutant `m_seq` — an extra `print("FORGED_EXTRA_CELL_OUTPUT")` injected into
  the replay's `hover` cell — leaves **both** rows **PASS**, because
  `classify_process` ignores stdout lines that are not `ERROR:`/`SCRIPT ERROR:`/
  `Parse Error:` and the signature is a substring test.

The sibling seats treat these rows as "contamination rows by design"
(`r100-reviewer` §5.4, `r100-verifier` R3) and the author report's §8 says
"first-divergence lines"; the *report's §2* wording ("pin the contamination
chain (10/14 and 5/14 reproduction)") overstates what the rows constrain.
**Smallest safe correction:** pin the transcript — a multi-line signature is
expressible without touching `execute()` (`"\n".join` of the replay's 14 lines,
or of the first divergence plus the last cell) — or reword §2 to "first
divergence only; the remaining cells are unconstrained".

### F3 — confirmed prior art (already filed) · the report's and commit subject's arithmetic describes the pre-merge worktree file, not the landed blob

| object | sha256 | CASES | results | numstat |
|---|---|---|---|---|
| landed blob `2dcbb6f6:…/run_battery.py` | `86a1aef8…` | **512** (509 unique) | **519** | **134 / 2** |
| report §4 "shipped file" = author worktree `wt-r100` | `43ce922e…` | 444 (444 unique) | 451 | 132 / 0 |
| repaired `9ede7c50` | `35233c8b…` | 509 (509 unique) | 516 | 3 / 2 |

The author's manifest pins `run_battery.py` = `43ce922e…`, and its three runs are
451 rows each; the landing added 68 rows (r97/r98/r99 blocks + the duplicates)
after the round's last verification, so `86a1aef8…` had never been run
end-to-end before §0 rows 1–2. Already filed by `r100-reviewer` F1–F3,
`r100-verifier` F2 and `r100-simplifier` F4 (and by `r99-critic` F1 for the
previous round). **Smallest safe correction:** append a landing-delta note to
`r100-author.md` (landed sha, 512→509 CASES, 519→516 results, 134/2 → 3/2); the
round's substantive claims survive — I re-measured all 25 rows on the landed
bytes (§2.2).

### F4 — confirmed prior art, repaired · the `.pyc` record

At `2dcbb6f6` the committed pyc embeds `src_size 507 894` — a fresh compile of
the *committed* harness (the report's §8 sentence "restored to HEAD bytes" is
the inaccurate part), and after `9ede7c50` it became stale until `619ad7e0`
refreshed it (`src_size 507 480` = the deduped source; verified against
`git show HEAD:…pyc`). Filed by `r100-reviewer` F4, `r100-verifier` F3,
`r100-simplifier` F6; repaired. No row impact.

### F5 — confirmed prior art, repaired · the duplicated crash-sentinel rows in `2dcbb6f6`, and verification of the repair

Independently confirmed: `2dcbb6f6` CASES = 512 entries / 509 distinct, dups
`crash_spontaneous_sigabrt` ×3 and `crash_self_sigkill` ×2 → 5 crash launches
instead of 2 (measured ≈1.4 s each), and duplicate case names in the results
list and the allowlist census. Filed by `r98-critic` F1, `r99-critic` F2/F3,
`r100-reviewer` F1, `r100-verifier` F1/F1b, `r100-simplifier` F1/F3; repaired by
`9ede7c50`. **The repair verifies on my own run:** CASES 509/509 unique; tail
order `… r100b_seq_noclean, crash_spontaneous_sigabrt, crash_self_sigkill,
descendant_pipe_detached_control, descendant_pipe_forged_signature_release`
(canonical copies immediately ahead of the descendant rows, satisfying the r88
sleep-8 adjacency); the r100 block untouched; `expected_errors` and the gate
dict untouched; **516/516 PASS** with exactly one execution per sentinel; and
the 25 r100 rows' captured outputs are **byte-identical** between `2dcbb6f6` and
`9ede7c50` (§2.8).

---

## 2. What I verified positively

### 2.1 Green ×2 on the landed bytes

Run 1: **519 results (512 CASES + 7 meta), 519 PASS, 0 FAIL**, verdict `PASS`;
`probe_error_clause_surface` `PASS` with **0 false discriminations across all 49
gates**; `dead_entry_count = 0`. Run 2 (separate tree, same archive bytes):
identical result (§2.9). Run 3 on the repaired harness: **516/516 PASS**.

### 2.2 The 25 r100 rows, row by row

All 25 PASS in runs 1–3. Every pinned signature appears **exactly once** in its
row's captured merged output and as a **whole line** (`sig_line_hits = 1`,
`whole_line_hits = 1`) — the "full PASS lines, no prefix cut" claim holds for all
25. `r100_gui_render` carries exactly 1 `ERROR:` line and each `r100b_seq_*` row
1 (their replays do include the render cell), all absorbed by the three declared
entries; no unallowlisted `ERROR:` line appears anywhere in the block.

### 2.3 The pins discriminate (two more arms)

Fixture-side mutants that change the mechanism a row names: `m_clip` (far sink
moved x 80 → 70) → `r100_gui_clip` **FAIL**; `m_focus` (initial `grab_focus()`
removed) → `r100_gui_focus` **FAIL** (`f0 owner=null`), both classified with the
production clause copied verbatim. These cover two arms not in
`r100-verifier` §5's five behavioral mutants (dragphase, cursorphase, gui_drag,
gui_routing, emul_state); together, 7 of the 25 arms have now been shown to fail
when their mechanism is altered.

### 2.4 The `expected_errors` floor is live and isolates cleanly

Fixture-side dead-entry mutant (§0 row 4): with the dummy-storage readback
suppressed but the printed line unchanged, the battery verdict flips to
**FAIL** with exactly one failing row (`probe_error_clause_surface`) and exactly
one false discrimination (`r100_expected_errors_all_matched`); the census records
`dead_entry_count = 1`, the render entry `matched_lines = 0 / dead_in_run = True`,
the two sibling entries still live, and the render **row** still `PASS` — so the
flip is attributable to the gate alone. `r100-verifier` §7.1 mutated the
*allowlist entry* instead (also tripping `census_bare_classifier_consistent`);
the two mutants agree that the floor is load-bearing. The four census-family
gates the new entries flow through are all `True` in runs 1–3.

**The four merge-stack gate entries carry no splice defect** (prefix audit):
`r97_expected_errors_all_matched` filters `stree_lattice_` (the r97 round has no
entry-bearing case — vacuous by design, as its comment states);
`r98_…` filters `("r98_canvas_", "r98b_", "r98c_")` and covers all three
entry-bearing r98 cases (`r98_canvas_clip`, `r98_canvas_draw_refusal`,
`r98b_clipmatrix`); `r99_…` filters `("r99_audio_", "r99b_")` and covers
`r99_audio_gen`; `r100_…` filters `("r100_gui_", "r100b_")` and covers all three
r100 entries. No entry-bearing case in the four rounds falls outside its round's
gate prefix, and no gate prefix names a case that does not exist.

### 2.5 No envelope / mode split is needed — independently re-measured

9 pinned arms (`r100_gui_{cursor,motion,hover,routing}`,
`r100b_phase_{cursorphase,flushpos,coalesce,dragphase}`, `r100b_seq_clean`) × 5
launch modes (`quiet`, `--fixed-fps 30/120/1`, `--single-threaded-scene`) = **45
fresh processes, 45/45 byte-identical** to the landed pins — including the four
arms whose laws are about the input-flush / frame boundary. This is my own
measurement of the "7 modes, no envelope needed" claim, on the landed fixture
bytes. (The battery itself cannot express these flags; the claim was previously
carried only by the boundary report's table.)

### 2.6 The four-round merge stack is content-faithful

Union of the round blocks (r96 base + r97 from `f67094bb` + r98/r99/r100 from
each author's own worktree file) against the landed file: **0 rows missing,
0 tuple mismatches** — every round's rows landed tuple-for-tuple identical, so
the splice damage is multiplicity only. Provenance: the four landed fixtures are
**byte-identical** to the frozen probes (`dd826f6e…`, `49298e6c…`, `31087e78…`,
`4718a19e…`, matching both the tracked `corpus/live/r100-scout/proj/` and
`corpus/live/r100-boundary/probes/` copies); no fixture was folded; the author's
`manifest.sha256` verifies **275/275 OK**; `expected_errors` has 82 keys, no
orphan key, and no duplicate dict key anywhere in the file.

### 2.7 The author's row evidence transfers to the landed bytes

My run-1 captures for the 25 r100 rows are **byte-identical to the author's
manifest-verified fresh-process smoke receipts** (25/25, merged stdout+stderr,
same clause) — their §5.4 crosscheck reproduced on a different artifact, tree and
host load. The author's own three runs (451 rows each, zero duplicate names) and
`rows.json` (`classifications [True,True,True]`, `uniq_sha 1` per row) are
internally consistent.

### 2.8 Repair invariance

`compare_runs(2dcbb6f6, 9ede7c50)`: no verdict differences; **all 25 r100 rows'
outputs byte-identical**; the only differing rows are the corpus's known
environment-coupled classes (`save_process_*` pids/paths, `r93b_anim` wall-clock
samples, crash-dump addresses). The dedupe disturbed nothing in the r100 block.

### 2.9 Second run on the landed bytes

Run 2 (`2dcbb6f6`, separate archive tree and run dir): **519 results, 519 PASS,
0 FAIL**, verdict `PASS`; r100 gate and all 49 discriminations `True`;
`dead_entry_count = 0`; the three r100 entries `matched_lines = 1` each. The
landed bytes are therefore **green ×2**, matching the round's own bar, and the
25 r100 rows are byte-identical between the two runs (`compare_runs` → 25
compared, 0 differences; 34 other rows differ across runs in the known
environment-coupled classes).

### 2.10 The harness cannot see an absent block (drop-mutant, measured)

`9ede7c50` with the 25 r100 tuples deleted (50 lines; AST-verified 484 CASES,
484 distinct, 0 r100 names; the three `expected_errors` entries and the r100
gate left exactly as landed; run dir
`dropmut/corpus/live/runs/20261016T095659721638Z/verdicts.json`):

* **verdict `PASS` — 491 rows (484 CASES + 7 meta), 491 PASS, 0 FAIL**;
* `r100_expected_errors_all_matched: **True**` — evaluated over **zero** rows;
  **0 false discriminations across all 49 gates**;
* census `rows_with_expected_errors = 75`, `dead_entry_count = 0`, and **no
  r100 census row at all** — the three r100 allowlist entries are still in the
  `expected_errors` dict and are simply never looked at, because the only
  orphan check in the harness (`expected_errors` key ↔ CASES row) does not
  exist.

So the harness's verdict is invariant to the entire r100 block being present or
absent: the block can be deleted, renamed, or duplicated and the battery reports
`PASS` either way. This is the measured form of F1 and the reason the union-merge
splice artifact survived three landings.

---

## 3. Verdict and what the judge should weigh

**PASS-with-findings** on `2dcbb6f6`, and **PASS** on the repaired harness
(`9ede7c50`, whose harness bytes are live at HEAD `f02ee348`). The 25 rows, their
three allowlist entries and their floor gate are live, covered, mode-portable
and falsifiable; the landed content is the union of the four round blocks with
no loss or mangling; the round's substantive claims survive independent
re-measurement. Nothing in the round's *claims* is falsified by local evidence,
so no axis of the capstone's substance needs rejecting.

What remains for the judge is the harness ceiling (F1): the gate family cannot
see a duplicated, dropped or renamed row, which is *why* the same splice artifact
rode three landings to green and needed five seats to catch. F2 (the seq rows'
one-line discrimination) and the record items (F3–F5, all already filed
upstream) are small, local corrections.

**Axes touched by this review** (as named by the round's own claims): pin
integrity (all 25 rows — green ×2, whole-line, mode-portable across 45 launches);
allowlist floor liveness (green; falsified cleanly by a dead entry, twice over);
harness row-count/identity integrity (ceiling — F1, measured by the drop-mutant);
seq-row discrimination breadth (gap — F2); report↔commit provenance (mismatch —
F3, already filed).

**Nothing was committed, staged or edited in the lane repo by this seat.** The
only file this seat writes in the lane repo is this report; all mutant trees,
archive checkouts and receipts live under `/var/tmp/r100-critic/`.
