# Round 47 independent reconnect scratch review

Independent Godot 4.7.2 scratch only at `corpus/live/r47-reconnect-reviewer/`; copied the r46 reviewer project and instrumented the nine-edge branch locally. No tracked fixture/runner, engine/editor source, or seeded fixture was edited.

Command: `timeout 20s godot --headless --path . --script slider_adjust.gd -- --repeat-right --second-focus-restore --reconnect-after-first-left`

Result: exit 0 with a distinct PASS marker only after nine parsed events and frames. Before every event, the expected GUI focus owner was asserted (slider, Button, Button, slider, slider, Button, Button, slider, slider). After every frame, numeric value, cumulative callback receipts, and Label were checked. The script also asserted callback state connected at edge0 before disconnection, disconnected after edge0, disconnected before edge3 reconnect, connected immediately after reconnect, and connected at completion.

| edge | event | owner | value | receipts | Label | callback connected after edge |
|---:|---|---|---:|---|---|---|
| 0 | right press | slider | 6 | [6] | Value 6 | no |
| 1 | right press | Button | 6 | [6] | Value 6 | no |
| 2 | right release | Button | 6 | [6] | Value 6 | no |
| 3 | left press | slider | 5 | [6] | Value 6 | yes |
| 4 | left release | slider | 5 | [6] | Value 6 | yes |
| 5 | left press | Button | 5 | [6] | Value 6 | yes |
| 6 | left release | Button | 5 | [6] | Value 6 | yes |
| 7 | left press | slider | 4 | [6,4] | Value 4 | yes |
| 8 | left release | slider | 4 | [6,4] | Value 4 | yes |

Observed numeric sequence `6,6,6,5,5,5,5,4,4`, receipts `[6]` through edge6 then `[6,4]`, and final Label `Value 4`. This independently supports the narrowly scoped synthetic parsed-input/frame calibration claim. It does not establish OS repeat, physical input/timing, rendered/pointer UI, accessibility, production behavior, or internal handling of no-change events.
