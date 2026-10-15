# Round 23 left-edge camera scout

Read-only Godot 4.7.2 feasibility check. Adapted the existing camera limit probe into scratch only at `corpus/live/r23-left-scout/camera_left.gd`; no tracked fixture was edited. Ran headless with `godot --headless --path . --script <scratch>` and the same command plus `-- --far-left-bound`.

- Positive: exit 0; target moved to `(-2000, 0)`; active camera center clamped to `(-640, 0)`, distinct from target; PASS. Authored left limit was `-1000`.
- Control: exit 2; far-left limit `-100000` let center follow target to `(-2000, 0)`; intended assertion failed.
- Both exercised the same setup and assertion. Runtime viewport width is 720px, so half-width 360 and expected left-edge center is `-1000 + 360 = -640`. This differs from the LOG's illustrative 64px / `-968` value; fixture should derive half-width from the active viewport, as the existing probes do.

This supports the proposed left-limit pair in this headless environment only. It does not establish rendered framing, production-camera behavior, other edges, or export reliability.
