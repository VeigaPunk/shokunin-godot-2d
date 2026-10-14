# Round 27 regression scout — UI / timeout / export boundaries

Read-only review only. I did not edit fixtures or runner, create a fixture, run the battery, or delegate. This report is scoped to the existing UI path and prior timeout/export path fixes.

## Existing UI signal is not a button activation path

`corpus/fixtures/ui_signal_hud.gd` builds an in-tree `CanvasLayer` and `Label`, checks initial text `Score: 0`, connects the script's custom `score_changed(value)` signal to `_on_score_changed`, directly calls `score_changed.emit(7)`, then asserts `Score: 7`. `--disconnect-signal` skips that custom signal connection. It is useful direct signal-to-label coverage, but it does not instantiate a `Button`, activate one through its API, observe `Button.pressed`, or test the button-to-label chain. The new positive should activate via `button.emit_signal("pressed")` or the engine’s documented button activation API rather than call the label receiver; the paired disconnected arm should do the same activation and fail only the final label assertion, not fail setup. Be explicit in evidence about what the API call means: programmatically emitting `pressed` tests signal dispatch, not physical input/hit testing.

## Existing timeout calibration fix and limits

Round 26 adjusted the opt-in Godot timeout threshold from 0.75s to 3.0s after adding a valid fixture that prints its marker then waits 1.5s before clean exit. The recorded verifier evidence has the old-bound slow-clean arm time out after marker, the new-bound arm exit 0, and a hold-open arm still time out after marker; direct child reaped in timeout arms. This addresses a measured false timeout on this one bounded synthetic startup shape while retaining the specific hold-open negative. It is not arbitrary hang detection, descendant/process-tree cleanup, a cross-platform guarantee, or production startup reliability. Keep 3.0s threshold and 1.5s delay stated as fixture/environment constants, not general reliability claims.

## Existing export path normalization and caveats

Round 25 normalized both Godot export target call sites with `Path.resolve()`: readiness export path and launch-probe executable path. Prior paired trials isolated relative target spelling as the failure mechanism on the observed Godot 4.7.2 Linux host (relative target failed; absolute target succeeded, while relative project root with absolute target succeeded). A later explicit-relative full replay passed 50/50, including readiness, expected missing-preset negative, and both launch arms; the earlier 49/50 replay remains an adverse historical result because the launch target was not yet normalized. This is a narrow CLI/path-form fix, not evidence that all export failures are fixed, nor broad production export reliability. Absolute path behavior, preset, artifact-size/hash checks, and platform are environmental details; successful synthetic exports do not prove a shippable game export.

## Regression relevance to this round

The proposed Button fixture is additive and can remain isolated from existing signal, timeout, export probe code. When parent runs full replay, compare the prior 50 rows and expected signatures/exits unchanged; new UI positive/negative rows should add coverage without changing those existing controls. No conclusion on regressions is possible from this read-only inspection alone.
