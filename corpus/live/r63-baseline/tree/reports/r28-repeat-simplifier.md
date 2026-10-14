# Round 28 repeat simplifier review

Read the standing brief and Round 28 claim in `LOG.md`, plus the tracked `button_activation.gd` fixture and battery case declarations. This is a read-only minimality review; I did not edit fixture or runner code.

## Smallest useful assertion shape

The existing signal receiver can derive distinct states from its receipt count: increment once, then set the label to `"Activated %d" % pressed_receipts`. Keep the current in-tree Button/Label setup, `ui_accept` route, signal connection, and paired positive/disconnected CASES. Replace the one-shot input block with two explicit activation pairs. For each pair, push pressed then released `InputEventAction` through `root.push_input`, await one `process_frame`, and immediately assert the expected cumulative receipt count and matching label (`1` / `Activated 1`, then `2` / `Activated 2`). The frame wait between completed pairs is the separation; asserting after release means an extra `pressed` on release also fails the exact count/state check. No new ordinary CASE is needed.

Keep assertion diagnostics tied to the step and expected/actual receipt and text, so a missing second event is distinguishable from setup failure. A scratch-only sabotage should remove/suppress the second pair while retaining its assertion: setup remains valid, first checkpoint passes, and the second checkpoint fails with one receipt / `Activated 1` rather than two / `Activated 2`. Do not add a tracked `--skip-second` branch just for sabotage; it expands fixture behavior without improving the ordinary observation.

## Boundaries / falsification notes

- Test the actual focused Button input path, not direct calls to the receiver or manual `pressed.emit`.
- Release between activations and await a frame before sending the second press. Assert post-release receipt count at both checkpoints; do not infer the second event from final text alone.
- The disconnect control should still take the same first action and fail its first positive checkpoint with zero receipts and `Ready`; ensure its intended diagnostic remains accepted by the existing negative classifier.
- Keep CASES unchanged (41), and replay the full battery plus existing opt-in probes in the verifier. This supports bounded repeated headless delivery only, not pointer input, real-time debounce/rate behavior, or arbitrary-mutation-proof signal provenance.

No constants or tracked files changed. No engine/editor or seeded control files were touched.
