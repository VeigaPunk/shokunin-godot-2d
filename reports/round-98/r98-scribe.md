# r98 scribe — custody audit of landing `9d421fb2` (merge-resolution union+repair)

Seat `SCRIBE` (lane `r98-scribe`) | host **devin** | Godot
`4.7.2.stable.arch_linux.ed1daf0bf` (`/usr/bin/godot`, `--headless`) | audit run
`2026-10-16T09:34Z`

**Commit sha verified: `9d421fb2c0577488cf6f34399c123d81a91a067b`** (r98 author landing on
`main`, parent `f67094bb9cbf665242f85499c59e8b2f59cd5531` = r97 author).
Lane HEAD at audit **start**: `2dcbb6f6ed491e51aa76237b96f80c0b38fe607f` (r100 author, `main`);
HEAD **advanced during the audit** to `9ede7c5000fcfb117da68b098461623923256bfd`
("r97-r100 integration fix: dedupe crash sentinel CASES rows (509/509 unique)") — see §6.
Lane worktree at audit start: clean except untracked `corpus/live/**` evidence dirs.

## Axes (Godspeed)

- **A1 provenance fidelity** — do the report's hashes/paths resolve to the bytes they name?
- **A2 claim-scope accuracy** — does each claim describe *the landing*, or a different base?
- **A3 disclosure completeness** — are the gaps between evidence frame and landed frame stated?
- **A4 behavioural intactness** — do the landed bytes pass the full battery, and do the new rows
  detect their own mechanisms?

## Verdict

**INTACT** — the union+repair landing is content-faithful and the landed bytes are green on an
independent full battery run. Five findings, all of them claim-scope / disclosure findings
(F1–F5); **none invalidates the landed content, and no fabricated evidence was found.**

---

## 1. Custody chain (measured)

| step | sha | parent | committer / time (−0300) | run_battery.py | report bytes |
|---|---|---|---|---|---|
| r96 base (author worktree base) | `89f85ed8` | — | — | `+0` (base) | — |
| **author-branch landing** (`wt-r98`) | `68bee6e7` | `89f85ed8` | `Devin <devin@cognition.ai>` 06:17:46 | `+150 / −0` | `d076831d…` |
| r97 author | `f67094bb` | `d5c05ff8` | lane 06:17:38 | `+65 / −0` | — |
| **audited landing** (`main`) | `9d421fb2` | `f67094bb` | lane 06:18:23 | `+150 / −2` | `d076831d…` |
| r99 author | `254e79dd` | `9d421fb2` | lane 06:19:07 | `+151 / −2` | — |
| r100 author | `2dcbb6f6` | `254e79dd` | lane 06:19:49 | `+134 / −2` | — |
| r97-r100 dedupe fix (= lane HEAD now) | `9ede7c50` | `2dcbb6f6` | lane 06:34:32 | `+3 / −2` | — |

