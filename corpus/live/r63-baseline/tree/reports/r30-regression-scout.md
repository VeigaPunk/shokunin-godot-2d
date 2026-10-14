# Round 30 regression scout — focus, disconnected, and opt-in boundaries

Read-only review of the r30 claim, tracked Button fixture/runner, and named r29 verifier evidence. I did not run Godot or edit fixture/runner files. My only write is this assigned report.

## Button regression boundary

The current tracked `button_activation.gd` still has the r29 focus setup: positive arm verifies `ActivateButton` owns viewport focus; `--no-focus` releases focus and verifies no owner; both use the same `ui_accept` route. The positive and `--disconnect-signal`/`--no-focus` cases currently assert only after complete press/release pairs. Thus r30's intermediate edge assertions are not yet present in the inspected source. Preserve both controls and their intentional diagnostics while adding press-only/release observations; the disconnected case should still fail its intended assertion with zero receipts/Ready, not setup. The prior r29 direct and full-replay evidence reports disconnected expected exit 2 at step 1 (`receipts=0`, `Ready`) and unfocused expected exit 2 at step 1 with verified absent focus owner. These are prior-run facts, not a fresh r30 execution.

`corpus/lessons/r29-focus-verifier.json` is top-level PASS with 53 records (42 ordinary +2 mutants +9 opt-ins), including the focused positive and both negative button cases. Its button signatures/output are post-pair step states `[Activated 1, Activated 2]` / receipts `[1,2]`; do not treat it as evidence for the proposed per-edge assertions. The positive currently uses Godot 4.7.2 headless `root.push_input(ui_accept)`, not pointer activation or rendered UI.

## Export, timeout, and fault caveats

The same r29 full raw records `probe_export_launch` PASS with positive assertion true / negative false, and `probe_timeout` PASS with inner classifications `[false, true, false]`. These are regression baselines only; this scout did not replay them for r30. The separate r29 fault-injection raw is an executor self-test: outer/meta PASS encloses intentional adverse inner failures (including timeout and unrelated-error cases). It is not seeded fixture evidence and must not be counted as a Button pass or clean fault-free run. A named r30 full replay is required before claiming these paths unchanged.

## Bounded conclusion

No source-level change outside the intended Button edge split appears required. Keep the r29 focus owner checks, disconnected diagnostic, ordinary count, and export/timeout paths intact; compare actual exits/signatures and prior records on the named r30 replay. This review makes no fresh runtime or regression-free claim, and no claim about pointer, rendered UI, production focus, debounce, or real-user behavior.
