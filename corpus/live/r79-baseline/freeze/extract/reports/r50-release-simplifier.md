# Round 50 release simplifier — bounded scratch evidence

## Result
Godot 4.7.2 supports the proposed additive release-after-press probe. In my isolated scratch copy, the inherited ten edges were preserved, and a fresh `ui_left` release was added as edge 10. The observed eleventh check retained numeric value `3`, cumulative receipts `[6, 3]`, Label `Value 3`, and a connected callback. The probe then emitted its unique expected-negative diagnostic and exited 2. This supports the declared calibration distinction for synthetic parsed actions plus frames; it does not justify broader input or UI claims.

## Scratch and commands
- Unique scratch project: `/tmp/r50-release-simplifier-2417005` (copied from immutable `.shokunin/game-dev-2d/corpus/fixtures`; only scratch `slider_adjust.gd` edited).
- New-branch command: `godot --headless --path /tmp/r50-release-simplifier-2417005 --script slider_adjust.gd -- --repeat-right --second-focus-restore --release-after-late-reconnect-press`
- Exit 2 after eleven checks. Marker: `SLIDER_RELEASE_AFTER_LATE_RECONNECT_PRESS values=6,6,6,5,5,5,5,4,4,3,3 receipts=6,3 Labels=Value 6,Value 3 callback_connected=true`; diagnostic: `SLIDER RELEASE AFTER LATE-RECONNECT PRESS ASSERTION FAILED: expected no new receipt after eleven checks`.
- Paired positive command with unchanged r49 flag: `godot --headless --path /tmp/r50-release-simplifier-2417005 --script slider_adjust.gd -- --repeat-right --second-focus-restore --press-after-late-reconnect`; exit 0 with the prior ten-edge `values=6,6,6,5,5,5,5,4,4,3 receipts=6,3 Labels=Value 6,Value 3` marker.

## Checks and limits
The scratch-only branch asserts expected focus owner and callback connection state before every event. After each event plus one frame, it checks numeric value, the complete receipts array, and Label text. No seeded file, runner, engine, editor, or other in-tree file was changed by this lane. This is a causal scratch probe, not an independent verifier or full battery replay. Scope is limited to Godot's synthetic `Input.parse_input_event` path and frame observations; no claim about physical input, OS repeat, rendering, pointer/accessibility behavior, production readiness, or generic replay.
