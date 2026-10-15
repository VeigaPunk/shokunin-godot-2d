# Round 39 repeat-mode simplifier — read-only design

The requested mode can stay isolated from the existing baseline and no-focus control: recognize a dedicated `--repeat-right` mode in `slider_adjust.gd`, and add exactly two runner rows using it—connected positive and `--disconnect-signal` paired negative. Do not alter existing slider rows or add an unrelated mode.

Before implementation, run this exact sequence against real Godot in scratch: focused connected HSlider value 5; fresh `ui_right` pressed=true + one process frame; a second fresh pressed=true + one frame (without an intervening release); `ui_right` release + one frame; then two `ui_left` press/release pairs, each edge followed by one frame. Measure each `(value, receipts, Label.text)` tuple. Repeat identically disconnected. Hold if any value, receipt ordering, label, focus, or release result differs from the declared sequence. This is deliberate synthetic event injection, not an OS auto-repeat or physical timing test.

If measured as specified, the per-edge connected expected tuples are:

| Edge | Expected tuple `(value, cumulative receipts, Label.text)` |
|---|---|
| right press 1 | `(6, [6], "Value 6")` |
| right press 2 | `(7, [6,7], "Value 7")` |
| right release | `(7, [6,7], "Value 7")` |
| left press 1 | `(6, [6,7,6], "Value 6")` |
| left release 1 | `(6, [6,7,6], "Value 6")` |
| left press 2 | `(5, [6,7,6,5], "Value 5")` |
| left release 2 | `(5, [6,7,6,5], "Value 5")` |

Disconnected should check the same seven numeric values with `receipts=[]` and `Label.text == "Value 5"` at every edge. Keep the expected-negative signal diagnostic until after all seven edges; edge checks should establish numeric history and absence of receipts without prematurely exiting on the intended disconnected condition. This proves the full history rather than merely the final value.

Minimal assertion shape: preserve the existing setup/focus checks; in the new mode inject each edge and check its tuple immediately after its existing one-frame boundary. Explicit per-edge checks are preferable here to a generalized event/assertion framework: there are only seven edges and distinct messages identify the failed edge. Avoid a second snapshot abstraction or emitting signals manually—the connected Label must change only through `value_changed`. After the sequence, verify the focused connected receipts/labels (or the disconnected control’s expected absence) and print one distinct PASS signature for the positive runner row. Give the disconnected row a distinct expected diagnostic that is emitted only after completion. Keep `--no-focus` behavior outside this mode.

Hold concerns: (1) do not infer repeat behavior from the r38 observation alone; remeasure the entire sequence on the target Godot version, especially second pressed event without a release and both releases; (2) verify every callback’s cumulative receipt and signal-driven Label, not just final value; (3) keep the intended disconnected failure last; (4) confirm both new runner signatures/exit codes and no changes to prior result triples. I made no source or runner edits and gathered no new runtime evidence; this report is design guidance only.
