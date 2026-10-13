# Round 27 critic — Button activation

Read-only critique of `corpus/fixtures/button_activation.gd`; all mutations below were isolated under `corpus/live/r27-button-critic/falsification/` and did not touch the assigned fixture or runner.

## Findings

- Positive runs on Godot 4.7.2 headless and passes: in-tree Button and Label, initial `Ready`, final `Activated`, one callback. The implementation sends `InputEventAction("ui_accept")` using `root.push_input()` after `grab_focus()`, then releases. This exercises a routed UI action, not `Button.press()` or physical/pointer interaction.
- Actual paired `--disconnect-signal` control fails closed as desired: `receipts=0 text=Ready`, exit 2 with `UI BUTTON ASSERTION FAILED`. Setup was reached and assertion was the expected final-state failure, not a setup failure.
- Direct receiver-callback spoof inserted before activation is rejected on the connected positive (`receipts=2`, exit 2), because the real activation also invokes the callback. Direct `button.pressed.emit()` spoof is likewise rejected on the connected positive (`receipts=2`, exit 2).
- **Adverse falsification:** when the receiver callback was directly invoked but the signal was disconnected, the check passed (`receipts=1`, `text=Activated`) despite there being no signal connection. Thus the assertion pair does not independently prove that the label change came from the `pressed` signal. The actual unmodified disconnected control still fails, but the positive/control logic can be spoofed by a callback executed in the disconnected arm. Suggested fix: keep callback receipt count but make it represent only signal delivery, e.g. have the callback increment and update label, and ensure no direct receiver invocation exists in either arm; the fixture currently meets this normally. To strengthen mutation resistance, a scratch-only test explicitly confirmed that a direct invocation in the disconnected arm false-passes. Do not claim the probe resists arbitrary fixture spoofing.
- Manual signal emission was also rejected on positive due to two callback receipts (manual emit plus input activation). This supports detection of additive manual-emission spoofing, but does not establish that UI action alone caused the signal absent a stronger per-arm guard.

## Boundary

No pointer hit-testing, rendered UI, keyboard focus/accessibility, or real scene was tested. No engine/editor or seeded control changed. The round's proposed narrow headless UI signal coverage is plausible, but this direct-call adverse limits the causal claim; parent should decide whether to require a correction before admission. The runner inclusion and independent full-battery replay were not evaluated here.
