# Round 65 baseline report — frozen before-state seven-flag replay (host: devin)

Seat: baseline (scout). This report is the immutable before-state for the r65
wave: no tracked fixture/runner edit, no commit, no LOG/SCORECARD write. All
artifacts under `corpus/live/r65-baseline/` (scratch) plus this report. The
r65 declared axis-move (the forged-REJECTION dual — reparenting-gated
descendant emitting an un-allowlisted `ERROR:`-class marker post-parent-death,
`probe_descendant_error_spoof`) is **not yet landed** at the frozen HEAD — the
meta-row list below carries no such row. This receipt is the pre-move
reference the wave's drift comparisons are made against.

## Frozen-tree provenance

- Frozen source: `git -C ~/Projects/shokunin/game-dev-2d-shokunin archive HEAD |
  tar -x -C corpus/live/r65-baseline/frozen` — tracked files only, no `.git`.
- HEAD frozen: `61ec1c04ae9ad54f5c0566c75debb8a5837867ef`
  (`game-dev-2d r64 adjudication: ADMIT — LOG/SCORECARD/lesson/verifier+
  adjudicator reports`, two commits after the r64 fix `5265da6` which landed
  the gated-read runner change the r64 verifier caught uncommitted at
  `a32920b`; carries the committed while-live gate +228 and the r64-landed
  meta row `probe_while_live_signature_gate`).
- Extracted **70,606 files** — exactly `git ls-files | wc -l` at HEAD. No
  tracked `frozen/` or `node_modules` paths exist at HEAD
  (`git ls-tree -r HEAD --name-only | grep -E 'frozen|node_modules'` → empty),
  so the archive contains **no nested prior frozen trees**; the untracked
  sibling `corpus/live/r64-baseline/frozen/` is excluded by construction
  (git archive emits tracked files only).
- Frozen `corpus/fixtures/run_battery.py` sha256
  `66a18a0056aedbd6c99ed8637ed30d03a3404556ab49d05826e8c63f4fe1f07d` —
  byte-identical to the live worktree copy, to the committed `HEAD:` blob,
  and to the corrected +228 worktree sha the r64 verifier recorded and
  recommended committing. The r64 integration gap is closed at this HEAD.
- Frozen `corpus/fixtures/descendant_pipe_probe.gd` sha256
  `4fce06765b091e9ffe649b06fca020115e07d2590b91200d57c4f319b3fdb3a2` —
  byte-identical to the live worktree copy and to the r63/r64-recorded blob.
- `verdicts.json["seed"]` records
  `/home/vgpnk/Projects/shokunin/game-dev-2d-shokunin/corpus/live/r65-baseline/frozen/corpus/fixtures`
  → the run provably executed the **frozen copy**, not the live tree.
  Contamination risk: none; concurrent sibling-lane edits cannot reach the
  archive.

## Exact invocation

cwd `~/Projects/prymeagnt/game-dev-2d` (worktree root; `.shokunin/game-dev-2d/`
symlinks into the canonical lane repo):

```
python3 .shokunin/game-dev-2d/corpus/live/r65-baseline/frozen/corpus/fixtures/run_battery.py \
  --godot /usr/bin/godot \
  --runs .shokunin/game-dev-2d/corpus/live/r65-baseline/runs \
  --probe-failing --probe-unrelated-error --probe-export-launch \
  --probe-godot-error --probe-stream-attribution --probe-crash-exit --probe-timeout
```

