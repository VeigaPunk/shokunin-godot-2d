# Round 34 executor — ButtonGroup toggle-mode Button selection

## Scope correction and failed draft telemetry
The declared RadioButton concept was invalid: Godot 4.7.2 has no `RadioButton` type. The first draft using that name failed type resolution; it is not fixture evidence and does not support a RadioButton claim. After the LOG correction, I replaced it with two native `Button` controls (`toggle_mode=true`) sharing one `ButtonGroup`; no custom class was introduced. The tracked fixture is `corpus/fixtures/button_group_selection.gd`, and the two runner rows are `button_group_selection` and `button_group_selection_disconnected`.

## Fixture and causal evidence
A starts selected during setup (`a.button_pressed = true`) before signal connections and before input; this is setup state, not a stimulus or manually mutated transition. The fixture focuses B, sends `ui_accept` press/release, then focuses A and sends the same action. Connected callbacks record each actual `toggled(bool)` event; when true they update the Label. It asserts group state after each action and exact ordered receipts. Disconnected arm runs the same focus/actions, verifies A=false/B=true after B while receipts remain empty and Label remains A, then verifies A=true/B=false after A and reaches the intended final missing-signal assertion (exit 2).

Godot 4.7.2 scratch connected: exit 0, `after_B A=false B=true receipts=[A:false,B:true] label=B`; `after_A A=true B=false receipts=[A:false,B:true,B:false,A:true] label=A`; PASS. Scratch disconnected: exit 2 only at intended final signal assertion after both state transitions; output shows after B `A=false B=true receipts=[] label=A`, after A `A=true B=false receipts=[] label=A`. Thus the changed property transitions are produced by the shared ButtonGroup and are distinct from absent consumer callbacks.

## Full battery replay
Author replay:
`python .shokunin/game-dev-2d/corpus/fixtures/run_battery.py --probe-failing --probe-unrelated-error --probe-export-launch --probe-godot-error --probe-stream-attribution --probe-crash-exit --probe-timeout --runs .shokunin/game-dev-2d/corpus/live/r34-radio-executor/runs`

Exit 0, battery verdict PASS, **58 results** (47 ordinary +2 mutants +9 opt-in probes). New connected case PASS/exit 0 with signature `PASS button_group_selection exclusive=true toggled=[A:false,B:true,B:false,A:true] labels=[B,A]`; disconnected PASS/actual expected exit 2 with signature `ERROR: BUTTON_GROUP SIGNAL ASSERTION FAILED: expected transitions [A:false,B:true,B:false,A:true], got []`. Raw battery: `corpus/live/r34-radio-executor/runs/20261013T052316781880Z/verdicts.json`; full captured output/probe artifacts alongside it. The godot-error and stream subprobes display their expected inner negative classifications as `FAIL` lines, while their enclosing probe summaries and overall battery are PASS; do not treat those inner expected adverse outcomes as battery regressions.

## Verdict / limits
Coverage improved: focused two-control exclusive selection with exact ordered `toggled(bool)` callback receipts and Label behavior, plus paired disconnected consumer retaining both property transitions. Depth unchanged; calibration unchanged; no harm observed in this finite replay. Counts changed 45→47 ordinary, 56→58 full. No RadioButton coverage claim; no pointer/rendered UI, physical timing, accessibility, production behavior, or generic ButtonGroup guarantee. No engine/editor/seeded fixture edits. No commit/push/merge.
