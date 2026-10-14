# Round 41 regression scout — mid-sequence focus handoff

## Scope and direct Godot scratch measurement

Read-only review of prior r37/r39/r40 evidence and current battery/export/fault boundaries, plus a scratch-only direct probe. Copied r40 scratch project to `.shokunin/game-dev-2d/corpus/live/r41-regression-scout/`; added only `r41_probe.gd`. No tracked fixture/runner, engine/editor, or seeded control was edited. Godot: `4.7.2.stable.arch_linux.ed1daf0bf`.

The probe creates an in-tree HSlider (0..10, step 1, initial 5) and a separate in-tree focusable Button, connects `value_changed` to a receipt list and Label, focuses the slider, then sends these fresh parsed `InputEventAction` events with one process frame each: ui_right press, ui_right press, ui_right release, ui_left press, ui_left release, ui_left press, ui_left release. Before edge 0, slider was focus owner. Immediately before edge 1, Button `grab_focus()` transferred focus; probe confirmed owner was Button and `slider.has_focus()` false. It checked that same external focus ownership before each remaining edge.

Bounded invocation (`timeout 15s godot --headless --path <absolute-scratch-path> --script res://r41_probe.gd`) completed in the bound with exit 2. Raw output:
```
HANDOFF owner_other=true slider_has_focus=false
R41_HANDOFF values=6,[6],[6],[6],[6],[6],[6] receipts=[6.0] label=Value 6 owner_other=true
ERROR: R41 HANDOFF EXPECTED-NEGATIVE: expected focus-dependent adjustment after transfer
```
The first event alone changed value 5→6, emitted receipt `[6]`, and set Label `Value 6`. Every remaining one of the six events/frames preserved value 6, receipts `[6]`, Label `Value 6`, and focus on the other Control. The distinct expected-negative exit 2 occurred only after all seven checks. Thus the requested initial scratch behavior is observed; no HOLD for differing focus transfer/event results.

The first unbounded attempt was terminated by the parent as >3-minute hung telemetry. It is not evidence. I retried with the requested 15-second bound and absolute project path; the bounded run above is the valid scratch result. An earlier script draft had a typed-array assignment error and exit 143; corrected scratch was rerun and only the corrected bounded run is cited as evidence.

## Prior evidence and caveats

- r37 measured the shorter no-focus sequence with no owner, no value change, no receipts, Label `Value 5`; it does not establish mid-sequence handoff.
- r39 measured deliberate focused seven-edge history (6,7,7,6,6,5,5; receipts [6,7,6,5]); it did not test handoff.
- r40 measured focused seven-edge sequence and seven-edge no-focus sequence; it did not test handoff. Its prior verification includes a scratch typed-array failure and early misclassified replay as adverse telemetry, not candidate proof.
- Battery fault-injection outer PASS can contain deliberately failing inner timeout and unrelated-error cases. Timeout claims are limited to tested direct-child behavior; not generic descendant cleanup. Export readiness has known relative-path failures (including separate export-launch probe); no export inference follows from this UI probe.

This report is a read-only scout and does not modify the slider fixture/runner or establish battery admission. Evidence is limited to synthetic parsed events and process frames in Godot 4.7.2 headless; not OS auto-repeat, physical timing, rendered/pointer UI, accessibility, production, or a generic HSlider guarantee. No commit, push, or merge.
