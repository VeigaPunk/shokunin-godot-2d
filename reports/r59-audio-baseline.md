# Round 59 independent seven-flag baseline

## Scope and method

Ran the declared seven opt-in flags, without `--probe-audio-warning`, against Godot 4.7.2. All runner output stayed in this leaf's unique scratch: `.shokunin/game-dev-2d/corpus/live/r59-audio-baseline/`.

Flags: `--probe-failing --probe-unrelated-error --probe-export-launch --probe-godot-error --probe-stream-attribution --probe-crash-exit --probe-timeout`.

## Initial run: retain as adverse telemetry

`runs/20261013T133544211489Z/verdicts.json` recorded 87 rows, 80 PASS and battery FAIL. During this run the tracked runner/fixture were changing (the audio fixture and runner now include the round's new cases). Seven existing slider cases failed, and seven prior tuple records differed from r58, including cases with matching signatures but a different verdict/exit. Thus this run is not a valid baseline comparison; I did not overwrite or discard its artifacts. It demonstrates that replay concurrent with tracked edits can produce an invalid comparison.

## Clean replay after tracked edits settled

`rerun/20261013T133843602231Z/verdicts.json`: **89/89 PASS** (78 ordinary rows, 2 mutants, 9 opt-in classifications). The 87 prior case rows match `corpus/lessons/r58-process-non-author.json` in `script`, `flags`, `expected_exit`, `actual_exit`, `signature`, `verdict`, and `error`: **87/87 stable**. The two additional cases are `audio_bus_route` and `audio_bus_route_invalid_control`.

The positive route case exits 0 and reports `requested=FixtureBus resolved_index=1 resolved_bus=FixtureBus playing=true position_advanced=true`. The paired `--invalid` control exits 2 and reports `requested=NoSuchFixtureBus resolved_index=0 resolved_bus=Master playing=true position_advanced=true`, with the expected `AUDIO BUS CONTROL ASSERTION FAILED` assertion. This is a baseline run, not my independent causal validation of the new fixture.

All nine opt-in classifications passed, including the expected paired inner classifications for Godot diagnostics, stream attribution, crash exit, and timeout. No additional opt-in flag was enabled. Runner SHA-256: `42104d95af5fcb98d742c495ee4562ea0c579c49d9ca22d11755302f685c31fb`; audio fixture SHA-256: `073319a042d153f066141666ebff34b91b7c5d481e93a46040b1ca6abb7a3212` at clean replay.

## Boundary

This establishes a clean exact-seven-flag replay and old-classification stability after edits settled. It does not itself admit the new claim; audible/rendered output, mixer fidelity, production audio, rights, and other platforms were not tested. No tracked files were edited by this baseline leaf.
