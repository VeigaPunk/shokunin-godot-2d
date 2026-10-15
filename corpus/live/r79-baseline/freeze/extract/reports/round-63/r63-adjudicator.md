# r63 Sol adjudicator — game-dev-2d lane, wave `shokunin-train-20261013-w3`

Adjudicator: Sol (parent session), host devin, 2026-10-14. Scope: round 63 declared depth move — pin the merged-stream signature-spoofing boundary (r62 critic's measured isolation) as a tracked known-accepting forgery row; prior 94 rows field-stable.

## Declared claim (verbatim)

"a tracked fixture arm where a pipe-holding descendant emits the signature post-parent-death produces a classification shape distinguishable from a genuine child signature ONLY via the child-death/timeout evidence fields (child_exit_at_timeout, timed_out), never via signature presence alone — i.e. the spoof is accepted on the signature axis and must be recorded as a documented forgery-accepting boundary, not fixed."

## Measured result

**CONFIRMED with critic corrections absorbed.** `classify_process`'s signature clause is `signature in output` over merged `stdout+stderr` — presence-only, origin-blind. The landed surface pins both shapes:

- `descendant_pipe_forged_signature_release` (CASES row): child withholds the signature; reparenting-gated descendant writes it post-exit and releases the pipes before the bound → **exit 0, error null, signature present → PASS** — a full PASS-shaped forgery indistinguishable from the genuine control on classification-visible fields.
- `probe_descendant_signature_spoof` (meta): hold arm under a 3.0s bound → TIMEOUT record carrying the forged signature (`child_exit_at_timeout=0`, `inner_classification=false`) — rejection rides the error axis only.

**Critic corrections applied at integration (two defects, both closed):**
1. Fabricated `write_ppid` slip class (self-reported ppid echo scored 8/8 pre-fix) → new `hold_write_ppid_kernel_corroborated` discrimination: kernel `/proc/<pid>/stat` ppid at return must equal the self-reported reparented ppid and differ from godot pid. Verified live: `kernel_ppid=1573 == write_ppid=1573 != godot_pid`.
2. Provenance anchor: `release_withheld_banner_present` discrimination requires the child's `child_signature=withheld` banner in the release row output — without it the signature's descendant authorship is unproven in-record.

Discriminations now total 10 (8 author + 2 integration). Claim wording narrowed per critic: the separation evidence is *output provenance* (withheld banner + kernel-corroborated ppid), not the death/timeout fields themselves, which take identical values forged vs genuine.

## Adjudicator's own reproduction (committed tree, HEAD `de78edb`)

Full seven-flag battery into `/tmp/r63-intfix/runs/20261014T011001647358Z/`: **96/96 PASS**, `PASS battery` exit 0; meta receipt `probe_descendant_signature_spoof` PASS — `hold_arm: timed_out=true, child_exit_at_timeout=0, marker_observed=true, write_ppid=1573, descendant_kernel_ppid_at_return=1573, inner_classification=false`; release row PASS exit 0 with `child_signature=withheld` banner + forged signature + `write_ppid=1573`.

## Seat-evidence audit

| seat | landed | key evidence |
|---|---|---|
| author | `r63-author.md` + tracked +31/−1 +155/−0 | 96/96 battery, 94 prior 0-mismatch, labrat receipt-confirmed |
| critic | `r63-critic.md` | two defects landed (self-reported ppid slip 8/8; death/timeout fields identical forged-vs-genuine — both absorbed); no liveness guard confirmed; stderr-forge parity |
| reviewer | `r63-reviewer.md` | r62 audit AGREE-all (94/94 fresh, reparenting gate source-verified); record-level forgery pre-corroborated on committed classify_process |
| baseline | `r63-baseline.md` | frozen `edbd945` 94/94, 0 mismatches vs r62 non-author receipt |
| scout | `r63-scout.md` | merge point :146, presence match :170 mapped; release shape measured as CASES-carryable; `classify_streams` also accepts forged fd1 |
| scribe | `r63-scribe.md` | lesson + LOG drafts inside report (see `corpus/lessons/r63-signature-spoof-boundary.md`) |
| simplifier | `r63-simplifier.md` | minimal-expression verdict; 96/96 independent; `write_ppid` echo singled out as the standout; optional `marker_occurrences==1` flagged |
| boundary | `r63-boundary.md` | depth-agnostic forgery (d2_spoof grandchild PASS); transitive holder set to arbitrary depth; startup knee recast as stochastic band 7.55–7.65@8s; zombies under live godot ≥1.1–2s |
| verifier | `r63-verifier.md` | **AGREE all five claims** — 96/96 (`ef9d9ac6…`), 94-row 0-mismatch, fabricated `write_ppid=5211102` caught by kernel check, 6/6 forgery spot-checks, no leaked processes |

## Disclosures recorded

- Stale-figure nit (verifier, cosmetic): author report cites pre-integration `+155/−0`/8-discrimination diff; committed is `+189/−0`/10 — the delta is exactly the critic's asks, named in `de78edb`'s message.
- Release-arm `write_ppid` is fixture-asserted only (descendant dead before return — kernel check impossible); the hold arm's corroboration covers the shared provenance mechanism.
- Simplifier's optional `marker_occurrences==1` suppression witness and the deletable `hold_descendant_orphaned_alive` clause noted; not applied (wash/deferred).
- XConnector synthesis proposal: a while-live marker-read gate (3d-style) would narrow the accepting boundary to post-death forgeries only — candidate for a future round, not landed.
- Runner comment ~L649 stale ("~1s after spawn" predates the ppid gate) — cosmetic, flagged by reviewer.

## Per-axis verdicts

- **depth: improved locally** — the presence-only signature clause is now a pinned, measured boundary: which record fields do and don't carry attribution is exhaustively characterized (kernel-corroborated provenance vs self-reported vs absent).
- **coverage: improved locally** — 94→96 rows; both forgery shapes tracked; transitive-depth forgery documented by boundary.
- **calibration: unchanged** — bounds/thresholds untouched; 3.0s meta bound inside the measured misattribution window.

Verdict: **ADMIT** — no demonstrated scoped harm; four SHONEN boxes remain checked without promotion.

## Bounds retained

Linux headless Godot 4.7.2, Python 3.14.7, POSIX pipes, CPython subprocess semantics; subreaper ppid 1573 host-specific; single-host timing margins; the boundary is documented-accepting, not hardened (policy decision, not this round's scope); no exported-build/non-POSIX claims.
