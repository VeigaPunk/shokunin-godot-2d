# r62 Sol adjudicator — game-dev-2d lane, wave `shokunin-train-20261013-w2`

Adjudicator: Sol (parent session), host devin, 2026-10-14. Scope: round 62 declared coverage move — formalize the tree-timeout pipe-EOF misattribution (descendant-held stdout blocks classification past direct-child death; no process-group kill) as a tracked classification surface, all prior 92 rows field-stable.

## Declared claim (verbatim)

"a fixture whose child spawns a pipe-holding descendant → observed classification under the timeout bound is pipe-EOF-bound (not child-liveness-bound); discriminating control (descendant closes/detaches stdout, or no descendant) → child-exit-bound classification. Zero-or-minimal additive runner change only; all prior 92 rows must stay field-stable."

## Measured result

**CONFIRMED and landed.** `communicate(timeout)` is a completion + pipe-drain deadline: the hold arm's direct child exits 0 at ~0.4s yet the record is `TIMEOUT after 3.0 seconds`, `actual_exit=None`, `post_exit_write_captured=true`, descendant orphaned alive — while the fd-detached control exits 0 in ~0.4s PASS. The pipe-EOF wait is proven by the critic's timeline probe (child reaped 0.533s, return 3.003s — 2.47s of pure EOF wait) and by release-gating (return tracks fd-release at 1.533s, not the bound).

## Adjudicator's own reproduction (committed tree, HEAD `81a100c`)

Ran the full seven-flag battery into `/tmp/r62-fix2/runs/20261014T000659225647Z/`:

- **94/94 PASS**, `PASS battery` exit 0; only 2 stdout FAIL lines are the designed inner rejections (`godot_error_unrelated`, `stream_reject`).
- Meta receipt `probe_descendant_pipe_eof`: all 7 discriminations true; `timed_out=true ∧ child_exit_at_timeout=0 ∧ post_exit_write_captured=true ∧ descendant_alive_at_return=true`, elapsed 3.004s.
- `descendant_pipe_detached_control`: PASS exit 0, signature verbatim.

Two integration corrections were applied on top of the author's landed diff, each driven by a named seat finding:

1. **Critic's slip class closed**: `post_exit_write_captured` was presence-only — a +0.05s pre-death write satisfied it. The fixture's hold arm now gates its write on kernel reparenting (`/proc/self/stat` ppid flip off the godot pid), making the write provably post-exit. First attempt (`kill -0` wait) deadlocked — zombie child isn't reaped until the bound, so the write never fired; corrected to the ppid-flip mechanism and re-verified 94/94 with `post_exit_write_captured=true`.
2. **Simplifier's thin-margin gate**: detached-descendant `sleep 5`→`sleep 8` (~1.5s → ~4.6s margin on the orphan-alive check; fails-closed flake risk only).

## Seat-evidence audit

| seat | landed | key evidence |
|---|---|---|
| author | `r62-author.md` + tracked +142/−0 + fixture | 94/94, 92 prior 0-mismatch, 7 discriminations |
| critic | `r62-critic.md` | 9 sabotage mutants 8-reject/1-slip (absorbed at integration); bound-exact 3.003–3.007s; knee ∈(2.6,2.7]s; timeline-probe pipe-EOF proof |
| reviewer | `r62-reviewer.md` | r61 audit AGREE-all; marker-clause forgery False; commits resolve |
| baseline | `r62-baseline.md` | frozen `08d80dc` 92/92, 0 mismatches vs r61 non-author receipt |
| boundary | `r62-boundary.md` | 3d-port recon: `OS.create_process` descendants are own-session leaders → `killpg` can't reach them; `start_new_session`-less killpg would kill the harness group |
| scout | `r62-scout.md` | `run_process` map (142–151), hold-arm impossibility as CASES row proven, insertion map |
| scribe | `r62-scribe.md` | lesson + LOG drafts (landed with post-fix updates `corpus/lessons/r62-pipe-eof-timeout.md`) |
| simplifier | `r62-simplifier.md` | minimal-diff verdict; `cases_cannot_carry_hold` proof; thin-margin watch item (applied) |
| verifier | `r62-verifier.md` | **AGREE all claims** — 94/94 fresh replay sha `7a4ee384…`, 92-row 0-mismatch, ppid-gate traced kernel-side (`gate_iters=2`, release at ppid=1573), stripped-gate forgery documented, no leaked processes post-run |

## Disclosures recorded (none gate-affecting)

- Reviewer nit: r61 reports cite pre-correction runner sha `3bb29044…`; committed is `d705bca7…` (delta = exactly the r61 marker-clause line). Substance verified; adjudications should pin post-correction shas.
- Verifier observation: the post-exit receipt field is presence-shaped — post-exit-ness is enforced by the fixture gate, not provable from the receipt alone (stripped-gate forge produces an identical receipt). Bounded honestly in the lesson.
- Boundary: a naive 3d→2d `killpg` port cannot reach own-session `OS.create_process` descendants, and without `start_new_session` would kill the harness's own group — port stays a future-round policy call.
- XConnector drift note: sibling file:line receipts may cite either pre- or post-edit frame of `run_battery.py`.

## Per-axis verdicts

- **coverage: improved locally** — 92→94 rows; the pipe-EOF/descendant-orphan surface now has a tracked accept control + 7-discrimination meta pin on a provable post-exit write.
- **depth: improved locally** — `communicate(timeout)` semantics pinned exactly (completion + pipe-drain; `return ≈ min(bound, max(child_exit, last_fd_EOF))`); single-stream and last-holder refinements measured.
- **calibration: unchanged** — thresholds/bounds untouched; meta bound 3.0s sits inside the measured misattribution window.

Verdict: **ADMIT** — no demonstrated scoped harm; four SHONEN boxes remain checked without promotion.

## Bounds retained

Linux headless Godot 4.7.2, Python 3.14.7, POSIX pipes, CPython subprocess semantics; no Windows/macOS, exported build, >1 descendant depth, >64KiB descendant writes, signal-origin, or general process-tree-policy inference. Orphan hygiene: meta reaps its bounded sleeps; verifier confirmed no leaks.
