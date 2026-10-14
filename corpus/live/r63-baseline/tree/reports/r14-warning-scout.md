# Round 14 warning scout — read-only findings

## Scope and sources

This scout is read-only. It examined `.shokunin/game-dev-2d/LOG.md` (Round 14 mission), `corpus/lessons/r12-initial-hold.json`, `corpus/lessons/r12-battery-verifier.json`, and `corpus/fixtures/run_battery.py`. No source/runtime changes or new executions were made. Godot version in the captured records is 4.7.2.stable.arch_linux.ed1daf0bf.

## Concrete evidence

The r12 initial-hold `audio_playback` record passed its ordinary expected checks: exit 0, signature `PASS audio_playback in_tree=true playing=true position_advanced=true`, and observed position advanced from `0.00580498855561` to `0.09868481010199` with `generated_samples=44100`. Its captured output then contained the exact shutdown diagnostic:

```text
WARNING: 2 ObjectDB instances were leaked at exit (run with `--verbose` for details).
   at: cleanup (core/object/object.cpp:2536)
```

The output includes the leak-count warning and its `at:` context line; it does not include verbose identities/details. The old `classify_process` only required expected exit, no launch error, signature present, no unrelated `ERROR:` lines, and no script/parse error. As a result that real leak warning did not invalidate `audio_playback` (PASS). Do not describe this as proven to be an audio-owned leak; the evidence establishes co-occurrence at shutdown, and the earlier scratch investigation only traced likely WAV resource/playback refs.

In the later `r12-battery-verifier.json`, `audio_playback` is warning-free and has the same PASS signature / exit 0; the no-play control exits 2 with its intended `AUDIO ASSERTION FAILED` diagnostic and no leak warning. The verifier's `export_readiness` and `export_preset_missing` outputs both contain the unrelated, expected Godot warning:

```text
WARNING: Detected another project.godot at res://controls. The folder will be ignored.
```

Both export records are PASS. Therefore a blanket “any WARNING fails every case” rule would regress established export behavior; this mission intentionally scopes rejection to audio playback.

## Current runner classification map

`run_battery.py` defines `classify_process`: exit code and timeout/launch error must match, signature must occur, unrelated `ERROR:` lines are rejected except explicitly enumerated exact/limited expected-error forms, and `SCRIPT ERROR:` / `Parse Error:` are rejected. It has `classify_audio_process`, which invokes the base classifier then rejects an output line matching the leak-warning regex. `audio_playback` alone uses this specialized classifier; `audio_no_play` continues through the normal expected-negative classifier. Export readiness uses a distinct output/artifact classifier (successful `[ DONE ]`, `savepack`, nonempty executable), and missing preset allows its exact expected error plus an empty output dir. Captured-warning probe `--probe-audio-warning` reclassifies the two r12 raw records with the production audio classifier and expects leaked record FAIL / clean record PASS.

The specialized matcher is anchored/full-line after stripping and accepts a decimal count: `WARNING: [0-9]+ ObjectDB instances were leaked at exit`. Thus it rejects the observed count 2 without requiring that count as a magic constant. It does not reject the following `at: cleanup` line by itself. It does not classify arbitrary warnings, unrelated ObjectDB messages, other leak wording/count formats, stderr provenance, or leak identity. Keep this guarantee narrow: known ObjectDB leaked-instances warning in `audio_playback` captured output makes that case fail closed.

## Calibration recommendation and honest probes

1. Preserve the case boundary and existing expected-negative treatment. Apply leak detection only to the positive `audio_playback` result, not all Godot runs or export records. Keep the generic classifier's error/parse checks intact; do not blanket-suppress warning output.
2. Retain an exact, line-scoped, count-flexible ObjectDB warning predicate. Ensure it examines combined captured stdout+stderr as stored by `run_process`, without pretending the JSON provides stream provenance. A malformed/variant warning is not covered; state that limitation rather than widening to all warnings without evidence.
3. Probe the *production* `classify_audio_process` against paired stored raw records as the runner option already does: r12 initial leak must classify FAIL despite matching exit/signature; r12 verifier clean must classify PASS. Also require the fixture runner's ordinary combined battery to keep expected export warnings accepted. A probe PASS means the probe assertions behaved as expected; it must not turn the historic initial-hold result into an admitted clean run.
4. Honest same-exit/signature counterfactuals: append the exact known ObjectDB warning to the clean captured audio output and require audio classifier FAIL; remove only that warning line from the historical leaked output and require audio classifier PASS, holding all remaining output/code/error/expected exit/signature fixed. If useful, test a different positive decimal count is rejected (the rule is count-flexible). Record each transformed output and verdict; label these as classifier counterfactuals, not Godot-generated warning evidence.
5. Guard scope with a captured export control: leave its nested-project warning present and confirm its normal export classifier still passes. A warning unrelated to ObjectDB should not fail audio solely because it is a warning under the narrow current contract. Conversely, do not claim other warning classes are checked.
6. Independent verification should replay the combined battery and warning probe, confirm leak→FAIL / clean→PASS / export warnings still accepted, and check tracked source/fixture digests are unchanged by verifier execution. Preserve raw JSON outputs and report any failure/initial adverse trace.

## Scope limits

This is calibration of one classifier/case and one observed warning form, not proof of a general leak detector, a causal attribution of leaked objects, warning-free Godot execution, stdout-vs-stderr behavior, arbitrary engine warning rejection, or production audio correctness. The repair's distinction is exactly that a previously passing positive audio case becomes fail-closed for this observed ObjectDB diagnostic while unrelated export warnings remain allowed.
