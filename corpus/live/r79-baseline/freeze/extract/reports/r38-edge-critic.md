# Round 38 edge critic — four-edge input attribution

## Method
Read-only against the existing `corpus/fixtures/slider_adjust.gd` copied to the critic's scratch directory `corpus/live/r38-edge-critic/` (Godot 4.7.2 headless). Instrumented a scratch-only clone to emit state immediately after `Input.parse_input_event` and after the following `process_frame`, for `ui_right` press/release and `ui_left` press/release. Ran focused connected, focused `--disconnect-signal`, and `--no-focus` arms. No fixture/runner/seeded controls were changed. Fixture SHA-256 before probing: `099bef37e61342d371d77bcd750106ceddb686b0f20ef36fed80e1b759a1449e`.

## Measurements
- Focused connected arm after each edge's next frame: right press `value=6 receipts=[6] Label=Value 6`; right release remains `6/[6]/Value 6`; left press `5/[6,5]/Value 5`; left release remains `5/[6,5]/Value 5`. Process exits 0.
- Focused disconnected arm: corresponding values `6,6,5,5`; receipts stay `[]`, label stays `Value 5`; expected-negative diagnostic occurs after all edges and process exits 2.
- No-focus arm: values stay `5` at all four edges; receipts `[]`, label `Value 5`; expected-negative diagnostic occurs after all edges and exits 2.
- At the instant immediately following each `Input.parse_input_event`, state still reflects the preceding edge. The value/signal transition is observed after yielding one process frame. Therefore edge attribution should explicitly mean the event followed by a frame, not synchronous effect inside the dispatch call.

## Falsification / limits
Release edges do not cause a second adjustment in the exact tested one-press/one-release sequence. This does **not** establish general absence of auto-repeat: an extra repeated `pressed=true` event with a process-frame yield was tested in scratch and changed rightward value 6→7 with receipt 7. Thus the harness can distinguish a release from a repeated press, but should not claim physical key repeat/timing behavior or that all repeated presses are harmless. Input is delivered via `Input.parse_input_event(InputEventAction)` to a focused in-tree HSlider, not physical keyboard/window routing. Frame observations establish the tested deferred processing order, not a universal frame-timing guarantee. All three controls' raw outcomes match the proposed edge attribution; no per-edge attribution mismatch found. No causal counterevidence requiring HOLD, subject to stating the press/release claim narrowly and not generalizing it to auto-repeat.
