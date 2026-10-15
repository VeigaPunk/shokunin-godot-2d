# Round 21 named non-author verifier — crash-exit

## Replay

Independently ran the full battery with Godot 4.7.2 using the default absolute `corpus/live/runs` path:

`python .shokunin/game-dev-2d/corpus/fixtures/run_battery.py --probe-failing --probe-unrelated-error --probe-export-launch --probe-godot-error --probe-stream-attribution --probe-crash-exit`

Run: `20261013T010223634713Z`. Exit 0; raw top-level verdict `PASS`, **45/45 PASS**: 35 ordinary cases, 2 mutation cases, and 8 opt-in cases. Export readiness and both export-launch variants passed; no export failure was hidden. Comparison with the preceding r20 verifier artifact found all 44 prior cases retained the same PASS verdict. The three displayed `FAIL` inner classifications (unrelated-error and stream reject arms, and expected fault injections below) are expected negative controls; their enclosing probe cases pass.

## Crash-exit evidence

Raw detailed artifact is preserved byte-for-byte as `corpus/lessons/r21-crash-detail.json`; the full raw battery JSON is preserved byte-for-byte as `corpus/lessons/r21-crash-verifier.json`.

Both arms ran the same `res://crash_exit_probe.gd` and emitted exactly `CRASH_EXIT_PROBE: expected signature`; both expected exit code 1. The normal arm exited 1, had `error: null`, and classified true. The live reject arm showed `process_was_running: true` after marker observation, received SIGTERM, returned **-15** (POSIX signal return convention), had `error: null`, and classified false. Probe verdict PASS. This supports only this bounded real-Godot normal-exit versus SIGTERM distinction, not general crash or process-tree guarantees.

No subprocess for this run remained: process search for the unique run path returned empty after completion. Tracked fixture/runner SHA256 values were identical before and after this verifier execution. (The repository already had unrelated dirty round-21 edits at start; I made no tracked edits.)

## Separate fault injection

Ran `--fault-injection` separately; exit 0, meta verdict PASS. Preserved raw meta JSON byte-for-byte as `corpus/lessons/r21-fault-verifier.json`. Its expected outcomes were hang timeout => inner FAIL, clean expected negative => PASS, unrelated error => FAIL; all expected signatures were observed. This is Python fault-injection evidence, not a Godot crash test.

## Scope

No runner or fixture edits, commits, pushes, or merges. Did not perform a separate sabotage of the signal guard; the real signal reject exercised its ordinary expected-exit guard directly. The prior relative-`--runs` export-path exception noted in the standing history is not resolved by this default-path successful replay.
