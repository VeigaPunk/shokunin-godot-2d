# Round 20 top-edge critic

## Scope and conclusion
Read-only causal review of the proposed top-bound Camera2D pair. I found no falsification of the top contrast in direct Godot 4.7.2 headless probes. The positive and far-top control execute the same movement and assertion path; the bound value and CLI mode are the intentional contrast.

## Assertions and expected center
`camera_limit.gd` sets `camera.limit_top = -1000` for the top case, moves the parent target from `(0, 0)` to `(0, -2000)`, disables position smoothing, calls `force_update_scroll()`, and checks current-camera status and movement before evaluating the clamp. For the top case, expected center is `top_boundary + visible_viewport_height / 2`; with the scratch viewport height 64 this is `-968`. The same predicate also requires center y >= -1000 - 0.01, center movement >100, and center-target distance >1.

## Reproduction evidence
Scratch project: `.shokunin/game-dev-2d/corpus/live/r20-top-critic-scratch` (copied fixture, 64x64 viewport; no seeded files changed).

- `godot --headless --path . --script res://camera_limit.gd -- --top-bound` — exit 0, `PASS ... center_at_viewport_adjusted_clamp=true center_differs_from_target=true ... top_test=true`.
- `godot --headless --path . --script res://camera_limit.gd -- --far-top-bound` — exit 2, prints `OBSERVED ... center=(0.00,-2000.00) boundary=-1000.00 expected_clamp=-968.00 target=(0.00,-2000.00) top_test=true`, then the same assertion emits `camera limit assertion failed: expected active center within top boundary and distinct from target`. This is a real intended negative, not camera-not-current or target-did-not-move setup failure.

The control does not technically isolate only a limit property in the entire fixture: the mode/target axis is also selected by `top_test`, but both top positive and top control share `top_test=true` and target `(0,-2000)`; among that pair, only `limit_top` differs (`-1000` vs `-100000`). `limit_right=1000` is unchanged and x stays zero, so it does not induce the observed y failure. On the positive, both `center.y=-968` expected clamp and the top-bound predicate pass; on the control, `center.y=-2000` violates them as expected. This is a credible causal contrast for the top limit.

## Caveats / telemetry
- The test verifies Camera2D screen-center coordinates, not rendered pixels, production scenes, or non-top edges.
- I did not run the full battery or mutate tracked files. Parent reported that its baseline with an explicit relative `--runs` path hit `StopIteration` at the export diagnostic probe (`marker_line=next(...savepack...)` in `run_battery.py:245`); treat that as separate adverse telemetry, not a top-coverage result or a reason to fold in an export fix.
- No engine/editor source, seeded controls, or runner files were edited.
