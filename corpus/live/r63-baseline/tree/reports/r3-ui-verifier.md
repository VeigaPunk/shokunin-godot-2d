# Round 3 UI verifier report — independent replay

## Replay evidence

I independently ran `python .shokunin/game-dev-2d/corpus/fixtures/run_battery.py --probe-failing` from the repository. It exited 0 on Godot 4.7.2 and wrote raw results to `corpus/live/runs/20261012T162357337589Z/verdicts.json`. The battery reports PASS for all 19/19 cases.

The UI positive case exited 0 and printed `PASS ui_signal connected=true hud_in_tree=true initial=Score: 0 hud_text=Score: 7`; its captured output has no `ERROR`, `SCRIPT ERROR`, or parse diagnostic. The disconnected-signal case exited 2 and produced exactly `ERROR: UI assertion failed: expected in-tree HUD text=Score: 7`, from the fixture assertion at `ui_signal_hud.gd:23`. It did not emit a script or parse error. Both raw output arrays are in the cited verdict JSON. The expected `ERROR` on this negative case is the deliberate `push_error`, not an unexpected runtime error.

The disconnected control takes the same fixture path and assertion, omitting the signal connection; it therefore fails to reach the expected updated text. As an additional scratch-only falsification, I changed the callback in this run's scratch copy to write `Wrong: 7` instead. The positive invocation then exited 2 at the same assertion. This confirms sensitivity to a wrong callback value in the synthetic probe; no tracked fixture was changed by that check.

All previous 17 cases remain PASS with the same exit codes as `corpus/lessons/r2-camera-verifier.json`. Their outputs are byte-for-byte identical for the 16 non-mutant cases; the broken-scene mutation also remains exit 2 with `chain incomplete` and the mutation verdict PASS, while its dynamic object identifier in the diagnostic differs. The 31 tracked fixture paths were SHA-256 hashed immediately before and after battery replay; every hash matched.

## Assessment and limits

This is narrow coverage of a synthetic, synchronous signal-to-`Label.text` path and detection of a disconnected connection (also a wrong callback value in the scratch falsification). It is not evidence about the production HUD, real model/state source, actual game scene wiring, or rendered UI. The test constructs its own signal, label, connection, and handler. `is_inside_tree()` and text equality establish tree membership and an in-memory property value only; no pixels, visibility, layout, clipping, theme, or legibility are checked. The runner accepts expected exit plus a log substring, so its signature contract could be spoofed by a changed probe that prints the signature without performing the assertion; current raw execution and scratch mutation provide evidence for this implementation, not a general proof of runner integrity.

## Axis verdicts

- Coverage: **improved** — 0 to 2 independently replayed UI cases, with the original 17 cases retained and all 31 tracked fixture paths unchanged.
- Depth: **unchanged** — no broader decision rule or production behavior tested.
- Calibration: **unchanged** — claims remain limited to the synthetic headless property-level probe; no rendered or production claim is supported.

No axis harm observed. This round is admissible only for the narrow synthetic headless signal/property behavior described above, not as production HUD or visual coverage. No fixture, runner, or log was edited; only this verifier report was written.
