# Round 20 top-edge executor report

## Scope and changes
Implemented the requested top-bound positive and far-top-bound control in `corpus/fixtures/camera_limit.gd` and registered both as ordinary cases in `corpus/fixtures/run_battery.py`. Kept right-edge behavior and case expectations intact. Top bound is `-1000`, far control top bound `-100000`; target moves from origin to `(0, -2000)`. Expected top screen center is `boundary + viewport_height / 2`; observed viewport height was 64, so clamp is `-968`. Right behavior remains bound 1000 / far 100000 and its existing case rows were preserved.

## Evidence
Command: `python .shokunin/game-dev-2d/corpus/fixtures/run_battery.py --godot godot --runs /tmp/r20-top-targeted2`

Exit 0, battery verdict PASS, **35/35** ordinary cases. Raw artifact: `/tmp/r20-top-targeted2/20261013T005339105359Z/verdicts.json`.

- `camera_limit`: PASS exit 0; right center `(968, 0)`, target `(2000,0)`.
- `camera_far_bound`: PASS as expected negative, exit 2 and intended assertion; observed center `(2000,0)`, right bound 1000, expected clamp x 968.
- `camera_top_limit`: PASS exit 0; top center y `-968`, target `(0,-2000)`; viewport-adjusted clamp and separation assertion met.
- `camera_far_top_bound`: PASS as expected negative, exit 2 and intended assertion (not setup failure); observed center `(0,-2000)`, top bound `-1000`, expected clamp y `-968`.
- Original other 31 outcomes stayed PASS in the same battery.

During initial targeted execution, far-top correctly exited 2 but was initially classified FAIL because the existing expected-diagnostic allowlist did not yet include its message. Added the exact intended top assertion to that allowlist and reran; final replay passed. No engine/editor or seeded-control edit, no commit/push/merge, and no LOG edit.

Parent separately reported an adverse baseline telemetry event: explicit relative `--runs` export diagnostic probe hit StopIteration at runner line 245 (`next(... "savepack" ...)`). This top-edge task did not modify export logic. My plain battery invocation completed export rows successfully.

SHA-256: `camera_limit.gd` `c3953ce103ed382ef288adb306b7783672181e7555457f62721f1b648bfefd79`; `run_battery.py` `ff5015734c22604b3cf5778b7ae4fcb3b452ebeb70cb687c2e4e0747b21513d1`.
