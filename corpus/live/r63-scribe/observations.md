# r63-scribe observations (read-only receipts)

All commands run from `~/Projects/shokunin/game-dev-2d-shokunin` (the
`.shokunin/game-dev-2d/` prefix in the dispatch). No runner or Godot executed
by this seat; no tracked file written; no commit/push.

## State at observation time (2026-10-14 ~00:41Z)

```
$ git log -1 --format='%H %s'
edbd945dff303a13cec1c9134d2eedf16b8be44d game-dev-2d r62 adjudication: ADMIT — LOG/SCORECARD/verifier+adjudicator reports + lesson

$ git status --short        # mid-flight snapshot
 M corpus/fixtures/descendant_pipe_probe.gd     <- r63 author diff, uncommitted
 M corpus/fixtures/run_battery.py               <- r63 author diff, uncommitted
?? corpus/fixtures/__pycache__/
?? corpus/live/r63-{author,baseline,boundary,reviewer,scout,scribe,simplifier}/
?? reports/round-63/

$ git diff --stat
 corpus/fixtures/descendant_pipe_probe.gd |  31 +++++++-
 corpus/fixtures/run_battery.py           | 155 ++++++++++++++++++++++++++++++++
```

## Baseline read (my read-only measurements)

```
$ sha256sum corpus/fixtures/run_battery.py
0c4c9bee70569c8ec29f98dea89c437d78587fd5c3c7b3220b76140ac59520dd   (pre-diff HEAD copy;
matches r62 author worktree sha / committed 81a100c runner)

$ sha256sum corpus/fixtures/descendant_pipe_probe.gd
054f37c9174db6be3e4579ecbd84705d25328c252a277827d418bd01b03365d3   (tracked HEAD copy)

$ python3 (ast count) -> CASES rows: 80
  unconditional meta rows in source: probe_save_independent_process (L506),
  probe_spontaneous_crash_classification (L540), probe_descendant_pipe_eof (L679)
$ python3 --version -> Python 3.14.7 ; uname -r -> 7.2.3-arch1-3
```

`classify_process` (L154-171): return is
`code == expected_exit and error is None and signature in output and not
unrelated_errors and "SCRIPT ERROR:" not in output and "Parse Error:" not in output`
— `signature in output` is a substring presence test over the merged
`proc.stdout + proc.stderr` string built by `run_process` (L143-151). No
writer attribution term exists. `classify_streams` (L173-202) is the
split-stream variant (signature must be in stdout) used only by the
stream-attribution probe path, not by CASES rows (classifier dispatch at
L437: `classify_audio_process if name == "audio_playback" else classify_process`).

## Landed r63 tracked surface (uncommitted author diff, observed)

- Fixture `descendant_pipe_probe.gd` +31/−1: new arms `--spawn-forge-hold` /
  `--spawn-forge-release`; child prints `DESCENDANT_PIPE_FORGE
  child_signature=withheld` instead of MARKER on forge arms; descendant
  reuses the `/proc/self/stat` ppid-flip gate (provably post-exit write),
  then echoes the expected signature + `DESCENDANT_PIPE_FORGE
  write_ppid=<ppid>`; `-hold` appends `; sleep 6` (holds pipes ~6s).
- `run_battery.py` +155/−0 additive:
  - CASES row `("descendant_pipe_forged_signature_release",
    "descendant_pipe_probe.gd", ["--spawn-forge-release"], 0,
    "DESCENDANT_PIPE_PROBE: expected signature")` — commented in source as
    "r63 KNOWN-ACCEPTING FORGERY ROW".
  - Unconditional meta `probe_descendant_signature_spoof` (mode
    `bounded_popen_plus_cases_forgery_row`): drives `--spawn-forge-hold`
    under one `Popen`/`communicate(timeout=3.0)` replica of the r62 meta
    shape; 8 discriminations: `hold_timed_out_with_child_dead`,
    `hold_forged_signature_captured`, `hold_write_post_orphan`
    (write_ppid != godot_pid), `hold_rejects_via_timeout_axis_only`,
    `hold_descendant_orphaned_alive`, `release_row_passes_on_forged_signature`,
    `release_write_post_orphan`, `release_shape_matches_genuine` (forged
    PASS field-equal to the detached control on classification-visible
    fields). Orphaned descendants SIGKILLed as ungated hygiene.
  - `bounded_claim`: "...signature presence over merged captured output is
    origin-blind ... documented forgery-accepting boundary, not a fix;
    Linux headless Godot 4.7.2 POSIX pipe semantics only".

