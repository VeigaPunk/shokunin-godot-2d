# Round 36 slider executor report

## Result
**Implemented after measuring real input semantics.** Godot 4.7.2.stable.arch_linux.ed1daf0bf: with an in-tree focused `HSlider` (0..10, step 1, value 5), `Input.action_press/release` did not change value at all. That probe was rejected as ineffective. `Input.parse_input_event(InputEventAction)` with `ui_right` pressed/released and then `ui_left` pressed/released changed the value to 6 then 5 and delivered one `value_changed(float)` receipt per transition. No `set_value` stimulus or manual signal emit is used.

Tracked changes are limited to `corpus/fixtures/slider_adjust.gd` and two `CASES` in `corpus/fixtures/run_battery.py`. The fixture verifies viewport focus owner at setup and before each action, checks no initial signal receipts, samples connected value/receipt/Label after the right action, and checks final state after left. Its disconnected branch verifies the right-action value=6 with no receipt and unchanged Label, then left-action value=5 with no receipts and unchanged Label; it emits the expected assertion only after both numeric transitions.

## Replay evidence

Command: `python .shokunin/game-dev-2d/corpus/fixtures/run_battery.py --runs .shokunin/game-dev-2d/corpus/live/r36-final`

Result: exit 0, battery PASS, 50/50 ordinary fixture rows. Raw verdict artifact: `.shokunin/game-dev-2d/corpus/live/r36-final/20261013T054339399780Z/verdicts.json` (SHA-256 `4392478eb65703824ccc0b49254c0e202bc84a4441f750baf29d21d7fbb36faa`). Connected slider row exits 0 with `PASS slider_adjust focused=true range=0..10 step=1 values=6,5 receipts=6,5 Labels=Value 6,Value 5`. Disconnected row exits 2 at the intended missing-signal assertion; classifier marks it PASS. It observes values `6.0,5.0`, receipts `[]`, Label `Value 5`; it does not fail before the second action.

The earlier attempted full replay after adding focus-owner assertions failed due to my use of undeclared `viewport`; that run is retained as scratch telemetry and is superseded by the passing replay above. The initial exploratory `Input.action_press` probe and the corrected `Input.parse_input_event` measurement are under `.shokunin/game-dev-2d/corpus/live/r36-measure-20261013T024116/`.

## Scope and axis

The fixture establishes a headless, synthetic focused keyboard-action path only. It does not test rendered/pointer input, physical timing, accessibility, production UI behavior, or general slider correctness. On this evidence the candidate is causal and plausibly adds numeric Range/HSlider input-driven control coverage beyond prior programmatic `TextureProgressBar` coverage. Executor does not claim final axis admission; named independent replay remains required.
