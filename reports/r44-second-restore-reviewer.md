# Round 44 second-restore reviewer (independent scratch)

## Result
Positive hypothesis confirmed on real Godot `4.7.2.stable.arch_linux.ed1daf0bf` in a fresh, independently constructed headless SceneTree scratch. Exit code **0** after all nine parsed actions and frames.

Scratch: `corpus/live/r44-second-restore-reviewer-scratch/` (`project.godot`, `slider_adjust.gd`). Reproduce from repository root:

```sh
cd .shokunin/game-dev-2d/corpus/live/r44-second-restore-reviewer-scratch
timeout 20s godot --headless --path . --script slider_adjust.gd
```

## Edge-by-edge observations

Every row verifies the expected GUI focus owner and slider focus status immediately before parsing the edge, then verifies value, complete cumulative `value_changed` receipt history, and Label text after one process frame.

| Edge | Owner before | Action | Value | Receipts | Label |
|---:|---|---|---:|---|---|
| 0 | HSlider | ui_right press | 6 | [6] | Value 6 |
| 1 | Button | ui_right press | 6 | [6] | Value 6 |
| 2 | Button | ui_right release | 6 | [6] | Value 6 |
| 3 | HSlider | ui_left press | 5 | [6, 5] | Value 5 |
| 4 | HSlider | ui_left release | 5 | [6, 5] | Value 5 |
| 5 | Button | ui_left press | 5 | [6, 5] | Value 5 |
| 6 | Button | ui_left release | 5 | [6, 5] | Value 5 |
| 7 | HSlider | ui_left press | 4 | [6, 5, 4] | Value 4 |
| 8 | HSlider | ui_left release | 4 | [6, 5, 4] | Value 4 |

All assertions passed. Focus ownership before edges 1–2 and 5–6 was Button; before 0,3–4,7–8 it was HSlider. The restored final press produced exactly one new value receipt; release produced none. The hypothesis is supported: values `6,6,6,5,5,5,5,4,4`, receipts `[6,5,4]`, Label `Value 4`.

## Scope
This is independent direct scratch evidence for connected in-tree HSlider/Label/Button and synthetic parsed actions with one frame per edge. It does not establish OS auto-repeat, physical keyboard/timing, rendered or pointer UI, accessibility, production behavior, or internal consumption of unchanged-value edges. No engine/editor or seeded files edited; no battery changes made.
