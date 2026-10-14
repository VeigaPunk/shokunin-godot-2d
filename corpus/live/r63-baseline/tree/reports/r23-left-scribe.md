# Round 23 left-edge scribe — raw evidence and verdict checklist

## Scope and before-state

This is a read-only scribe report, not an execution or admission verdict. Round 23 proposes two new ordinary headless Camera2D rows: a left-limit positive and a far-left-bound control, sharing the active-center assertion. At baseline `HEAD=0d73a4c09300f201ba0233b73e4f3548c15201bb` (round 22), the committed runner contains 35 ordinary cases; `corpus/lessons/r22-timeout-verifier.json` records 46 results, aggregate PASS (35 ordinary + 2 mutants + 9 opt-in). Its camera rows cover right and top bound pairs, not left. Baseline SHA-256: `run_battery.py` `3d41153339cdea549dcda008bce157c8134409a8ab35cc1ee71b612ea53b8f84`; `camera_limit.gd` `c3953ce103ed382ef288adb306b7783672181e7555457f62721f1b648bfefd79`.

The current worktree already has changes to both assigned executor fixtures. I did not make or alter those changes, execute the battery/Godot, or modify controls. Current fixture changes appear to add a `-1000` authored left edge, a `-100000` far-left override, and the paired runner rows. The current scout/reviewer reports are feasibility evidence, not the named non-author full-replay result or committed raw verifier artifact.

## Evidence already reported (not independently replayed here)

- `reports/r23-left-scout.md` describes a scratch-only Godot 4.7.2 run: positive center `x=-640` with target `x=-2000`, exit 0; far-left control followed target to `-2000` and exited 2 on intended assertion. Scout says viewport width was 720, hence half-width 360 and clamp `-1000+360=-640`.
- `reports/r23-mutation-reviewer.md` describes a separate scratch positive/control: viewport half-width 32, positive center `-968`; with authored left limit sabotaged to `-100000`, center followed target and failed intended assertion. This is useful causal/sensitivity evidence, but it is not a replay of the final tracked fixture.
- The LOG's `-968`/64px is explicitly an illustrative observed viewport value, not a portable constant. Scout's 720px viewport yields `-640`. Admission must rely on deriving half-width from the runtime viewport, not hard-coding either coordinate.

These reports differ in viewport geometry, so their absolute centers should not be conflated. Both report the same expected relation: `left_limit + viewport_width/2`.

## Checklist for named verifier and parent

1. Preserve the exact full-replay command, exit status, raw output/JSON path, Godot version, and scratch/viewport dimensions. Verify 37 ordinary rows and 48 total PASS records (35 + 2 mutants + 11 opt-in), preserving all prior 46 outcomes. If row totals differ, explain rather than assume.
2. Confirm both new rows use the same `camera_limit.gd` script and active-center assertion. Positive should use authored `limit_left=-1000`, target x=-2000, current camera, moved parent, center x equal to `-1000 + runtime viewport width/2` within epsilon, and center distinct from target.
3. Confirm the far-left control changes only the limit to `-100000`; it must reach the same assertion after successful setup, follow the target rather than clamp, exit with the expected assertion code, and not fail from setup/parse/runtime errors. Record raw observed center and assertion diagnostic.
4. Check that the runner's expected signature/error allowlist requires the intended left assertion; a generic nonzero exit is insufficient. Preserve right/top rows' prior signatures and outcomes.
5. Compare tracked fixture and runner hashes before/after verifier execution; replay should not mutate them. Preserve full raw verifier JSON in the assigned lessons location and verifier report under reports.
6. Preserve prior export caveats. Earlier r16 export adverse observation and the explicit-relative-`--runs` StopIteration exception are unresolved; a successful default-path replay does not prove export reliability or erase either caveat.

## Verdict conditions and limits

Coverage improves only if the named non-author full replay verifies the raw positive/control pair and all previous rows remain passing, with no harmed axis. Depth and calibration should remain unchanged for this finite coverage addition unless the replay reveals otherwise. If no named raw replay is available, classify the result as incomplete/HOLD, not admitted. Bound any eventual claim to headless Camera2D active center state on the tested Godot/platform/viewport; do not claim rendered framing, production-camera behavior, other uncovered edges, export readiness, or general camera correctness.

No tracked edits, battery execution, engine/editor launch, or new constants were introduced by this scribe.