- `reports/round-98/r98-author.md` is **byte-identical** (`d076831d…`) in `68bee6e7` and
  `9d421fb2`; the r98 report is committed in both. The author report's own frame is the worktree
  (`…/game-dev-2d-shokunin-wt-r98`, branch `wt-r98`, base `89f85ed8`, "nothing committed, nothing
  staged"); it never names `f67094bb` or `9d421fb2`. The `wt-r98` worktree is now clean at
  `68bee6e7`.
- File shas at the audited landing (`git show 9d421fb2:… | sha256sum`):

| file | sha256 (landing) |
|---|---|
| `corpus/fixtures/run_battery.py` | `df4563c8ec1f22c31ea1c60fc10817fabeec20ae29b376d8ab4579f891bac973` |
| `corpus/fixtures/canvas_lattice.gd` | `866480a1aaa0a385ad5a0e56a3066af4e5341db2e4ab5a5963366aef949394f0` |
| `corpus/fixtures/r98b_attack.gd` | `2e71c7158c4f53dbaf5497798cef5cea7769c5799b443ffa5b3a2b289e95a2f8` |
| `corpus/fixtures/r98b_rksenum.gd` | `7bb519025cba6bb2102fcc96eaf72938955fa180d4b52871f76b12742174f76a` |
| `corpus/fixtures/r98c_flush.gd` | `c038f748a8572e4164fc0f6586199805b60f90929bdbed742bfcb7be28e1932e` |
| `reports/round-98/r98-author.md` | `d076831dc4c8e113a1a735ef77acc19b65646c20d8c2596c3e263ac8fab7c290` |

- **Author-branch bytes (the bytes the green battery evidence was produced on)**:
  `b5b86169c962f22ae591c8e729fa778f8d6819de88389546cdbee502028f65fa` for
  `run_battery.py` (author `final_bytes.sha256`, `68bee6e7`, and the `wt-r98` worktree all agree;
  the four fixture shas are identical to the landing's). The landing's `run_battery.py` is a
  **different byte-state** (`df4563c8…`) — see F3.

## 2. Committed-diff verification (the union+repair claims)

`git diff --numstat f67094bb 9d421fb2`:

```
791  0  corpus/fixtures/canvas_lattice.gd
822  0  corpus/fixtures/r98b_attack.gd
 68  0  corpus/fixtures/r98b_rksenum.gd
272  0  corpus/fixtures/r98c_flush.gd
150  2  corpus/fixtures/run_battery.py
244  0  reports/round-98/r98-author.md
```

**Union — CONFIRMED, measured by parsing both files (AST + `CASES` execution):**

- all 431 parent `CASES` names are present in the landing in parent order; the r97 block's
  12 `stree_lattice_*` tuples are **byte-equal** to `f67094bb`'s;
- the 32 r98 tuples (15 `r98_canvas_*` + 16 `r98b_*` + 1 `r98c_flush`) are **byte-equal** to the
  author's tuples (`b5b86169…`); inserted after the r97 block, ahead of the crash/descendant tail;
- `CASES` = **463**, zero duplicate case names, `ast.parse` clean; the r98 `expected_errors`
  region and the `r98_expected_errors_all_matched` floor gate are **byte-identical** to the
  author's; the r97 gate is intact;
- no r97/r96 file is touched by the landing diff (6 files, all r98);
- the crash/descendant tail order is preserved and `crash_spontaneous_sigabrt` still appears
  **exactly once** in `CASES`.

**Repair (the two `-2` lines) — the landing is *not* byte-insertion-only.** Exact re-flows:

- landed `run_battery.py:1281` = the r97 `stree_lattice_scene_probe` signature line with the r98
  block header appended as a trailing comment:
  `…rev=false'),    # --- r98 block: the CanvasItem draw/transform lattice ----…`
- landed `run_battery.py:1403` = the `r98c_flush` row with the `crash_spontaneous_sigabrt` tuple
  appended after it:
  `…bounded=1'),    ("crash_spontaneous_sigabrt", "spontaneous_crash_probe.gd", ["--spontaneous-crash"], -6, "SPONTANEOUS_CRASH_PROBE: expected signature"),`

Both deleted parent lines are **byte-verbatim substrings** of those landing lines; line-multiset
comparison shows the author file has exactly **3** lines that do not appear standalone in the
landing (the two above plus the standalone header line) and the landing has exactly **66** lines
the author file lacks — **64 of the r97 block's 65 added lines** (one r97 line coincides with a
line the author file already had) **plus the 2 joined lines**. **No content lost, none
duplicated, no other textual delta.** The commit message's "All 149 added lines verified present"
undercounts the actual 150 added lines (123 + 17 + 10 hunk lines) and does not disclose the
2 re-flows.

## 3. Independent execution evidence on the **landed** bytes

Fresh `git archive 9d421fb2` checkout (`corpus/fixtures/run_battery.py` sha re-verified
`df4563c8…` before and after the run), full battery from the tree root:

```
python3 corpus/fixtures/run_battery.py --runs corpus/live/r98-scribe/battery
```

Result (`corpus/live/r98-scribe/battery/20261016T092634245436Z/verdicts.json`, log
`…-battery-runA.log`): **`EXIT=0`, payload `verdict: PASS`, 470/470 results PASS**
(463 `CASES` + 7 meta rows), **32/32 r98 rows PASS**, 0 `FAIL` lines, gates
`r98_expected_errors_all_matched=true` and `r97_expected_errors_all_matched=true`,
`dead_entry_count=0`, census for the three r98 allowlist rows `matched_lines` **2 / 1 / 6**,
`dead_in_run=false`, `bare_classification_rejects=true`. Wall ≈ 7.5 min, one run.

- The landed run's row count is **470**, not the report's 458 — the difference is exactly the
  12 r97 rows the landing carries (see F2).
- **Host/load caveat, honest:** one full battery run on the landed bytes (not ×2). The author's
  ×2 greens (458/458 each, `verdict PASS`, same gates/census) are verified **from its retained
  verdicts** and are on the author-branch bytes `b5b86169…`, not on `df4563c8…`.
- **Deviation:** the contract's "archive-tree runs under `/tmp`" was blocked by the `/tmp` tmpfs
  quota (16 GiB fs, ≈3.1 GiB free; `tar` aborted with `Cannot write: Disk quota exceeded` on the
  1.82 GB / 125 220-file tracked tree). The fresh archive checkout therefore lives at
  `/home/vgpnk/Projects/shokunin/r98-scribe-archive`. No battery run used the lane worktree or
  the author worktree bytes.

## 4. Independent row verification against the author's 186 receipts

Own verifier (`scribe_verify_rows.py`), **landed** classifier (extracted verbatim by AST) +
**landed** rows + **landed** allowlist, against
`wt-r98/corpus/live/r98-author/runs/{quiet,load,munged}/*.rep*.out`:

- `classify_process` segment sha256 = `749fa0607e7707e614c1ab157a6f8e756dfc2f460746e6d218e6734ad8fa72c3`
  — **identical in the author file and the landed file** and equal to the hash the author's
  `analysis.json` records (the same segment earlier rounds pinned);
- **32/32 rows × 6/6 receipts = 192/192 PASS**, 0 mismatches, **0 foreign-cell signature hits**;
- the three allowlist rows **bare-reject** (production classifier, no allowlist) and pass with it;
- none of the six declared rep-unstable keys (`coalesce_draws`, `distinct_draw_pf`,
  `frames_with_tick`, `ticks_window`, `stagger`, `stagger_off`) is pinned by any landed row;
  all six measured varying across the 6 receipts of their cell;
- signature forms: **27 full-line + 3 declared prefixes + 2 declared substrings = 32**;
- **mutation check CONFIRMED on the landed bytes**: the retained mutant probe differs from the
  landed `r98c_flush.gd` at exactly line 131 (`pace.delay_ms = 0` vs `= 80`); the production
  classifier rejects the mutant payload (`multitick_frames_ge2=0 draws_gt_frames=0
  max_draws_per_pf_ge2=0 hide_ticksep_same_frame=0`) and accepts the clean receipt;
- receipts census: **186 runs** (31 cells × 2 reps × 3 batches), all `rc=0`, no `TIMEOUT`, `.err`
  non-empty only for the three allowlist cells; `r98c_flush` wall **2604–2696 ms** (bound 8 s);
  scout/attack cells **459–1026 ms**.

**Upstream provenance:** the three byte-copy fixtures hash-match the frozen upstream probes and
their manifests (`r98-scout/manifest.sha256` `866480a1…`; `r98-boundary/manifest.sha256`
`2e71c715…`, `7bb51902…`). All 15 landed `r98_canvas_*` signatures are byte-equal to the scout's
own `ROWS_PREFIX` entries (14 of them also equal the scout's full-line `ROWS`; the declared
`queue` prefix cut before ` events_tail=` is byte-exact). The boundary's own `analysis.txt`
carries the r98b pinned payloads in all 7 modes (`scout_match=True`, `SCOUT_DIFF=[]`) and its §6
line "nothing here changes the scout's 15 rows" is quoted accurately. The author's disclosed
gap is real: the scout/boundary manifests list **471 / 1057** run artifacts, the raw `runs/`
trees are absent from `wt-r98` and only partial in the lane worktree
(`r98-scout/runs` 260 entries, `r98-boundary/runs` 10 entries).

## 5. Findings

**F1 — claim-scope, medium — "insertion-only +150/−0" does not describe the landing.**
The report's "Insertion-only proof" (`git diff --numstat` = `150 0`; `grep -c '^-[^-]'` = 0) and
the commit message's "All 149 added lines" are statements about the pre-r97 base `89f85ed8`
(true at `68bee6e7`: `+150/−0`). On the audited landing (`f67094bb → 9d421fb2`) the diff is
**`+150/−2`** and the literal `-0` count is **2**. Content is fully preserved (both deletions are
verbatim substrings of the joined landing lines), so this is a fidelity/scope defect in the
claim, not lost work.

**F2 — claim-scope, medium — row-count arithmetic describes the author branch, not the landing.**
Report: "CASES 419 → 451 tuples (results rows 426 → 458 incl. the 7 meta rows)"; commit message:
"CASES 419->451 block". Measured: `f67094bb` = **431** `CASES`, landing = **463**, landed battery
results = **470**; `451`/`458` are `89f85ed8 → author file` numbers. A judge reading the report's
counts against the landed commit sees a 12-row gap that is simply the r97 union.

**F3 — provenance, medium — the green evidence bytes ≠ the landed bytes.**
Both battery greens and `final_bytes.sha256` name `b5b86169…` (`68bee6e7` / `wt-r98`); the landed
`run_battery.py` is `df4563c8…` (two line-joins apart). The report never states that the landing
is a different byte-state, so its green claims are, strictly, author-branch claims. This seat
closes the gap with its own full battery on the landed bytes (**470/470 PASS**, §3) — the landed
bytes are green; the report's own evidence is not about them.

**F4 — disclosure, low-medium — "nothing committed, nothing staged" is stale.**
The report text (committed byte-identically at `68bee6e7` 06:17:46 and `9d421fb2` 06:18:23) says
nothing was committed; the r98 work is committed on `wt-r98` (`68bee6e7`) and on `main`
(`9d421fb2`), and the worktree is clean at `68bee6e7`. True when written (report mtime 06:09:21),
never updated. The only text describing the merge resolution is the landing commit message —
which itself misstates the counts (F1/F2).

**F5 — disclosure, low — the independent probe has no artifact; one numeric range is narrow.**
The report's "Independent probe (frozen `probeParent` dispatch) — exactly one" (ufo-labrat, 7/7
CONFIRMED) has no artifact: no r98 labrat task file in the wave `tasks/` dir and no
`corpus/live/r98-labrat*`. Its verdict is report-only (advisory, as the report itself labels it)
and cannot be verified from artifacts. Also, the report's "0.5–0.7 s per scout/attack cell" is
narrower than the retained receipts (**459–1026 ms**); both remain far under the 8 s bound.

