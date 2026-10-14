# Round 64 baseline report — frozen before-state seven-flag replay (host: devin)

Seat: baseline (scout). This report is the immutable before-state for the r64
wave: no tracked fixture/runner edit, no commit, no LOG/SCORECARD write. All
artifacts under `corpus/live/r64-baseline/` (scratch) plus this report. The
r64 declared axis-move (bounded-Popen meta arm gating the signature read on
child liveness) is not yet landed at the frozen HEAD — this receipt is the
pre-move reference the wave's drift comparisons are made against.

## Frozen-tree provenance

- Frozen source: `git -C ~/Projects/shokunin/game-dev-2d-shokunin archive HEAD |
  tar -x -C corpus/live/r64-baseline/frozen` — tracked files only, no `.git`.
- HEAD frozen: `a7e0cb11399ec52c1e0453db345af8c35a0a86f3`
  (`game-dev-2d r63 adjudication: ADMIT — LOG/SCORECARD/verifier+adjudicator
  reports + lesson`, one commit after the r63 work commit `de78edb`; carries
  the r63-landed CASES row `descendant_pipe_forged_signature_release` and the
  10-discrimination meta `probe_descendant_signature_spoof`).
- Extracted 69,279 files — exactly `git ls-files | wc -l` at HEAD (the tree
  nests prior committed `corpus/live/` history incl. `r63-baseline/tree/`).
- Frozen `corpus/fixtures/run_battery.py` sha256
  `fb7cab2bb0364bef802cd3ed67892510377b8c45024daa378ca632129d96d7c2` —
  byte-identical to the live worktree copy and to the committed blob the r63
  verifier recorded (`fb7cab2b…`).
- Frozen `corpus/fixtures/descendant_pipe_probe.gd` sha256
  `4fce06765b091e9ffe649b06fca020115e07d2590b91200d57c4f319b3fdb3a2` —
  byte-identical to the live worktree copy and to the r63-verifier-recorded
  committed blob.
- `verdicts.json["seed"]` records
  `/home/vgpnk/Projects/shokunin/game-dev-2d-shokunin/corpus/live/r64-baseline/frozen/corpus/fixtures`
  → the run provably executed the **frozen copy**, not the live tree.
  Contamination risk: none; concurrent sibling-lane edits cannot reach the
  archive.

## Exact invocation

cwd `~/Projects/prymeagnt/game-dev-2d` (worktree root; `.shokunin/game-dev-2d/`
symlinks into the canonical lane repo):

```
python3 .shokunin/game-dev-2d/corpus/live/r64-baseline/frozen/corpus/fixtures/run_battery.py \
  --godot /usr/bin/godot \
  --runs .shokunin/game-dev-2d/corpus/live/r64-baseline/runs \
  --probe-failing --probe-unrelated-error --probe-export-launch \
  --probe-godot-error --probe-stream-attribution --probe-crash-exit --probe-timeout
```