## Sibling receipts observed (in-flight, uncommitted wave)

- Author post-diff seven-flag run
  `corpus/live/r63-author/runs/20261014T004113548836Z/verdicts.json`:
  **96/96 PASS** (94 prior + 2 new). Forged-release CASES record: `verdict
  PASS, actual_exit 0, error null`, output shows `child_signature=withheld`,
  `godot_pid=1071156`, `spawned_pid=1071195`, forged
  `DESCENDANT_PIPE_PROBE: expected signature`, `write_ppid=1573`. Meta
  hold-arm record: `timed_out=true, child_exit_at_timeout=0,
  actual_exit=null, error="TIMEOUT after 3.0 seconds", marker_observed=true,
  write_ppid=1573, godot_alive_at_return=false,
  descendant_alive_at_return=true, inner_classification=false,
  elapsed=3.001`; all 8 discriminations true.
  (Author's pre-diff run `20261014T003829532517Z/verdicts.json`: 94/94 PASS.)
- Baseline frozen replay `corpus/live/r63-baseline/runs/20261014T003458637390Z/verdicts.json`: **94/94 PASS** (sha256 `10348fcb…`).
- Reviewer fresh run `corpus/live/r63-reviewer/runs/20261014T003518096525Z/verdicts.json`: **94/94 PASS** (sha256 `4efb4f1e…`); report r63-reviewer.md "AGREE" on battery task.
- Scout `corpus/live/r63-scout/spoof-verdicts.json` (sha256 `6fd32ffe…`):
  `run_process`/`classify_process` `ast.get_source_segment`-extracted
  verbatim, `/usr/bin/sh` children, bound 3.0s:
  - `genuine`: exit0, sig present, classify True.
  - `spoof_release` (descendant writes sig post-death then exits):
    exit0, error None, sig present, classify **True**, elapsed 0.002s —
    forged clean PASS; child dead at return.
  - `spoof_hold` (same write + `sleep 5`): TIMEOUT 3.002s, exit None, sig
    present, classify False, `classify_if_error_none` **True**.
  - `spoof_hold_popen` (Popen+communicate replica): timed_out True,
    `child_exit_at_timeout=0`, sig present, inner_classification False,
    `classify_if_error_none` True, elapsed 3.004s.
- Boundary `corpus/live/r63-boundary/depth-verdicts.json` (sha256 `e85d1918…`;
  real Godot children via verbatim `run_process`):
  `d2_spoof` (depth-2 grandchild forges signature, godot suppresses):
  exit0, classify **True**, 1.524s; `d2_spoof_hold`: TIMEOUT 3.003s + forged
  sig, False; `d2_hold`/`d2_hang`/`d2_reparent`: TIMEOUT at bound with
  depth-2 holder orphaned alive (ppid 1573); `d2_release`/`d2_mixed`/
  `d2_detach`: exit0 True 0.686-1.998s with depth-2 orphan leaked;
  `d3_hold`: depth-3 holder alone blocks EOF → TIMEOUT 3.002s.
  Knee sweep (`drive_knee.py`) still running at observation time.
- Sibling reports settled at observation time: r63-baseline.md,
  r63-reviewer.md, r63-scout.md. Author/critic/simplifier/boundary reports
  not yet written; no commit landed.

## Not observed (pending slots for the drafts)

- Prior-row field-stability vs the r62 non-author receipt (verifier wave-2
  surface; no r63 verifier dispatched in this wave's task list —
  G2dR63{Scout,Author,Critic,Reviewer,Simplifier,Scribe,Baseline,Boundary}
  only).
- Critic mutants / simplifier minimal-diff verdict / boundary knee results.
- Work commit hash; parent's integration corrections (if any).
