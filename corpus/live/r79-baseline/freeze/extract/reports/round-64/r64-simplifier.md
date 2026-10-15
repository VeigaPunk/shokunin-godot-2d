# Round 64 simplifier report — minimal-design critique of the while-live signature gate (host: devin)

Seat: simplifier (report-only). Lane axis: **depth** — a `poll()`-gated
signature read discriminating forged post-death signatures from genuine child
signatures (XConnector wave-3 synthesis, ported to `descendant_pipe_probe`).
I polled `git -C ~/Projects/shokunin/game-dev-2d-shokunin diff` until the
author's tracked diff existed, judged it element-by-element against the
production classifier, and re-ran the seven-flag battery into my own `--runs`
scope. No tracked edit, no commit, no sibling-scope write. Scratch under
`corpus/live/r64-simplifier/`; this report is my only tracked-path write.

## Poll evidence

- ~22:34 local (01:34Z): `git status`/`git diff` empty of tracked changes —
  only untracked `corpus/live/r64-*` sibling scratch (`pre-diff-status.txt`).
  Pre-diff shas: runner `fb7cab2bb0364b…`, fixture `4fce06765b091e9f…`
  (`pre-diff-sha256.txt`, matching the r64-baseline frozen record).
- ~22:44 local (01:44Z): one tracked hunk landed —
  `M corpus/fixtures/run_battery.py` **+224/−0**, contiguous block after the
  r63 meta, before `if args.probe_failing:`. Fixture untouched. Diff stable
  at re-poll (`tracked-diff.patch`, worktree diff sha256
  `305de6ef1bc02f47…` identical twice).
- Worktree shas at review (`tracked-sha256.txt`): runner
  `15ecad36aa996426…`; fixture `4fce06765b091e9f…` (unchanged).

## The diff as landed (verbatim inventory)

One file, one contiguous block (:879–1102), no existing line touched:

1. Constants `gate_marker` / `gate_bound=3.0` / `gate_poll_tick=0.005`.
2. `gated_signature_run(case, extra_args)` — the new observation path:
   raw `Popen` on **binary** pipes, `selectors.DefaultSelector` (module
   import reused from :13; the crash-exit arm already uses this selector
   idiom at :1385), `select(min(tick, remaining))` loop, `os.read(fd,65536)`
   accumulated into a `bytearray`, EOF → `unregister`. Per iteration a
   `process.poll()` heartbeat timestamps `dead_observed_at`; per event the
   poll bracket `alive_before`/`alive_after` straddles `os.read`; the gate
   verdict is `marker_observed and child_alive_at_marker_observation` where
   `child_alive_at_marker_observation` is the pre-read poll of the
   marker-completing chunk. Post-loop: timeout error, unconditional stream
   close, `wait(3)`/`kill` hygiene, `finally` kill — same shape as r62/r63.
   Post-return it reuses in-scope `pid_alive` (:629), `kernel_ppid` (:781),
   `classify_process` (:160) and the existing pid/banner regexes.
3. Eight gated runs: `genuine_default` ×3, `genuine_detach` ×1
   (`--spawn-detach`), `forge_release` ×3 (`--spawn-forge-release`),
   `forge_hold` ×1 (`--spawn-forge-hold`) — all EXISTING fixture arms, no
   fixture edit.
4. 12 discriminations → `all()` gate → one appended meta row
   `probe_while_live_signature_gate` (unconditional, per the r62/r63 meta
   convention), plus the non-gating orphan-reap loop.

Absent, correctly: no CASES tuple, no `--probe-*` flag, no fixture edit, no
`run_process`/`classify_process` change, no `expected_errors` entry.

## Independence evidence (my own measurements)

- `python3 corpus/fixtures/run_battery.py --godot /usr/bin/godot --runs
  corpus/live/r64-simplifier/runs <seven flags>` →
  `runs/20261014T014351500065Z/verdicts.json` **97/97 PASS** (sha256
  `b7c55beb166b3c91…`; console `battery.stdout`; arm extract
  `meta-row-evidence.json`).
- New meta observed: all 12 discriminations True. Margins
  (`dead_observed_at − marker_observed_at`): genuine +66.6/+66.8/+68.8ms,
  detach +68.9ms; forge_release −31.9/−31.7/−31.8ms; forge_hold −31.5ms.
  The gate accepts every genuine arm and rejects every forged arm on a
  **present** marker — the declared divergence reproduced independently,
  and `forge_release_*_inner_classification=True` on the same bytes.
