# r62 verifier report — game-dev-2d (non-author, independent)

- Seat: named NON-AUTHOR verifier for round 62 (wave shokunin-train-20261013-w2).
  I authored none of the r62 content; all measurements below are my own
  executions/captures on the committed tree.
- Repo under review: `~/Projects/shokunin/game-dev-2d-shokunin` (canonical;
  `.shokunin/game-dev-2d` symlink from `~/Projects/prymeagnt/game-dev-2d`).
- HEAD under test: `81a100c` "game-dev-2d r62: tracked pipe-EOF
  descendant-timeout classification surface". `git status` clean except my own
  untracked `corpus/live/r62-verifier/` scratch.
- Host: `/usr/bin/godot` → `4.7.2.stable.arch_linux.ed1daf0bf`; python 3.14.7.
- My run dir: `corpus/live/r62-verifier/runs/20261014T001002305311Z/`;
  captured stdout `corpus/live/r62-verifier/battery.stdout`; independent
  descendant driver `corpus/live/r62-verifier/scratch/verifier_drive.py`,
  instrumented variant `corpus/live/r62-verifier/scratch/proj/verifier_pipe_probe.gd`,
  verdicts `corpus/live/r62-verifier/scratch/verifier-drive-verdicts.json`.

## Task 1 — seven-flag battery replay — AGREE

Command (repo root):

    python3 corpus/fixtures/run_battery.py --godot /usr/bin/godot \
      --runs corpus/live/r62-verifier/runs \
      --probe-failing --probe-unrelated-error --probe-export-launch \
      --probe-godot-error --probe-stream-attribution --probe-crash-exit --probe-timeout

- Last line: `PASS battery: corpus/live/r62-verifier/runs/20261014T001002305311Z/verdicts.json`.
- `verdicts.json` sha256
  `7a4ee384f708a54787c8d782a326a31b1dae8c7d103fc7acabede5bbec221c4f`:
  **94 results, all 94 PASS**, top-level `verdict: PASS`,
  `godot: /usr/bin/godot`, `probe_failing: true`.
- stdout: 93 `^PASS` rows + `PASS battery`; 2 `^FAIL` lines are the designed
  inner rejections (`FAIL godot_error_unrelated: exit=1 classification=False`,
  `FAIL stream_reject: exit=0 classification=False`) inside their enclosing
  PASS probes — same shape as r61, not defects.
- Opt-in artifacts all PASS: `export-launch-verdicts.json`,
  `godot-error-verdicts.json`, `stream-attribution-verdicts.json`,
  `crash-exit-verdicts.json`, `timeout-verdicts.json`,
  `save-process-verdicts.json`.

## Task 2 — 92 prior rows field-identical — AGREE (vs both baselines)

Tuple `(script, flags, expected_exit, actual_exit, signature, verdict, error)`
indexed by `case` (meta rows carry only `verdict`, per r60/r61 precedent).

    mine=json.load(open('corpus/live/r62-verifier/runs/20261014T001002305311Z/verdicts.json'))
    base=json.load(open('corpus/lessons/r61-crash-non-author.json'))   # 92 rows
    # also run against corpus/live/r62-baseline/runs/20261013T233453788036Z/verdicts.json

- vs `r61-crash-non-author.json`: mine 94 rows; extras exactly
  `['descendant_pipe_detached_control', 'probe_descendant_pipe_eof']`;
  base-only `[]`; **0 field mismatches** over the 92 shared cases.
- vs the committed r62-baseline receipt: identical outcome — same two extras,
  **0 mismatches**. The r62 surface is additive and the r61 field shape is
  field-stable under my independent run.

## Task 3 — `probe_descendant_pipe_eof` meta + post-exit proof — AGREE

My own run's meta row (`verdicts.json`, row 94):

- `verdict: PASS`, `mode: bounded_popen_plus_cases_control`, `bound_seconds: 3.0`.
- `hold_arm`: `timed_out=true` while `child_exit_at_timeout=0` — the pinned
  misattribution reproduces under my hand: `subprocess.TimeoutExpired` fired
  and `proc.poll()` in the except-block already reaped the child at exit 0.
  `actual_exit=null`, `error="TIMEOUT after 3.0 seconds"`,
  `marker_observed=true`, `post_exit_write_captured=true`,
  `godot_alive_at_return=false`, `descendant_alive_at_return=true`,
  `inner_classification=false`, `elapsed_seconds=3.004`.
