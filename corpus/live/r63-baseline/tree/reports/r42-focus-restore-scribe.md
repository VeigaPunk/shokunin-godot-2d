# Round 42 focus-restoration scribe: evidence and admission checklist

## Direct scratch evidence

The scout's disposable scratch run used Godot `4.7.2.stable.arch_linux.ed1daf0bf` and exited 0. Scratch project: `.shokunin/game-dev-2d/corpus/live/r42-focus-restore-scout/scratch`; probe: `slider_adjust.gd`; raw stdout/stderr: `../godot.log` relative to the scratch directory. The probe used a connected in-tree HSlider (`min=0`, `max=10`, `step=1`, initial `5`), a signal-connected Label, and a separate focusable in-tree Button. It created a fresh `InputEventAction` for each of seven actions and awaited one process frame after each.

| Edge | Action | Focus owner before event | Value after frame | Full receipts | Label |
|---:|---|---|---:|---|---|
| 0 | right press | HSlider | 6 | [6] | Value 6 |
| 1 | right press | Button | 6 | [6] | Value 6 |
| 2 | right release | Button | 6 | [6] | Value 6 |
| 3 | left press | HSlider (restored) | 5 | [6, 5] | Value 5 |
| 4 | left release | HSlider | 5 | [6, 5] | Value 5 |
| 5 | left press | HSlider | 4 | [6, 5, 4] | Value 4 |
| 6 | left release | HSlider | 4 | [6, 5, 4] | Value 4 |

This supports the declared scratch hypothesis, including owner checks immediately before every event and value/history/Label checks after each frame. No value or signal was artificially changed. The scout reports its first scratch assertion incorrectly expected a receipt for the unchanged second edge; it corrected that expectation to the declared cumulative history and the successful run then matched. Treat the corrected run/log as candidate evidence; retain the initial probe mistake as telemetry, not a behavioral failure.

## Admission checklist (still pending parent/verifier)

- [x] Direct real-Godot scratch hypothesis checked before any fixture/runner edit; observed edges match the claim.
- [x] Connected signal consumer and changing Label checked alongside numeric state; focus owner checked before each edge.
- [ ] Executor confirms any in-tree candidate change is causal and limited to `slider_adjust.gd` / `run_battery.py`; otherwise no source change.
- [ ] Named non-author verifier replays the full default-path battery and required fault probes from the declared baseline; retain raw lesson artifact and report.
- [ ] Compare all 66 baseline `(case, verdict, actual_exit, signature)` rows unchanged and nine opt-in classifications stable; candidate adds exactly one intended ordinary PASS exit-0 row (55→56 ordinary, 66→67 full) only if causal.
- [ ] Focus-restoration sabotage / omitted-edge checks fail at the appropriate assertion, not via an unrelated setup or terminal condition.
- [ ] Record all failed/hung attempts as telemetry and distinguish them from the successful candidate evidence.
- [ ] Parent records axis verdict from verifier evidence; no inference of admission from this scratch-only report.

## Scope

This is synthetic parsed actions plus process frames in a headless Godot scratch project. It does not establish OS auto-repeat, physical keyboard timing, rendered/pointer behavior, accessibility, production behavior, or a generic slider guarantee. No engine/editor or seeded-control files were changed by this scribe. No commit, push, or merge.
