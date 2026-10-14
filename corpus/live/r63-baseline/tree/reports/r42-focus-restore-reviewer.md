# Round 42 independent focus-restoration scratch review

## Result

Direct scratch check on Godot `4.7.2.stable.arch_linux.ed1daf0bf`: **the predicted focus handoff and restoration behavior occurred**. Starting with the in-tree HSlider focused at value 5, the first fresh parsed `ui_right` press and frame yielded value 6, receipt `[6.0]`, and Label `Value 6`. Before the second right press, a separate in-tree Button took focus; I checked focus ownership before that edge and the subsequent right release. Both edges held value 6, receipt `[6.0]`, and Label `Value 6`. Before the first left press, I restored HSlider focus and checked owner before that edge and each remaining left release/press/release. The four remaining edges yielded/held `5,5,4,4`; receipts progressed `[6.0,5.0]` then `[6.0,5.0,4.0]`; the Label tracked `Value 5` then `Value 4`. Focus owner was asserted before **every** edge, and value/receipts/Label were checked after **every** edge.

Raw command: `godot --headless --path .shokunin/game-dev-2d/corpus/live/r42-focus-restore-reviewer-scratch --script slider_adjust.gd -- --repeat-right --focus-restore`

Exit code `0`; terminal output: `SLIDER_FOCUS_RESTORE values=6,6,6,5,5,4,4 receipts=[6.0, 5.0, 4.0] label=Value 4 focus_owner_slider=true`.

## Scratch and bounds

Scratch: `.shokunin/game-dev-2d/corpus/live/r42-focus-restore-reviewer-scratch/` (`project.godot`, `slider_adjust.gd`), copied from the in-tree fixture into my own scratch and extended only with this focus-restore branch. SHA256 of scratch script: `9dd1aadf5b12dea901cd8d31aebecffb0a60d1192b88fc44b3b427913b002267`. No fixture, runner, seeded source, engine/editor source, or other agent files were changed. This tests synthetic parsed actions plus process frames only; it does not establish OS auto-repeat, physical keyboard/timing, rendered/pointer UI, accessibility, production behavior, or a generic slider guarantee.
