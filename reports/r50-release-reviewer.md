# Round 50 independent direct scratch — fresh release after late reconnect press

Reviewer role: independent bounded Godot scratch; no tracked fixture/runner edits. Unique scratch: `.shokunin/game-dev-2d/corpus/live/r50-release-reviewer-unique-20261013/`, copied from the r49 reviewer project and extended only there. Engine: Godot `4.7.2.stable.arch_linux.ed1daf0bf`.

## Commands and observations

- `godot --headless --path .shokunin/game-dev-2d/corpus/live/r50-release-reviewer-unique-20261013 --script slider_adjust.gd -- --repeat-right --second-focus-restore --release-after-late-reconnect-press` exited **2** after exactly eleven edge checks, with unique diagnostic `SLIDER R50 RELEASE ASSERTION FAILED: expected no value_changed receipt on fresh ui_left release after eleven checks`.
- Each edge asserted GUI focus owner and slider focus before dispatch, callback connection state before dispatch, and numeric value, full receipt array, and Label after one process frame. Edge owner sequence: slider, Button, Button, slider, slider, Button, Button, slider, slider, slider, slider. Callback connection was true at edge0, false at edges1–7, true at edges8–10. The edge0 callback receipt was `[6]`, then callback disconnected. It reconnected after edge7, following numeric4/[6]/Value6. Edge8 release retained numeric4/[6]/Value6. Fresh edge9 press produced numeric3/[6,3]/Value3. Fresh edge10 release remained numeric3/[6,3]/Value3. Thus the hypothesis was observed: no new receipt on the release.
- Paired ten-edge positive command on the unchanged scratch baseline (`--repeat-right --second-focus-restore --press-after-late-reconnect`) exited **0** with ten checks, values `6,6,6,5,5,5,5,4,4,3`, receipts `[6,3]`, Label `Value 3`.

## Finding and limits

Direct independent evidence supports the round-50 release hypothesis on Godot 4.7.2 for headless synthetic parsed actions and process frames: after the late-reconnect press adjusts from 4 to 3, the following release causes no adjustment or `value_changed` receipt. This does not establish OS key repeat, physical input or timing, rendered/pointer behavior, accessibility, production behavior, or internal consumer behavior beyond the observed Label and receipts. No tracked fixture or runner was edited.
