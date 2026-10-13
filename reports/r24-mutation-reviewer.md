# Round 24 mutation reviewer — bottom Camera2D clamp

Scratch-only runtime checks; no seeded fixture/control, engine, or editor files were changed. Godot was `/usr/bin/godot`, version 4.7.2.stable.arch_linux.ed1daf0bf. Work area: `.shokunin/game-dev-2d/corpus/live/r24-mutation-reviewer/scratch`.

Built a disposable copy of the fixture and project settings. The scratch fixture uses target `(0, 2000)`, fixed authored bottom limit `1000`, and a viewport-derived half-height; the relevant active-center expectation is `1000 - half_height`. At the battery viewport (64px high), the observed center y was 968.

| Scratch invocation | Result | Evidence |
|---|---|---|
| `godot --headless --path <scratch> --script camera_limit.gd -- --bottom-bound` | exit 0 | `PASS ... center_at_viewport_adjusted_clamp=true ... bottom_test=true`; center y 968, target y 2000 |
| same, `-- --far-bottom-bound` (sets bottom limit to 100000, assertion still boundary=1000) | exit 2, intended failure | `OBSERVED ... center=(0.00,2000.00) boundary=1000.00 expected_clamp=968.00 target=(0.00,2000.00)` then `camera limit assertion failed: expected active center within bottom boundary and distinct from target`; setup stayed valid, no script/parse error |
| positive `--bottom-bound` after scratch sabotage of authored `camera.limit_bottom = 1000` to `100000` | exit 2, intended failure | same observed center/expected clamp and bottom-bound assertion failure; confirms assertion sensitivity to authored-bound loss |

The paired runtime control and authored-limit sabotage both expose the intended bottom clamp regression. Scope is the headless active center only; this is not a rendered-framing or production-camera claim. Executor separately reported its 39-case replay had an export-readiness-only failure and used relative `--runs`; I did not reproduce or validate that result, and it does not alter these standalone bottom-edge runs. Parent has the executor raw at `corpus/live/r24-bottom-executor/20261013T012020522893Z/verdicts.json`. Constants: target y=2000, authored assertion boundary=1000 (unchanged in far-bound control), far control/sabotage limit=100000, tolerance=0.01, viewport half-height=32 observed.