- Prior-row stability vs `corpus/live/r64-baseline/runs/
  20261014T013523271164Z/verdicts.json` on the 8-field tuple
  (case/script/flags/expected_exit/signature/actual_exit/verdict/error):
  **0 mismatches, 0 missing** across all 96 prior rows; exactly +1 row
  (`probe_while_live_signature_gate`). The r63 pinned
  `descendant_pipe_forged_signature_release` row passes unchanged — its
  accepting boundary stays byte-stable and is documented, not fixed.
- `ast`-extraction: `CASES` **byte-identical** HEAD↔worktree; `run_process`,
  `classify_process`, `classify_streams`, `execute`, `pid_alive`,
  `kernel_ppid` all byte-identical; only `main` differs (+meta block) plus
  the new nested `gated_signature_run`.

## Verdict: minimal expression — YES; keep/drop per element

### KEEP — load-bearing

- **The selector+`os.read` gated-read loop itself.** Not duplicable into
  `run_process` (:149): `subprocess.run` exposes output only at return /
  `TimeoutExpired` — no observation-time hook can exist there. Not foldable
  into the :1385 crash-exit selector either: that loop reads one stream,
  breaks on `poll() is not None`, and uses `readline` — this gate's entire
  point is to keep reading *after* death and to catch a mid-chunk marker.
  Smallest mechanism that discriminates. Keep.
- **`process.poll()` as the liveness primitive.** This is the load-bearing
  choice of the whole diff: `poll()` (waitpid WNOHANG) reaps, so a dead
  child never reads alive. The scout measured the alternative —
  `os.kill(pid,0)`, i.e. `pid_alive`'s primitive — false-accepting the same
  forged bytes **5/5** through the dead-but-unreaped zombie window
  (`marker_states=['Z']`). The diff uses `pid_alive` only for post-return
  descendant checks, which is its correct use. Keep — this is exactly the
  zombie-window discrimination, killed by primitive choice with no new
  machinery.
- **`dead_observed_at` heartbeat + `dead < marker` ordering clauses.**
  Reader-side in-record ordering proof (~32ms lag on every forged rep) —
  what r63 could only fixture-assert via `write_ppid`. Real kill: it is
  what makes "post-death" receipt-carried rather than inferred. Keep.
- **`forge_release_marker_captured_post_death` +
  `forge_release_gate_rejects_what_classifier_accepts`.** The claim
  verbatim: a *present* marker rejected while the same bytes classify True
  — "rejects a present marker, never an absent one". Keep both.
- **`forge_hold_marker_captured_post_death`.** Second declared arm, same
  post-death write inside the bound record. Keep.
- **`detach_marker_accepted_while_live`.** Kills a real confound family —
  "the gate penalizes descendant survival rather than post-death writes".
  Without it the discrimination is unattributed. Keep.
- **`forge_withheld_banner_present`, `forge_write_post_orphan`,
  `forge_hold_write_ppid_kernel_corroborated`.** Descendant-authorship
  provenance, kernel-corroborated on the live hold descendant — carries
  r63's slip-class closure into this row. Keep all three.
- **`genuine_marker_accepted_while_live` +
  `gate_discriminates_forged_from_genuine`.** The positive arm and the
  headline. The headline clause is a strict composite of the per-arm
  clauses (implied), but it is the row's thesis statement — keep as named
  summary.
- **Rep scheme 3+1+3+1.** Genuine and release arms carry the timing-margin
  evidence; detach/hold outcomes are deterministic by construction so
  single reps suffice. ~7s added wall clock per battery — bounded. Keep.
