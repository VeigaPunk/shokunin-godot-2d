# Round 63 baseline report — frozen before-state seven-flag replay (host: devin)

Seat: baseline (scout). Lane axis this round: **depth** (pin the merged-stream
signature-spoofing boundary the r62 critic measured in isolation as a tracked
known-accepting forgery row). This report is the immutable before-state: no
tracked fixture/runner edit, no commit, no LOG/SCORECARD write. All artifacts
under `corpus/live/r63-baseline/` (scratch) plus this report.

## Frozen-tree provenance (no in-place fallback needed)

- Frozen source: `git -C ~/Projects/shokunin/game-dev-2d-shokunin archive HEAD | tar -x -C .shokunin/game-dev-2d/corpus/live/r63-baseline/tree`
- HEAD frozen: `edbd945dff303a13cec1c9134d2eedf16b8be44d`
  (`game-dev-2d r62 adjudication: ADMIT — LOG/SCORECARD/verifier+adjudicator
  reports + lesson`, one commit after the r62 work commit `81a100c`; carries
  the r62-landed `descendant_pipe_detached_control` CASES row, the
  `descendant_pipe_probe.gd` fixture, and the `probe_descendant_pipe_eof`
  meta row).
- Frozen runner sha256 `0c4c9bee70569c8ec29f98dea89c437d78587fd5c3c7b3220b76140ac59520dd`
  — byte-identical to the live worktree copy.
- Frozen `corpus/fixtures/descendant_pipe_probe.gd` sha256
  `054f37c9174db6be3e4579ecbd84705d25328c252a277827d418bd01b03365d3` —
  byte-identical to the live worktree copy.
- `verdicts.json["seed"]` records
  `/home/vgpnk/Projects/shokunin/game-dev-2d-shokunin/corpus/live/r63-baseline/tree/corpus/fixtures`
  → the run provably executed the **frozen copy**, not the live tree.
  Contamination risk: none; concurrent sibling-lane edits cannot reach the
  archive.

## Exact invocation

cwd `~/Projects/prymeagnt/game-dev-2d` (worktree root; `.shokunin/game-dev-2d/`
symlinks into the canonical lane repo):

```
python3 .shokunin/game-dev-2d/corpus/live/r63-baseline/tree/corpus/fixtures/run_battery.py \
  --godot /usr/bin/godot \
  --runs .shokunin/game-dev-2d/corpus/live/r63-baseline/runs \
  --probe-failing --probe-unrelated-error --probe-export-launch \
  --probe-godot-error --probe-stream-attribution --probe-crash-exit --probe-timeout
```

Environment: Godot `4.7.2.stable.arch_linux.ed1daf0bf` (`/usr/bin/godot`),
Linux `7.2.3-arch1-3 x86_64`, Python `3.14.7`.

## Before-state receipt summary (verbatim tail of `battery.stdout`)

```
PASS stream attribution probe: .shokunin/game-dev-2d/corpus/live/r63-baseline/runs/20261014T003458637390Z/stream-attribution-verdicts.json
PASS crash-exit probe: .shokunin/game-dev-2d/corpus/live/r63-baseline/runs/20261014T003458637390Z/crash-exit-verdicts.json
PASS timeout probe: .shokunin/game-dev-2d/corpus/live/r63-baseline/runs/20261014T003458637390Z/timeout-verdicts.json
PASS battery: .shokunin/game-dev-2d/corpus/live/r63-baseline/runs/20261014T003458637390Z/verdicts.json
```

- `verdicts.json`: **`"verdict": "PASS"`, 94 results, 94 PASS / 0 FAIL**
  (80 CASES + 2 mutants + 12 probe/meta rows; `probe_failing: true`).
- stdout: 93 `^PASS` lines (includes the closing `PASS battery` and the two
  PASS inner-classification lines `godot_error_expected_negative` /
  `stream_accept`) + exactly 2 designed inner `^FAIL` lines
  (`godot_error_unrelated` exit=1 classification=False;
  `stream_reject` exit=0 classification=False).
- Field-diff vs the r62 named non-author replay
  `corpus/live/r62-verifier/runs/20261014T001002305311Z/verdicts.json` (94/94)
  over `(script, flags, expected_exit, actual_exit, signature, verdict,
  error)`: **94 common cases, 0 mismatches** — before-state replays the r62
  non-author baseline field-exact on this host.
