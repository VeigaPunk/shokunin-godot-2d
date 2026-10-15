# Round 53 named non-author verifier — composite push-and-clear

## Verdict: PASS

LEAF non-author replay, no delegation. Godot `4.7.2.stable.arch_linux.ed1daf0bf`. Read the standing mission, r53 LOG declaration and wave reports. The candidate diff is additive: dedicated `--composite-push-and-clear` fixture branch, one CASE and its exact classifier allowlist, plus observer initialization for this flag. Existing r51 parsed and r52 push-only branches/cases remain distinct. Tracked bytes before/after verification were unchanged: fixture SHA-256 `2e82a957a7f8e0393b2fe58b799fe387fba3e72b889af1ae`; runner `db473b8e8a50f609a4504d0f664d8409d99ae255e257f9763a558c539d855f85`.

## Full default-path battery and regression comparison

Command:

```text
python .shokunin/game-dev-2d/corpus/fixtures/run_battery.py --probe-failing --probe-unrelated-error --probe-export-launch --probe-godot-error --probe-stream-attribution --probe-crash-exit --probe-timeout --runs .shokunin/game-dev-2d/corpus/live/r53-composite-verifier/runs
```

**78/78 classifications PASS:** 67 ordinary cases + 2 mutants + 9 opt-in classifications. Raw `corpus/live/r53-named-verifier/runs/20261013T100445520979Z/verdicts.json` (the run directory retains its initially chosen name); copied byte-identically to `corpus/lessons/r53-composite-non-author.json`, SHA-256 `acb3e9edff664cd89e52d05251da53b90855fc3018dcf12c1ddfa7afe5ee8cd1`. Note: an earlier report I sent misstated the denominator as 69 ordinary + 7 probes; corrected arithmetic is 67 ordinary + 2 mutants + 9 opt-ins = 78 total. The raw artifact has 78 result records, including 69 signature-bearing ordinary/mutant rows and 9 opt-in records.

Compared with `corpus/lessons/r52-route-non-author.json`, all **68/68** prior tuple-bearing `(case, verdict, actual_exit, signature)` rows match exactly by case, no missing/mismatch. Exactly one additional expected-negative row: `slider_adjust_repeat_right_second_focus_restore_composite_push_and_clear`, expected/actual exit2, classifier PASS, unique terminal `SLIDER COMPOSITE PUSH AND CLEAR ASSERTION FAILED: expected no new receipt after eleven checks`. All nine opt-in classifications are unchanged (export launch, Godot error, stream attribution, crash exit, timeout and the probe-failing/unrelated-error classifications); inner `godot_error_unrelated` and `stream_reject` are expected failures under outer probe PASS. Opt-in artifacts' paths/run timestamps naturally differ.

Separate fault injection command used `--fault-injection`; outer PASS. Raw `corpus/live/r53-named-verifier/fault-runs/20261013T100445520959Z/fault-verdicts.json`, byte-identical copy `corpus/lessons/r53-fault-non-author.json`, SHA-256 `c4a526f2f9e1bef2cb241a53ee3f5ffc11478990ae37a28c6817ffbeb3a2c453`. Inner results as designed: hang timeout, unrelated error rejected/FAIL, clean expected-negative PASS.

## Route observation and targeted sabotage

The new raw composite row reaches its unique expected-negative terminal after eleven checks. Output records final numeric history `6,6,6,5,5,5,5,4,4,3,3`, receipts `[6,3]`, Labels `Value 6,Value 3`, callback connected true. The wave1 direct scratch and fixture assertions capture edge10 observer 3→4, action pressed true→false, numeric 3 / receipts `[6,3]` / Label `Value 3`, with owner/callback preconditions maintained. Paired r51 parsed control and r52 push-only control remain unchanged; push-only left action pressed true. These are measured synthetic fixture signals only.

Fresh unique scratch copies under `corpus/live/r53-composite-verifier/` with the production expected-negative signature/classifier contract:

1. Omitted only direct `Input.action_release("ui_left")`, retained `root.push_input(composite)`: exit2 early, `ui_left remains pressed`; unique expected-negative terminal absent. Thus classifier rejects before terminal.
2. **Added requested control:** omitted only `root.push_input(composite)`, retained `Input.action_release("ui_left")`: exit2 early with `SLIDER parsed ui_left release observer failed: expected exactly one delivered release`; expected composite terminal absent. Applied production classifier contract (expected exit2 + unique composite terminal + no unrelated errors): rejected. Log `corpus/live/r53-composite-verifier/sabotage-omit-push.log`.

A malformed first shell-quoting invocation in my earlier verifier turn exited 127 before launching Python; no battery ran. It is retained as setup adversity only; successful full/fault replays above are the evidence. No constants changed; no tracked/seeded or engine/editor edits, commit, push, or merge.

## Scope

Conclusion is limited to this explicit synthetic Godot 4.7.2 sequence: push matching release then direct global action clear reproduces measured observer/action-state postconditions without parsed dispatch at edge10. It does not show route uniqueness (different event routes may satisfy the observations), nor establish HSlider internal consumption, OS/physical input or timing, rendering/pointer/accessibility, production behavior, or generic provenance.
