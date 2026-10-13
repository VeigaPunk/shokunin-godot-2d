# Round 41 focus-handoff scout

## Direct scratch result

Ran a real Godot **4.7.2.stable.arch_linux.ed1daf0bf** headless scratch at `corpus/live/r41-focus-handoff-scout/slider_handoff_scratch.gd`. It creates an in-tree HSlider (`min=0`, `max=10`, `step=1`, initial `5`), an in-tree focusable Button, and Label; connects `value_changed` to a receipt array and the Label. The slider is focused before the first event. Each deliberate fresh parsed `InputEventAction` is followed by one `process_frame`.

| Check | GUI focus owner | Slider focused | Value | Receipts | Label |
|---|---|---:|---:|---|---|
| Initial | HSlider | yes | 5 | `[]` | `Value 5` |
| `ui_right` press + frame | HSlider | yes | 6 | `[6]` | `Value 6` |
| Transfer via `other.grab_focus()` + frame | Button | no | 6 | `[6]` | `Value 6` |
| second `ui_right` press + frame | Button | no | 6 | `[6]` | `Value 6` |
| `ui_right` release + frame | Button | no | 6 | `[6]` | `Value 6` |
| first `ui_left` press + frame | Button | no | 6 | `[6]` | `Value 6` |
| first `ui_left` release + frame | Button | no | 6 | `[6]` | `Value 6` |
| second `ui_left` press + frame | Button | no | 6 | `[6]` | `Value 6` |
| second `ui_left` release + frame | Button | no | 6 | `[6]` | `Value 6` |

The Button was confirmed as `gui_get_focus_owner()` and the slider's `has_focus()` was false before each of the six remaining event edges (and remained so after each frame). Scratch exited 0 after printing observations; no assertion/negative exit was implemented in this scout. This demonstrates the requested causal contrast at scratch level: one focused right press adjusts, then focus handoff precedes six unchanged events. It does not test OS auto-repeat, physical keyboard input/timing, rendered/pointer UI, accessibility, production, or generic slider behavior.

## Raw run

Command: `godot --headless --path .shokunin/game-dev-2d/corpus/live/r41-focus-handoff-scout --script res://slider_handoff_scratch.gd`

Exit code: 0. Raw stdout:

```text
Godot Engine v4.7.2.stable.arch_linux.ed1daf0bf (2026-08-17 01:18:38 UTC) - https://godotengine.org

SETUP slider_in_tree=true focus_owner_slider=true focus_owner=@HSlider@2:<HSlider#26373785034> value=5.0 receipts=[] label=Value 5
EDGE ui_right press value=6.0 receipts=[6.0] label=Value 6 owner_other=false slider_focus=true
HANDOFF owner_other=true slider_has_focus=false owner=@Button@3:<Button#26407339468>
EDGE ui_right press value=6.0 receipts=[6.0] label=Value 6 owner_other=true slider_focus=false
EDGE ui_right release value=6.0 receipts=[6.0] label=Value 6 owner_other=true slider_focus=false
EDGE ui_left press value=6.0 receipts=[6.0] label=Value 6 owner_other=true slider_focus=false
EDGE ui_left release value=6.0 receipts=[6.0] label=Value 6 owner_other=true slider_focus=false
EDGE ui_left press value=6.0 receipts=[6.0] label=Value 6 owner_other=true slider_focus=false
EDGE ui_left release value=6.0 receipts=[6.0] label=Value 6 owner_other=true slider_focus=false
```
