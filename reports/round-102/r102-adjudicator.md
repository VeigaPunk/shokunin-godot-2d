# r102-adjudicator — round 102 verdict (orchestrator seat)

Date: 2026-10-18. Swarm: 64 seats, opencode-go-7/deepseek-v4.1-flash, 61+
completed (no provider casualties; all claims fully staffed). Host: load 4–9.

## Declared claims

| claim | axis | before | after (target) |
|---|---|---|---|
| C1 export launch matrix | coverage | 0 rows; r101 measured the embedded/stock launch split unpinned | +8 `export_launch` rows green ×2 |
| C2 timeout-probe old-bound repair | depth | `slow_clean_old_bound.marker_observed=false` in both r101 runs (0.75s bound vs ~0.8s spawn→marker latency); probe meta red | bound re-derived (1.25s) with counterfactuals; probe green ×2 |
| C3 simplifier queue + stale-cite repair | calibration | r98/r99/r100/r91 queues unlanded; live `.shokunin/` counting commands at SCORECARD 8-10, PROVINCE | 10 folds landed byte-proven (−59 lines unique), census pin re-anchored, live citations repaired |

## Attribution correction (r101 record, append-only)

The r101 adjudicator/LOG attributed the timeout-probe redness to the
`hold_open_new_bound` arm ("r62 descendant-pipe class") — **mechanically wrong**.
Recomputation over both r101 records (PLANNER + CONNECTOR seats independently):
the failing conjunct is `old_rejects`, solely because
`slow_clean_old_bound.marker_observed=false` at the 0.75s bound; the hold arm is
green in both runs (`hold_rejects=True`, elapsed 3.005/3.006), and the actual
r62 `probe_descendant_pipe_eof` row PASSes. CONNECTOR's 50-receipt census: 46/46
pre-r101 receipts PASS; only the two r101 runs fail. Cause: host spawn→marker
latency drifted ~0.39s (r22 era) → ~0.8s (r101+); the bound now kills the marker
pre-capture. Correction recorded here + LOG; r101 files unchanged (append-only).

## Landed changes

