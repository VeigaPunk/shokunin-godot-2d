# Round 20 simplifier review

Read the Round 20 declaration in `.shokunin/game-dev-2d/LOG.md`, `/tmp/mission-game-dev-2d-standing.md`, and the current `camera_limit.gd` / `run_battery.py` diff. This was read-only review; I made no fixture or runner edits and ran no tests.

## Recommendation

Keep the shared directional fixture/assertion structure in the current diff. It is the smallest clear extension I see that preserves the existing right-edge positive and far-bound control without duplicating the core assertions: `top_test` selects target direction, boundary, viewport dimension, expected clamp coordinate, and boundary predicate, while the same movement/current/separation checks and failure path serve both directions. The separate `camera_top_limit` and `camera_far_top_bound` CASES add the two desired observations, and the far-top case retains the same runtime diagnostic classifier pattern as the right-edge control.

The existing right-edge rows remain behaviorally represented: their args still select rightward movement; right boundary remains `1000`; expected x clamp remains `1000 - viewport_width / 2`; far-bound changes the right limit; and its expected diagnostic text is unchanged. The stdout PASS line now has extra fields, but the old positive signature remains an exact substring, so the existing classifier signature should still match.

Top-edge positive checks more than a boundary inequality: it asserts `center.y == -1000 + viewport_height / 2` within tolerance, center movement, and separation from the target moved to `(0, -2000)`. The far-top control deliberately moves the top limit to `-100000`, making that same authored-bound expectation fail while target movement/setup remain intact.

No simplification recommendation requiring code changes. The duplicated-looking per-axis conditional expressions are limited to selecting axis-specific geometry; extracting helpers or duplicating a whole top fixture would add complexity or repeated assertions without a demonstrated gain.
