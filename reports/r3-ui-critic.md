# Round 3 UI/HUD signal fixture — adversarial critique

## Scope and evidence inspected

Read the Round 3 declaration in `LOG.md`, `corpus/fixtures/run_battery.py`, `corpus/fixtures/ui_signal_hud.gd`, and the raw battery record `corpus/live/runs/20261012T162109514460Z/verdicts.json`. The recorded UI positive and disconnected-signal case both have their intended exit/signature and are marked PASS in this run. This is a static/adversarial review of the test contract, not an independent replay or rendered-UI verification.

## What the fixture demonstrates

`ui_signal_hud.gd` creates a Label, initializes it to `Score: 0`, connects a locally declared `score_changed` signal to a handler that assigns `Label.text`, emits 7, and asserts the property becomes `Score: 7`. Its `--disconnect-signal` control skips that connection and reaches the same assertion, which exits 2. This is a useful same-script, same-assertion check that detects this particular missing-connection mutation.

## False-positive risks (defect accepted)

1. **Not the game HUD or its wiring.** The fixture synthesizes the signal, Label, connection, and handler in one test script. It never loads the production HUD or observes the production score/state source. A broken production signal route, wrong HUD node path, absent HUD from a real scene, or stale real score can coexist with this PASS. Describe this narrowly as an isolated signal-to-Label-property probe, not production HUD coverage.
2. **Property is not rendered UI.** `Label.text` equality proves an in-memory property update only. It does not prove the Label enters the scene tree/visible viewport, is drawn, legible, positioned, unclipped, or visible against the background. Headless mode has no screenshot/pixel assertion. Do not call it visual/HUD rendering coverage.
3. **Self-fulfilling local wiring.** The handler writes the expected literal-derived text and the test checks that same object immediately after synchronous emit. A test-only implementation can satisfy this while the production updater is absent or wrong. Strengthen only if scope requires real HUD behavior: instantiate the real scene/controller and drive the real state change, then read the resulting HUD node (and use a separate rendered check for pixels).
4. **Runner signature is not a proof of assertion execution.** The positive runner case accepts exit 0 plus a printed `PASS ui_signal hud_text=Score: 7` substring. A modified probe that prints that line and quits 0 without checking/updating the Label would be accepted. Similarly, expected-failure cases accept exit 2 plus the error substring; an unrelated path can emit the same text. The fixture currently performs the assertion, but the runner's signature contract alone is spoofable. Prefer structured result output tied to measured before/after values, and mutation evidence from the identical assertion path.
5. **Potential error noise in negative controls.** Runner rejects `SCRIPT ERROR:` and `Parse Error:` but otherwise relies on exit/signature. Unexpected runtime errors accompanying the expected signature are not categorically rejected. Keep captured output inspection in replay evidence; do not interpret expected exit alone as successful behavioral detection.

## False-negative risks (working behavior rejected)

1. The positive requires exact text `Score: 7`; a legitimate HUD using a different localization, prefix, number formatting, or equivalent presentation would fail. This is appropriate only for this hard-coded fixture contract, not a general HUD acceptance test.
2. A legitimate production updater that defers/coalesces updates until a process frame would fail because the fixture checks immediately after `emit`. This particular test defines a synchronous local handler, so it should not be generalized to asynchronous production UI.
3. If the intended contract allows hidden HUDs or no HUD in headless mode, any future extension to require visibility/drawing could reject valid headless behavior. Separate property-level and rendered-visibility contracts rather than conflating them.

## Behavioral mutation check

The current `--disconnect-signal` branch is a credible narrow behavioral mutation: it omits only the connection while retaining the same Label setup, signal emission, and `Label.text == "Score: 7"` assertion. The raw run records exit 2 and the intended assertion-failure message for this negative case, while the positive records exit 0 and the expected text. This supports detection of a disconnected local signal in this toy fixture. It does **not** demonstrate sensitivity to a broken production HUD route, to incorrect value source/format, or to invisible/non-rendered UI. For stronger mutation evidence, compare positive and disconnected scratch executions from the same script and assert the observed pre/post text and precise intended failure, not just an exit code and log substring.

## Recommendation

Count this as narrow headless coverage of synchronous signal-to-`Label.text` propagation plus a disconnected-connection control. Do not claim actual production HUD integration or rendered UI coverage. No source or fixture edits were made during this review.
