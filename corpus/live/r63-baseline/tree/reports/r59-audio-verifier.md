# Round 59 named non-author audio verification

## Result and bounds

Ran the fresh declared seven opt-ins with Godot 4.7.2 and unique `--runs` under `.shokunin/game-dev-2d/corpus/live/r59-audio-verifier/full-runs`; did not enable `--probe-audio-warning`. Battery verdict: **89/89 PASS** (87 prior case records plus two additive audio cases). This is an independent replay, not an audio-output/audibility test. Positive route-resolution/playback-state evidence is bounded to headless Godot 4.7.2. No audible/rendered output, mixer fidelity, production sound, asset rights, or other-platform claim.

## Exact invocation and raw evidence

Command (stdout/stderr captured verbatim at `full.stdout`; every result retains command, output arrays, expected/actual exits and errors in the run JSON):

```sh
python3 /home/vgpnk/Projects/prymeagnt/game-dev-2d/.shokunin/game-dev-2d/corpus/fixtures/run_battery.py --godot godot --runs .shokunin/game-dev-2d/corpus/live/r59-audio-verifier/full-runs --probe-failing --probe-unrelated-error --probe-export-launch --probe-godot-error --probe-stream-attribution --probe-crash-exit --probe-timeout > .shokunin/game-dev-2d/corpus/live/r59-audio-verifier/full.stdout 2>&1
```

Run directory: `.shokunin/game-dev-2d/corpus/live/r59-audio-verifier/full-runs/20261013T134219828150Z`. Full structured raw evidence is `verdicts.json`; supporting raw artifacts are `export-launch-verdicts.json`, `godot-error-verdicts.json`, `stream-attribution-verdicts.json`, `crash-exit-verdicts.json`, `timeout-verdicts.json`, plus probe-specific files in the same run. `full.stdout` records all runner output including expected inner negative classifications (`godot_error_unrelated` false and `stream_reject` false) within passing outer probes. The eight rows named `probe_*` include the runner's additional export-readiness and independent-process meta records; the seven requested flag arguments above were supplied exactly.

All 87 prior rows from `corpus/lessons/r58-process-non-author.json` match all requested fields exactly: `script`, `flags`, `expected_exit`, `actual_exit`, `signature`, `verdict`, and `error` (**87/87**, no deltas). The two additional records are `audio_bus_route` and `audio_bus_route_invalid_control`.

## Audio observations

- `audio_bus_route`: exit 0; `requested=FixtureBus resolved_index=1 resolved_bus=FixtureBus playing=true position_advanced=true`.
- `audio_bus_route_invalid_control`: exit 2; exact diagnostic `AUDIO BUS CONTROL ASSERTION FAILED: requested invalid route silently fell back to Master`; the output also records `requested=NoSuchFixtureBus resolved_index=0 resolved_bus=Master playing=true position_advanced=true`. Thus playback advances in the invalid case too; rejection is due to route resolution/fallback, not transport failure.
- Inspected both complete audio outputs: neither contains an ObjectDB leak warning nor any `WARNING:` line.

## Scratch-only sabotage / fault evidence

Separate copies and all mutations stayed under `.shokunin/game-dev-2d/corpus/live/r59-audio-verifier/fault-injection`. No tracked fixture or runner was changed.

1. Positive sabotage replaced `player.bus = requested_bus` with `player.bus = "Master"`. Hash of copied fixture before/after: `073319a042d153f066141666ebff34b91b7c5d481e93a46040b1ca6abb7a3212` → `54029e129cad3f6b036463823517003ecac2fea51c31abf81dc6fbcbdadfa4bc`. Command/output/exit in `positive-sabotage.json`: same positive route fixture, exit 2, `in_tree=true playing=true advanced=true requested=FixtureBus resolved_index=0 resolved_bus=Master`, diagnostic `AUDIO BUS ROUTE ASSERTION FAILED: explicit non-Master route/playback mismatch`. Transport remained active, but classifier/assertion rejected the missing explicit non-Master route.
2. Negative sabotage first attempted to add the bus with an indentation-damaging textual replacement; the script parse-failed (exit 1). Retained in `negative-sabotage.json` as adverse attempt, not treated as route evidence. Corrected the scratch-only mutation so a real `NoSuchFixtureBus` is added even in invalid mode. Before/after hashes: `073319a042d153f066141666ebff34b91b7c5d481e93a46040b1ca6abb7a3212` → `21b29858e6abee9d998832bcec3db70b27463dc91c322a7525e58d4ba355483c`. Command/output/exit in `negative-sabotage-real-bus-invalid-arg.json`: exit 2 and `requested=NoSuchFixtureBus resolved_index=1 resolved_bus=NoSuchFixtureBus`; exact `AUDIO BUS CONTROL ASSERTION FAILED: requested bus resolved to a non-Master route`. Thus the control rejects when its expected fallback terminal is absent, not merely on process exit.

The runner separate `--fault-injection` mode was **not run**; only the required positive/negative audio route sabotage arms were run in the isolated copy. The original scratch-copy fixture was restored between sabotage arms. Tracked SHA-256 before and after verification: `run_battery.py` `42104d95af5fcb98d742c495ee4562ea0c579c49d9ca22d11755302f685c31fb`; `audio_bus_route.gd` `073319a042d153f066141666ebff34b91b7c5d481e93a46040b1ca6abb7a3212` (same as independent baseline report). No editor or engine settings were mutated. The executor's report notes its earlier transient seven-flag failure and the separate corrected clean run; those adverse attempts were not erased or reclassified as this verifier's result.

## Disposition

Named non-author replay supports the narrow route-resolution plus playback-state distinction and retains all 87 prior classifications. The scope does not claim general audio signal flow or audibility.
