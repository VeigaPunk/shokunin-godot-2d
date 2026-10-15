# Round 52 route scribe — read-only admission checklist and bounded scratch

## Read-only evidence reviewed

- Standing mission: `/tmp/mission-game-dev-2d-standing.md`.
- Round 52 declaration and planned one-claim axis move: `.shokunin/game-dev-2d/LOG.md`.
- Round 51 named non-author report/raw: `reports/r51-provenance-verifier.md`, `corpus/lessons/r51-provenance-non-author.json`; round 51 executor report: `reports/r51-provenance-executor.md` (including its rejected initial non-additive edit/tainted run and later additive correction).
- Round 50 repaired baseline report/raw: `reports/r50-release-verifier.md`, `corpus/lessons/r50-release-repaired-non-author.json`.
- Read current `corpus/fixtures/slider_adjust.gd` and `run_battery.py`; did not edit tracked sources. Round-51 paired baseline is expected to retain eleven actions, owner/callback preconditions, edge10 action-state pre/post checks, observer delta, numeric/full receipts/Label checks, and exact expected-negative classification.

## Bounded independent scratch result

Scratch is an isolated copy at `.shokunin/game-dev-2d/corpus/live/r52-route-scribe-scratch/project`. It used the in-tree Godot **4.7.2.stable.arch_linux.ed1daf0bf** binary. No tracked fixture, runner, seeded corpus, engine, or editor files were changed.

Paired clean command:
`godot --headless --path <scratch-project> --script slider_adjust.gd -- --repeat-right --second-focus-restore --observe-parsed-release`

The paired parse case reached its existing terminal expected-negative marker after eleven checks, with values `6,6,6,5,5,5,5,4,4,3,3`, receipts `[6,3]`, labels `Value 6,Value 3`, exit 2. This is scratch confirmation only; named non-author battery evidence remains required.

For the contrast, changed only the scratch edge10 dispatch: built `InputEventAction` (`action="ui_left"`, `pressed=false`) and called `root.push_input(pushed)`; edges 0–9 remained their existing `_action`/`Input.parse_input_event` route. Kept edge10 focus-owner and callback preconditions, pre-state pressed assertion, observer count check, one-frame wait, post-state assertion, numeric/full receipts/Label assertions. Added one scratch print capturing measured values. Command otherwise identical.

Observed at edge10: observer **3→4**; `Input.is_action_pressed("ui_left")` **true**; value **3.0**; full receipts **[6.0, 3.0]**; Label **Value 3**; owner true; callback connected true. Then the existing post-release action-state assertion failed (`ui_left remains pressed`), exit 2, before the terminal marker. The identical parse baseline had passed its edge checks and reached its terminal marker. This confirms the hypothesized distinction in this bounded route contrast: `push_input` delivered the release to this separate in-tree `_input` observer, yet did not clear the global pressed state as `parse_input_event` did.

The raw scratch script is `.shokunin/game-dev-2d/corpus/live/r52-route-scribe-scratch/project/slider_adjust.gd` and contains the push variant. The paired baseline output and push output are preserved in `.shokunin/game-dev-2d/corpus/live/r52-route-scribe-scratch/` as `baseline.stdout` and `push.stdout`.

## Admission checklist for parent / named verifier

- [x] One bounded causal distinction directly reproduced in scratch; candidate can be considered, not presumed admitted.
- [x] Clean paired r51 parse route reaches the terminal marker only after eleven checks.
- [x] Push route distinguishes observer delivery from action-state clearing with the same event fields; value, full receipts, Label, owner, and callback match expected edge10 values.
- [ ] If executor adds the branch, it must be additive: preserve r51 and earlier cases/allowlists; add one distinct exact negative case and allowance only.
- [ ] Named non-author must run the fresh seven-flag default path and separate fault replay; preserve all prior tuple-bearing rows and opt-in classifications.
- [ ] Exact negative classifier must accept only the intended terminal expected-negative row. Confirm push contrast fails before terminal due the action-state assertion; confirm clean paired parse reaches marker. Preserve script/parse errors and false positives as adverse.
- [ ] Parent must adjudicate calibration; this scribe makes no axis verdict and supplies no battery/non-author evidence.

Scope is synthetic Godot action routing plus process frames in this fixture only. This does not establish OS input, HSlider internal consumption, physical timing, rendered/pointer/accessibility behavior, or production behavior. No constants changed. No commit/push/merge.

Adverse setup telemetry: first invocation passed a relative `--path` while changing directory and Godot rejected that invalid project path (exit 1); rerun with the absolute scratch path above succeeded. Not counted as behavior evidence.
