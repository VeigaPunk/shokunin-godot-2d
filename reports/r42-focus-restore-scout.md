# Round 42 focus-restoration scout

## Result
The declared seven-edge hypothesis held in a real Godot 4.7.2 headless scratch run. Exit 0. I used a disposable copy under `corpus/live/r42-focus-restore-scout/scratch`; no seeded/in-tree fixture source was changed.

Connected in-tree HSlider min=0 max=10 step=1, initial=5, signal-connected Label; a separate focusable Button was added. For each edge, I checked GUI focus owner and slider.has_focus() immediately before dispatch, parsed a fresh InputEventAction, awaited one process frame, then checked value, full receipt history, and Label. Handoff to Button occurred before edge 1; slider focus was explicitly restored before edge 3.

| Edge | Action | Owner before dispatch | Value after frame | Receipts | Label |
|---:|---|---|---:|---|---|
| 0 | right press | HSlider | 6 | [6] | Value 6 |
| 1 | right press | Button | 6 | [6] | Value 6 |
| 2 | right release | Button | 6 | [6] | Value 6 |
| 3 | left press | HSlider (restored) | 5 | [6,5] | Value 5 |
| 4 | left release | HSlider | 5 | [6,5] | Value 5 |
| 5 | left press | HSlider | 4 | [6,5,4] | Value 4 |
| 6 | left release | HSlider | 4 | [6,5,4] | Value 4 |

Raw scratch stdout/stderr: `.shokunin/game-dev-2d/corpus/live/r42-focus-restore-scout/godot.log`; disposable probe script: `.../scratch/slider_adjust.gd`. The first scratch assertion was incorrectly written to expect a receipt on the unchanged second edge; observed [6] disproved that local assertion, which I corrected to the specified history before the successful run. This was probe expectation setup, not a hypothesis failure.

Scope: synthetic parsed actions with process frames only; not OS key repeat, physical timing, rendered/pointer UI, accessibility, production, or a generic slider guarantee.
