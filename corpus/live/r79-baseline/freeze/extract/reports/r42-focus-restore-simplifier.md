# Round 42 focus-restore simplifier (read-only)

## Direct scratch result

On real Godot 4.7.2, an isolated copy of the connected HSlider fixture was run with a dedicated `--r42` path. The seven fresh parsed actions were each followed by a process frame. Before every event, the script asserted the GUI focus owner and slider focus bit; after every event it checked numeric value, the connected signal receipt history, and label.

Observed edges:

| edge | owner before | action | value | receipts | label |
|---:|---|---|---:|---|---|
| 0 | slider | right press | 6 | `[6]` | Value 6 |
| 1 | Button | right press | 6 | `[6]` | Value 6 |
| 2 | Button | right release | 6 | `[6]` | Value 6 |
| 3 | slider | left press | 5 | `[6, 5]` | Value 5 |
| 4 | slider | left release | 5 | `[6, 5]` | Value 5 |
| 5 | slider | left press | 4 | `[6, 5, 4]` | Value 4 |
| 6 | slider | left release | 4 | `[6, 5, 4]` | Value 4 |

The terminal result was `PASS R42 values=6,6,6,5,5,4,4 receipts=6,5,4`, exit 0. Thus the declared hypothesis held in this direct scratch. This demonstrates the proposed narrow synthetic focus-restoration sequence only; it does not establish physical keyboard, OS repeat, timing, rendered/pointer UI, accessibility, or production behavior.

## Minimum dedicated-mode proposal

Add a single `--r42` branch in the existing slider fixture, ahead of existing `--repeat-right` modes, leaving those modes and default paths intact. Reuse the current setup, `_action`, connected `value_changed` consumer, and existing Button pattern. The dedicated branch should contain the seven ordered edges, focus handoff immediately before edge 1, slider restoration immediately before edge 3, owner assertion before each dispatch, and expected state assertion after each frame. Use one clear terminal PASS only after all seven edge checks. Do not alter the old mode's action sequences or expected values. Fixture edit appears justified by the successful isolated causal scratch, but I made no fixture or battery edits (executor ownership).

Run the scratch first and retain its stdout/exit as direct evidence. Parent/verifier should decide battery integration and baseline classification; this report makes no full-suite or regression claim.
