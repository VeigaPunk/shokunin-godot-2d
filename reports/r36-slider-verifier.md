# Round 36 named verifier report

## Result
Independent non-author verification confirms a causal, bounded HSlider input/signal probe on Godot 4.7.2. The probe is headless and uses a focused in-tree HSlider with min=0, max=10, step=1, value=5. A fresh pressed/released `InputEventAction` for `ui_right` parsed through `Input.parse_input_event` yields value 6, one `value_changed(float)` receipt `[6]`, and Label `Value 6`; `ui_left` then yields value 5, receipts `[6,5]`, Label `Value 5`. The slider remains the GUI focus owner before each action.

With the signal consumer disconnected and otherwise identical setup/actions, values still become 6 then 5 while receipts remain `[]` and Label remains `Value 5`. The disconnected fixture exits 2 only after both numeric transitions, at its intended missing-signal assertion. No programmatic value assignment is used as stimulus and no signal is manually emitted. The measured input route differs from the executor’s retained initial `Input.action_press` attempt, which was ineffective; the executor’s earlier undeclared `viewport` run also remains adverse telemetry, superseded by its corrected replay.

## Full default-path replay
Command: `python .shokunin/game-dev-2d/corpus/fixtures/run_battery.py --probe-failing --probe-unrelated-error --probe-export-launch --probe-godot-error --probe-stream-attribution --probe-crash-exit --probe-timeout`

Exit 0. Raw full result copied byte-identically to `.shokunin/game-dev-2d/corpus/lessons/r36-slider-verifier.json` (SHA-256 `ad79ea348031d2ce1048c3fbb105ff8a2b2b60cf966a5445394d30050b8ae2e1`). It has 61 result rows. Compared with `.shokunin/game-dev-2d/corpus/lessons/r35-group-absence-verifier.json`, all 59 old `(verdict, actual_exit, signature)` triples are unchanged; exactly two rows were added: `slider_adjust` PASS/exit 0 and `slider_adjust_disconnected` PASS/exit 2. The disconnected row’s inner intended assertion is classified as an expected negative, hence PASS.

Separate `--fault-injection` run exited 0; raw copied byte-identically to `.shokunin/game-dev-2d/corpus/lessons/r36-fault-verifier.json`. The outer artifact verdict is PASS; inner timeout and unrelated-error injections are correctly FAIL, while clean expected-negative injection is PASS.

## Sabotage and source integrity
In disposable scratch, removing `Input.parse_input_event(event)` caused the connected case to fail the actual transition/signal assertion with exit 2. The disconnected case likewise failed at its first expected numeric transition with exit 2; neither false-passed. No tracked source edits were made by this verifier. At replay completion, fixture and runner SHA-256 values were `1c0850ff6daf74696c19cbe0bd45e66dc1d21e074d4b6b588c59166351576e87` and `5e6bc978a5098ac2ef104b378d3641902c8d595ad9fba57058e82abdc31f4b2a`.

## Scope
This establishes only a synthetic, headless, focused keyboard-action path for HSlider numeric adjustment and signal-driven Label updates. It is distinct from the existing `health_gauge` programmatic TextureProgressBar update. It does not establish pointer/rendered interaction, physical timing, accessibility, production UI behavior, or general slider correctness.
