# Round 42 regression scout — focus restoration and battery caveats

Read-only regression scout; no tracked fixture/runner or seeded-control edits. Direct scratch only at `corpus/live/r42-regression-scout/`, Godot `4.7.2.stable.arch_linux.ed1daf0bf`.

## First scratch result

Created connected in-tree HSlider (min 0, max 10, step 1, initial 5), separate focusable in-tree Button, and Label. On every edge the probe checked GUI focus owner immediately before dispatch and again after one process frame, and asserted value, accumulated `value_changed` receipts, and callback-driven Label after the frame. The sequence was: focused right press; Button focus handoff; right press and right release while Button owned focus; restore slider focus; left press/release/press/release while slider owned focus. `timeout 15s godot --headless --path <absolute-scratch-path> --script res://r42_probe.gd` completed in 0.61s, exit 0.

Raw output:
```
EDGE ui_right press focus_ok=true value=6.0 receipts=[6.0] label=Value 6
EDGE ui_right press focus_ok=true value=6.0 receipts=[6.0] label=Value 6
EDGE ui_right release focus_ok=true value=6.0 receipts=[6.0] label=Value 6
EDGE ui_left press focus_ok=true value=5.0 receipts=[6.0, 5.0] label=Value 5
EDGE ui_left release focus_ok=true value=5.0 receipts=[6.0, 5.0] label=Value 5
EDGE ui_left press focus_ok=true value=4.0 receipts=[6.0, 5.0, 4.0] label=Value 4
EDGE ui_left release focus_ok=true value=4.0 receipts=[6.0, 5.0, 4.0] label=Value 4
R42 PASS values=[6.0, 6.0, 6.0, 5.0, 5.0, 4.0, 4.0] receipts=[6.0, 5.0, 4.0] label=Value 4
```

The scratch supports the stated hypothesis: first focused adjustment to 6/[6]/Value 6; handoff keeps 6/[6]/Value 6; after slider focus restoration left presses adjust to 5 then 4, with receipts `[6,5,4]`, and releases hold. No HOLD condition observed. This confirms only a manually constructed synthetic event/frame sequence; it does not independently prove which Control consumed each event beyond owner checks and state results.

## Prior regressions and boundary reminders

- r39's focused seven-edge history was 6,7,7,6,6,5,5 with receipts `[6,7,6,5]`; r40 added a seven-edge no-focus control; r41 measured a handoff after the first right press, with the remaining six events holding 6/[6]/Value 6. None tested restored focus followed by renewed left adjustment. Their reports are read-only context, not this round's evidence.
- Preserve battery/export/fault boundaries: export launch and export runs have separate bounds (historically 5s startup and 60s export); relative export target/path behavior has known failures, so slider evidence says nothing about export readiness or portability. Timeout evidence is bounded to tested direct-child timeout/kill/reap behavior, not descendant cleanup or generic timeout safety. Fault-injection outer PASS can include intentionally failing inner hang/timeout and unrelated-error classifications; do not call those inner checks clean PASS. Expected-negative slider classification must require the intended diagnostic and exit code, not exit 2 alone.
- This scout did not run the fixture battery, verify prior tuple rows, or establish round admission. No engine/editor or seeded control changes, commit, push, or merge.

Scope: Godot 4.7.2 headless, synthetic parsed actions and process-frame yields only; not OS auto-repeat, physical keyboard timing, rendered/pointer behavior, accessibility, production, or generic HSlider behavior.
