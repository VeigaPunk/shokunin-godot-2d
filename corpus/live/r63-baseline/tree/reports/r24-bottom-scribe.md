# Round 24 bottom-edge scribe — raw evidence and verdict checklist

## Scope and before-state

This is a read-only scribe report, not an execution or admission verdict. Round 24 proposes two ordinary headless Camera2D rows: an authored bottom-limit positive and a far-bottom control. Baseline `HEAD=3b23caa25f00d3929a863ba9d3515be9aa5bb760` closes round 23. Its committed `run_battery.py` has 37 ordinary cases, including right/top/left limit pairs, and `corpus/lessons/r23-left-verifier.json` records the 48-result full replay (37 ordinary + 2 mutants + 9 opt-in), aggregate PASS.

At inspection, the committed and working-tree fixture sources are identical: `run_battery.py` SHA-256 `3f449c02d9539270875fd1a2bda01e37df7e39083fcfc1203f2e87836eef822f`; `camera_limit.gd` SHA-256 `4d86b802205b06527fd84af9f187dd7ad89ea34d12b42995a06620536d3c69ec`. Neither bottom mode nor bottom rows are present yet. The r24 raw verifier artifact/report are not present at this inspection. I did not run Godot/the battery, alter fixture/control files, or modify other reports.

## Design/evidence review (not independently replayed)

The r24 declaration requires target `(0,2000)`, authored bottom `1000`, dynamic expected center `1000 - viewport_height/2` (968 for the battery's observed 64px viewport), and a same-assertion control that changes only `camera.limit_bottom` to `100000`. The control must follow the target and fail at the authored bottom assertion, not setup. The read-only critic and simplifier reports (`reports/r24-bottom-critic.md`, `reports/r24-bottom-simplifier.md`) agree that the unaffected x=0 and existing top/left bounds do not compete, and warn against deriving the asserted boundary from the far control limit. These are design reviews, not runtime evidence.

## Named-verifier and report-last checklist

1. Record exact verifier command, process exit, Godot version, raw console/output, raw JSON path, scratch path, and observed viewport dimensions. Target is 39 ordinary rows + 2 mutants + 9 opt-in = 50 total PASS records, with all prior 48 outcomes preserved; explain any count discrepancy rather than infer success.
2. Confirm the final fixture has explicit `--bottom-bound` and `--far-bottom-bound` modes and the paired CASES both invoke the same script and active-center assertion. The positive must retain asserted boundary 1000, target y=2000, center y=`1000 - runtime viewport height/2` within 0.01, center movement, and separation from target.
3. Confirm the control changes only bottom limit to 100000 while retaining authored assertion boundary 1000 and target `(0,2000)`. Require exit 2 with the same intended bottom-limit assertion and no setup/parse/runtime failure. The raw center should follow the target and violate the authored boundary.
4. Check bottom-specific diagnostic/signature and exact expected-exit classification; a generic nonzero exit does not establish the causal control. Ensure existing right/top/left pairs and all prior rows retain their prior results.
5. Preserve raw verifier JSON at `corpus/lessons/r24-bottom-verifier.json` and named verifier report at `reports/r24-bottom-verifier.md`. Compare tracked fixture/runner hashes before/after replay and record unchanged hashes (expected to differ from baseline only because of admitted r24 fixture edits, not because replay mutates them).
6. Keep prior adverse export caveats intact: r16 export failure and the r20 explicit-relative-`--runs` StopIteration remain unresolved. A passing default-path replay does not establish export reliability or erase those observations.

## Verdict conditions and limits

Coverage improves only after a named non-author full replay verifies both new rows and preserves prior outcomes, with no harmed axis. Depth/calibration should remain unchanged for this finite coverage addition unless replay evidence shows otherwise. If the final raw replay/report is absent or the control fails setup rather than the intended assertion, classify HOLD/incomplete, not admitted. Bound any eventual claim to tested headless Camera2D active-center state; do not claim rendered framing, production camera behavior, export reliability, or general camera correctness.
