# Round 31 focus-loss reviewer — independent scratch paired replay

## Result
The second `ui_accept` pair did **not** activate the Button after its focus was explicitly released following the first complete pair. The focused same-wiring control activated twice. This supports the bounded claim that continued Button focus is required for the second activation in this Godot headless synthetic input path.

## Method
I copied the tracked `button_activation.gd` and `project.godot` into my independent scratch project at `corpus/live/r31-focus-loss-reviewer-scratch/project/`. The focused control is an unchanged copy of the tracked fixture. For the paired focus-loss arm only, I inserted `button.release_focus()` and a `process_frame` after the first release edge and before the second press edge; I checked that the Button lacked focus and viewport focus owner was null before pair 2. Action generation (`root.push_input(InputEventAction)` with `ui_accept`), signal connection, callback, Button/Label setup, and pair edges otherwise remained identical. After pair 2 I checked receipt/text and focus owner. No tracked fixture or runner was edited.

## Raw exact results
Godot version: `Godot Engine v4.7.2.stable.arch_linux.ed1daf0bf (2026-08-17 01:18:38 UTC)`.

Focused control, exit **0** (`corpus/live/r31-focus-loss-reviewer-scratch/focused-control.raw.txt`):
```text
BUTTON_FOCUS edge=release1 focused=true button_has_focus=true receipts=1 text=Activated 1
BUTTON_FOCUS step=2 focused=true button_has_focus=true receipts=2 text=Activated 2
PASS button_activation in_tree=true initial=Ready edge_texts=[Ready,Activated 1,Activated 1,Activated 2] receipts=[0,1,1,2]
```

Release-focus arm, exit **0** (`corpus/live/r31-focus-loss-reviewer-scratch/focus-loss.raw.txt`):
```text
BUTTON_FOCUS edge=release1 focused=true button_has_focus=true receipts=1 text=Activated 1
BUTTON_FOCUS edge=after_release_focus focused=false button_has_focus=false owner_is_null=true receipts=1 text=Activated 1
BUTTON_FOCUS step=2 focused=false button_has_focus=false receipts=1 text=Activated 1
BUTTON_FOCUS edge=release2 focused=false button_has_focus=false owner_is_null=true receipts=1 text=Activated 1
PASS button_focus_loss receipts=[0,1,1,1] texts=[Ready,Activated 1,Activated 1,Activated 1]
```

Thus the second press-only and release states both retained exactly one receipt and `Activated 1`; after release2 the focus owner remained null. The control pair changed from 1 to 2 receipts and `Activated 2` while focus remained on the Button.

## Integrity / scope
Tracked fixture SHA-256: `edb777640fe19bdd62960ef18898f8fb181fcb28db57f20025f4430d1cbb68af`. Tracked runner SHA-256: `38a27c76ceb18a8b5e14b90504ca8010856b305929487ccef18252f96c6bc0eb`. I did not change either file. This is independent scratch evidence only; it does not verify an executor change or a full battery replay. It establishes only a focus-loss contrast for this headless `root.push_input(ui_accept)` fixture, not pointer hit-testing, production UI behavior, or real-user timing.