- Opt-in artifact verdicts, all **PASS**: `crash-exit-verdicts.json` (2 rows),
  `timeout-verdicts.json` (3 rows), `godot-error-verdicts.json` (2 rows),
  `stream-attribution-verdicts.json` (2 rows), `export-launch-verdicts.json`
  (2 rows), `save-process-verdicts.json`.

## Artifact inventory (all under `corpus/live/r63-baseline/`)

- `tree/` — `git archive HEAD` extraction (frozen before-state source).
- `runs/20261014T003458637390Z/verdicts.json` — sha256
  `10348fcb4210f5d3bd448bfb384db29d06924a1c9a314306b08829cfbd45a1eb`.
- `runs/20261014T003458637390Z/` — `scratch/`, `xdg-data/`, `export-launch/`,
  `missing-preset-scratch/`, and the six probe `*-verdicts.json` above.
- `battery.stdout` — verbatim runner stdout, sha256
  `904d7dbcd7529aaeed57896d42c9a1fd10353be65f1ad653fc17791248f95139`.

## Before-state position for the r63 move

The classification path the r63 depth move targets, as it stands frozen:

- `run_process` concatenates `proc.stdout + proc.stderr` into one merged
  `output`; `classify_process` (frozen runner lines 143–171) is
  **presence-based** over that merged stream — `signature in output` plus
  exit/error/no-unrelated-ERROR gates. No record field carries which process
  wrote a line; there is no attribution gate to bypass.
- The only tracked descendant surfaces are the CASES row
  `descendant_pipe_detached_control` (fd-detached descendant — cannot reach
  the pipes, immune to spoofing by construction) and the unconditional meta
  `probe_descendant_pipe_eof`, whose bounded-Popen **hold** arm this run
  re-pinned verbatim: `timed_out=true`, `child_exit_at_timeout=0`,
  `marker_observed=true`, `post_exit_write_captured=true`,
  `inner_classification=false`, `godot_alive_at_return=false`,
  `descendant_alive_at_return=true`, `elapsed_seconds=3.002` at bound 3.0 —
  all seven r62 discriminations true. That arm's `error` is always set, so
  its classification is always False; it is a rejection-side pin, not an
  accepting-side one.
- The **accepting-side** spoof shape exists only as untracked r62 critic
  scratch evidence: `corpus/live/r62-critic/attack-verdicts.json` case
  `spoof` — child run with `--no-signature`, descendant wrote the signature
  into the inherited pipe at +0.6s and released ~1.4s → `actual_exit=0`,
  `error=null`, `marker_observed=true`, `inner_classification=true`,
  `elapsed=1.749s`. No tracked CASES row or meta arm exercises a
  descendant-emitted signature accepted on the positive path; the receipt
  contains no field identifying the writer.
- The evidence fields the lane's declared claim names —
  `child_exit_at_timeout`, `timed_out` — exist only inside meta-row
  bounded-Popen arm records, never in `run_process`/`classify_process` CASES
  records. A CASES-level row whose pipe-holding descendant emits the
  signature post-parent-death and releases before the bound returns clean
  `exit 0` with the merged signature present — `classify_process` True,
  indistinguishable from a genuine child signature on the signature axis.
  That is the forgery-accepting boundary the r63 move records (fixture arm +
  CASES/meta rows), holding this 94/94 receipt stable on all prior rows.

## UNKNOWNs / caveats

- Row arithmetic: 94 = 80 CASES + 2 mutants + 12 probe/meta rows (r62 added
  the `descendant_pipe_detached_control` CASES row and the
  `probe_descendant_pipe_eof` meta row on top of r61's 92).
- Naturally varying fields (`command`, `scratch`, `xdg_data_home`, pids,
  `elapsed_seconds`, export sha256/bytes) differ from prior runs by
  construction; the compared scope is the 7-field verdict tuple.
- Not re-measured here (r61/r62 retained): signal-origin indistinguishability
  of `returncode`; `post_exit_write_captured` is a presence check whose
  post-exit-ness is carried by the fixture's ppid gate, not provable from the
  receipt alone; no core-dump capture; >1 descendant depth, >64KiB descendant
  writes, exported builds, non-POSIX unprobed.
- Single clean run; no transient flake observed. Sibling r63 lane seats
  (`r63-boundary`, `r63-reviewer`, `r63-scout` scratch dirs) were already
  writing under `corpus/live/` concurrently during this run; no interference
  was observed on this host during this window — this receipt stands on its
  own frozen-tree evidence regardless.
