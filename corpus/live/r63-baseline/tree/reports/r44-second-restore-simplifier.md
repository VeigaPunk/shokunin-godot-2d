# Round 44 second-restore simplifier (read-only)

## Direct Godot scratch result

Ran a dedicated scratch copy under `.shokunin/game-dev-2d/corpus/live/r44-second-restore-executor-scratch/` using system Godot 4.7.2 (`4.7.2.stable.arch_linux.ed1daf0bf`). It copied the current in-tree HSlider fixture and added only an untracked scratch branch. The connected HSlider (min 0, max 10, step 1, initial 5), connected value_changed receipt/Label, focusable Button, nine fresh parsed actions and a process frame per action were used. Owner was asserted before every edge; value, complete receipt history, and Label were checked after every edge.

Observed exactly the proposed history: `6,6,6,5,5,5,5,4,4`, receipts `[6,5,4]`, terminal `Label=Value 4`. Slider owned edges 0,3,4,7; Button owned 1,2,5,6. The terminal PASS was printed only after all nine checks and Godot exited 0. This confirms the stated narrow behavioral hypothesis in real Godot 4.7.2.

## Minimum change proposal

Add a distinct, read-only-mode-preserving branch in `slider_adjust.gd`, adjacent to the second-focus-loss branch. Reuse setup, action parser, callback, and Button; replay its seven existing edges, then restore slider focus before edges 7 and 8 (third left press/release). Keep explicit owner assertions before each edge and state/receipts/Label checks after every frame. Expected values `[6,6,6,5,5,5,5,4,4]`, receipt counts `[1,1,1,2,2,2,2,3,3]`, final receipts `[6,5,4]`. Print terminal PASS and exit 0 only after all nine assertions. Leave all existing branch behavior and expectations intact.

One new ordinary positive battery row is causally justified if integrated with that isolated mode. This scratch does not establish suite/regression behavior or verifier admission.

## Bounds

Headless synthetic parsed actions plus process frames only. No claims about OS repeat, physical keyboard/timing, rendered/pointer UI, accessibility, production, internal consumption of unchanged edges, or generic HSlider behavior. No tracked fixture/battery, seeded corpus, engine/editor, or other worker files were edited.
