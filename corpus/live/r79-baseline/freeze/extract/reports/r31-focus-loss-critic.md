# Round 31 critic — second activation requires continued Button focus

## Result
The proposed focus-loss control is a causal contrast in Godot 4.7.2 headless `root.push_input(ui_accept)`: with unchanged Button setup, signal connection, and two press/release pairs, the focused positive reaches 2 receipts; releasing focus after completed pair 1, then verifying there is no GUI focus owner before pair 2, leaves the count at 1 and fails the existing release-2 assertion. This supports the narrow calibration claim that the second activation in this fixture requires continued Button focus.

## Evidence
- Immutable seeded Button fixture SHA-256: `edb777640fe19bdd62960ef18898f8fb181fcb28db57f20025f4430d1cbb68af`.
- Positive scratch: `.shokunin/game-dev-2d/corpus/live/r31-focus-loss-critic/positive`; same fixture hash. Command: `godot --headless --path <positive> --script res://button_activation.gd`. Exit 0; output: `edge=release1 focused=true ... receipts=1 text=Activated 1`, `step=2 focused=true ... receipts=2 text=Activated 2`, PASS `[0,1,1,2]`.
- Contrast scratch: `.shokunin/game-dev-2d/corpus/live/r31-focus-loss-critic/project`; only scratch script change adds `button.release_focus()` after release1’s completed assertion and before press2, awaits one frame, then checks `gui_get_focus_owner() == null` and `button.has_focus() == false`. Contrast fixture SHA-256: `d056eebbf63875b61db4419f9f435dd0e8085e855ec659e661c143efc791d2ca`.
- Contrast command is identical except scratch path. Exit 2 (expected failed positive assertion); output: release1 focused=true, receipts=1/Activated 1; immediately pre-press2 `focused=false button_has_focus=false receipts=1 text=Activated 1`; post-pair-2 `focused=false ... receipts=1 text=Activated 1`; failure at existing release2 check expecting `Activated 2`/2 receipts.
- The first exploratory insertion put focus release after press2 and would change edge order, so it was discarded. Final contrast inserts release only between the fully completed first pair and second press; only scratch files changed. No seeded fixture/runner, engine/editor, or controls were edited.

## Falsification checks
- **Automatic reacquisition:** excluded in the actual contrast at the critical point: after `release_focus()` plus `await process_frame`, both `has_focus()` is false and viewport GUI focus owner is null, immediately before press2. It remains false after pair2. Thus no auto-focus silently restores the Button in the tested sequence.
- **Stale held input / first-pair release mechanics:** unchanged fixture explicitly sent `ui_accept` pressed=true, awaited a frame, then pressed=false, awaited another frame before checking receipt 1 and releasing focus. The completed release1 receipt proves first pair processed. In the contrast, second press and release are likewise both sent and awaited; no second receipt occurs. It therefore is not an omitted-release / continuously-held test. No extra `Input.is_action_pressed()` assertion was added, so this does not independently prove internal action-state reset beyond observed edge path and completed receipt.
- **Same signal wiring:** positive and contrast preserve the exact seeded script’s connection `_on_button_pressed`; only scratch contrast inserted `release_focus` + owner checks after the first activation. No disconnection flags used.

## Limit
This establishes only the synthetic headless fixture behavior under the specified awaited `root.push_input` action edges, not pointer/physical input, rendered UI, focus policy generally, or production behavior. Parent should require the named verifier/full battery to adjudicate admission and regression.
