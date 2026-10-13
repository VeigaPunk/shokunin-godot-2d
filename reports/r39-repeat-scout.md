# Round 39 repeat scout — scratch measurement

## Setup
Ran Godot 4.7.2.stable headless scratch project at `corpus/live/r39-repeat-scout/measure.gd`; no fixture, runner, engine/editor source, or seeded corpus was changed. The focused HSlider was min=0, max=10, step=1, initial value=5. One connected run wired `value_changed` to append receipts and update the Label; paired `--disconnect-signal` run retained the same numeric action route but omitted the connection. Focus owner was the HSlider at start and each edge.

The event sequence deliberately parsed a fresh `InputEventAction` for each edge, with one `process_frame` before measuring: `ui_right pressed=true`, a second distinct `ui_right pressed=true`, `ui_right pressed=false`, `ui_left pressed=true`, `ui_left pressed=false`, another `ui_left pressed=true`, `ui_left pressed=false`.

## Observed results

| Edge | Connected value | Connected receipts | Connected Label | Disconnected value | Disconnected receipts | Disconnected Label |
|---|---:|---|---|---:|---|---|
| first ui_right press | 6 | [6] | Value 6 | 6 | [] | Value 5 |
| second fresh ui_right press | 7 | [6,7] | Value 7 | 7 | [] | Value 5 |
| ui_right release | 7 | [6,7] | Value 7 | 7 | [] | Value 5 |
| first ui_left press | 6 | [6,7,6] | Value 6 | 6 | [] | Value 5 |
| first ui_left release | 6 | [6,7,6] | Value 6 | 6 | [] | Value 5 |
| second ui_left press | 5 | [6,7,6,5] | Value 5 | 5 | [] | Value 5 |
| second ui_left release | 5 | [6,7,6,5] | Value 5 | 5 | [] | Value 5 |

Both invocations exited 0. Connected signal-driven Labels and cumulative receipts track each numeric transition; releases leave value and receipts unchanged. Disconnected arm reaches the same numeric history and baseline 5, with no receipts and its unchanged Label. This supports the proposed paired history/control distinction and negative assertion only after the full edge sequence.

## Boundary
This measures deliberately injected fresh synthetic action events separated by one process frame in Godot 4.7.2 headless. It does **not** establish OS keyboard auto-repeat, physical keyboard behavior, or timing behavior. No code change recommended by this scout.
