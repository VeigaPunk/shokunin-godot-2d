# Round 36 HSlider input semantics scout

## Result: measured positive; no HOLD

Scratch: `.shokunin/game-dev-2d/corpus/live/r36-measure-20261013T024116/measure_slider.gd`, run with `/usr/bin/godot --headless --path .shokunin/game-dev-2d/corpus/live/r36-measure-20261013T024116 --script measure_slider.gd` (Godot `4.7.2.stable.arch_linux.ed1daf0bf`). The scratch creates a focused `HSlider` with min=0, max=10, step=1, initial value=5. It uses fresh `InputEventAction` instances for each press/release and waits one process frame after each event. No calls to set the slider value or manually emit signals.

Connected case actual trace:
```
CASE connected=true BEFORE focus=true value=5.0 label=Value 5 rec=[]
RIGHT_PRESS value=6.0 label=Value 6 rec=[6.0]
RIGHT_RELEASE value=6.0 label=Value 6 rec=[6.0]
LEFT_PRESS value=5.0 label=Value 5 rec=[6.0, 5.0]
LEFT_RELEASE value=5.0 label=Value 5 rec=[6.0, 5.0]
```
Disconnected paired control, same initial slider and same two press/release actions:
```
CASE connected=false BEFORE focus=true value=5.0 label=Value 5 rec=[]
RIGHT_PRESS value=6.0 label=Value 5 rec=[]
RIGHT_RELEASE value=6.0 label=Value 5 rec=[]
LEFT_PRESS value=5.0 label=Value 5 rec=[]
LEFT_RELEASE value=5.0 label=Value 5 rec=[]
```

Thus synthetic action events do drive the focused Range in Godot 4.7.2: `ui_right` changes 5→6 once and `ui_left` changes 6→5 once. Release causes no duplicate. Connected `value_changed(float)` receipts are ordered `[6.0, 5.0]`; label reflects each signal-driven transition. With no connection, numeric value still transitions identically but receipts remain empty and label stays at initial `Value 5`. This supports the proposed causal positive and absent-consumer negative fixture, subject to executor/verifier replay. Important implementation detail: `Input.action_press/release()` alone did not reach the focused HSlider in SceneTree scratch; `Input.parse_input_event(InputEventAction)` did. A first probe accidentally reused event object in one frame and emitted Godot's warning; corrected by using fresh event per press/release and a frame between. Do not reuse those early probe traces as evidence.

Scope: headless synthetic focused input only; this does not establish physical keyboard timing, pointer interaction, rendered GUI behavior, accessibility, production behavior, or general HSlider coverage.
