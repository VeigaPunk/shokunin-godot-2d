# Round 52 route executor — bounded SceneTree push-input control

## Result

The r51 eleven-edge focused/reconnected HSlider history distinguishes the alternate `SceneTree.root.push_input` route from the parsed route on the bounded action-state dimension. In a unique scratch project on Godot 4.7.2, edge10 used an `InputEventAction` with the same `ui_left` and `pressed=false` fields and one process frame. The in-tree `_input` observer advanced 3→4, while `Input.is_action_pressed("ui_left")` stayed true. The focused slider remained at 3, callback receipts remained `[6,3]`, Label remained `Value 3`, and callback was connected. Paired ordinary parsed release retains observer 3→4 and pressed-state true→false. No claim is made about HSlider consuming the pushed event or any OS/physical input behavior.

## Bounded fixture change

Added a distinct `--observe-push-input-release` branch to `corpus/fixtures/slider_adjust.gd`; did not replace or edit r51/r50 branches. It creates the observer under the new flag, asserts focus owner and callback state before each edge, then on edge10 performs `get_root().push_input(pushed)` with an `InputEventAction` (`ui_left`, `pressed=false`), awaits one frame, requires exactly one observer receipt and requires the global action remain pressed. It checks the existing per-edge numeric values, complete callback receipt history, and Label, then exits only after all eleven checks with the unique marker `SLIDER_PUSH_INPUT_RELEASE ... observer_delta=1 pressed=true ...` and expected-negative terminal error. Added exactly one expected-negative runner case and one exact non-allowlisted classifier mapping.

The causal scratch contrast used the r51 source without changing tracked files; the tracked runner executes the new dedicated branch. Corrected ordinary battery: 66/66 PASS (65 ordinary inherited cases plus the one new negative), raw `corpus/live/runs/20261013T093647471068Z/verdicts.json`. The new negative exits 2 and is classified only by its exact terminal error.

## Adverse telemetry

- Earlier scratch experiments first hit the intended r51 post-state guard because that guard expected parsed-release behavior; they established the push-input state difference but were not an admitted candidate PASS. A malformed candidate initially copied the wrong state expectation and wrong terminal, likewise not evidence of a passing runner case.
- A concurrent simplifier made unauthorized overlapping edits to the tracked fixture and runner, introducing duplicate/mismatched same-key classifier data. I retained the single additive branch/case/mapping as sole tracked owner and repaired the unique terminal and classifier. The first ordinary run failed the duplicate/mismatch (`20261013T093600520090Z`); it remains adverse telemetry. The corrected clean ordinary run is separately recorded above.

## Scope

Synthetic Godot 4.7.2 action routing and frames only. No inference about OS input, HSlider internal consumption, physical timing/repeat, rendering, pointer/accessibility behavior, or production input. No engine/editor source or seeded fixture edits; no commit, push, or merge made.
