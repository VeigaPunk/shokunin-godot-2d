# Round 46 executor — mid-run signal disconnect

## Causal scratch
Godot reported `4.7.2.stable.arch_linux.ed1daf0bf`. An isolated project in `corpus/live/r46-mid-disconnect-scratch/` ran the in-tree-style HSlider (min 0, max 10, step 1, initial 5), with Button focus transfers matching r44 at edges 1, 3, 5, and 7. Each of nine actions was a fresh `InputEventAction` sent through `Input.parse_input_event`, followed by one `process_frame`; focus owner was asserted before every edge and value/receipt/Label after each. At edge 0 the callback was still connected and observed value 6, receipts `[6]`, Label `Value 6`, then disconnected. Edges 1–8 maintained cumulative receipts `[6]` and Label `Value 6` while numeric values were 6,6,5,5,5,5,4,4. The dedicated marker appeared after all nine checks and process exited 2 as expected.

Paired scratch controls: connected r44 path exited 0 with values `6,6,6,5,5,5,5,4,4`, receipts `[6,5,4]`, Labels `Value 6,Value 5,Value 4`; disconnect-at-start r45 exited 2 with the same numeric values, empty receipts, Label `Value 5`. Mid-disconnect is distinct.

## Implementation and replay
After scratch confirmation, added one dedicated `--disconnect-after-first` branch guarded by `--repeat-right` and `--second-focus-restore`, before existing r45/r44 branches. It retains all nine owner-before-edge and state-after-edge assertions, checks `[6]`/`Value 6` on first edge, disconnects only then, and requires `[6]`/`Value 6` on remaining eight edges. It ends with unique marker and expected-negative `push_error`, exit 2 only after all checks. Added one runner row and exact diagnostic classifier. Existing fixture branches and rows were preserved.

Ordinary runner replay exited 0: **60/60 PASS**, including the new negative row (expected/actual exit 2, exact signature `SLIDER MID-DISCONNECT ASSERTION FAILED: expected cumulative callback history to stay [6]`). It reports the final marker `SLIDER_MID_DISCONNECT values=6,6,6,5,5,5,5,4,4 receipts=[6] Label=Value 6`. Against r45 verifier raw evidence, the 59 prior ordinary tuples are unchanged; the 11 existing opt-in/fault rows were not run in this ordinary replay. No broad full battery, sabotage, tracked-independent verifier, commit or push was performed here; these remain parent/non-author-verifier work.

## Axis and limits
Calibration evidence improved: same nine-edge numeric/focus history with callback history deliberately interrupted after the first adjustment. Depth and coverage unchanged as axes; no observed harm in this finite replay. Scope is headless Godot 4.7.2 and synthetic parsed events+frames only, not OS repeat, physical timing/input, rendered/pointer UI, accessibility, production, generic sliders, or internal consumers of unchanged edges.
