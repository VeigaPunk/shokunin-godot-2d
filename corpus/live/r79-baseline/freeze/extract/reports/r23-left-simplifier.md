# Round 23 left-edge simplifier review

Read-only review of `corpus/fixtures/camera_limit.gd` and `corpus/fixtures/run_battery.py`.

## Minimal compatible change

Keep one fixture and its existing active-center assertion. Add a left-test selector that is also enabled by `--far-left-bound`; set `camera.limit_left = -1000` (negative far-bound override `-100000`), move the parent target to `(-2000, 0)`, and compare the center's x coordinate against `limit_left + viewport_width / 2`. The intended positive center is therefore -968 for the fixture's 64px-wide viewport. The far-left control should use the identical assertion and fail because the center follows the target rather than being viewport-adjusted to the boundary.

To avoid cloning the right/top branch, reduce the selected coordinate, authored boundary, viewport half-size, and direction of the within-boundary comparison to scalar values, then share the existing checks (`at_expected_clamp`, center advanced, center distinct from target). Left and right use x; top uses y. Keep direction-specific labels in failure output so the control's expected assertion remains identifiable. This is a narrow extension, not a need to refactor the fixture into a generalized camera framework.

In `run_battery.py`, add exactly the paired ordinary rows for left positive and far-left negative using the existing exit/signature conventions. Extend the expected assertion-error mapping with the left wording. Preserve all existing row order/outcomes; do not alter unrelated camera cases or controls.

## Review risks / evidence needed

- Check that the left fixture establishes camera current status and that the target moved before interpreting the clamp; those are existing setup guards and should remain.
- `center.x >= -1000 + half_width` alone is not sufficient: retain equality-to-expected-clamp and center/target separation so the far-left mutant cannot pass on a weak boundary-only check.
- Verify the negative row is an intentional assertion failure (not parse/setup error), and that both rows use the same script and intended-center assertion.
- This is headless center-state coverage only; it does not evidence rendered framing or a production camera.

No files other than this scoped report were changed; no engine was run.
