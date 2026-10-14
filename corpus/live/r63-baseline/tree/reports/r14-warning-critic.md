# Round 14 — warning classifier critic (LEAF)

## Verdict: calibration claim is not established by the current runner

The intended scope is reasonable: reject the audio positive when its captured Godot output includes the ObjectDB leak warning, but do not turn unrelated nested-project export warnings into failures. The evolving classifier appears narrowly scoped to `audio_playback`, yet its current expression does **not** match the exact captured Round 12 warning. Consequently, the key regression target is accepted rather than rejected. Do not treat the classifier/probe as calibrated until this is repaired and independently replayed.

## Evidence and adversarial checks

I read Round 14's mission in `LOG.md`, `corpus/lessons/r12-initial-hold.json`, the cleanup author record, `reports/r12-audio-verifier.md`, and the current `corpus/fixtures/run_battery.py` plus its working diff. The initial-hold audio positive is marked PASS and its captured output includes:

```text
WARNING: 2 ObjectDB instances were leaked at exit (run with `--verbose` for details).
```

The current classifier uses `re.fullmatch(r"WARNING: [0-9]+ ObjectDB instances were leaked at exit", line.strip())`. That pattern rejects the literal captured line because the real diagnostic has a parenthetical suffix. A direct scratch check (`re.fullmatch` against the literal above) returns false. Since this warning is not an `ERROR:`, the shared `classify_process` accepts the otherwise matching exit/signature, and `classify_audio_process` therefore accepts this leaked result too. The `--probe-audio-warning` meta record is expected to classify captured leak as FAIL and clean as PASS, so it should expose this bug by returning FAIL; it does not make the production classifier correct merely by existing.

The production audio path does call `classify_audio_process`; unrelated ordinary cases and export cases continue to use `classify_process`. The observed existing export warning is `WARNING: Detected another project.godot at res://controls. The folder will be ignored.` in the Round 6 export logs. This does not match the ObjectDB prefix and the audio-only application means the new rule should not reject export readiness. No execution of the whole battery was needed for these code-path facts; the pending author/verifier run should record actual results after repair.

### Calibration/specificity boundaries

- The rule checks only output assembled as stdout + stderr by `run_process`, so it is capable of seeing the actual captured warning (not just a fixture's print marker) when that process runs.
- The regex should be line-anchored and accept the known suffix. For example, match a stripped line beginning `WARNING: <positive integer> ObjectDB instances were leaked at exit` followed by end-of-line or whitespace/parenthetical details. A broad substring search risks matching quoted/copied text; a full-line pattern that assumes the diagnostic has no details misses this observed form.
- Keep application case-specific. Existing export warnings are legitimate in this fixture and must remain accepted. Also verify a clean audio output is accepted, and that a warning-like unrelated audio line and unrelated warning class do not trigger the ObjectDB-specific check.
- This targeted filter establishes detection only for this warning form/count and these output channels. It does not establish general memory-leak detection or reject other WARNING classes; the mission explicitly disclaims those broader claims.

## Is the meta probe tautological?

Not wholly: `--probe-audio-warning` feeds two persisted, distinct R12 captured outputs through the same `classify_audio_process` called by the live audio case, then asserts the expected pair of outcomes. That is a useful captured-output regression test, rather than merely checking that the warning string exists. But its evidence is bounded: the clean/leak expected outputs are themselves sourced from static lesson JSON, and the meta verdict is not independent verification of classifier semantics. A mutation/removal of the warning in the stored fixture could weaken the test unless the probe also asserts the exact warning occurrence and records/checks source identity. Nor does this replay alone prove the live Godot process capture path; the independently executed full battery must show a clean current audio run accepted, alongside a raw-output warning control rejected. Be explicit which of these forms is being tested.

## Recommendation for verifier / decision

1. Repair the ObjectDB line matcher to accommodate the suffix visible in the raw verifier output, and retain a narrow anchored match.
2. Replay the captured pair and inspect the raw warning line and classifications; assert exactly one matching warning in leak output and zero in clean output, not just a pair of verdicts.
3. Independently run the combined battery and verify audio positive accepted when clean, a warning-bearing audio control rejected, audio no-play behavior preserved, and nested-project export warnings still accepted. Record raw output and hashes; leave all other output classes unchanged.
4. If any of these fail, HOLD the calibration claim. If they pass, the bounded claim can be considered improved only for this sampled ObjectDB leak warning form, not warning handling generally.

I made no source edits, ran no repository tests/battery, delegated nobody, and made no commit/push. No scratch files were needed; the regex check was in-memory. Only the assigned critic report should be written by this lane.
