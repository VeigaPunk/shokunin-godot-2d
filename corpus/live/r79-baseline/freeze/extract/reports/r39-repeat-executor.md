# Round 39 repeat-right executor report

## Measurement and implementation

Measured the exact frame-delimited sequence in a scratch Godot 4.7.2 project before editing the fixture. With the focused, connected `HSlider` (0..10, step 1, initial 5), fresh parsed events produced values at the seven edges `6,7,7,6,6,5,5`, connected receipts `[6,7,6,5]`, and signal-updated Label values `Value 6`, `Value 7`, `Value 6`, `Value 5` at the four changes. The disconnected control retained numeric history `6,7,7,6,6,5,5`, no receipts, and `Value 5`. Focus remained on the slider throughout. No OS auto-repeat or physical timing claim.

Added `--repeat-right` fixture mode with explicit per-edge value, receipt-count, Label, and focus-owner assertions. The repeat press is a second fresh `InputEventAction` with `pressed=true`, before the right release. The paired `--repeat-right --disconnect-signal` case checks all seven edges and emits its expected negative only afterward. Added two ordinary battery cases and precise expected-negative classification. Only `slider_adjust.gd` and `run_battery.py` changed.

## Replay evidence

An initial full run before adding the exact allowed expected-error classifier was retained as telemetry: the disconnected control exited 2 at its intended diagnostic but battery classified it FAIL; unrelated-error and stream-reject probes are designed negative inner classifications. After the classifier correction, author full replay:

`python .shokunin/game-dev-2d/corpus/fixtures/run_battery.py --probe-failing --probe-unrelated-error --probe-export-launch --probe-godot-error --probe-stream-attribution --probe-crash-exit --probe-timeout`

completed exit 0, battery verdict PASS, 64 total result rows (53 ordinary, 2 mutants, 9 opt-ins). Comparing against `corpus/lessons/r38-edge-verifier.json`, all 62 prior `(case, verdict, actual_exit, signature)` triples are unchanged; only `slider_adjust_repeat_right` and `slider_adjust_repeat_right_disconnected` were added. Raw run: `.shokunin/game-dev-2d/corpus/live/runs/20261013T062205834944Z/verdicts.json`. Standalone default run also passed 64/64 at `.shokunin/game-dev-2d/corpus/live/runs/20261013T062133048613Z/verdicts.json`.

## Scope and outstanding verification

This supports the bounded synthetic Godot input-history claim only; it does not establish operating-system keyboard auto-repeat, physical timing, or production UI behavior. A named non-author verifier replay and sabotage remain for the orchestrator. No engine/editor/seeded control was edited; no commit, push, or merge performed.