(stdout tee'd to `corpus/live/r65-baseline/battery.stdout`; pipeline exit 0.)

Environment: Godot `4.7.2.stable.arch_linux.ed1daf0bf` (`/usr/bin/godot`),
Python `3.14.7`, this host's `systemd --user` subreaper ppid 1573 — identical
to the r64 baseline environment.

## Before-state receipt summary (verbatim tail of `battery.stdout`)

```
FAIL godot_error_unrelated: exit=1 classification=False
PASS Godot diagnostic probe: .shokunin/game-dev-2d/corpus/live/r65-baseline/runs/20261014T022523005280Z/godot-error-verdicts.json
PASS stream_accept: exit=0 classification=True
FAIL stream_reject: exit=0 classification=False
PASS stream attribution probe: .shokunin/game-dev-2d/corpus/live/r65-baseline/runs/20261014T022523005280Z/stream-attribution-verdicts.json
PASS crash-exit probe: .shokunin/game-dev-2d/corpus/live/r65-baseline/runs/20261014T022523005280Z/crash-exit-verdicts.json
PASS timeout probe: .shokunin/game-dev-2d/corpus/live/r65-baseline/runs/20261014T022523005280Z/timeout-verdicts.json
PASS battery: .shokunin/game-dev-2d/corpus/live/r65-baseline/runs/20261014T022523005280Z/verdicts.json
```

- `verdicts.json`: **`"verdict": "PASS"`, 97 results, 97 PASS / 0 FAIL**
  (81 CASES + 2 mutants + 4 unrelated-error + 10 meta/probe rows;
  `probe_failing: true`). sha256
  `276bab1564b92c1fca1683aa66fe8e7c7c17f3749552e13038b0ec666363ddca`.
- stdout: 96 `^PASS` lines (includes closing `PASS battery` and the two inner
  PASS-classification lines `godot_error_expected_negative` / `stream_accept`)
  + exactly 2 designed inner `^FAIL` lines (`godot_error_unrelated` exit=1
  classification=False; `stream_reject` exit=0 classification=False) — the
  same shape as the r63/r64 runs, not defects.
- Opt-in artifact verdicts, all **PASS**: `export-launch-verdicts.json` (2
  rows), `godot-error-verdicts.json` (2), `stream-attribution-verdicts.json`
  (2), `crash-exit-verdicts.json` (2), `timeout-verdicts.json` (3),
  `save-process-verdicts.json` (evidence dict, verdict PASS).

## Drift vs the committed r64 receipt — ZERO

Field-diff of my `verdicts.json` vs the r64-verifier receipt
`corpus/live/r64-verifier/runs/20261014T021400329665Z/verdicts.json` (97
results, PASS; sha256
`8e41ed763f00c170e2b2f0f2c2baa307427c4c1d948f14cc34de3476b1246652`) over the
r62–r64-established tuple `(script, flags, expected_exit, actual_exit,
signature, verdict, error)` indexed by `case`; meta rows (no `script` key)
compared on `verdict` per precedent:

- **97 common cases, 0 mismatches** — 83 rows on the full 7-field tuple, 14
  meta rows on verdict (`probe_save_independent_process`,
  `probe_spontaneous_crash_classification`, `probe_descendant_pipe_eof`,
  `probe_descendant_signature_spoof`, `probe_while_live_signature_gate`,
  `probe_export_launch`, `probe_godot_error`, `probe_stream_attribution`,
  `probe_crash_exit`, `probe_timeout`, 4 `probe_unrelated_error_*`).
- new-only `[]`, old-only `[]` — the r65 frozen surface is exactly the r64
  committed surface. No `probe_descendant_error_spoof` row exists yet; the
  r65 arm lands against this 97-row base.

## Pinned boundary rows — byte-stable (documented, not fixed)

- `descendant_pipe_forged_signature_release` (CASES row): `verdict PASS`,
  `expected_exit 0`, `actual_exit 0`, `error null`,
  `flags ["--spawn-forge-release"]`,
  `signature 'DESCENDANT_PIPE_PROBE: expected signature'` — tuple-identical
  to r63 and r64. The CASES-path classifier still accepts the forged
  post-death signature; the r64 gate lives in the meta probe, not the CASES
  classify path — origin-blind acceptance reproduced as documented.
- `probe_while_live_signature_gate` meta row: `verdict PASS`, all **12
  discriminations true**. Arm shape reproduces r64:
  `genuine_default_r0/r1/r2` + `genuine_detach` gate-ACCEPT
  (`gated_signature_accepted=true`, `child_alive_at_marker_observation=true`);
  `forge_release_r0/r1/r2` gate-REJECT (`accepted=false`,
  `alive@marker=false`, `write_ppid=1573`, `inner_classification=true` — the
  gate rejects what the un-gated classifier accepts);
  `forge_hold` gate-REJECT (`accepted=false`, `inner=false`,
  `write_ppid=1573`, `descendant_kernel_ppid_at_return=1573` ≠ godot_pid —
  kernel-corroborated post-orphan write).
- `probe_descendant_signature_spoof` meta row: `verdict PASS` (tuple-stable
  vs r64 per the 0-mismatch diff).

## Artifact inventory (all under `corpus/live/r65-baseline/`)

- `frozen/` — `git archive HEAD` extraction (frozen before-state source;
  70,606 files, ~1.4G).
- `runs/20261014T022523005280Z/verdicts.json` — sha256 `276bab15…` above.
- `runs/20261014T022523005280Z/` — `scratch/`, `xdg-data/`, `export-launch/`,
  `missing-preset-scratch/`, and the six probe `*-verdicts.json` above.
- `battery.stdout` — verbatim runner stdout, sha256
  `0fb0f160c3e615150470a4dff5ec58a87130c1304132fa309c13f7378f61e4d2`.

## Process hygiene

Post-run `ps -eo pid,ppid,stat,etime,args | grep -E 'godot|sleep'`: **no godot
engine processes and no fixture `sleep` descendants** attributable to this
run. Remaining matches are unrelated host `godot-mcp` node services — none
this lane, none leaked by this replay.

## UNKNOWNs / caveats

- Naturally varying fields (`command`, `scratch`, `xdg_data_home`, pids,
  `elapsed_seconds`, export sha256/bytes, the verdicts.json sha itself) differ
  from prior runs by construction; the compared scope is the 7-field verdict
  tuple, per r62–r64 verifier precedent.
- Single host, single clean run; no transient flake observed. Concurrent
  sibling-lane writes were in flight during this run — post-run `git status`
  shows the live worktree `run_battery.py` now at sha `1acbc73d…` (+431) and
  `descendant_pipe_probe.gd` at `37cf5015…` (+35), i.e. the r65-author arm
  landing in the live tree alongside `corpus/live/r65-author|reviewer|scribe|
  simplifier/` scratch. None of it reaches this receipt: the frozen copy is
  the committed `61ec1c0` blobs (`66a18a00…`/`4fce0676…`, verified above) and
  `verdicts.json["seed"]` proves execution from `frozen/`.
- The r64 verifier compared against an *uncommitted*-code receipt (the gate
  was dirty-tree at `a32920b`); at `61ec1c0` the identical `66a18a00…` runner
  is committed, so this frozen run is the first 97-row receipt on a clean
  committed tree — and it is tuple-identical to that dirty-tree receipt.
- Not re-measured here (carried from r61–r64): signal-origin
  indistinguishability of `returncode`; live-window forgery acceptance under
  the poll() gate (r64-verifier claim-4b: `--forge-during-life`/`--forge-early`
  accepted — the gate authenticates observation-time, not authorship);
  >1 descendant depth, >64KiB descendant writes, exported builds, non-POSIX
  unprobed. The r65 forged-REJECTION dual (`probe_descendant_error_spoof`)
  is the wave's move, not baseline scope — this receipt is its before-state;
  whether the while-live gate also rejects a post-death `ERROR:`-class marker
  (gate-invisible per the claim) is measurable against this base once the arm
  lands.
