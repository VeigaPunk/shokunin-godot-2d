# Round 46 independent mid-disconnect scratch review

Independent Godot 4.7.2 scratch only; no tracked fixture/runner edits. Copied r45 standalone baseline into `corpus/live/r46-mid-disconnect-reviewer/`, added `--disconnect-after-first`, connected callback for initialization/edge0, then disconnected immediately after edge0 frame. Ran with bounded `timeout 20s`:

`godot --headless --path .shokunin/game-dev-2d/corpus/live/r46-mid-disconnect-reviewer --script slider_adjust.gd -- --repeat-right --second-focus-restore --disconnect-after-first`

Exit 2 is the expected terminal negative after nine assertions. Every action was fresh, one parsed action and frame per edge; focus owner was checked before each edge. Observed:

| edge | action | focus owner | value | cumulative receipts | Label |
|---:|---|---|---:|---|---|
| 0 | right press | slider | 6 | [6] | Value 6 |
| 1 | right press | Button | 6 | [6] | Value 6 |
| 2 | right release | Button | 6 | [6] | Value 6 |
| 3 | left press | slider | 5 | [6] | Value 6 |
| 4 | left release | slider | 5 | [6] | Value 6 |
| 5 | left press | Button | 5 | [6] | Value 6 |
| 6 | left release | Button | 5 | [6] | Value 6 |
| 7 | left press | slider | 4 | [6] | Value 6 |
| 8 | left release | slider | 4 | [6] | Value 6 |

Final output marker confirms values `6,6,6,5,5,5,5,4,4`, receipts `[6]`, Label `Value 6`; diagnostic was emitted only after all nine checks and process exited 2. Initial scratch attempt hit a GDScript typed-array assignment error before running; corrected the scratch-only array construction and reran successfully. No engine/editor/seeded or tracked files modified. This supports the narrow synthetic parsed-input calibration claim only.
