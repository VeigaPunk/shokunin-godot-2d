# Round 61 baseline report — frozen before-state seven-flag replay (host: devin)

Seat: baseline (scout). Lane axis this round: **coverage** (tracked
spontaneous-crash classification row identified at r60). This report is the
immutable before-state: no tracked fixture/runner edit, no commit, no
LOG/SCORECARD write. All artifacts under
`corpus/live/r61-baseline/` (scratch) plus this report.

## Frozen-tree provenance (no in-place fallback needed)

- Frozen source: `git -C ~/Projects/shokunin/game-dev-2d-shokunin archive HEAD | tar -x -C .shokunin/game-dev-2d/corpus/live/r61-baseline/tree`
- HEAD frozen: `3ee05ff5f47f6d1716b7012fc44b711d24387592`
  (`Revert "HOURS.md: craft-hours ledger opened (§Craft-hours canon)"`, two
  commits after r60's `8aca02e`; none touch `corpus/fixtures/`).
- Frozen runner sha256 `42104d95af5fcb98d742c495ee4562ea0c579c49d9ca22d11755302f685c31fb`
  — byte-identical to the live worktree copy and to the r59/r60 recorded hash.
- `verdicts.json["seed"]` records
  `/home/vgpnk/Projects/shokunin/game-dev-2d-shokunin/corpus/live/r61-baseline/tree/corpus/fixtures`
  → the run provably executed the **frozen copy**, not the live tree.
  Contamination risk: none; concurrent sibling-lane edits cannot reach the archive.

## Exact invocation

cwd `~/Projects/prymeagnt/game-dev-2d` (worktree root; `.shokunin/game-dev-2d/`
symlinks into the canonical lane repo):

```
python3 .shokunin/game-dev-2d/corpus/live/r61-baseline/tree/corpus/fixtures/run_battery.py \
  --godot godot \
  --runs .shokunin/game-dev-2d/corpus/live/r61-baseline/runs \
  --probe-failing --probe-unrelated-error --probe-export-launch \
  --probe-godot-error --probe-stream-attribution --probe-crash-exit --probe-timeout
```

Environment: Godot `4.7.2.stable.arch_linux.ed1daf0bf` (`/usr/bin/godot`),
Linux `7.2.3-arch1-3 x86_64`, Python `3.14.7`.

## Before-state receipt summary (verbatim tail of `battery.stdout`)

```
PASS stream attribution probe: .shokunin/game-dev-2d/corpus/live/r61-baseline/runs/20261013T220006012870Z/stream-attribution-verdicts.json
PASS crash-exit probe: .shokunin/game-dev-2d/corpus/live/r61-baseline/runs/20261013T220006012870Z/crash-exit-verdicts.json
PASS timeout probe: .shokunin/game-dev-2d/corpus/live/r61-baseline/runs/20261013T220006012870Z/timeout-verdicts.json
PASS battery: .shokunin/game-dev-2d/corpus/live/r61-baseline/runs/20261013T220006012870Z/verdicts.json
```

- `verdicts.json`: **`"verdict": "PASS"`, 89 results, 89 PASS / 0 FAIL**
  (77 CASES + 2 mutants + 10 probe/meta rows — same accounting as r60 verifier;
  `probe_failing: true`).
- stdout: 88 `^PASS` lines + exactly 2 designed inner `^FAIL` lines
  (`godot_error_unrelated` exit=1 classification=False;
  `stream_reject` exit=0 classification=False) + final `PASS battery`.
- Field-diff vs the frozen tree's `corpus/lessons/r59-audio-non-author.json`
  over `(script, flags, expected_exit, actual_exit, signature, verdict, error)`:
  **89 common cases, 0 mismatches** — before-state replays the r59 non-author
  baseline byte-exact on this host.
- Opt-in artifact verdicts, all **PASS**: `crash-exit-verdicts.json`,
  `timeout-verdicts.json`, `godot-error-verdicts.json`,
  `stream-attribution-verdicts.json`, `export-launch-verdicts.json`,
  `save-process-verdicts.json`.

## Artifact inventory (all under `corpus/live/r61-baseline/`)

- `tree/` — `git archive HEAD` extraction (frozen before-state source).
- `runs/20261013T220006012870Z/verdicts.json` — sha256 `522afbec7af196e3e13fd95e899d14ac3d3f75c7d53c85af82149de58ae23389`.
- `runs/20261013T220006012870Z/` — `scratch/`, `xdg-data/`, `export-launch/`,
  `missing-preset-scratch/`, and the six probe `*-verdicts.json` above.
- `battery.stdout` — verbatim runner stdout, sha256
  `871106e9febb731df1f81790b1e9779bd1e69f5f98770e5df8031ec8b5a7f216`.

## Before-state position for the r61 move

Pre-change `run_battery.py` carries **no** crash-`ERROR:` allowlist entry and
no spontaneous-crash CASES row: `classify_process` rejects any unallowlisted
`ERROR:` line, so an `OS.crash` SIGABRT (-6) emitting its own `ERROR:` marker
classifies False today — matching r60's measured scratch probes. The r61
coverage move (tracked row classifying True for expected -6 via allowlist)
must hold this 89/89 receipt stable.

## UNKNOWNs / caveats

- Row arithmetic: my "77 CASES + 2 mutants + 10 probe/meta" lumping follows
  the r60 verifier's accounting (author's "78 ordinary" counts the
  save-process meta row with CASES); total 89 either way.
- Naturally varying fields (`command`, `scratch`, `xdg_data_home`, pids,
  `elapsed_seconds`, export sha256/bytes) differ from prior runs by
  construction; the compared scope is the 7-field verdict tuple.
- Not re-measured here (r60 retained): signal-origin indistinguishability of
  `returncode`; no core-dump capture; no process-tree timeout claim.
- Single clean run; no transient flake observed (r59's concurrent-run slider
  flake did not recur — no sibling battery ran concurrently during this window
  as far as observable; if a sibling reports a flake, this receipt stands on
  its own frozen-tree evidence).
