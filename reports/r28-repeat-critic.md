# Round 28 critic — repeated Button activations

Scope: read-only review of the tracked `button_activation.gd` and battery signature plus scratch-only Godot probes. No tracked source edits.

## Evidence

- The tracked fixture now sends `ui_accept` twice through `_send_action`, separated by `await process_frame`, and checks the resulting ordered values `Activated 1`/receipt 1 then `Activated 2`/receipt 2. `button_activation` battery expectation matches its PASS line. The disconnected control expects the first-step assertion diagnostic and exit 2.
- Replayed the tracked fixture in isolated scratch on Godot 4.7.2: connected path PASS, exit 0, receipts `[1,2]`; `--disconnect-signal` failed at step 1 with zero receipts and `Ready`, exit 2.
- Replayed a scratch-only `--skip-second` suppression (same tracked script; no second `_send_action`): it failed the second-step assertion with receipt 1 / `Activated 1`, exit 2. It does not false-pass when the second action is actually omitted.
- Inspected the tracked callback and fixture: `_on_button_pressed` is connected only via `button.pressed.connect`; no direct `_on_button_pressed()` invocation and no manual `pressed.emit()` occur. This is source inspection, not arbitrary-mutation provenance proof.
- Separate scratch probe sent one `ui_accept` press, awaited a frame, then release and awaited a frame: observed `n=0/Ready` after press and `n=1/Activated 1` after release. A second release left `n=1`. This confirms the observed activation is delivered on release in this headless route and that a duplicate release alone did not add a receipt in that probe.

## Critic limits / diagnostic

`_send_action` pushes press and release back-to-back before yielding. Thus the fixture validates two distinct action pairs and per-pair cumulative receipts, but does **not** capture state between press and release or establish press-time delivery. Its release behavior is implicit in the paired route; the isolated probe shows release-delivery semantics and duplicate-release stability for this Godot version. Keep the claim bounded to headless paired `ui_accept` activations, not real-time key timing/debouncing.

Setup has a separate `UI BUTTON setup assertion failed` branch before actions. The connected and disconnected replays reached their intended success / step-1 assertion respectively; neither was a setup diagnostic. The disconnected failure is not mistaken for a setup failure. No hidden direct callback/manual signal exists in current tracked fixture, but an adversarial edited fixture could fabricate receipts; no general mutation resistance claim is supported.

**Verdict suggestion:** two-step count and skipped-second falsification supported for inspected current fixture. Release duplicate narrowly supported by separate scratch probe, with ordering caveat above. No arbitrary-source provenance claim. This is one critic lane, not independent admission verification.