- All **7 discriminations true**: `hold_timed_out_with_child_dead`,
  `hold_post_exit_write_captured`, `hold_misattributed_rejects`,
  `hold_descendant_orphaned_alive`, `detached_case_passes_clean`,
  `detached_lacks_post_exit_write`, `detached_descendant_orphaned_alive`.
- `hold_output_lines` ends with `DESCENDANT_PIPE_AFTER_EXIT_WRITE` — the
  descendant's write drained through the captured pipe inside the bound.
- Detached control row: `descendant_pipe_detached_control` exit=0, error=null,
  PASS; output shows `spawned_pid` but no `AFTER_EXIT_WRITE` line; the meta
  recorded its descendant (pid 883908) alive at return — the "descendant
  silently outlives the run" half holds for the control too.

Independent post-exit verification (my scratch; NOT trusting the fixture's
own gate): `verifier_drive.py` reruns the **committed** fixture plus my
instrumented variant under a `Popen+communicate(3.0)` harness shaped like the
meta block, while a sampler thread records kernel-side `/proc` state at 15 ms
cadence — godot child state and descendant ppid — so reparenting is observed
by the harness, not self-reported. `classify_process` was ast-extracted
verbatim from the committed runner.

- `committed_hold` (committed fixture copy, sha256 `054f37c9…` identical):
  `timed_out=true`, `child_exit_at_timeout=0`, `post_write=true`,
  `inner=false`, `desc_alive=true`. Sampler: descendant first seen with
  `ppid=886230` (the godot pid — `OS.create_process` makes a direct child);
  at t≈0.37s `godot_state=Z` and `desc_ppid` flipped to `1573` (= `systemd`,
  the session subreaper) in the same sample — kernel reparenting coincides
  with godot's death. The descendant's write is emitted only after its own
  ppid leaves the godot pid, i.e. post-exit. **The write is genuinely
  post-exit, observed from the kernel side.**
- `gate_trace_d500` (my variant, `--parent-delay-ms=500`): descendant trace
  `first_pp=886274 godot_pid=886274` → gate armed on the real parent;
  `gate_iters=11` (≈550 ms ≈ the 500 ms delay + teardown), then
  `release_pp=1573 godot_state_at_release=Z` — the gate held while the parent
  lived and released exactly at reparenting. Sampler agrees (flip t=0.877s,
  godot Z).
- `gate_trace_d0` (real committed timing): `first_pp=886332==godot_pid`,
  `gate_iters=2`, `release_pp=1573`, `godot_state_at_release=Z` — even without
  the delay the loop observes the parent-alive state for ~2 ticks before
  teardown completes; write remains post-exit.

## Task 4 — forgery spot-checks — recorded (gate is load-bearing)

Same scratch driver; the harness-side receipt fields are what a CASES/meta
row would observe.

- `forge_d2000` — stripped ppid loop + `--parent-delay-ms=2000`
  (deterministic pre-exit): descendant trace `pre_write pp=886451
  godot_state=S` — the marker was written **while godot was demonstrably
  alive** (state S, ppid still the godot pid). Yet the harness observed
  `timed_out=true`, `child_exit_at_timeout=0` (godot died ~2.33s < 3s bound),
  `post_write=true`, `inner=false`, `desc_alive=true` — **every observable
  receipt field identical to the genuine arm**. A presence-only
  `AFTER_EXIT_WRITE` string satisfies the receipt while the pinned semantic
  ("written after parent death") is false. Conclusion: the receipt alone
  cannot carry the semantics — the fixture's reparenting gate is the
  load-bearing element, and per Task 3 it does gate.
- `forge_d0` — stripped loop at committed timing: `pre_write pp=886514
  godot_state=S` — pre-exit even in the real race (sh spawn beats godot
  teardown); identical receipt fields as above.
- `forge_detach` — marker written through the pipe, then all stdio exec'd to
  `/dev/null`, descendant lives 8 s more: `timed_out=false`,
  `actual_exit=0`, `post_write=true`, `inner_classification=true`,
  `desc_alive=true`, **elapsed 0.698s vs 3.0s** for every held-pipe arm.
  Writing without holding pipes does not satisfy the pinned semantics:
  communicate returns at child exit — no TIMEOUT, inner classification
  accepts (PASS-shaped) — and it doubles as direct evidence the bound is
  pipe-drain (EOF returns early) rather than a fixed timer or liveness wait.
- Hygiene: both the committed meta block and my driver SIGKILL-reap the
  bounded orphaned sleeps; `pgrep` post-run shows no leaked `sleep 6/8`.

