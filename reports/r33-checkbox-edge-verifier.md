# Round 33 named non-author CheckBox edge verifier

## Replay

I independently ran the requested default-path battery from the repository root:

```text
python .shokunin/game-dev-2d/corpus/fixtures/run_battery.py --probe-failing --probe-unrelated-error --probe-export-launch --probe-godot-error --probe-stream-attribution --probe-crash-exit --probe-timeout
```

Exit 0; **56/56 PASS** (45 ordinary, 2 mutants, 9 opt-in/probe rows). The raw full receipt is byte-identical at `corpus/lessons/r33-checkbox-edge-verifier.json` to the runner output under `corpus/live/runs/20261013T051711263477Z/verdicts.json`. Comparing all 56 result records against r32: all **54 non-CheckBox** `(verdict, actual_exit, signature)` tuples are identical (45 have signatures; 9 probe summaries have no signature). Both CheckBox rows retain PASS and their prior exits (connected 0, disconnected expected-negative 2). Connected positive signature intentionally changed to `edge_states=[false,true,true,false]`; disconnected signature is unchanged.

Direct current-source Godot 4.7.2 headless runs:

- Connected exit 0: `press=false release_state=true receipts=[true] label=On`; then `press=true release_state=false receipts=[true, false] label=Off`; final PASS includes `[false,true,true,false]`.
- `-- --disconnect-signal` exits 2 only after both printed release observations: true then false state, receipts always `[]`, Label always `Ready`; final diagnostic is the expected missing toggled sequence.

## Independent release-omission probe

Copied the fixture project into `corpus/live/r33-checkbox-edge-verifier/release-omission/` and omitted the first release event only in that scratch copy, retaining the release1 state assertion. The setup/focus and press1 checks pass; the run exits 2 at `CHECKBOX release-only state assertion failed: expected checked=true got=false`. No tracked sabotage switch or source change was used.

## Separate battery fault injection

`--fault-injection` exited 0 and classified its harness PASS. Its raw receipt is `corpus/lessons/r33-fault-verifier.json`. Interpret the inner intentional adverse cases separately: `fault_hang` FAIL (timeout at 0.25s), `fault_clean_expected_negative` PASS (exit 2), `fault_unrelated_error` FAIL (exit 2). These are injected faults, not seeded battery failures.

## Integrity and limits

Tracked hashes before/after replay and scratch mutation remained unchanged:

- `checkbox_toggle.gd`: `a9dea80b3b14e0643c4402b4d1a9c709ef836760b4439dcb20c5bb4b7614ec9b`
- `run_battery.py`: `e584780f2b88c57947cfa723ba8f47dbce01b24d49ce1b0077555d6fff0f38f2`

**Verification supports the declared depth move**: the focused synthetic `root.push_input(ui_accept)` path is separately observed at each press and release, and the first-release omission is caught at the intended state assertion. Evidence is headless-only. It does not establish pointer or rendered interaction, physical timing, accessibility, or production-user behavior. No tracked edits, commit, push, or merge by this verifier.
