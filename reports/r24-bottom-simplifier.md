# Round 24 bottom simplifier review

Read-only directional assertion review of `camera_limit.gd` and the r24 declaration.

The existing fixture can cover bottom with a narrow vertical-direction extension, preserving the authored boundary as the assertion oracle in both rows:

- Recognize `--bottom-bound` and `--far-bottom-bound`; bottom positive/control both select the same vertical target `(0, 2000)` and authored boundary `1000`. The far flag changes only `camera.limit_bottom` to `100000`.
- Treat either vertical flag as a vertical test, without combining top and bottom flags. Use viewport **height** / 2 and `center.y`; expected bottom clamp is `boundary - half_height` (dynamic, 968 for the 64px-high battery viewport). The positive requires `center.y <= boundary + 0.01`, equals the expected clamp within `0.01`, advances, and differs from target. The far-bottom control should follow y=2000 and fail this same authored-boundary assertion.
- Keep the right/left horizontal paths unchanged. In diagnostics, label bottom explicitly and report `far_bottom_bound`; avoid labeling it as top or right. Setup failures (not current, target did not move) must remain distinct from the intended boundary assertion failure.

Key false-positive to avoid: deriving the asserted boundary from the mutated far limit would make the control test the wrong condition. Also avoid changing target position or assertion boundary between bottom positive and far-bottom rows. This is a minimal direction-specific extension; it does not establish rendered framing or other camera behavior.