(stdout tee'd to `corpus/live/r64-baseline/battery.stdout`; pipeline exit 0.)

Environment: Godot `4.7.2.stable.arch_linux.ed1daf0bf` (`/usr/bin/godot`),
Python `3.14.7`, this host's `systemd --user` subreaper ppid 1573.

## Before-state receipt summary (verbatim tail of `battery.stdout`)

```
PASS stream attribution probe: .shokunin/game-dev-2d/corpus/live/r64-baseline/runs/20261014T013523271164Z/stream-attribution-verdicts.json
PASS crash-exit probe: .shokunin/game-dev-2d/corpus/live/r64-baseline/runs/20261014T013523271164Z/crash-exit-verdicts.json
PASS timeout probe: .shokunin/game-dev-2d/corpus/live/r64-baseline/runs/20261014T013523271164Z/timeout-verdicts.json
PASS battery: .shokunin/game-dev-2d/corpus/live/r64-baseline/runs/20261014T013523271164Z/verdicts.json
```

- `verdicts.json`: **`"verdict": "PASS"`, 96 results, 96 PASS / 0 FAIL**
  (81 CASES + 2 mutants + 4 unrelated-error + 9 meta/probe rows;
  `probe_failing: true`). sha256
  `e14867017bbf0cfe0184ab78675dd2076385bf36e924222648a7b0eed35a72f7`.
- stdout: 95 `^PASS` lines (includes closing `PASS battery` and the two inner
  PASS-classification lines `godot_error_expected_negative` / `stream_accept`)
  + exactly 2 designed inner `^FAIL` lines (`godot_error_unrelated` exit=1
  classification=False; `stream_reject` exit=0 classification=False) — the
  same shape as the r63 verifier run, not defects.
- Opt-in artifact verdicts, all **PASS**: `export-launch-verdicts.json` (2
  rows), `godot-error-verdicts.json` (2), `stream-attribution-verdicts.json`
  (2), `crash-exit-verdicts.json` (2), `timeout-verdicts.json` (3),
  `save-process-verdicts.json` (1).

## Drift vs the committed r63 receipt — ZERO

Field-diff of my `verdicts.json` vs the r63-verifier committed receipt
`corpus/live/r63-verifier/runs/20261014T011438671964Z/verdicts.json` (sha256
`ef9d9ac664dc50cf0b7c296c0698f8f175625c55d782ea7c0a2daf3a9001071b`) over the
r62/r63-established tuple `(script, flags, expected_exit, actual_exit,
signature, verdict, error)` indexed by `case`; meta rows (no `script` key)
compared on `verdict` per precedent:

- **96 common cases, 0 mismatches** — 83 rows on the full 7-field tuple, 13
  meta rows on verdict (`probe_save_independent_process`,
  `probe_spontaneous_crash_classification`, `probe_descendant_pipe_eof`,
  `probe_descendant_signature_spoof`, `probe_export_launch`,
  `probe_godot_error`, `probe_stream_attribution`, `probe_crash_exit`,
  `probe_timeout`, 4 `probe_unrelated_error_*`).
- new-only `[]`, old-only `[]` — the r64 frozen surface is exactly the r63
  committed surface.

## r63 pinned accepting-boundary row — byte-stable (documented, not fixed)

- `descendant_pipe_forged_signature_release` (CASES row): `verdict PASS`,
  `expected_exit 0`, `actual_exit 0`, `error null`,
  `flags ["--spawn-forge-release"]` — tuple-identical to r63. Output carries
  `DESCENDANT_PIPE_FORGE child_signature=withheld`, `godot_pid=1251344`,
  `spawned_pid=1251394`, the expected signature, then
  `DESCENDANT_PIPE_FORGE write_ppid=1573`: the accepted signature is still the
  descendant's post-child-exit write — origin-blind acceptance reproduced.
- `probe_descendant_signature_spoof` meta row: `verdict PASS`, all **10
  discriminations true**; hold arm `timed_out=true`,
  `child_exit_at_timeout=0`, `marker_observed=true`, `write_ppid=1573`,
  `godot_alive_at_return=false`, `descendant_alive_at_return=true`,
  `descendant_kernel_ppid_at_return=1573` (kernel-corroborated ≠ godot_pid
  1251481), `inner_classification=false`, `elapsed_seconds=3.003` at bound 3.0.
- Runner and probe fixture bytes at frozen HEAD are identical to the r63
  committed blobs (shas above) — the boundary the r64 claim targets stands
  exactly as r63 committed it.

## Artifact inventory (all under `corpus/live/r64-baseline/`)

- `frozen/` — `git archive HEAD` extraction (frozen before-state source;
  69,279 files, ~1.4G).
- `runs/20261014T013523271164Z/verdicts.json` — sha256 `e1486701…` above.
- `runs/20261014T013523271164Z/` — `scratch/`, `xdg-data/`, `export-launch/`,
  `missing-preset-scratch/`, and the six probe `*-verdicts.json` above.
- `battery.stdout` — verbatim runner stdout, sha256
  `6bdc506deb205cd415fed392727ba64784b7e04e4cc62eabf9cd048b27d9cb77`.

## Process hygiene

Post-run `ps -eo pid,ppid,stat,etime,args`: **no godot engine processes and no
fixture `sleep 6/8` descendants** attributable to this run. Remaining matches
are unrelated host `godot-mcp` node services, fleet `sleep 240/45` watchers,
and a concurrent sibling lane (`r64-author` running its own
`pretree` battery under `corpus/live/r64-author/`) — none this lane, none
leaked by this replay.

## UNKNOWNs / caveats

- Naturally varying fields (`command`, `scratch`, `xdg_data_home`, pids,
  `elapsed_seconds`, export sha256/bytes, the verdicts.json sha itself) differ
  from prior runs by construction; the compared scope is the 7-field verdict
  tuple, per r62/r63 verifier precedent.
- Single host, single clean run; no transient flake observed. Concurrent
  sibling-lane writes under `corpus/live/` (r64-author, r64-reviewer) were
  in flight during this run; the frozen archive isolates this receipt from
  them by construction.
- Not re-measured here (carried from r61–r63): signal-origin
  indistinguishability of `returncode`; `post_exit_write_captured` is a
  presence check whose post-exit-ness is carried by the fixture's ppid gate;
  >1 descendant depth, >64KiB descendant writes, exported builds, non-POSIX
  unprobed. The r64 while-live marker-gate claim itself is the wave's move,
  not baseline scope — this receipt is its before-state.
