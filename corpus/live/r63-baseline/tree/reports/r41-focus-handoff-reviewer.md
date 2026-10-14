# Round 41 independent focus-handoff scratch review

## Result

Direct scratch check on Godot `4.7.2.stable.arch_linux.ed1daf0bf`: **the requested focus handoff behaved as predicted**. The first fresh parsed `ui_right` press plus a process frame, while the in-tree HSlider owned GUI focus, changed value `5→6`, emitted receipt `[6.0]`, and updated the connected Label to `Value 6`. I then called `grab_focus()` on a separate in-tree focusable `Button`, awaited a frame, and asserted the GUI focus owner was that Button and `slider.has_focus()` was false. Each of the six remaining specified fresh action edges plus its frame preserved value `6`, receipts `[6.0]`, and Label `Value 6`, with the Button still owning focus before every edge. The expected-negative diagnostic occurred only after all seven checks, with process exit 2.

Raw command: `godot --headless --path .shokunin/game-dev-2d/corpus/live/r41-focus-handoff-reviewer-scratch --script .shokunin/game-dev-2d/corpus/live/r41-focus-handoff-reviewer-scratch/slider_adjust.gd -- --repeat-right --focus-handoff`

Terminal output included `HANDOFF values=6,6,6,6,6,6,6 receipts=[6.0] label=Value 6 focus_owner=@Button...`, followed by the intentional `SLIDER HANDOFF ASSERTION FAILED` diagnostic; exit code `2` is expected, not a runtime error. Actual UI event focus routing for this synthetic headless test supports the proposed one-row focus-loss calibration control.

## Scratch and bounds

Scratch: `.shokunin/game-dev-2d/corpus/live/r41-focus-handoff-reviewer-scratch/` (`project.godot`, `slider_adjust.gd`). Derived from the existing fixture into my own scratch only; added a focusable Button and a `--focus-handoff` branch. No fixture, runner, seeded source, engine/editor source, or other agent files were changed. This checks synthetic parsed events plus process frames only; it does not establish OS auto-repeat, physical keyboard/timing, rendered/pointer UI, accessibility, production behavior, or a generic slider guarantee.

SHA256 scratch script: `aff0526ff5c95f0ce442909c71093493db2195fd13d6fe7f47d87661b53c04e9`