*No finding against the landed content, the byte-copy provenance, the allowlist/gate behaviour,
the mutation check, or the receipts census.*

## 6. Out-of-scope observations (verbatim for the canonical judge; r99/r100 custody, not r98)

- `254e79dd` (r99): `CASES` = **485**, **duplicate case name `crash_spontaneous_sigabrt`**;
  `run_battery.py` landing `+151/−2`.
- `2dcbb6f6` (r100 = lane HEAD at audit start): `CASES` = **512**, multiplicities
  `crash_spontaneous_sigabrt ×3`, `crash_self_sigkill ×2`; `run_battery.py` landing `+134/−2`;
  the 32 r98 rows are still present. The r100 report claims "battery 451/451 on final bytes"
  while the file carries 512 `CASES`.
- Both later landings repeat the same 2-deletion pattern seen at r98's landing. The first
  duplicate appears at r99, i.e. after r98's re-flow moved the crash tuple off its standalone
  line.
- **Resolved during this audit, independently corroborated:** HEAD advanced to `9ede7c50`
  ("r97-r100 integration fix: dedupe crash sentinel CASES rows (509/509 unique)", parent
  `2dcbb6f6`, `+3/−2`). Its message attributes the flag to **r98-critic F1** ("union-merge splice
  artifact … crash_spontaneous_sigabrt appeared x3 and crash_self_sigkill x2 after serial union
  landings. Semantically inert (same row run twice) but broke CASES uniqueness and row-count
  arithmetic"). My own AST census confirms it: `9ede7c50` → `CASES` **509**, **0 duplicates**
  (`crash_*` ×1 each), all 32 r98 rows intact. **Not judged here** — recorded as fact for the
  canonical judge; the r98 landing `9d421fb2` itself has zero duplicate names (§2).

## 7. Scope discipline

Read-only in the lane repo; the only write is this untracked report
(`reports/round-98/r98-scribe.md`, written 06:35:19 −0300). No product-code edit, no
commit, no judge invocation, no other runtime, no author-worktree mutation. Scratch artifacts
live under `/home/vgpnk/Projects/shokunin/r98-scribe-archive` (archive checkout + battery run)
and `/home/vgpnk/Projects/shokunin/r98-scribe-scratch`.

Not this seat's write, recorded for completeness: the lane worktree shows tracked
`corpus/fixtures/__pycache__/run_battery.cpython-314.pyc` modified (`Bin 457028 → 456798`),
mtime **06:34:12 −0300** — the same second as `run_battery.py`'s edit by the integration commit
`9ede7c50` (06:34:32), i.e. a regenerated bytecode sidecar of that fix, not of this audit. The
r98 landing's own diff does not touch `__pycache__` (§2).

## 8. Artifact paths and exact commands

Evidence produced by this seat:

- `reports/round-98/r98-scribe.md` (this report)
- `/home/vgpnk/Projects/shokunin/r98-scribe-archive/corpus/live/r98-scribe/battery/20261016T092634245436Z/verdicts.json`
- `/home/vgpnk/Projects/shokunin/r98-scribe-archive-battery-runA.log` (battery stdout, `EXIT=0`)
- `/tmp/r98-audit/landing/{run_battery.py,canvas_lattice.gd,r98b_attack.gd,r98b_rksenum.gd,r98c_flush.gd}`
  (landed bytes extracted from `9d421fb2`), `/tmp/r98-audit/scribe_verify_rows.py`
- author evidence read (not produced) at
  `/home/vgpnk/Projects/shokunin/game-dev-2d-shokunin-wt-r98/corpus/live/r98-author/**`

```
git rev-parse HEAD                                   # 2dcbb6f6… (lane HEAD)
git diff --numstat f67094bb 9d421fb2                 # 150 2 run_battery.py
git diff -U0 f67094bb 9d421fb2 -- corpus/fixtures/run_battery.py | grep -c '^-[^-]'   # 2
git show --stat 9d421fb2                             # 6 files, 2347 insertions, 2 deletions
git show 9d421fb2:corpus/fixtures/run_battery.py | sha256sum    # df4563c8…
sha256sum wt-r98/corpus/fixtures/run_battery.py      # b5b86169…
python3 -c "<AST: exec CASES, count names/dups/r98 rows, compare author|parent>"  # §2
python3 /tmp/r98-audit/scribe_verify_rows.py         # §4 (32×6/6, mutant, forms)
git archive 9d421fb2 | tar -x -C …/r98-scribe-archive
cd …/r98-scribe-archive && python3 corpus/fixtures/run_battery.py --runs corpus/live/r98-scribe/battery
                                                     # EXIT=0, 470/470 PASS
```

**Report authored by the `scribe` seat; the canonical Rust runtime remains the sole judge.**