- **Orphan-reap hygiene loop**, per-arm `elapsed_seconds`/`output_lines`/
  `command` evidence fields, and the honestly-scoped `bounded_claim`
  ("not a claim that observation-time liveness proves authorship in
  general (a pre-death-scheduled or faster-racing forge is out of scope)").
  Keep.

### WASH — strictly implied, decorative-but-cheap

- `genuine_never_observed_post_death` — can never be the sole failing
  clause (any failure is already caught by
  `genuine_marker_accepted_while_live`; a missing marker leaves
  `alive_at_obs` None → passes vacuously). It is the *named* falsification
  axis, which is the declared claim's own language — keep-or-delete; the
  author's report assigns it that documentary role explicitly. Wash.
- `forge_hold_gate_rejects` — implied by
  `forge_hold_marker_captured_post_death` (`alive_at_obs is False` ⟹
  `not gated_signature_accepted`). Wash.
- `hold_descendant_orphaned_alive` — implied by
  `forge_hold_write_ppid_kernel_corroborated` (`kernel_ppid` on a dead
  descendant returns None → corroboration fails). Same verdict the r63
  seat gave the identical clause. Wash.
- `child_alive_after_marker_read` — recorded, never gated. Correctly
  ungated (gating on it would false-reject a genuine straddling read); it
  documents the bracket surface per scout's keep-both-fields note.
  Keep-as-evidence, not a discriminator.

12 clauses → 8 load-bearing + 4 implied/documentary. Slightly oversized vs
the strict minimum, but each implied clause is 2–5 lines naming a distinct
claim-level concept under the file's discriminate-then-`all()` convention —
none mislead, and every real family (post-death write, confounded
descendant-existence, forged-vs-classifier divergence, provenance) is
killed by a load-bearing clause.

### Missing minimal additions — none required

- **Zombie-window race: dead by construction, no clause needed.** The only
  primitive that would leave it open is `os.kill(pid,0)`; the diff gates on
  `poll()`. Had it reused `pid_alive` for the child gate it would have been
  falsified outright (scout: 5/5 false-accepts). Nothing to add — the
  correct primitive *is* the fix.
- **r63's optional marker-count/suppression witness is unnecessary here.**
  A child-suppression regression (child prints the marker AND the
  descendant writes) flips `child_alive_at_marker_observation` to True on
  forged reps and is caught by `forge_*_marker_captured_post_death` —
  the gate itself now covers what r63's un-gated meta could not see.
- **Optional, not required:** a `genuine_inner_classification` clause
  (classify True on the genuine arms' same bytes) would mirror the release
  divergence symmetrically; classifier behavior on byte-identical genuine
  output is already pinned by prior rows.
- No dead code found in the block; all record fields are gated or emitted
  evidence consistent with prior meta schemas.

## Bounded correctness notes

- Same-tick collision: `now` is shared by the heartbeat and event reads, so
  `dead_observed_at == marker_observed_at` makes the strict `<` clause fail
  — fail-closed, and unreachable on this fixture (forged writes lag death
  ≥~30ms vs the 5ms tick, ~6 ticks of separation measured).
- Forged markers can never have `alive_before=True`: the descendant's
  ppid-gated write is provably post-death, so gating on the pre-read poll
  alone is sound for this arm family; the bracket field is honest evidence.
- `dead_observed_at=None` on genuine EOF-before-reap is documented in-code
  as while-live evidence — accurate (EOF can precede zombie reapability).
- POSIX-only (`/proc`, `os.kill`, `selectors`, signal kill hygiene);
  `bounded_claim` scopes Linux headless Godot 4.7.2.
- Convention note (same trade as r63): the meta re-shapes ~30 lines of
  bounded-Popen hygiene (record dict, regexes, wait/kill/close, orphan
  reap) rather than extracting a shared helper — convention-consistent,
  leaves hash-cited blocks byte-untouched; not line-minimal, admissible.

## Artifact inventory (my scope)

- `corpus/live/r64-simplifier/tracked-diff.patch` — reviewed diff snapshot
  (+224/−0; sha256 `305de6ef1bc02f47…` of `git diff` output, stable on
  re-poll); `tracked-sha256.txt`, `pre-diff-sha256.txt`,
  `pre-diff-status.txt`.
- `corpus/live/r64-simplifier/runs/20261014T014351500065Z/verdicts.json` —
  independent seven-flag battery **97/97 PASS**; all 12 discriminations
  true; prior 96 rows field-stable vs the r64-baseline receipt (0
  mismatches). `battery.stdout` — console stream.
- `corpus/live/r64-simplifier/meta-row-evidence.json` — per-arm extract
  with measured margins (genuine +66.6…+68.9ms while-live lead; forged
  −31.5…−31.9ms post-death lag).
- This report. No commit, no tracked-fixture mutation, no LOG/SCORECARD
  write.

Tooling note: no `lsp` device is exposed to this seat — the wash-candidate
clauses are dict keys produced and consumed inside the same meta hunk
(`all(gate_discriminations.values())`); their absence of external callers
was established by full-file read of the 1567-line runner plus `ast`
byte-identity checks, not grep sampling. Text fallback per seat card.

**Bottom line**: the landed diff is the minimal honest expression of the
declared move — one self-contained meta closure over the EXISTING arms, the
smallest new observation path (`poll()`-gated select+`os.read`) that can
discriminate them, additive +224/−0 with `CASES`, the classifier, and the
r63 pinned row byte-stable. The primitive choice is the standout: `poll()`
kills the zombie-window forgery family by construction where
`os.kill(pid,0)` would have been falsified 5/5 — the feared race needed no
new machinery, only the right syscall. Measured on this host: the gate
accepts genuine signatures (+67ms while-live margin) and rejects forged
ones (−32ms post-death lag) though present — the claim **holds**, and the
per-rep timing fields record the bounds rather than hiding them. Only trims
worth naming are the three strictly-implied discriminations (wash —
documentary naming, zero added constraint); no missing minimal additions;
no dead code.
