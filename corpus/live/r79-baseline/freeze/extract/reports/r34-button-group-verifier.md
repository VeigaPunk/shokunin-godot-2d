# Round 34 named non-author verifier — ButtonGroup selection

## Scope and claim

I independently verified only two native Godot `Button` controls with `toggle_mode = true` sharing one `ButtonGroup`. This is **not RadioButton coverage**: the literal `RadioButton` parser/type failure remains adverse telemetry (including the separately reported hung `ClassDB` attempt terminated by the parent). No claim is made about pointer/rendered UI, physical timing, accessibility, or production behavior. I changed no tracked source or fixture; my additions are this report, the two requested raw JSON copies, and scratch artifacts under `corpus/live/`.

## Runner replay and baseline comparison

Executed from the repository root:

```text
python .shokunin/game-dev-2d/corpus/fixtures/run_battery.py --probe-failing --probe-unrelated-error --probe-export-launch --probe-godot-error --probe-stream-attribution --probe-crash-exit --probe-timeout
```

Exit 0; **58/58 PASS** (47 ordinary, 2 mutants, 9 opt-in/probe rows). The 56 pre-existing r33 `(verdict, actual_exit, signature)` triples all match `r33-checkbox-edge-verifier.json` exactly; 0 differences. Both new rows PASS: connected exits 0 with expected signature; disconnected exits 2 with the intended missing-signal signature. Inner adverse probe classifications (`godot_error_unrelated`, `stream_reject`) remain recorded as expected probe telemetry, not battery regressions. Byte-identical receipt: `corpus/lessons/r34-button-group-verifier.json` (SHA-256 `3e705bd77ae4cb62b70c2cf18b9f9f2364122d462256211095ad1e598e3974ce`).

Separate `--fault-injection` outer run exited 0. Its raw evidence records `fault_hang` and `fault_unrelated_error` as inner FAIL, and the clean expected negative as PASS; it is not a seeded battery result. Byte-identical `corpus/lessons/r34-fault-verifier.json` (SHA-256 `cd49178d1f70d6a05dc89abffb6d9f756f22cb258b9f1854133597e4592849de`).

## Direct Godot and adversarial check

Copied the tracked fixture and project config to verifier scratch and ran both actual headless Godot 4.7.2 commands. Connected exited 0: initial A=true/B=false and no setup receipts; after focused B action A=false/B=true, receipts `[A:false,B:true]`, Label B; after focused A action A=true/B=false, receipts `[A:false,B:true,B:false,A:true]`, Label A. Disconnected traversed the same two exclusive property transitions, receipts remained empty and Label remained A, then exited 2 at the intended final missing-signal assertion. No selection property was mutated as stimulus and no signal was manually emitted.

For causal sabotage, a scratch-only copy omitted `b.button_group = group` while retaining selection and receipt assertions. It exited 2 at `BUTTON_GROUP selection assertion failed after B: expected A=false B=true`, before later assertions. The shared-group property assertion therefore detects this omission. Scratch path: `corpus/live/r34-button-group-verifier/`; sabotage: `corpus/live/r34-button-group-verifier-sabotage/`.

## Disposition

Evidence supports the corrected, bounded **ButtonGroup toggle-mode Button** claim. Depth unchanged; coverage improved by two ordinary rows for grouped mutual exclusion; calibration unchanged; no harm observed in the full finite replay. Constants changed from r33: ordinary rows 45→47 and full rows 56→58. No RadioButton claim. Hashes of the fixture and runner were recorded before verification; I did not edit either.
