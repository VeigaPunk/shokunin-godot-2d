# Round 53 named non-author verifier — composite push-and-clear route

## Verdict: PASS

LEAF non-author replay, no delegation or tracked edits. Godot `4.7.2.stable.arch_linux.ed1daf0bf`. Full default-path command:

```text
python .shokunin/game-dev-2d/corpus/fixtures/run_battery.py --probe-failing --probe-unrelated-error --probe-export-launch --probe-godot-error --probe-stream-attribution --probe-crash-exit --probe-timeout --runs .shokunin/game-dev-2d/corpus/live/r53-named-verifier/runs
```

All **78/78** classifications PASS (67 ordinary cases + 2 mutants + 9 opt-in classifications). This initial report was superseded by `r53-composite-verifier.md`, which records both targeted sabotages and the corrected count; this report is retained as adverse reporting telemetry. Raw: `corpus/live/r53-named-verifier/runs/20261013T100445520979Z/verdicts.json`; copied byte-identically to `corpus/lessons/r53-composite-non-author.json` (SHA-256 `acb3e9edff664cd89e52d05251da53b90855fc3018dcf12c1ddfa7afe5ee8cd1`). Prior r52 raw `corpus/lessons/r52-route-non-author.json` has 68 tuple-bearing rows; **68/68 exact** `(case, verdict, actual_exit, signature)` matches by case, zero missing/mismatches. One new case only: `slider_adjust_repeat_right_second_focus_restore_composite_push_and_clear`, expected/actual exit 2, classifier PASS, unique terminal `SLIDER COMPOSITE PUSH AND CLEAR ASSERTION FAILED: expected no new receipt after eleven checks`. Its raw stdout includes final values `6,6,6,5,5,5,5,4,4,3,3`, receipts `[6,3]`, Labels `Value 6,Value 3`, callback connected true, followed by the expected terminal. Probe classifications: Godot-error `[true,false]`, stream `[true,false]`, crash `[true,false]`, timeout `[false,true,false]`; export-launch PASS. Inner `godot_error_unrelated` and `stream_reject` are expected failures, not clean cases.

## Separate fault injection

Command `python .shokunin/game-dev-2d/corpus/fixtures/run_battery.py --fault-injection --runs .shokunin/game-dev-2d/corpus/live/r53-named-verifier/fault-runs`. Outer verdict PASS; raw `corpus/live/r53-named-verifier/fault-runs/20261013T100445520959Z/fault-verdicts.json`, byte-identical lesson copy `corpus/lessons/r53-fault-non-author.json` (SHA-256 `c4a526f2f9e1bef2cb241a53ee3f5ffc11478990ae37a28c6817ffbeb3a2c453`). Expected inner outcomes: hang timeout 0.25s, clean expected-negative exit2, unrelated-error exit2; no unexpected clean claim.

## Exact composite-route sabotage

Unique verifier scratch `.shokunin/game-dev-2d/corpus/live/r53-named-verifier/composite-sabotage/`; removed only `Input.action_release("ui_left")` after edge10's matching `root.push_input(composite)` (left composite flag and rest of source intact). Command `godot --headless --path <scratch> --script slider_adjust.gd -- --repeat-right --second-focus-restore --composite-push-and-clear`; exit 2 before terminal, output `ERROR: SLIDER input-state post-release assertion failed: ui_left remains pressed`, backtrace line 251. Thus exact missing-clear sabotage is rejected before the unique terminal; it cannot be mislabeled as expected composite terminal.

Tracked fixture and runner hashes remained `2e82a957a7f8e0393b2fe58b799fe387fba3e72b889af1ae` and `db473b8e8a50f609a4504d0f664d8409d99ae255e257f9763a558c539d855f85` throughout verification. The candidate is additive against r52: one case and one classifier allowlist alongside one distinct flag branch. Bounded conclusion only: in this synthetic Godot 4.7.2 fixture, matching `root.push_input` plus explicit `Input.action_release` reproduces the measured observer/action-state postconditions without parsed dispatch at edge10. No claim about HSlider internal consumption, OS/physical input or timing, rendering, pointer/accessibility, production behavior, or general event provenance. No constants changed; no engine/editor/seeded edits, commits, push, or merge.