- C1: `corpus/fixtures/export_launch.gd` (+s01–s06 companions, unregistered —
  harness-consolidated, same disposition class as r101's) + 8 CASES rows +
  `r102_expected_errors_all_matched` gate + `cases_integrity` prefix.
- C2: `run_battery.py` old bound 0.75→1.25 with measured rationale comment
  (counterfactuals: 1.0→4/4, 1.25→4/4 marker captures timed_out still true,
  1.4→2/2 — r102-D3 replica sha 8f93033e…).
- C3: 10 folded fixtures (audio, canvas, dss, nav, particles, r95b_order,
  r98b_attack, r98b_rksenum, scene_io, stree) — byte-proven vs claimed folded
  shas (S0 scratch trees; order-independence verified); census row re-anchored
  (r95b_lines 778→776, sha 4f7e945e→b367559e — the blocking companion B2);
  harness comment shas B1/B3 + Group C; SCORECARD 8-10 live counting commands;
  PROVINCE 2 citations. S4 census: historical records (corpus/live receipts,
  lesson old-absolute lines) deliberately NOT rewritten — 3985+ live-record
  citations are evidence, not defects.

## Before → after measurements

Counting command: `python corpus/fixtures/run_battery.py --probe-failing
--probe-unrelated-error --probe-export-launch --probe-godot-error
--probe-stream-attribution --probe-crash-exit --probe-timeout` (the r102-repaired
SCORECARD form).

- C1: 0 → 8 rows; receipts: 8/8 PASS in both runs (embed_boot, embed_self_contained,
  embed_mainpack_refusal, stock_boot, stock_sidecar_census, stock_mainpack_refusal,
  editor_mainpack_contrast, stock_missing_sidecar).
- C2: timeout probe meta **PASS ×2**; old arm now times out at 1.25s WITH marker
  observed (run 2: err=`TIMEOUT after 1.25 seconds`, marker=True), new arm clean,
  hold arm rejects — all three designed outcomes restored.
- C3: −59 unique lines across 10 fixtures; cross-run stability: 543 shared rows
  r101↔r102, byte-identical receipts except run-dir path lines (comparator's 8
  "mismatches" are all verdict-path summaries) — the folds' defining property
  holds at the battery level; census row green on the re-anchored pin;
  `grep -c '.shokunin/game-dev-2d/corpus/fixtures/run_battery.py' SCORECARD.md` = 0 (was 3).

## Mutation / verification battery

- mut08 filter-case inversion: **REJECT all swapped arms** +
  `row_rejects_swapped_fixture=True`, triangulation OK; measured finding: Godot
  export filters are CASE-INSENSITIVE (`case_flip_mutant_byte_identical=true`) —
  E4's probe row pins that no-op honestly.
- mut09 span attack: foreign lines injected pre/post the pinned span run but
  `pinned_identical: True` — the known bounded residual class (no whole-blob
  row-count gate; r100-critic F1 family, same disclosure as r101's seqfull
  post-END residual). Routed, not a new defect.
- mut01_launch: script staging defect (`no registry spec` — expected an artifact
  the seat didn't ship); its attack class (ELF-magic/size forgery) is covered by
  the rows' own `tail_magic`/`bin_gt_template` pins + W1's guard spec. Disclosed.
- mut06 gate: script path bug (double `reports/` prefix); the gate itself
  verified by direct probe — a resurrected stale citation is caught
  (`echo 'python .shokunin/...run_battery.py' | grep -c '.shokunin/game-dev-2d/corpus/fixtures/run_battery.py'` → 1).
- C2's counterfactual requirement: D3's replica measured 1.0→4/4, 1.25→4/4
  marker captures (timed_out still true), 1.4→2/2 — the fix is not a tautology
  (the bound still rejects the genuinely-slow arm); MUT-04's inverse script on
  file for the fixed probe.
- Seat dry-runs for mut02/03/04/05/07 on record in their shards; two scripts
  (mut03_s10, mut05) hit mid-swarm path/CLI drift — disclosed, evidence not
  asserted.

## Environmental / bounded

- joys device still enumerates intermittently — the r101 F3 folded pins hold
  (no trio redness expected in r102 receipts).
- r101-ytrans lesson's r95b sha citation: dated r102 correction appended (fold
  changed the tripwired sha by design).
- S4 residual: lessons old-absolute citation family (384 lines) = historical
  strategy records; routed policy decision to operator (rewrite-history vs
  preserve) — NOT unilaterally rewritten.

## Verdict

| axis | verdict | evidence |
|---|---|---|
| coverage | **improved** | +8 `export_launch` rows green ×2 in-battery (embedded boot/self-contained/refusal, stock boot/sidecar/refusal, editor contrast, missing-sidecar hole class); launch matrix binds the path-override support split r101 left unpinned |
| depth | **improved** | timeout-probe mechanism closed: failing conjunct isolated (`slow_clean_old_bound.marker_observed` at the 0.75s bound; hold arm green — r101 attribution corrected), latency drift measured (~0.39s→~0.8s since r22), bound re-derived to 1.25s with non-tautological counterfactuals; probe meta green ×2 |
| calibration | **improved** | 10 byte-proven simplifier folds landed (−59 lines; per-hunk discrimination evidence; cross-run receipt stability 543 rows); census pin re-anchored with the r95b fold (blocking companion); live stale citations repaired (SCORECARD 3 counting commands, PROVINCE 2) with gate verified |

**Admission: ADMIT-WITH-FINDINGS** (bounded: pre/post-span foreign-line residual
routed; mut01/mut06 script staging defects disclosed; 2 by-design reject-arm
print lines are informational, probe metas green).

## SHONEN

- [ ] decision tables — `[~]`: +3 r102 lesson drafts (launch matrix, timeout
  repair, hygiene) with cited sources; probation gate operator-owned.
- [ ] end-to-end domain task — `[ ]` untouched.
- [ ] executable instructions — `[~]`: export_launch path runs end-to-end
  (8 rows + lesson), non-author review pending.
- [ ] no cross-domain bleed — `[~]`: connector filed 0 contests; 3D lane
  untouched (its r106 observed active under the parallel session; side-round
  deferral stands via L0, must run before 2D r105).

L0: unchanged + one addition: S4's lessons old-absolute citation family (384
lines) is a preserve-vs-rewrite policy call for the operator (historical
strategy records vs live docs). The QUALITY.md note from a r101 scribe could
not be actioned — no QUALITY.md exists in the lane repo (scribe likely meant
corpus/knowledge or a fleet file; routed to scout-class census in a future
round).
