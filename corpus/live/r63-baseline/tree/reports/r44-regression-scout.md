# Round 44 regression scout — second focus restoration

## Direct scratch measurement

Read-only scout plus an independent scratch-only direct probe at `corpus/live/r44-regression-scout/`. It copied only `project.godot` from the r43 scratch and added `r44_probe.gd`; no fixture/runner, engine/editor source, or seeded control was edited. Godot was `4.7.2.stable.arch_linux.ed1daf0bf`. Bounded command `timeout 15s godot --headless --path <scratch> --script res://r44_probe.gd` completed in 0.60s, exit 0.

The probe created a connected in-tree HSlider (min 0, max 10, step 1, initial 5), separate focusable in-tree Button, and Label. For each of nine fresh parsed `InputEventAction` events, it asserted expected GUI focus owner immediately before dispatch, yielded one process frame, then checked owner, slider value, cumulative `value_changed` receipts, and callback-driven Label. The first seven edges reproduce r43. Slider owned edge 0; Button owned edges 1–2; slider was restored for edges 3–4; Button owned edges 5–6; slider was restored again before edges 7–8.

| Edge | Owner before dispatch | Value / receipts / Label after frame |
|---|---|---|
| right press | HSlider | 6 / [6] / Value 6 |
| right press | Button | 6 / [6] / Value 6 |
| right release | Button | 6 / [6] / Value 6 |
| left press | HSlider restored | 5 / [6,5] / Value 5 |
| left release | HSlider | 5 / [6,5] / Value 5 |
| left press | Button after second handoff | 5 / [6,5] / Value 5 |
| left release | Button | 5 / [6,5] / Value 5 |
| left press | HSlider restored a second time | 4 / [6,5,4] / Value 4 |
| left release | HSlider | 4 / [6,5,4] / Value 4 |

Raw result:
```
R44 PASS values=[6.0, 6.0, 6.0, 5.0, 5.0, 5.0, 5.0, 4.0, 4.0] receipts=[6.0, 5.0, 4.0] label=Value 4
```
The positive exit 0 occurred only after all nine per-edge assertions. The observed hypothesis matches; no HOLD condition arose. This scratch alone does not establish battery integration/admission and cannot identify internal event consumption from unchanged edges.

## Prior evidence and caveats

- r41 measured a single mid-sequence focus handoff; r42 measured restoration then renewed adjustment; r43 measured a second handoff before the final left press. This scratch extends those bounded histories with a second restoration and renewed adjustment.
- Regression scout did not run the fixture battery or test tuple stability. The r43/r42 fault-injection caveat remains: an outer PASS may contain intentionally failing inner hang/timeout or unrelated-error probes; do not describe those inner results as clean PASS. Timeout evidence is bounded to tested direct-child behavior, not generic descendant cleanup.
- Export launch and export runs have separate bounds (historically 5-second startup and 60-second export); relative export target/path behavior has known failures. This UI probe provides no export readiness or portability evidence.
- Scope is headless Godot 4.7.2 with synthetic parsed actions and process-frame yields only—not OS auto-repeat, physical keyboard/timing, rendered/pointer behavior, accessibility, production, or a generic HSlider guarantee. No commit, push, or merge.
