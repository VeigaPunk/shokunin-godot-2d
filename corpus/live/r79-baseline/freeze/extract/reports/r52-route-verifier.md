# R52 named route verifier (non-author)

## Result

PASS. Godot 4.7.2; verifier used own scratch `.shokunin/game-dev-2d/corpus/live/r52-route-verifier/`. All 77 full-path classifications PASS (68 ordinary rows plus 9 opt-in classifications), and the 67 prior comparable tuples match exactly by case. Separate fault-injection outer verdict PASS with expected inner outcomes. Both route mutations failed early with exit 2 and the expected state-specific error, before the normal terminal marker. Fixture and runner tracked bytes were unchanged (SHA-256 fixture `eeea197a8a566ecb3fb48c929985d63bd5723796bb54467d24a382c352a31010`, runner `168058fa168917a39a3c561deef2102b93ea10df983cf6c5e30081fb0ca10c4c`, same before/after).

## Full default-path run

Command: `python .shokunin/game-dev-2d/corpus/fixtures/run_battery.py --probe-failing --probe-unrelated-error --probe-export-launch --probe-godot-error --probe-stream-attribution --probe-crash-exit --probe-timeout --runs .shokunin/game-dev-2d/corpus/live/r52-route-verifier/runs`

All 77 rows PASS. Raw: `corpus/live/r52-route-verifier/runs/20261013T094310757366Z/verdicts.json`; copied to `corpus/lessons/r52-route-non-author.json` byte-identically (SHA-256 copy check true). It has 68 tuple-bearing rows. Added row `slider_adjust_repeat_right_second_focus_restore_observe_push_input_release`: expected/actual exit 2, classifier PASS, unique terminal signature `SLIDER PUSH INPUT RELEASE ASSERTION FAILED: expected no new receipt after eleven checks`. Its output records `observer_delta=1 pressed=true callback_connected=true`, values `6,6,6,5,5,5,5,4,4,3,3`, receipts `[6,3]`, Labels `Value 6,Value 3`.

## Comparison

Compared all 67 prior r51 rows by exact `(case, verdict, actual_exit, signature)`; 67/67 match, zero mismatches. Current run adds exactly the one push-input route row. Opt-in evidence: export-launch, Godot-error, stream-attribution, crash-exit and timeout outer classifications all PASS; inner vectors respectively Godot `[true,false]`, stream `[true,false]`, crash `[true,false]`, timeout `[false,true,false]`. Probe-failing mutations and unrelated-error probes are PASS-classified as expected.

## Separate fault injection

Command: `python .shokunin/game-dev-2d/corpus/fixtures/run_battery.py --fault-injection --runs .shokunin/game-dev-2d/corpus/live/r52-route-verifier/fault-runs`

Outer PASS; raw `corpus/live/r52-route-verifier/fault-runs/20261013T094556126921Z/fault-verdicts.json`, copied byte-identically to `corpus/lessons/r52-fault-non-author.json`. Inner cases: `fault_hang` expected FAIL (timeout 0.25s), `fault_clean_expected_negative` PASS exit 2, `fault_unrelated_error` expected FAIL exit 2. No seeded battery contamination.

## Exact route mutations in unique scratch

1. On new push-input control, replaced its sole `root.push_input(pushed)` with `Input.parse_input_event(pushed)`. Exact action: `godot --headless --path <alternate-sabotage> --script slider_adjust.gd -- --repeat-right --second-focus-restore --observe-push-input-release`. Exit 2 early: `SLIDER pushed ui_left release action-state assertion failed: expected action to remain pressed`; no terminal marker. This proves parsed release does not satisfy push branch state expectation.
2. On r51 parsed observer control, replaced only edge-10 `_action(edges[i][0], edges[i][1])` with construction of matching `InputEventAction(ui_left, pressed=false)` and `root.push_input(reverse)`. Same runner options except `--observe-parsed-release`. Exit 2 early: `SLIDER input-state post-release assertion failed: ui_left remains pressed`; no terminal marker. This proves push route cannot substitute for parsed release in r51 branch.

Mutations were in `.shokunin/game-dev-2d/corpus/live/r52-route-verifier/alternate-sabotage/slider_adjust.gd` only. Scope supports the bounded synthetic Godot route distinction, not OS/physical input, HSlider internal event consumption, render/pointer/accessibility, or general provenance claims.
