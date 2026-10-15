# Round 39 named non-author repeat verifier

## Scope and identity

Independent verifier replay (no tracked source edits). Godot: godot. Scratch and full-run artifacts: `corpus/live/runs/20261013T062747264384Z`; direct paired probe and sabotage: `corpus/live/r39-repeat-verifier/paired-direct`. Captured raw battery: `corpus/lessons/r39-repeat-verifier.json` (SHA-256 `b720f109f0ed10f13a149be2a654177a289a7f256cdc176b2549bb0adb86c1f6`), byte-identical to the run's `verdicts.json`. Tracked fixture/runner SHA-256 at inspection and after replay: `8cea925f464478943f4a67de0ad8db886c4002a65f3cdf5a0f1444811da28dc9` / `8f3a03a88e6e2db7777f1e049aa89f476c1e0ec08bca0ba8c05b7f59d47e18a0`; no verifier edits.

## Direct paired Godot probe

Fresh Godot 4.7.2 headless runs dispatched a newly parsed `InputEventAction` for each of seven edges, awaited one process frame, and checked the HSlider owned GUI focus before every event. Connected result values were `[6,7,7,6,6,5,5]`, cumulative `value_changed` receipts `[6]`, `[6,7]`, `[6,7]`, `[6,7,6]`, `[6,7,6]`, `[6,7,6,5]`, `[6,7,6,5]`; signal-driven Label followed each value. The paired disconnected arm had the same numeric history, receipts `[]`, and Label `Value 5` throughout; it exited 2 only after all seven checks and printed the complete final history before the exact terminal diagnostic. Connected exited 0. Raw stdout is in `corpus/live/r39-repeat-verifier/paired-direct`.

A first scratch-only sabotage accidentally shortened the `edges` array as well as omitting an event. It correctly failed but at `ui_right release`, not the requested second-press assertion; this is retained as honest initial telemetry, not counted as requested sabotage evidence. A corrected scratch sabotage retained all seven loop edges/assertions and replaced only the second `Input.parse_input_event` dispatch with a no-op. It failed at edge index 1 (`ui_right pressed=true`) with actual value 6/receipts `[6]` against expected 7/`[6,7]`; exit 1. No false-PASS. See `corpus/live/r39-repeat-verifier/paired-direct/probe_sabotage.gd`.

## Full battery and comparisons

Ran the required default-path command with `--probe-failing --probe-unrelated-error --probe-export-launch --probe-godot-error --probe-stream-attribution --probe-crash-exit --probe-timeout`; exit 0 and payload verdict PASS, 64 results. The two intentionally negative inner classifications (unrelated Godot error and stream reject) are FAIL as expected; their enclosing diagnostic/attribution probes PASS. All 62 r38 named-verifier result tuples `(case, verdict, actual_exit, signature)` are unchanged; exactly two additions PASS, one exit 0 and one exit 2: `slider_adjust_repeat_right`, `slider_adjust_repeat_right_disconnected`. Existing three slider rows are unchanged.

Separate `--fault-injection` run: outer PASS; inner deliberate hang FAIL, clean expected-negative PASS, unrelated-error FAIL. Raw verifier-owned fault result: `corpus/lessons/r39-fault-verifier.json` (SHA-256 `cd49178d1f70d6a05dc89abffb6d9f756f22cb258b9f1854133597e4592849de`).

## Bounded claim

This verifies deliberate synthetic `InputEventAction` edges in Godot 4.7.2, each followed by one process frame, with explicit focus-owner checks. The second right press is a deliberate second fresh synthetic event. This does **not** establish OS auto-repeat, physical-key timing, rendered or pointer interaction, accessibility behavior, or production behavior. No tracked edits, commit, push, or merge by verifier.
