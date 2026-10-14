# Round 39 repeat-event critic — read-only falsification

## Method
Copied `project.godot` into the critic-owned scratch directory `.shokunin/game-dev-2d/corpus/live/r39-repeat-critic/` and ran a scratch-only SceneTree probe with Godot `4.7.2.stable.arch_linux.ed1daf0bf`. It instantiated an in-tree HSlider (0..10, step 1, value 5), grabbed GUI focus, and dispatched fresh `InputEventAction` instances for `ui_right` pressed=true twice, right release, and two `ui_left` press/release pairs. Each event was followed by one `process_frame`; probe logged state immediately after parse and after frame, and recorded the connected `value_changed` callback and Label consumer. Repeated with the signal disconnected. Raw stdout: `corpus/live/r39-repeat-critic/focused.stdout.txt`, `disconnected.stdout.txt`; probe: `r39_probe.gd`. Fixture SHA-256 before/after: `093ae11de4e854ffb954ce5158133be2c3d5f890c8fef738990190a9bcfcd036` (unchanged).

## Observations
- Setup reports focus=true, value=5, receipts=[], Label `Value 5`.
- Each constructed event has a distinct instance ID within the run. Immediately after `Input.parse_input_event`, the previous state remains; transition/callback happens by the following frame.
- Connected sequence after frames: second right pressed=true is a distinct event and changes 6→7, adding receipt 7 and updating Label to `Value 7`; right release leaves 7/[6,7]/`Value 7`. First left press changes 7→6, appending receipt 6 and Label `Value 6`; its release leaves state unchanged. Second left press changes 6→5, appending receipt 5 and Label `Value 5`; its release leaves state unchanged. Final receipts `[6,7,6,5]` and value 5.
- Disconnected paired sequence has the same numeric history 5→6→7→7→6→6→5→5; receipts remain `[]` and Label remains `Value 5` throughout, including after all edges. This supports signal-driven Labels rather than an independently refreshed Label.
- Callback logs occur during the frame-driven transition and see the appended receipt/updated Label; no callback appears for release edges.

## Falsification / limits
No contradiction to the proposed synthetic event sequence, release behavior, paired negative control, or signal ordering was observed on this Godot version. Distinctness is from separately constructed `InputEventAction` instances in this probe; event IDs are runtime-local evidence, not a stable external identifier. This is not evidence about OS auto-repeat, physical key timing, held-key behavior, or how a platform generates repeated events. It only shows that deliberately dispatching a second fresh `pressed=true` event followed by a frame increments this focused HSlider again. No source fixture, runner, seeded control, engine/editor, or tracked file was modified by this critic.
