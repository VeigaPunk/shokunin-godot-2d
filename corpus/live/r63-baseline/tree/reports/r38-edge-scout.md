# Round 38 edge scout — real Godot measurement

Measured on Godot `4.7.2.stable.arch_linux.ed1daf0bf` with an isolated scratch project under `corpus/live/r38-edge-scout/` (not the tracked fixture). Script creates an in-tree HSlider with min=0, max=10, step=1, initial value=5 and Label consumer; parses a fresh `InputEventAction` for each edge, awaits one process frame, and captures focus owner, value, receipts, and Label. Source: `measure.gd`; raw outputs: `focused.stdout.txt`, `disconnected.stdout.txt`, `no-focus.stdout.txt`.

| Arm | ui_right press | ui_right release | ui_left press | ui_left release |
|---|---|---|---|---|
| Focused + connected | 6 / `[6]` / `Value 6` | 6 / `[6]` / `Value 6` | 5 / `[6,5]` / `Value 5` | 5 / `[6,5]` / `Value 5` |
| Focused + signal disconnected | 6 / `[]` / `Value 5` | 6 / `[]` / `Value 5` | 5 / `[]` / `Value 5` | 5 / `[]` / `Value 5` |
| No focus + connected | 5 / `[]` / `Value 5` | 5 / `[]` / `Value 5` | 5 / `[]` / `Value 5` | 5 / `[]` / `Value 5` |

Focus owner is the slider for all focused edges and null for the no-focus arm. Every command exited 0. The observed result supports the declared edge claim: each press adjusts exactly once and the corresponding release causes no additional value/signal/Label change; disconnected and no-focus controls separate numeric adjustment from signal wiring and focus routing. No contradictory behavior; recommend proceed with edge assertions. Scope is one synthetic event followed by one frame per edge in headless Godot, not physical key timing/repeat or rendered interaction. I did not edit the fixture, runner, engine/editor files, or seeded controls.
