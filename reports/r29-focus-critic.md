# Round 29 focus falsification (read-only)

## Result
The focus-dependence claim survives a bounded real-Godot contrast. In a disposable project, identical `ui_accept` press/release input routed through `root.push_input` activated the currently focused Button, whether that was the target or a different Button; with verified `gui_get_focus_owner() == null`, the same input produced no pressed receipts. This supports the narrow claim that the fixture's positive is delivered through GUI focus, rather than merely proving that its signal is connected. No tracked fixture/runner changes were made.

## Raw replay
Scratch probe: `.shokunin/game-dev-2d/corpus/live/r29-focus-critic/focus_probe.gd`; project copy: `.shokunin/game-dev-2d/corpus/live/r29-focus-critic/project/`. Command: `godot --headless --path <scratch-project> --script res://focus_probe.gd`; exit 0, Godot 4.7.2. Stdout:

```text
FOCUSED owner=target
FOCUSED receipts=["target"]
OTHER owner=other
OTHER receipts=["other"]
NONE owner=null
NONE receipts=[]
MANUAL pressed.emit receipts=["target"]
```

Probe wiring: two in-tree Buttons, each signal connected to the same receipt collector with its own identity; each arm sends one `ui_accept` press and release and waits one process frame. The focused-target arm verified target owner and collected target; other-focus verified other owner and collected other. The no-focus arm called `release_focus()` on both, awaited a frame, confirmed null owner, then sent identical input; no receipt. Thus input action follows another focus owner rather than firing the target independent of focus. A direct `pressed.emit()` afterward did produce target receipt, isolating manual signal invocation from GUI input routing.

## Falsification / caveats
- Root/default focus: no assumption that the initial default is unfocused; probe explicitly establishes and prints focus owner for every arm. A default or auto-focused control would invalidate a naive “never grab focus” control, so explicit null-owner assertion is necessary.
- Other owners: tested a second Button as focus owner; `ui_accept` triggered it, not the target. This also shows that absence of target receipt alone is insufficient unless the active owner is recorded.
- Manual signal versus input: input and direct signal emission were separate. Manual `pressed.emit()` triggers connected callback without focus and is not evidence that `ui_accept` was routed.
- No-focus setup: verified null owner immediately before input; no setup error was used as an outcome. The no-focus observation is zero receipts, not a fixture/tree failure.
- Wrong mechanism: a Button with `focus_mode=FOCUS_NONE` or a different action mapping would be weaker controls; this probe kept ordinary Button defaults and exact `ui_accept` action. It does not test pointer hit-testing or window-level user focus.

Recommendation: retain the proposed calibration distinction if paired in the assigned fixture/runner: explicitly assert target focus for positive, then verify null owner before no-focus input and expect zero; do not describe all Buttons as requiring focus to exist or claim general production behavior. This critic evidence is not the named verifier and does not itself admit a change.
