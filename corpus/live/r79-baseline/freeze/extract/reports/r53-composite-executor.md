# Round 53 executor report — composite push-and-clear route

Status: causal scratch confirmed; additive implementation and author batteries passed. Named non-author verification and parent adjudication remain pending.

## Baseline and causal scratch

Read the standing mission, round 53/52/51 LOG entries, the r51/r52 lessons/raw evidence and reports, and the r53 scout, baseline-reviewer, and scribe reports. r51 edge10 ordinary parsed dispatch yielded observer count 3→4 and `ui_left` pressed true→false. r52 `root.push_input` matching release alone also yielded observer 3→4 but left pressed true. Both retained numeric 3, receipts `[6,3]`, Label `Value 3`, focus/callback state.

Before tracked edits, copied the r51 parsed-release fixture to `.shokunin/game-dev-2d/corpus/live/r53-composite-executor/scratch/project`. Kept edges 0–9 parsed, all eleven owner/callback-before and numeric/full receipt/Label-after checks, and the existing observer/action checks. Replaced only edge10 with a matching `InputEventAction(ui_left, pressed=false)` delivered by `root.push_input`, then `Input.action_release("ui_left")` at the same frame boundary. Godot 4.7.2 output reached the unique terminal after all checks:

```text
SLIDER_PARSED_RELEASE_OBSERVER values=6,6,6,5,5,5,5,4,4,3,3 receipts=6,3 Labels=Value 6,Value 3 callback_connected=true
ERROR: SLIDER PARSED RELEASE OBSERVER ASSERTION FAILED: expected no new receipt after eleven checks
```

Thus observer count advanced 3→4, global action state became false, numeric/receipts/Label remained 3/`[6,3]`/`Value 3`, and focus/callback assertions held. This matches the measured r51 state while edge10 itself did not use `Input.parse_input_event`. A first attempt used the r52 push-only branch as the comparator; its pressed-true assertion necessarily failed after adding `Input.action_release`. This was the wrong control, retained as adverse scratch telemetry and not used for the causal result.

## Additive tracked case

Only after the corrected scratch, added one dedicated `--composite-push-and-clear` branch in `corpus/fixtures/slider_adjust.gd`, plus one expected-negative `CASE` and its exact diagnostic allowlist in `corpus/fixtures/run_battery.py`. The branch checks owner/callback before each edge and per-edge numeric/full receipts/Label after each frame; at edge10 it additionally checks observer +1 and action pressed true→false. Its unique terminal expected-negative exit2 occurs only after all eleven checks. Existing r51 parsed and r52 push-only branches/rows were not edited.

- Fresh ordinary author battery: **67/67 PASS**.
- Full seven-flag author replay: **78/78 PASS** = 67 ordinary + 2 mutants + 9 opt-ins. Raw: `corpus/live/runs/20261013T095812887945Z/verdicts.json`.
- Compared by case to `corpus/lessons/r52-route-non-author.json`: all **68** prior tuple-bearing `(case, verdict, actual_exit, signature)` records match; exactly one new expected-negative case `slider_adjust_repeat_right_second_focus_restore_composite_push_and_clear` (exit2); prior opt-in cases remain present and unchanged.
- The inner intentional negative probes `godot_error_unrelated` and `stream_reject` report FAIL as expected under their outer probe PASS; they are not miscounted as clean fixture passes.

No non-author replay performed by executor. This report is not an admission verdict.

## Limits

The result calibrates only the bounded synthetic Godot 4.7.2 composite route counterexample: observer delivery plus global action-state transition do not prove parsed-route provenance against this explicit push-plus-clear composite. It does not establish HSlider internal consumption, OS input/auto-repeat, physical timing, rendering, pointer behavior, accessibility, production behavior, or generic event provenance. No engine/editor/seeded edits, commit, push, or merge.
