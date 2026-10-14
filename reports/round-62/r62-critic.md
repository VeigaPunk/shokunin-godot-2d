# Round 62 — critic: adversarial falsification of the pipe-EOF attribution and the landed rows

## Scope and method

LEAF critic seat, scratch-only and report-only. I wrote only this report and
`.shokunin/game-dev-2d/corpus/live/r62-critic/`. No tracked fixture, runner,
CASES row, lesson, LOG, or SCORECARD entry was touched; no subagent dispatch;
no git mutation.

Method: `corpus/live/r62-critic/drive_attacks.py` `ast.get_source_segment`-
extracts `run_process` and `classify_process` **verbatim** from the tracked
`corpus/fixtures/run_battery.py` and `exec`s them, so classification numbers
below are the production code path. `timeline_probe.py` replicates the
`subprocess.run` POSIX timeout shape (`Popen` + `communicate(timeout)`; on
`TimeoutExpired`: `kill()` + `wait()`, direct child only) while a monitor
thread polls `proc.poll()` and scans `/proc` for descendants — yielding the
timestamped child-death-vs-return datum a verdict record cannot carry.
`sabotage_eval.py` applies the landed meta row's seven discrimination
predicates verbatim to my mutant arm outcomes.

**Mid-flight provenance.** At probe time the tracked runner was HEAD sha256
`d705bca719fcdf24009f2302866ecf8066d49baa2adbc81dbd044c77b3bc5019`; the r62
author's working-tree diff landed mid-flight (worktree sha
`0c4c9bee70569c8ec29f98dea89c437d78587fd5c3c7b3220b76140ac59520dd`). I verified
via the same `ast` extraction that `run_process`, `classify_process`,
`classify_streams`, and `classify_audio_process` are **byte-identical**
HEAD↔worktree — the +142/−0 diff is additive only outside those functions, so
all arm numbers characterize both revisions.

Environment: Godot `4.7.2.stable.arch_linux.ed1daf0bf`, Linux
`7.2.3-arch1-3 x86_64`, Python `3.14.7`, `/usr/bin/sh` → `bash`.

## Landed rows under attack (author diff +142/−0, uncommitted at probe time)

- CASES `("descendant_pipe_detached_control", "descendant_pipe_probe.gd",
  ["--spawn-detach"], 0, "DESCENDANT_PIPE_PROBE: expected signature")` —
  descendant execs with all stdio → `/dev/null` (pipes EOF at child exit) yet
  outlives the run: child-exit-bound PASS.
- Meta `probe_descendant_pipe_eof` — drives `--spawn-hold` under one bounded
  `Popen`+`communicate(timeout=3.0)`; requires all seven discriminations:
  `hold_timed_out_with_child_dead` (`poll()`==0 at the `TimeoutExpired` catch),
  `hold_post_exit_write_captured`, `hold_misattributed_rejects`
  (`inner_classification is False`), `hold_descendant_orphaned_alive`,
  `detached_case_passes_clean`, `detached_lacks_post_exit_write`,
  `detached_descendant_orphaned_alive`; then SIGKILLs both orphaned descendant
  pids as harness hygiene.

My independent base-battery run of the landed worktree:
`python corpus/fixtures/run_battery.py --runs corpus/live/r62-critic/runs`
→ `runs/20261013T235355231215Z/verdicts.json` **PASS, 83/83 rows** (80 CASES
incl. the new control + 3 meta rows). The meta record observed:
`timed_out=true, child_exit_at_timeout=0, post_exit_write_captured=true,
godot_alive_at_return=false, descendant_alive_at_return=true,
elapsed=3.003s` — all seven discriminations true.

## Attack (a) — is the timeout actually child-liveness, not pipe-EOF?

**Attribution survives; falsification failed on both required arms.**

| arm | descendant | exit | error | elapsed | classify |
|---|---|---|---|---|---|
| clean | none | 0 | None | 0.408s | True |
| hold_silent | `sh` inherits pipes, sleeps 5s, silent | None | TIMEOUT 3.0s | 3.004s | False |
| hold_write | same + `DESC_POST_PARENT_WRITE` at +1.0s | None | TIMEOUT 3.0s | 3.003s | False |
| **early_release** | inherits pipes, exits at +1.2s | **0** | **None** | **1.533s** | **True** |
| detach_alive | all stdio →/dev/null, lives 6s | 0 | None | 0.409s | True |
| stderr_only | closes fd1, keeps fd2, sleeps 5s | None | TIMEOUT 3.0s | 3.003s | False |
| stdout_only | keeps fd1, closes fd2, sleeps 5s | None | TIMEOUT 3.0s | 3.003s | False |
| hold_pair_long | holders at 1.0s + 5s | None | TIMEOUT 3.0s | 3.003s | False |
| hold_pair_short | holders at 1.0s + 1.4s | 0 | None | 1.848s | True |
| flood | 9000 lines then holds 5s | None | TIMEOUT 3.0s | 3.004s | False |

