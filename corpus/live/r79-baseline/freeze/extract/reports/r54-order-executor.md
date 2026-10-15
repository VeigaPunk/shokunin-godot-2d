# Round 54 executor report — clear-then-push ordering

Status: causal scratch confirmed; additive implementation and author batteries passed. Named non-author verification and parent adjudication remain pending.

## Bounded scratch result

Read the standing mission, r54 declaration, and r51–r53 reports/lessons/raw fixtures. Used a unique scratch copy under `corpus/live/r54-order-executor/scratch/project`; tracked changes were not made until after this test. The scene kept edges 0–9 parsed and preserved the eleven-edge focus/reconnect history. For edge 10 only, it executed `Input.action_release("ui_left")` followed by `root.push_input(matching InputEventAction(ui_left, pressed=false))`, then awaited the same `process_frame`.

Godot 4.7.2 scratch output directly measured edge10 observer count **3→4**, global `ui_left` action **false** after frame, numeric value **3**, receipts `[6,3]`, Label `Value 3`, focus owner still slider, and callback connected. The full eleven-edge expected history and the existing exact expected-negative terminal also completed. This matches r51 parsed edge10 and r53 push-then-clear on the requested measured state. Therefore reverse order also mimics the composite postconditions; r53 order is not necessary for these bounded observations. This does not claim the sequences are identical internally.

## Additive implementation and author evidence

After causal scratch, added only a dedicated `--clear-then-push-release` branch in `slider_adjust.gd`, its exact expected-negative case and matching exact diagnostic allowance in `run_battery.py`, and the observer initialization flag. The new branch explicitly uses clear THEN matching pushed release before the same frame. Existing r51/r52/r53 branch bodies and rows were preserved; no allowance or prior row was changed.

- Fresh ordinary author battery: **68/68 PASS**.
- Full seven-flag default-path author battery: **79/79 PASS** = 68 ordinary + 2 mutants + 9 opt-ins. Raw: `corpus/live/r54-order-executor/full/20261013T101729912320Z/verdicts.json`.
- Compared with `corpus/lessons/r53-composite-non-author.json`: all **69** prior tuple-bearing `(case, verdict, actual_exit, signature)` rows match exactly by case; one new expected-negative row `slider_adjust_repeat_right_second_focus_restore_clear_then_push_release` has expected/actual exit 2. The nine opt-in classifications remain stable. The inner `godot_error_unrelated` and `stream_reject` outcomes are intentionally FAIL under their outer probe PASS, not clean fixture passes.
- Targeted sabotage in separate scratch, under the exact new branch flags and production expected-negative contract: omitting clear exited 2 early (`ui_left remains pressed`); omitting push exited 2 early (observer did not advance). Neither reached the unique new terminal, so neither qualifies under its exact classifier.

## Adverse scratch telemetry

An initial quoted-shell invocation treated the whole command as an executable (exit 127); no engine test ran. An intermediate instrumented scratch edit landed a diagnostic in the wrong historical branch and had parse errors; another first flag run lacked observer initialization and failed with nil observer. These setup failures were discarded, not counted as evidence. The corrected causal scratch is the direct measurement above. No other tracked-file edits were made during these attempts.

## Limits

This calibration is only for the synthetic Godot 4.7.2 route and stated observations. It establishes neither HSlider internal consumption nor OS/physical input, timing, rendering, pointer, accessibility, production behavior, nor a general event-provenance claim. No engine/editor/seeded edits, commit, push, or merge.
