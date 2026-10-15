# Round 43 second-loss simplifier (read-only)

## Direct scratch evidence

Ran a dedicated scratch copy with system Godot 4.7.2 (`4.7.2.stable.arch_linux.ed1daf0bf`) before proposing any fixture change. It used a connected in-tree HSlider (min 0, max 10, step 1, initial 5), a Label updated by the connected `value_changed` callback, a focusable Button, seven fresh parsed `InputEventAction`s, and one process frame after each event. GUI owner was checked before every action; value, receipt history, and Label were checked after every frame.

Observed: slider first right press → `6 / [6] / Value 6`; Button second right press and release each held `6 / [6] / Value 6`; restored slider first left press → `5 / [6,5] / Value 5`, release held; Button regained focus before second left press, and the press and release each held `5 / [6,5] / Value 5`. The terminal `PASS R43 values=6,6,6,5,5,5,5 receipts=6,5` appeared only after all seven per-edge assertions; the process then exited **2** via the deliberate expected-negative terminal. Thus direct scratch behavior matches the claim.

Scratch: `.shokunin/game-dev-2d/corpus/live/r43-second-loss-simplifier/scratch/`. No fixture, battery, seeded corpus, engine/editor source, or another worker's files were edited.

## Minimum dedicated-mode proposal

Add one isolated `--repeat-right --focus-second-loss` branch in `slider_adjust.gd`, adjacent to (not mutating) the existing focus-restore branch. Reuse setup, `_action`, signal consumer, and Button pattern. Encode the existing seven events; transfer to Button before edge 1, restore slider before edge 3, then transfer to Button again before edge 5. Assert the expected owner before each event and value/receipts/Label after each frame. Expected values `[6,6,6,5,5,5,5]`, receipt counts `[1,1,1,2,2,2,2]`, final receipts `[6,5]`. Emit a distinct terminal PASS only after every edge, then deliberately `quit(2)` (with expected-negative classifier semantics after verified checks, as in existing handoff precedent). Do not alter old modes or their expectations.

A single ordinary expected-negative battery row is causally justified by this direct scratch, conditional on the executor integrating the dedicated mode and the existing classifier treating exit 2 as the expected terminal. The prior r42 positive mode should remain unchanged so it provides the paired final `4 / [6,5,4]` outcome. I made no fixture/battery edit and make no full-suite or regression claim.

## Bounds

This evidence concerns headless synthetic parsed actions plus process frames in Godot 4.7.2. It does not establish OS auto-repeat, physical keyboard/timing, rendered or pointer UI, accessibility, production behavior, internal consumption of unchanged edges, or generic HSlider behavior.
