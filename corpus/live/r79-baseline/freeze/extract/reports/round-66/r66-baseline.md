# Round 66 baseline report — frozen before-state replay (host: devin)

Seat: baseline (scout). This report is the immutable before-state for the r66
wave: no tracked fixture/runner edit, no commit, no LOG/SCORECARD write. All
artifacts under `corpus/live/r66-baseline/` (scratch; `frozen/` gitignored by
`corpus/.gitignore: live/*/frozen/`) plus this report. The r66 declared
axis-move (the rejection-clause SURFACE map — allowlist-as-preemptor,
breakable `count("ERROR:")==1`/match-shape gates, `ERR\n`+`OR:` newline-split
evasion / interleaved-splice fabrication, dead-entry census) is **not yet
landed** at the frozen HEAD — the 87-row list below is the pre-move surface
the wave's drift comparisons are made against.

## Frozen-tree provenance

- Frozen source:
  `git -C /home/vgpnk/Projects/shokunin/game-dev-2d-shokunin archive HEAD | tar -x -C corpus/live/r66-baseline/frozen`
  — tracked files only, no `.git`, no extraction-then-re-archive.
- HEAD frozen: `2efaae2e554ea0210c66a5e82c88a63fda94d36c`
  (`hygiene: untrack r63-baseline/tree (34,522-file extracted snapshot) +
  ignore future tree/frozen dirs`, the post-r65 tip; parent chain carries
  r65-boundary `b8a5a04`, r65-adjudication `44b6d2b`, and the r65 landed arm
  `414eb8e` forged-REJECTION dual → committed `probe_descendant_error_spoof`
  row).
- Extracted **36,912 files** — exactly `git ls-files | wc -l` at HEAD. The
  r63-baseline/tree untrack removed 33,694 tracked files vs the r65 baseline
  HEAD (`61ec1c0`, 70,606 files); only two `r63-baseline` paths remain
  tracked, both receipts: `corpus/live/r63-baseline/battery.stdout` and
  `reports/round-63/r63-baseline.md`.
- No tracked `frozen/`, `tree/`, or `node_modules` paths exist at HEAD
  (`git ls-tree -r HEAD --name-only | grep -cE 'frozen|baseline/tree|node_modules'` → 0),
  so the archive contains **no nested prior frozen trees**; the on-disk
  untracked leftover `corpus/live/r63-baseline/tree/` is excluded by
  construction.
- **Archive size: raw tar `git archive HEAD | wc -c` = 644,106,240 bytes
  (~614 MiB); extracted tree `du -sb` = 611,373,544 bytes (`du -sh` 700M
  block-allocated) vs r65-baseline's ~1.4G extracted — the r63-tree untrack
  shrank the frozen surface by ~56%.** Claim "the untrack shrank the
  archive": confirmed by direct measurement.
- Frozen `corpus/fixtures/run_battery.py` sha256
  `cd4824cc1a0199c2886ee8c5815ed5065757f50f6f59420ef79d56b4fd302d58`
  (138,299 bytes) — byte-identical to the live worktree copy and to the
  `HEAD:` blob, and identical to the sha the r65 verifier recorded on the
  committed `414eb8e` bytes.
- Frozen `corpus/fixtures/descendant_pipe_probe.gd` sha256
  `37cf50156839502a1372746d31c3db6b8c835df734acf838025c1664f3262e59` —
  byte-identical to live worktree and `HEAD:` blob (the r65-committed
  fixture carrying `--spawn-errforge-release|hold` arms).
- `verdicts.json["seed"]` records
  `/home/vgpnk/Projects/shokunin/game-dev-2d-shokunin/corpus/live/r66-baseline/frozen/corpus/fixtures`
  → the run provably executed the **frozen copy**, not the live tree.
  Contamination risk: none; concurrent sibling-lane/seat edits cannot reach
  the archive.

## Exact invocation

cwd `/home/vgpnk/Projects/shokunin/game-dev-2d-shokunin` (canonical lane
repo; `~/Projects/prymeagnt/game-dev-2d/.shokunin/game-dev-2d` symlinks here):