## Task 5 — commits + ast-hashes — AGREE

- `git rev-parse --verify`: `b95d180` → `b95d180185b7eb8c67f4673f175b3457c2f5de46`,
  `08d80dc` → `08d80dc0e7a74a6a26c7ed4d50f9fcc5341b95fd`,
  `81a100c` → `81a100c85ec8fb72e6e8c53afb6de08f9cba13d4`; all three
  `git merge-base --is-ancestor <c> HEAD` → yes (`81a100c` is HEAD).
- Runner shas: r61 committed `b95d180:run_battery.py` sha256
  `d705bca719fcdf24009f2302866ecf8066d49baa2adbc81dbd044c77b3bc5019` (the
  dispatch's `d705bca7…`, matches the baseline/scribe records); HEAD
  `0c4c9bee70569c8ec29f98dea89c437d78587fd5c3c7b3220b76140ac59520dd`.
- Per-function hashes (both source-segment sha256 and `ast.dump` sha256) of
  the four pinned functions, `b95d180` vs HEAD — **all identical**:

      main.run_process            src 88728b23…07c5  ast b5bc4337…ae63
      main.classify_process       src 749fa060…fa72  ast 03fdbf78…71da
      main.classify_streams       src a886968f…c6d7  ast 4dcdba31…1193
      main.classify_audio_process src 3a6bc0e8…cfaa  ast 2d58be0c…7e9b

  Whole-file function-set diff: only `main` changed (new nested
  `main.pid_alive` + the r62 meta block); every other function is
  source-identical r61→r62.
- Diff shape `git diff b95d180 81a100c -- corpus/fixtures/run_battery.py`:
  `+++`/`---` headers aside, **0 removed lines, 142 added** (140 non-empty +
  2 bare `+`) — the "+142/−0 additive" claim is exact;
  `descendant_pipe_probe.gd` +39 new file.

## Low-severity observations (non-blocking)

- The meta's `hold_descendant_orphaned_alive` discrimination is checked at
  run-return (~0.4–0.7s after spawn); a descendant sleeping < that window
  would flip it. The committed `sleep 6`/`sleep 8` bounds leave comfortable
  margin on this host; not gate-enforced.
- `probe_descendant_pipe_eof` runs unconditionally, so every battery
  invocation spawns/kills two short-lived OS descendants — intended and
  documented in the row; ~3s wall clock.
- The committed meta's `post_exit_write_captured` is a presence check on the
  captured text — the "post-exit" meaning is carried entirely by the
  fixture's ppid gate (my `forge_d2000` proves an ungated marker produces an
  identical receipt). The gate is verified working (Task 3); just noting the
  check itself is not self-verifying — exactly the critic's forgery class,
  closed in the fixture, not in the receipt shape.

## Residual risk / verification gaps

- Single host (this machine, `Linux 7.2.3-arch1-3`-era userspace, python
  3.14.7, godot 4.7.2). The row's own `bounded_claim` scopes to Linux
  headless Godot 4.7.2 POSIX semantics — honest and consistent with what I
  reproduced.
- `gate_iters=2` on the real-timing arm: the gate held, but the margin is
  ~100 ms of engine teardown. On a faster-teardown build the descendant's
  first `/proc/self/stat` read could already observe the flipped ppid — the
  write would still be post-exit (ppid flip ⟹ parent dead), just with
  `gate_iters=0` semantics: still correct, only less demonstrably "waited".
- `first_pp==godot_pid` in every arm confirms `OS.create_process` makes a
  direct child here; if a future Godot spawned via an intermediate, the gate
  would open instantly (write pre-exit but after spawn) — the fixture comment
  and my `forge_*` arms document that failure shape.

## Verdict

Every checkable claim reproduces under my own execution: 94/94 PASS
(`verdicts.json` sha `7a4ee384…`), the 92 prior rows field-identical to both
committed baselines with extras exactly the two new r62 rows, the meta row's
7 discriminations all true with `timed_out=true` ∧ `child_exit_at_timeout=0`
∧ `post_exit_write_captured=true`, the post-exit write confirmed
kernel-side (descendant ppid flip to systemd coincident with godot's zombie
state, `godot_state_at_release=Z`), forgery arms showing a stripped gate
forges the receipt but not the semantics and a non-held-pipe write doesn't
misattribute at all, all three commits resolve and are ancestors of HEAD, and
the four classify/run functions are source- and ast-identical to the r61
runner (`d705bca7…`). **No actionable defect found in scope. I agree with
the author's coverage claim.**
