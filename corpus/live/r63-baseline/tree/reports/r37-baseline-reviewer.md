# Round 37 baseline reviewer report

## Immutable r36 baseline

Reviewed immutable `HEAD` **e66314d93f498010ec6ca661d84a59a1178b0c18** (tree `c8bbd18fef2fc075330d6681b6492b21c97eb658`), with r36 fixture source commit `847efb8bf748b657f56fe4f745392140844fec48`. The r36 named-verifier artifact `.shokunin/game-dev-2d/corpus/lessons/r36-slider-verifier.json` SHA-256 is `ad79ea348031d2ce1048c3fbb105ff8a2b2b60cf966a5445394d30050b8ae2e1`; fixture SHA-256 `1c0850ff6daf74696c19cbe0bd45e66dc1d21e074d4b6b588c59166351576e87`; runner SHA-256 `5e6bc978a5098ac2ef104b378d3641902c8d595ad9fba57058e82abdc31f4b2a`.

Compared r35 verifier result rows against r36 by case. All **50/50 ordinary** `(verdict, actual_exit, signature)` triples are unchanged. r36 adds precisely `slider_adjust` (PASS, exit 0) and `slider_adjust_disconnected` (PASS, intended exit 2); aggregate 50 ordinary / 61 full. Both fixture and runner tracked hashes at current checkout match the immutable r36 values above; this reviewer made no tracked-source edits.

## First actual unfocused measurement — HOLD criterion not met

A separate disposable Godot 4.7.2 headless project under `.shokunin/game-dev-2d/corpus/live/r37-baseline-reviewer/` used the r36 fixture setup, connected `value_changed` handler, initial value 5, and parsed pressed/released `ui_right` then `ui_left` events. It omitted `grab_focus()` and any value mutation or manual signal emission. Before both actions Godot reported focus owner `<Object#null>` and `slider.has_focus() == false`. After right: value 5, receipts `[]`, Label `Value 5`; after left: value 5, receipts `[]`, Label `Value 5`. Command `godot --headless --path . --script slider_adjust.gd` exited 0 for this measurement harness. Thus the requested absent-focus control is causally supported by direct engine observation and the negative route does not move the value. It should produce expected negative exit 2 only after both actions are observed, as scoped in LOG; no contrary engine behavior observed.

Raw console measurement is captured in `measurement.txt`. Scope is only this synthetic headless Godot focus/input path; no claim about pointer, rendered GUI, or physical input.