```
python3 corpus/live/r66-baseline/frozen/corpus/fixtures/run_battery.py \
  --godot /usr/bin/godot \
  --runs /home/vgpnk/Projects/shokunin/game-dev-2d-shokunin/corpus/live/r66-baseline/runs
```

Bare invocation — no opt-in probe flags — to reproduce the r65-verifier
comparison surface (81 CASES + 6 meta = 87 rows). stdout tee'd to
`corpus/live/r66-baseline/battery.stdout`; pipeline exit 0.

Environment: Godot `4.7.2.stable.arch_linux.ed1daf0bf` (`/usr/bin/godot`),
Python `3.14.7`, this host's `systemd --user` subreaper — identical profile
to the r65 baseline/verifier environment.

## Before-state receipt summary (verbatim tail of `battery.stdout`)

```
PASS descendant_pipe_detached_control: exit=0 signature='DESCENDANT_PIPE_PROBE: expected signature'
PASS descendant_pipe_forged_signature_release: exit=0 signature='DESCENDANT_PIPE_PROBE: expected signature'
PASS independent save process probe: /home/vgpnk/Projects/shokunin/game-dev-2d-shokunin/corpus/live/r66-baseline/runs/20261014T050234068765Z/save-process-verdicts.json
PASS spontaneous crash classification meta
PASS descendant pipe-EOF meta
PASS descendant signature-spoof meta
PASS while-live signature-gate meta
PASS descendant error-spoof meta
PASS battery: /home/vgpnk/Projects/shokunin/game-dev-2d-shokunin/corpus/live/r66-baseline/runs/20261014T050234068765Z/verdicts.json
```

- `verdicts.json`: **`"verdict": "PASS"`, 87 results, 87 PASS / 0 FAIL**
  (81 CASES + 6 meta rows). sha256
  `fa1a1c8b31ff692cd02e528b473c92618b153c236924e3e5f407c8e2015a25c3`.
- stdout: 88 `^PASS` lines (81 case lines + 6 meta lines + closing
  `PASS battery`), **0 `^FAIL` lines** — the same shape as the
  r65-verifier bare run.
- Opt-in artifact: `save-process-verdicts.json` present; no flag-gated
  `export-launch`/`godot-error`/`stream-attribution`/`crash-exit`/`timeout`
  artifacts — bare run by design.

## Drift vs the committed r65-verifier receipt — ZERO

Field-diff of my `verdicts.json` vs the r65-verifier receipt
`corpus/live/runs/20261014T043948860752Z/verdicts.json` (87 results, PASS,
bare invocation at `414eb8e`) over the r62–r65-established tuple
`(script, flags, expected_exit, actual_exit, signature, verdict, error)`
indexed by `case`; meta rows (no `script` key) compared on `verdict`:

- **87 common cases, 0 mismatches** — 81 rows on the full 7-field tuple, 6
  meta rows on verdict (`probe_save_independent_process`,
  `probe_spontaneous_crash_classification`, `probe_descendant_pipe_eof`,
  `probe_descendant_signature_spoof`, `probe_while_live_signature_gate`,
  `probe_descendant_error_spoof`).
- new-only `[]`, old-only `[]` — the r66 frozen surface is exactly the
  committed r65-verifier surface.
- Meta discriminations stable (bool-dict comparison, mine vs receipt):
  `probe_descendant_error_spoof` **29 keys / all True** both runs;
  `probe_while_live_signature_gate` **12/12 True**;
  `probe_descendant_signature_spoof` **10/10 True** — identical key sets.

## Pinned boundary rows — byte-stable (documented, not fixed)

- `descendant_pipe_forged_signature_release` (CASES row): `verdict PASS`,
  `expected_exit 0`, `actual_exit 0`, `error null`,
  `flags ["--spawn-forge-release"]`,
  `signature 'DESCENDANT_PIPE_PROBE: expected signature'` — tuple-identical
  to r63/r64/r65. Origin-blind signature acceptance reproduced as
  documented.
