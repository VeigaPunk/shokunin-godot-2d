# Round 43 regression scout — second focus loss before final left press

## Direct scratch measurement

Read-only regression scout plus own scratch-only direct probe in `corpus/live/r43-regression-scout/` using real Godot `4.7.2.stable.arch_linux.ed1daf0bf`. Copied only `project.godot` from the r42 scratch project and created `r43_probe.gd`; no tracked fixture/runner, engine/editor source, or seeded control was changed. Bounded command: `timeout 15s godot --headless --path <absolute-scratch-path> --script res://r43_probe.gd`; completed in 0.61s with the deliberate expected-negative exit 2.

Connected in-tree HSlider (min 0, max 10, step 1, initial 5), separate focusable in-tree Button, signal-driven receipt list and Label. Seven fresh `InputEventAction`s were parsed, each followed by one process frame. Before every dispatch the GUI focus owner and slider focus state were asserted; after each, value, cumulative `value_changed` receipts, and Label were asserted. Slider was focused for the first right press; Button took focus for second right press and release; slider focus was restored for first left press and release; Button took focus again before the second left press and stayed focused for its release. All seven checks passed:

| Edge | Owner before dispatch | Value / receipts / Label after frame |
|---|---|---|
| right press | HSlider | 6 / [6] / Value 6 |
| right press | Button | 6 / [6] / Value 6 |
| right release | Button | 6 / [6] / Value 6 |
| left press | HSlider restored | 5 / [6,5] / Value 5 |
| left release | HSlider | 5 / [6,5] / Value 5 |
| left press | Button after second handoff | 5 / [6,5] / Value 5 |
| left release | Button | 5 / [6,5] / Value 5 |

Raw terminal evidence:
```
R43 EXPECTED-NEGATIVE values=[6.0, 6.0, 6.0, 5.0, 5.0, 5.0, 5.0] receipts=[6.0, 5.0] label=Value 5
R43 EXPECTED-NEGATIVE: final left press did not adjust after second focus loss
```
Exit 2 was emitted only after all seven per-edge assertions, via the distinct expected-negative diagnostic. This matches the requested r43 hypothesis; no HOLD condition observed in this scratch. Contrast: r42's measured restoration case kept slider focus through the final left press and reached 4/[6,5,4]/Value 4. The evidence isolates a second focus handoff immediately before the final left press in this deliberate sequence; unchanged value/receipts alone do not prove which Control internally consumed an unchanged action.

## Regression and harness boundaries

- r40 records the seven-edge focused/no-focus contrast; r41 records one mid-sequence handoff with later edges holding at 6/[6]; r42 records restoration followed by a second successful left adjustment to 4/[6,5,4]. They are read-only context, not r43 battery admission evidence. This scratch is not a full battery replay and makes no tuple-stability or admission claim.
- Fault-injection outer PASS can include intentionally failing inner hang/timeout and unrelated-error probes; do not call those inner cases clean PASS. Expected-negative fixture classification must require the intended diagnostic plus exit code, not exit 2 alone.
- Timeout evidence is limited to the runner's tested direct-child timeout/kill/reap behavior; it does not establish descendant cleanup or generic timeout safety. This scratch command's 15-second bound is not a broader timeout-safety claim.
- Export-launch and export-run probes have separate bounds (historically 5-second startup and 60-second export); relative export target/path behavior has known failures. No export readiness or portability inference follows from this UI result.

Scope: headless Godot 4.7.2, synthetic parsed actions and process-frame yields only—not OS auto-repeat, physical keyboard/timing, rendered or pointer behavior, accessibility, production, or a generic HSlider guarantee. No commit, push, or merge.
