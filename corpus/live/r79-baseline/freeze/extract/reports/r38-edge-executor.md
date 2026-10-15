# Round 38 edge executor report — HSlider press/release attribution

## Measurement before edit
Godot 4.7.2.stable.arch_linux headless scratch measurement with one `Input.parse_input_event(InputEventAction)` edge followed by one `process_frame` confirmed the narrow claim. Focused connected `ui_right` press/release values/receipts/Label: `6/[6]/Value 6`, `6/[6]/Value 6`; `ui_left` press/release: `5/[6,5]/Value 5`, `5/[6,5]/Value 5`. Focused disconnected control: values 6,6,5,5; receipts `[]`, Label `Value 5`. No-focus control: values 5,5,5,5; receipts `[]`, Label `Value 5`. Negative arms reach their existing intended final diagnostic and exit 2. Independent scratch measurements are recorded by scout and critic reports.

The event dispatch call itself does not synchronously change the value; the changes are observed after the next process frame. Critic also found an extra repeated `pressed=true` followed by a frame advances 6→7. This test establishes only one explicit press/release pair per direction, not generic repeat immunity or physical-key timing.

## Implementation
Edited only `corpus/fixtures/slider_adjust.gd`; no runner, CASES/row/signature, engine/editor, or seeded control changes. Added explicit checks after each of the four event+frame edges in each existing arm: right expectations are defined once and reused on press and release; left final state/receipt expectation is likewise checked on both edges. Connected, disconnected, and no-focus expected values/receipts/labels remain distinguished; existing final assertions and negative diagnostics remain. A first implementation replay failed due to assigning an untyped conditional Array to `Array[float]` and timed out all three slider rows; that raw failed replay remains in `corpus/live/r38-edge-executor-full/20261013T060918147952Z/`. Fixed with typed arrays populated by `append`.

## Replay
Direct Godot smoke: connected exit 0; disconnected exit 2 at existing `SLIDER SIGNAL ASSERTION FAILED`; no-focus exit 2 at existing `SLIDER NO-FOCUS ASSERTION FAILED`. Full command:

`python .shokunin/game-dev-2d/corpus/fixtures/run_battery.py --runs .shokunin/game-dev-2d/corpus/live/r38-edge-executor-full2 --probe-failing --probe-unrelated-error --probe-export-launch --probe-godot-error --probe-stream-attribution --probe-crash-exit --probe-timeout`

Final full replay raw: `corpus/live/r38-edge-executor-full2/20261013T061030668693Z/verdicts.json`; exit 0, 62/62 PASS (51 ordinary +2 mutants +9 opt-ins), including all three slider arms. The unrelated-error and stream-reject probe inner results are expected negatives and their probe groups passed. Runner SHA-256 unchanged: `69d94dd63f0a32769731d7942b831a3d7e7ad84a5ce571153df2abe231a1914f`. Updated fixture SHA-256: `093ae11de4e854ffb954ce5158133be2c3d5f890c8fef738990190a9bcfcd036`.

Scope is bounded to synthetic parsed actions followed by one frame on the tested headless focused HSlider; not physical keyboard timing, general repeat behavior, rendered/pointer/accessibility UI, or generic Range guarantees.
