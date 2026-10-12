# Round 14 warning verifier — LEAF

## Verdict

**RELEASE the narrow calibration change.** The production `audio_playback` classifier now rejects the known captured ObjectDB leaked-instances warning while accepting clean audio output. It does not reject an unrelated warning or alter export warning acceptance. This only verifies the sampled warning grammar in the `audio_playback` output; it is not a general warning/leak detector.

I acted as the named non-author verifier. I did not delegate, edit fixtures/runner, commit, or push. The sole repository write is this report.

## Mission inputs and captured r12 evidence

Read the Round 14 mission in `.shokunin/game-dev-2d/LOG.md`, the r14 scout/executor/critic reports, Round 12 initial HOLD and re-verification reports, and the raw r12 lesson captures.

- `.shokunin/game-dev-2d/corpus/lessons/r12-initial-hold.json`: `audio_playback` has actual/expected exit 0 and the matching `PASS audio_playback in_tree=true playing=true position_advanced=true` signature, but its captured output includes `WARNING: 2 ObjectDB instances were leaked at exit (run with `--verbose` for details).` The historic record itself says PASS under its old classification. The new production audio classifier returns FAIL for this same output.
- `.shokunin/game-dev-2d/corpus/lessons/r12-battery-verifier.json`: same exit/signature and playback evidence with no leak warning; new classifier returns PASS.
- The prior r12 re-verification's live positive audio was warning-free; this replay independently obtained a clean live positive as well.

## Independent combined replay

Ran the required command from the repository root:

```text
python .shokunin/game-dev-2d/corpus/fixtures/run_battery.py --probe-failing --probe-unrelated-error --probe-export-launch --probe-godot-error --probe-audio-warning
```

Exit **0**, overall **PASS battery**. Raw record: `.shokunin/game-dev-2d/corpus/live/runs/20261012T182651598625Z/verdicts.json`.

- **31 ordinary cases PASS** (29 seeded feature/control cases plus the two existing scratch mutants); all prior cases remain present. The live `audio_playback` exits 0 and advances position `0.00580498855561 → 0.09868481010199`; its captured output contains no warning. `audio_no_play` remains its expected exit-2 assertion negative.
- **7 probe/meta records PASS**, yielding 38 total result records: captured r12 warning probe, two unrelated-error probes, export-launch probe, and real-Godot error probe (plus the two corresponding export case records are included in the 31 ordinary case count; no extra case omitted from the stated total). Captured warning meta outcome is leak FAIL / clean PASS.
- Export readiness and missing-preset cases both PASS and retain `WARNING: Detected another project.godot at res://controls. The folder will be ignored.`. The unrelated nested-project warning remains accepted; no blanket warning rejection was introduced.
- Godot error probe's inner clean expected-negative classification is true and unrelated-error classification false, as expected by the meta probe.

Fault injection:

```text
python .shokunin/game-dev-2d/corpus/fixtures/run_battery.py --fault-injection
```

Exit **0**, `PASS fault injection`; raw `.shokunin/game-dev-2d/corpus/live/runs/20261012T182729608584Z/fault-verdicts.json`. The expected inner results are timeout FAIL, clean expected negative PASS, and unrelated-error FAIL.

## Adversarial classifier checks

All mutations were isolated under `/tmp`; repository sources and lesson captures were not altered.

1. Copied the runner and lessons to `/tmp/r14-audio-warning-adversarial`, removed only `and not leaked_objectdb` from `classify_audio_process`, then ran `python .../fixtures/run_battery.py --probe-audio-warning`. Exit **1**; the captured audio-warning meta probe and overall battery FAIL. Thus disabling the new rejection is detected by the probe.
2. Copied unmodified runner and lesson data to `/tmp/r14-audio-warning-data`. Appending `WARNING: Unrelated harmless diagnostic` to clean audio output retained exit/signature and still made `--probe-audio-warning` exit **0** (meta and command PASS).
3. In the same isolated data, replacing that appended line with `WARNING: 3 ObjectDB instances were leaked at exit (run with `--verbose` for details).` retained exit/signature but made the probe FAIL and command exit **1**. This checks a genuine matching warning with a different positive count.

The probes support specificity for the known ObjectDB warning line, not arbitrary warning forms, warning stream provenance, or a general suppression policy.

## Fixture immutability and axis verdict

Hashed all **40 tracked** paths under `.shokunin/game-dev-2d/corpus/fixtures` before and after the combined and fault-injection runs. Every SHA-256 matched; changed paths: **none**. The only repository output from this verifier is `reports/r14-warning-verifier.md`.

- **Calibration: improved.** The initial r12 captured result with successful exit/signature but the observed ObjectDB warning is now rejected by the production audio classifier; clean r12 capture and current live clean audio are accepted. Unrelated warnings and nested-project export warnings remain allowed.
- **Coverage: unchanged.** No feature/control case was added or removed; all 31 ordinary cases passed.
- **Depth: unchanged.** No additional behavioral scope is claimed.
- **Harm: none observed** in the required replay and adversarial checks.

Limits: the rule is case-scoped to positive `audio_playback` and the known anchored ObjectDB leaked-instances warning grammar, including its verbose-details suffix and decimal count. It does not establish causal leak ownership, check every warning class or leak form, or prove audible/production audio behavior.
