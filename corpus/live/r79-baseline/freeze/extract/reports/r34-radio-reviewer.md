# Round 34 independent scratch reviewer — grouped toggle controls

## Scope and setup
Independent scratch-only Godot 4.7.2 test; no tracked source edits. I first tried the literal `RadioButton.new()` from the original prompt. Godot rejected it at parse time (`Identifier "RadioButton" not declared in the current scope`); `ClassDB.class_exists("RadioButton")` also returned false. Following the amended task, I tested actual native `Button` controls with `toggle_mode = true`, both assigned to the same `ButtonGroup`. A starts selected, B starts unselected. Each control was focused in sequence and received a synthetic `ui_accept` press and release. Connected run connected each control's `toggled(bool)` to a receiver; the receiver records exact control/value order and updates a Label only when the value is true. Disconnected run omitted both connections.

Scratch files: `.shokunin/game-dev-2d/corpus/live/r34-radio-reviewer/radio_probe.gd`, `class_probe.gd`, and copied `project.godot`. Commands:

```sh
godot --headless --path .shokunin/game-dev-2d/corpus/live/r34-radio-reviewer --script radio_probe.gd
godot --headless --path .shokunin/game-dev-2d/corpus/live/r34-radio-reviewer --script radio_probe.gd -- --disconnect
godot --headless --path .shokunin/game-dev-2d/corpus/live/r34-radio-reviewer --script class_probe.gd
```

## Raw connected output (exit 0)
```text
Godot Engine v4.7.2.stable.arch_linux.ed1daf0bf (2026-08-17 01:18:38 UTC) - https://godotengine.org
SETUP A=true B=false receipts=[] label=Ready
PRESS target=B A=true B=false receipts=[] label=Ready
RELEASE target=B A=false B=true receipts=["A:false", "B:true"] label=B
PRESS target=A A=false B=true receipts=["A:false", "B:true"] label=B
RELEASE target=A A=true B=false receipts=["A:false", "B:true", "B:false", "A:true"] label=A
```

## Raw disconnected output (exit 0)
```text
Godot Engine v4.7.2.stable.arch_linux.ed1daf0bf (2026-08-17 01:18:38 UTC) - https://godotengine.org
SETUP A=true B=false receipts=[] label=Ready
PRESS target=B A=true B=false receipts=[] label=Ready
RELEASE target=B A=false B=true receipts=[] label=Ready
PRESS target=A A=false B=true receipts=[] label=Ready
RELEASE target=A A=true B=false receipts=[] label=Ready
```

Class probe output: `RadioButton exists=false`, `CheckBox exists=true` (exit 0).

## Finding / limit
ButtonGroup-backed toggle Buttons enforce exclusivity across B then A. Both property transitions occur on the synthetic action's release, not press. Connected callbacks arrive in exact order `A:false`, `B:true`, then `B:false`, `A:true`; the label ends at B then A. Disconnected controls still complete both selection transitions, with no callback receipts and unchanged Ready label. This validates the proposed connected/disconnected behavioral contrast for native toggle Buttons, not a nonexistent `RadioButton` class. The parent fixture should use this actual API/type and retain group-backed exclusivity assertions; do not report this as RadioButton coverage. Scratch probe did not test a retained expected-signal failure after both disconnected actions.
