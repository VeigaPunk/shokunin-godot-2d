# Round 36 independent HSlider input review

## Result
Actual Godot 4.7.2 headless semantics support the proposed bounded two-action probe. A focused in-tree `HSlider` at 5.0 with min=0, max=10, step=1 responded to synthetic `ui_right` with value 6.0, then synthetic `ui_left` with value 5.0. Each produced exactly one `value_changed(float)` receipt, ordered `[6.0, 5.0]`, and the connected Label advanced `Value 5` → `Value 6` → `Value 5`. Focus remained on the HSlider throughout.

With both consumers disconnected, using the same HSlider setup and same actions, value still transitioned 5.0 → 6.0 → 5.0; receipts stayed empty and the label remained `Value 5`. The change itself is therefore attributable to focused Range input, not a programmatic value assignment, and both signal-dependent consumers are isolated.

## Reproduction
Scratch files are isolated at `.shokunin/game-dev-2d/corpus/live/r36-slider-reviewer-scratch/slider.gd` and `project.godot`. No seeded fixture or engine/editor source changed. Commands from that scratch directory:

- `godot --headless --path . --script res://slider.gd`
- `godot --headless --path . --script res://slider.gd -- --disconnect`

Connected output:
```
SETUP value=5.0 focused=true focus_owner=@HSlider@2:<HSlider#26457671116> label=Value 5
AFTER_RIGHT value=6.0 receipts=[6.0] label=Value 6 focus=true
AFTER_LEFT value=5.0 receipts=[6.0, 5.0] label=Value 5 focus=true
```
Disconnected output:
```
SETUP value=5.0 focused=true focus_owner=@HSlider@2:<HSlider#26457671116> label=Value 5
AFTER_RIGHT value=6.0 receipts=[] label=Value 5 focus=true
AFTER_LEFT value=5.0 receipts=[] label=Value 5 focus=true
```

Each action was sent as a pressed `InputEventAction` through `Input.parse_input_event`, followed next frame by its released event; a further process frame allowed handling before reading state. No manual `set_value` stimulus or manual signal emission was used. This establishes the requested synthetic action mapping/step/signal behavior in this Godot build only; it does not establish rendered, physical keyboard, timing, accessibility, or general HSlider behavior.
