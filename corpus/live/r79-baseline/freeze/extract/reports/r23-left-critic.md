# Round 23 left-edge camera-limit adversarial review

## Scope
Read-only review of the proposed left-edge positive/control pair against the existing `camera_limit.gd` and battery cases. No source or fixture edits; no engine/editor run. The declared geometry is headless active-camera center state only.

## Geometry and overlap
For the existing 64-pixel-wide viewport, `limit_left=-1000` should clamp the active screen center to `limit_left + viewport_width/2 = -968`, not to -1000. Put the parent target at `(-2000, 0)`: it lies 1000 units beyond the authored left limit, while the expected center is 1032 units from the target. Thus `center.x >= -1000 - 0.01`, equality to -968 within 0.01, and center/target separation all independently describe the intended edge response. The target movement from zero is 2000 (>1000 setup threshold); center movement from its initial center also exceeds 100.

The existing right limit (`1000`) does not compete: this test is on the negative-x side, and the interval from -1000 to 1000 is much wider than the viewport. The far-left control should change only `limit_left` to -100000 while keeping the target at -2000 and `limit_right=1000`. The target is then inside the left/right interval, so the center follows it to about -2000 rather than clamping at -968. It violates both the left-side boundary predicate and expected-clamp predicate. No right-boundary explanation accounts for that difference.

Keep left mode explicit and independent of `top_test`/`far_top_bound`; otherwise legacy right/top cases can accidentally inherit left geometry. Report the measured viewport width and observed center in raw verifier output rather than assuming 64px universally.

## Failure/control sensitivity
The control must exit 2 through the same final camera-limit assertion as the positive uses, with a left-specific diagnostic such as `expected active center within left boundary and distinct from target`. Do not accept a setup error: camera-current checks, target-moved check, and any fixture-start/setup diagnostics must remain separate and cause HOLD if they fire. In the far-left arm, `within_boundary` is false and `at_expected_clamp` is false; `center_advanced` is true, while `separated_from_target` is false. The intended assertion fails even though movement/current setup succeeds.

## Existing edge regression exposure
The existing right and top positive/far-bound pairs should retain their previous arguments, case names, expected exits, and matched failure assertions. A left selector must not redefine `top_test`; right remains default for no direction flag. Verify prior ordinary rows in the full replay, not just the new pair. The current script's right and top boundary/half-viewport calculations are direction-specific; adding left should use x half-width and `left + half-width` (not the top formula `boundary + half-height`).

## Verdict
Geometry supports a causally discriminating left pair, with no right-edge confound under the declared coordinates. Admit coverage only if independent replay observes positive center near -968 (or measured `left + width/2`), control center following target, successful setup in both, and the control's exact same left-edge assertion failure; preserve all prior rows. This is not evidence for rendered framing, other edge pairs, production camera behavior, or export readiness.
