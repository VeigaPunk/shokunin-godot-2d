# Round 44 second-restoration critic — focus and receipt chronology

**Verdict: direct scratch supports the declared nine-edge hypothesis; no chronology/focus falsification found.**

I copied the prior r43 critic scratch into `.shokunin/game-dev-2d/corpus/live/r44-second-restore-critic/`, changed only that scratch script, and ran real Godot `4.7.2.stable.arch_linux.ed1daf0bf` with `--headless --path ... --script slider_adjust.gd -- --repeat-right --focus-restore`. Exit was 0.

The first seven parsed `InputEventAction`s preserve r43's observed trace. Before edge 7, the script calls `slider.grab_focus()`, awaits a frame, then checks both `gui_get_focus_owner() == slider` and `slider.has_focus()` before dispatching the fresh left press; edge 8 likewise checks slider ownership before the release. Each fresh action is followed by `process_frame`. After every edge, the script checks the current HSlider value, complete cumulative `value_changed` receipt prefix, and Label. Results were values `6,6,6,5,5,5,5,4,4`, receipts `[6]`, `[6]`, `[6]`, `[6,5]` through edge 6, then `[6,5,4]` at edges 7 and 8; Labels track `Value 6`, `Value 5`, and finally `Value 4`. Terminal positive exit occurs only after all nine checks.

This is adequate evidence for a second restoration after two Button focus handoffs: a new left press adjusts the slider once focus is restored, adding exactly one receipt, and its release adds none. It does not prove which internal control consumed unchanged edges; it is synthetic parsed events plus frames, not OS repeat, physical timing, rendered/pointer UI, accessibility, or production behavior. No in-tree, engine/editor, or seeded fixture files were changed. Scratch: `.shokunin/game-dev-2d/corpus/live/r44-second-restore-critic/`.