- `detach_alive`: a descendant alive past the bound but holding **no** pipes
  produces **no delay** (0.409s, descendant `alive_at_return=true`, orphaned to
  ppid 1573) — a live descendant alone cannot trigger the timeout.
  Falsification arm (a1) fails: liveness is not the trigger.
- `early_release`: a pipe-holding descendant released at +1.2s produces return
  at **1.533s** with exit 0 — the wait ended at its fd release, far inside the
  3.0s bound. Falsification arm (a2) fails: the wait tracks the pipe, not a
  fixed deadline or a liveness poll.
- `stderr_only`/`stdout_only`: holding **either single** captured stream
  blocks → attribution is *any captured fd*, not stdout-specific.
- `hold_pair_*`: EOF arrives only when the **last** holder releases (1.4s
  holder → return 1.848s; 5s holder → TIMEOUT).
- `flood`: 9000 descendant-written lines (`desc_flood_lines_captured=9000`)
  landed in the TIMEOUT record's captured output — bulk post-parent-death
  capture, origin-blind.

Timestamped proof (`timeline-verdicts.json`): `tl_hold_silent` —
`child_reaped_at_s=0.533` (returncode 0), `communicate_ended_at_s=3.003`
(timed_out) — the harness waited **2.47s after confirmed child reap**;
descendant still alive at 3.015s, orphaned to ppid 1573. `tl_hang` —
child never reaped at bound (`child_reaped_at_s=null`), kill sent 3.011s,
descendant orphaned alive. `tl_early_release` — communicate returned 1.670s,
`timed_out=false`, `final_returncode=0`. `tl_detach` — returned 0.531s while
the descendant (pid 807856) lived on, orphaned.

**Refined invariant**: observed return ≈ `min(bound, max(child_exit,
last_captured_fd_release))`. The verdict record's `TIMEOUT`/`None`/`False`
cannot distinguish which term dominated — that is the pinned misattribution.

## Attack (b) — do the new rows pass for the wrong reason?

I evaluated all seven landed discriminations verbatim against nine mutant arm
outcomes (`sabotage-eval.json`):

| mutant | hold/control side | result |
|---|---|---|
| hold arm as authored (post-death write + 7s hold) | hold | accepts (intended) |
| **early_write**: descendant writes the marker +0.05s post-spawn — **before** the child's ~0.4s exit — then holds 5s | hold | **SLIPS**: all four hold discriminations true (`timed_out`+poll==0, marker present, classify False, descendant alive) although the "post-exit" line was written while the parent was still alive |
| hang_hold: child alive at bound + holder | hold | rejects — `poll()`→None, `hold_timed_out_with_child_dead` false |
| early_release (holder exits 1.2s) | hold | rejects — no timeout |
| silent_hold (holder never writes) | hold | rejects — `post_exit_write` absent |
| stderr_only / stdout_only holders | hold | rejects — `post_exit_write` absent |
| flood (9000 post-death lines, no marker) | hold | rejects — `post_exit_write` absent |
| spoof_hold (descendant wrote signature post-death; child suppressed it) | hold | rejects — `post_exit_write` absent |
| control as authored (detach, descendant sleeps 5s) | control | accepts (intended) |
| control descendant dies before meta check | control | rejects — `detached_descendant_orphaned_alive` false |
| control actually holds pipes (detached redirect removed) | control | rejects — row FAILs (exit None + TIMEOUT) |
| control emits the post-exit marker itself | control | rejects — `detached_lacks_post_exit_write` false |

**One slip, bounded**: `hold_post_exit_write_captured` verifies marker
*presence*, not write *ordering* — the "post-exit" property is timing-inferred
(fixture descendant sleeps 1.0s; child exits ~0.4s). A descendant writing the
same line at +0.05s satisfies the discrimination although the line is
pre-death. Consequence is bounded, not mechanism-breaking: even with the write
evidence discounted, `hold_timed_out_with_child_dead` (poll()==0 at the
timeout catch) alone proves the bound fired with the child dead — the only
remaining thing `communicate` waits on is captured-fd EOF. Hardening options:
rename the discrimination to `descendant_write_captured` (honest — a captured
descendant write, ordering unproven) or have the descendant write a line
carrying `ppid=$PPID` — ppid ≠ the printed `godot_pid` is post-orphan proof a
pre-death write cannot forge.

**Origin-blindness confirmed but correctly avoided**: my `spoof` arm — child
prints no signature, exits 0 at ~0.4s; descendant writes
`PIPE_CRITIC: expected signature` into the held pipe at +0.8s and releases at
~1.4s — produced `exit=0, marker=True, classify_process=True` at 1.749s: a
positive-path PASS on a signature the child never emitted. The landed control
row is immune **by construction** (its descendant is fd-detached — cannot
reach the pipes), and the hold arm's `marker_observed` is recorded but
**not gated**. This origin-blindness is a real hazard for any future row that
asserts signature presence over merged output from a pipe-held child; the
landed design does not fall into it.

