# Round 62 baseline report — frozen before-state seven-flag replay (host: devin)

Seat: baseline (scout). Lane axis this round: **coverage** (formalize the
tree-timeout pipe-EOF misattribution the r61 boundary seat probed as a tracked
classification surface). This report is the immutable before-state: no tracked
fixture/runner edit, no commit, no LOG/SCORECARD write. All artifacts under
`corpus/live/r62-baseline/` (scratch) plus this report.

## Frozen-tree provenance (no in-place fallback needed)

- Frozen source: `git -C ~/Projects/shokunin/game-dev-2d-shokunin archive HEAD | tar -x -C .shokunin/game-dev-2d/corpus/live/r62-baseline/tree`
- HEAD frozen: `08d80dc0e7a74a6a26c7ed4d50f9fcc5341b95fd`
  (`game-dev-2d r61 adjudication: ADMIT coverage — verifier report + lessons +
  LOG/SCORECARD`, one commit after the r61 work commit `b95d180`; carries the
  r61-landed crash CASES rows, allowlist entry, and meta row).
- Frozen runner sha256 `d705bca719fcdf24009f2302866ecf8066d49baa2adbc81dbd044c77b3bc5019`
  — byte-identical to the live worktree copy.
- Frozen `corpus/fixtures/spontaneous_crash_probe.gd` sha256
  `8d4c5b43939f48ce1f099286cb0002415e53373177e4e81aae1922b01ca81ba5` —
  byte-identical to the live worktree copy.
- `verdicts.json["seed"]` records
  `/home/vgpnk/Projects/shokunin/game-dev-2d-shokunin/corpus/live/r62-baseline/tree/corpus/fixtures`
  → the run provably executed the **frozen copy**, not the live tree.
  Contamination risk: none; concurrent sibling-lane edits cannot reach the archive.

## Exact invocation

cwd `~/Projects/prymeagnt/game-dev-2d` (worktree root; `.shokunin/game-dev-2d/`
symlinks into the canonical lane repo):

```
python3 .shokunin/game-dev-2d/corpus/live/r62-baseline/tree/corpus/fixtures/run_battery.py \
  --godot /usr/bin/godot \
  --runs .shokunin/game-dev-2d/corpus/live/r62-baseline/runs \
  --probe-failing --probe-unrelated-error --probe-export-launch \
  --probe-godot-error --probe-stream-attribution --probe-crash-exit --probe-timeout
```

Environment: Godot `4.7.2.stable.arch_linux.ed1daf0bf` (`/usr/bin/godot`),
Linux `7.2.3-arch1-3 x86_64`, Python `3.14.7`.

## Before-state receipt summary (verbatim tail of `battery.stdout`)

```
PASS stream attribution probe: .shokunin/game-dev-2d/corpus/live/r62-baseline/runs/20261013T233453788036Z/stream-attribution-verdicts.json
PASS crash-exit probe: .shokunin/game-dev-2d/corpus/live/r62-baseline/runs/20261013T233453788036Z/crash-exit-verdicts.json
PASS timeout probe: .shokunin/game-dev-2d/corpus/live/r62-baseline/runs/20261013T233453788036Z/timeout-verdicts.json
PASS battery: .shokunin/game-dev-2d/corpus/live/r62-baseline/runs/20261013T233453788036Z/verdicts.json
```

- `verdicts.json`: **`"verdict": "PASS"`, 92 results, 92 PASS / 0 FAIL**
  (79 CASES + 2 mutants + 11 probe/meta rows; `probe_failing: true`).
- stdout: 91 `^PASS` lines + exactly 2 designed inner `^FAIL` lines
  (`godot_error_unrelated` exit=1 classification=False;
  `stream_reject` exit=0 classification=False) + final `PASS battery`.
- Field-diff vs the frozen tree's `corpus/lessons/r61-crash-non-author.json`
  over `(script, flags, expected_exit, actual_exit, signature, verdict, error)`:
  **92 common cases, 0 mismatches** — before-state replays the r61 non-author
  baseline byte-exact on this host.
- Opt-in artifact verdicts, all **PASS**: `crash-exit-verdicts.json` (2 rows),
  `timeout-verdicts.json` (3 rows), `godot-error-verdicts.json` (2 rows),
  `stream-attribution-verdicts.json` (2 rows), `export-launch-verdicts.json`
  (2 rows), `save-process-verdicts.json`.

## Artifact inventory (all under `corpus/live/r62-baseline/`)

- `tree/` — `git archive HEAD` extraction (frozen before-state source).
- `runs/20261013T233453788036Z/verdicts.json` — sha256
  `1e1cb265ca32931abc2a29bda6edcca305c4c3125747587fd61fca7054746b0d`.
- `runs/20261013T233453788036Z/` — `scratch/`, `xdg-data/`, `export-launch/`,
  `missing-preset-scratch/`, and the six probe `*-verdicts.json` above.
- `battery.stdout` — verbatim runner stdout, sha256
  `499251ec98bd8050debd7fe7e2ce1bf1e3ea5a6ca9c5e03b91fceb95c5146e04`.

## Before-state position for the r62 move

Pre-change `run_battery.py` timeout coverage is the three-arm
`probe_timeout` meta row (`timeout-verdicts.json`,
`"mode": "real_godot_timeout_three_arm"`), all arms running the same
`timeout_probe.gd` direct child:

- `slow_clean_old_bound` — `--delay-clean` under `timeout_seconds=0.75`:
  `timed_out=true`, `error="TIMEOUT after 0.75 seconds"`, cleanup `-9`.
- `slow_clean_new_bound` — same script under `timeout_seconds=3.0`:
  clean `exit=0` in `elapsed_seconds=1.987`.
- `hold_open_new_bound` — `--hold-open` under `timeout_seconds=3.0`:
  `timed_out=true`, cleanup `-9`.

Every arm carries `direct_child_alive_after_cleanup: false` and the probe's
own `bounded_claim` reads `"direct child cleanup only"` — the before-state
confirms exactly what the r61 boundary seat measured: timeout classification
is bound to **direct-child liveness only**; no CASES row or fixture spawns a
descendant that inherits and holds the captured stdout/stderr pipes, so the
pipe-EOF wait misattribution is unprobed in tracked rows; and no
process-group kill exists (cleanup targets the direct child, `-9`).
The r62 coverage move (fixture child spawning a pipe-holding descendant +
detached/no-descendant discriminating control) must hold this 92/92 receipt
stable on all prior rows.

## UNKNOWNs / caveats

- Row arithmetic: 92 = 79 CASES + 2 mutants + 11 probe/meta rows (r61 added the
  two crash CASES rows and `probe_spontaneous_crash_classification`; the
  save-process meta row stays lumped with CASES in the author's "ordinary"
  accounting — 79 either way on CASES-keyed rows).
- Naturally varying fields (`command`, `scratch`, `xdg_data_home`, pids,
  `elapsed_seconds`, export sha256/bytes) differ from prior runs by
  construction; the compared scope is the 7-field verdict tuple.
- Not re-measured here (r60/r61 retained): signal-origin indistinguishability
  of `returncode`; no core-dump capture.
- Single clean run; no transient flake observed. Sibling lanes (audio r63,
  game-dev-3d r71) run concurrently in this wave; no interference was observed
  on this host during this window — this receipt stands on its own
  frozen-tree evidence regardless.
