# Round 35 executor — ButtonGroup absence control

**Result: causal paired control implemented and replayed.** This is native `Button(toggle_mode=true)` selection with a `ButtonGroup`, not RadioButton coverage.

## Change

Added opt-in `--ungroup-b` in `corpus/fixtures/button_group_selection.gd` and one ordinary row in `corpus/fixtures/run_battery.py`. The control leaves A in the ButtonGroup but omits B's `button_group` assignment. Both buttons still use toggle mode, share the same Label and `toggled(bool)` receipt handlers, and receive the same focused synthetic `ui_accept` actions B→A with the same frame waits. The grouped and disconnected paths remain otherwise intact.

Expected negative is evaluated only after both actions. In ungrouped mode, each button toggles independently; after B: `A=true B=true`, receipts `[B:true]`, Label `B`; after A: `A=true B=true`, receipts `[B:true,A:true]`, Label `A`. It then exits 2 at `BUTTON_GROUP ABSENCE ASSERTION FAILED after B→A: expected exclusive selection, got A=true B=true`. Disconnected mode continues to have no receipts and Label A, and is not the new ordinary row.

## Evidence

- Godot `4.7.2.stable.arch_linux.ed1daf0bf`.
- Paired full battery command: `python3 .shokunin/game-dev-2d/corpus/fixtures/run_battery.py --probe-failing --probe-unrelated-error --probe-export-launch --probe-godot-error --probe-stream-attribution --probe-crash-exit --probe-timeout --runs .shokunin/game-dev-2d/corpus/live/r35-group-absence-executor-full`
- Raw battery: `.shokunin/game-dev-2d/corpus/live/r35-group-absence-executor-full/20261013T053318856711Z/verdicts.json`; outer battery exit 0, **59/59 PASS** (48 ordinary, 2 mutants, 9 opt-ins). New expected-negative row itself records expected/actual exit 2 and PASS, with both after-action observations above. Full replay's intended-inner-failure probes also preserve outer PASS semantics; godot-error unrelated and stream-reject are expected adverse inner classifications.
- Baseline raw: `corpus/lessons/r34-button-group-verifier.json` (58 result rows). Compared each matching row's verdict/actual-exit/signature to the full replay: **all 58 old rows identical**; no disconnected fixture changed.
- Runner also passed isolated plain replay: `.shokunin/game-dev-2d/corpus/live/r35-group-absence-executor-replay2/20261013T053244944164Z/verdicts.json` (59/59).
- Final source SHA-256: fixture `bc9f4aadfcfb2ea4930985ca4acb4d440ad3fd3c99411c891ca434e748053957`; runner `78072024d092964c9e214be418df10933092caf3f73168cbc27ef189f43ebc87`.

Earlier drafts stopped after B or used an unrecognized expected-error classification. They are retained as live scratch telemetry; the cited final full replay is after both control-flow and classifier corrections.

## Scope

Evidence supports this paired synthetic headless control only. It does not establish pointer/rendered UI, physical timing, accessibility, production behavior, generic group guarantees, or RadioButton coverage. Only constants added are `--ungroup-b`, the new ordinary expected-exit-2 assertion, and its exact after-B/after-A assertions. No engine/editor/seeded edits, commit, push or merge.