**The load-bearing discriminator is `child_exit_at_timeout`**: `hold_silent`
and `hang_hold` produce byte-identical verdict-record fields
(`error=TIMEOUT`, `actual_exit=None`, `marker_observed=true`,
`inner_classification=False`, elapsed≈bound, godot dead at return — in the
hang arm dead *by kill*, in the hold arm dead *by exit*). Only the meta's
`poll()` inside the `TimeoutExpired` handler separates them: `0` vs `None`,
and my hang mutant is rejected by exactly that clause. A CASES-only pin of
this surface would have been impossible — the bounded-Popen meta is necessary,
not optional, and it carries the one field that distinguishes dead-child
pipe-wait from live-child kill.

## Attack (c) — platform/scheduling race analysis

- All TIMEOUT arms return bound-exact: elapsed 3.003–3.007s at bound 3.0
  (13 TIMEOUT arms across my runs + the author's meta at 3.003s).
- **Knee measured** (`bound-sweep.json`, bound 3.0): descendant-hold ≤2.6s →
  clean exit 0 (elapsed 2.511–2.950s); hold 2.7s → TIMEOUT. The flip point is
  `bound − spawn_offset(~0.33s)`; a hold arm within ~0.4s of the bound sits
  inside jitter — the last passing 2.6s run returned at 2.950s, only 0.05s of
  headroom. The authored hold (~7s: `sleep 1; echo; sleep 6`) has ~4.3s margin
  — robust; and the control descendant's aliveness check has ~1.5s margin
  (descendant dies 5s after control-case start; meta checks ~3.5s later).
  That second margin is the only real flake surface: a >1.5s scheduler stall
  between control row and meta check makes
  `detached_descendant_orphaned_alive` false — but that direction *fails
  closed* (meta FAIL on a healthy mechanism), never slips.
- `child_exit_at_timeout` cannot date the death — a child exiting at 2.99s
  reads identically to one exiting at 0.4s. Both still prove dead-at-bound;
  mechanism unaffected; precision bound only.
- `poll()` inside the `except TimeoutExpired` has a sub-ms race: a child dying
  exactly at the deadline could read as dead-at-bound when it was alive at
  deadline. Negligible; fails neither direction in practice.
- The post-exit-write ordering margin (~0.6s: write at +1.0s vs child exit
  ~0.4s) can invert on a stalled host where child startup exceeds 1.0s — the
  discrimination still passes (presence-only), so this is the same
  evidence-integrity slip class as `early_write`, reachable without sabotage.

## Verdict

- **(a) Not falsified.** Pipe-EOF attribution confirmed by release-tracking
  (1.533s return at descendant release), live-detached-descendant control
  (0.409s), any-pipe and last-holder semantics, and a 2.47s timestamped
  dead-child wait. Mechanism claim sharpened to
  `min(bound, max(child_exit, last_fd_EOF))`.
- **(b) Mostly sound.** 8/9 mutants rejected; the single slip
  (`early_write`) is evidence-integrity, not mechanism-breaking —
  `hold_timed_out_with_child_dead` carries the attribution alone. Recommend
  the marker rename or the `ppid=$PPID` hardening; neither is required for the
  bounded claim as worded.
- **(c) Margins measured.** Hold margin ~4.3s robust; control-aliveness
  ~1.5s fails-closed; write-ordering ~0.6s can invert under stall (same slip
  class); knee at hold ∈ (2.6, 2.7]s under bound 3.0 forbids any future
  near-bound hold fixture.
- Field stability: my independent landed-worktree base run was 83/83 PASS;
  `run_process`/`classify_process`/`classify_streams`/`classify_audio_process`
  byte-identical HEAD↔worktree; the diff is additive outside classifier code.
  The full seven-flag 94/94 and 92-prior-row field-compare is the verifier's
  surface, not duplicated here.

## Artifact inventory (`.shokunin/game-dev-2d/corpus/live/r62-critic/`)

- `proj/pipe_critic_probe.gd` (mutant fixture) + `proj/project.godot`;
  `drive_attacks.py` (verbatim-extraction arm driver, 14 arms + 8 sweep);
  `timeline_probe.py` (Popen+`/proc` poll timeline replica, 4 arms);
  `sabotage_eval.py` (author's predicates × mutants).
- `attack-verdicts.json` sha256
  `e24910a83d9aaf9762189dbccb3ce86b3b56e83d96d6240ea4fdac8cb7310157`;
  `bound-sweep.json` `22c8b42e795fcb2139917ea6b82efd7ee7a0c1cabfbbb8b275a3f61433413e65`;
  `timeline-verdicts.json` `93443858656e4d0f9ce32a7a1d4ca6cfea61ba0c7f7a9e4c03992c6cc1c8d8d6`;
  `early-write.json` (single-arm slip record); `sabotage-eval.json`.
- Raw captures `raw/*.stdout` (flood arm: 9000 `DESC_FLOOD_*` lines captured
  post-parent-death in a TIMEOUT record); `*.outlived` files landed by
  outliving descendants; `runs/20261013T235355231215Z/` = independent
  landed-worktree battery 83/83 PASS.

No commit, no tracked-fixture mutation, no LOG/SCORECARD write. All spawned
descendants self-exited (bounded `sleep`s); no stray processes remain.