- `probe_descendant_error_spoof` meta row (the r65-landed arm): `verdict
  PASS`, all **29 discriminations true** — including
  `release_flips_to_fail`, `release_forged_error_captured`,
  `gate_does_not_reject_forged_error_arm`,
  `merged_classification_stream_blind`, and the r66-relevant
  `forged_error_lands_on_stdout` / `genuine_error_lands_on_stderr` split.
  This row is the r66 axis-move's before-state anchor: the un-allowlisted
  `ERROR:` presence scan in the merged classifier is the rejection surface
  the wave maps.

## Artifact inventory (all under `corpus/live/r66-baseline/`)

- `frozen/` — `git archive HEAD` extraction (36,912 files, 611,373,544
  bytes; raw tar 644,106,240 bytes). Gitignored by `corpus/.gitignore:
  live/*/frozen/`.
- `runs/20261014T050234068765Z/verdicts.json` — sha256 `fa1a1c8b…` above;
  siblings `scratch/`, `xdg-data/`, `missing-preset-scratch/`,
  `save-process-verdicts.json`.
- `battery.stdout` — verbatim runner stdout, sha256
  `e350d984e86362b7e5a8fa4bf9d0ab97304ad4b591bbbe86c566dfd2df525ed8`.

## Process hygiene

Post-run `ps -eo pid,ppid,stat,etime,args | grep -E 'godot|sleep'`: **no
godot engine processes and no fixture `sleep` descendants attributable to
this run** — every `--headless` invocation under my runs path exited, and
the error-spoof harness reaps its errforge orphans. Remaining matches are
unrelated: host `godot-mcp` node services and a **sibling lane's**
in-flight `game-dev-3d r75-baseline` run (different repo tree, pid
1923294 + its godot child) — none this lane, none leaked by this replay.

## Drift / archive-size / command / sha summary

| item | value |
|------|-------|
| frozen HEAD | `2efaae2e554ea0210c66a5e82c88a63fda94d36c` |
| archive raw tar | 644,106,240 B (~614 MiB) |
| extracted tree | 36,912 files / 611,373,544 B (`du -sb`; `du -sh` 700M) vs r65 ~1.4G → **~56% smaller** |
| battery | bare, exit 0 → `verdict PASS`, **87/87** |
| tuple-diff vs r65-verifier receipt | **0 mismatches** (81 full + 6 meta) |
| discriminations | error_spoof 29/29, while_live_gate 12/12, sig_spoof 10/10 — all True |
| verdicts.json sha256 | `fa1a1c8b31ff692cd02e528b473c92618b153c236924e3e5f407c8e2015a25c3` |
| frozen runner/probe sha256 | `cd4824cc…` / `37cf5015…` == HEAD blobs |

## UNKNOWNs / caveats

- Naturally varying fields (`command`, `scratch`, `xdg_data_home`, pids,
  `elapsed_seconds`, receipt shas) differ from prior runs by construction;
  the compared scope is the 7-field verdict tuple + meta verdicts +
  discrimination bool-maps, per r62–r65 verifier precedent.
- Single host, single clean run; no transient flake observed. Concurrent
  sibling-lane writes were in flight during this run (`corpus/live/
  r65-boundary/edge-verdicts.json`, `corpus/live/r66-reviewer/` untracked
  at post-run `git status`); none reach this receipt — the frozen copy is
  the committed `2efaae2` blobs (verified above) and
  `verdicts.json["seed"]` proves execution from `frozen/`.
- The brief's "87/87 expected" is the bare-invocation surface (matching the
  r65-verifier receipt it names). The 10 flag-gated opt-in rows of the r65
  baseline's full-flag run (2 mutants, 4 `probe_unrelated_error_*`,
  export-launch/godot-error/stream-attribution/crash-exit/timeout) are not
  emitted by a bare run — not removed rows.
- Not re-measured here (carried from r61–r65): signal-origin
  indistinguishability of `returncode`; live-window forgery acceptance
  under the poll() gate; >1 descendant depth, >64KiB descendant writes,
  exported builds, non-POSIX unprobed. The r66 rejection-clause surface map
  (allowlist preemptor, gate breakability, newline-split/splice, dead-entry
  census) is the wave's move, not baseline scope — this receipt is its
  before-state.
