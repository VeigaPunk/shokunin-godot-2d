# Round 23 left-edge executor report

Implemented only the paired left-edge camera cases in `corpus/fixtures/camera_limit.gd` and `corpus/fixtures/run_battery.py`.

- `camera_left_limit`: authored `limit_left=-1000`, move target to `(-2000, 0)`, assert active center reaches authored boundary plus half the current viewport width, remains inside the authored boundary, advances, and differs from target.
- `camera_far_left_bound`: same target and assertion, but set only the camera limit to `-100000`; expected boundary remains authored `-1000`, so the control fails the same intended assertion (not setup).
- The half-width is read at runtime. Battery viewport is 64 px and positive center observed at x=-968. Scout scratch viewport was 720 px, which correctly yields x=-640; no hard-coded viewport-specific expected center.

Author full battery replay after the final correction: `python .shokunin/game-dev-2d/corpus/fixtures/run_battery.py`, exit 0, 37/37 cases PASS, including prior right/top positives and controls plus both left rows. Raw verdicts: `.shokunin/game-dev-2d/corpus/live/runs/20261013T011424773225Z/verdicts.json`. Left positive exit 0; far-left control exit 2 with intended signature `camera limit assertion failed: expected active center within left boundary and distinct from target`. Raw control reports center `(-2000,0)`, authored boundary `-1000`, expected clamp `-968`, and target `(-2000,0)`. No setup error or parse error.

Scope remained the two assigned fixtures and this report. No engine/editor or seeded-control mutation, no delegation, and no commit/push/merge. This is headless camera-center evidence only.
