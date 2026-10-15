# Round 45 — minimal disconnected double-restore negative design

## Scratch finding

Real Godot 4.7.2 scratch (only `corpus/live/r45-double-restore-disconnect-scratch/`) ran the r44 nine parsed-action/frame sequence twice. Connected positive exited 0 with values `6,6,6,5,5,5,5,4,4`, receipts `[6,5,4]`, and labels `Value 6`, `Value 5`, `Value 4`. `--disconnect-signal` alone exited 2 in the existing baseline probe as expected (`values=6,5`, receipts `[]`, label `Value 5`). But the requested paired flags `--repeat-right --second-focus-restore --disconnect-signal` currently exit **0**, printing the ordinary positive PASS marker and receipts `[6,5,4]` in the marker.

The reason: `slider_adjust.gd`'s `--second-focus-restore` branch checks expected values, receipt history, and labels edge-by-edge with disconnect-aware expectations, but its terminal path unconditionally prints positive and quits 0. The current test does not make an honest disconnected negative outcome. HOLD; do not edit fixture/runner or admit calibration.

## Smallest dedicated design

Keep the existing connected positive branch and its `slider_adjust_repeat_right_second_focus_restore` row byte-for-byte/behaviorally unchanged. Add a **separate** disconnected double-restore branch selected by `--repeat-right && --second-focus-restore && --disconnect-signal`, before the existing positive branch (or by an explicit terminal `if disconnected` after its same nine checked edges). Reuse exactly the existing nine actions, focus transfers, owner-before-action checks, and disconnect-aware per-edge assertions: expected numeric values `[6,6,6,5,5,5,5,4,4]`, receipts `[]`, and Label `Value 5` after every edge. Only after all nine assertions, emit a unique terminal diagnostic/marker for this negative and `quit(2)`; it must not print the existing positive PASS marker. No added action or focus timing.

Add one runner case with a distinct name, the same fixture and flags plus `--disconnect-signal`, expected exit 2, and the exact unique terminal diagnostic as its expected signature/error. Preserve the current connected row, all prior rows, and classifier rules. Ensure setup/edge assertion failures cannot accidentally match the terminal negative signature; parse/runtime errors remain disqualifying. This is a design note only, no source/runner changes made.

## Scope and caveat

The direct scratch establishes the numeric/focus sequence is achievable, and shows the existing branch can pass the disconnect-aware loop while returning the wrong terminal status. It does **not** establish the requested dedicated row, full battery compatibility, or prior-row preservation. Calibration claim therefore remains unproven/held pending a causal implementation and replay. Synthetic headless parsed events plus frames only; no OS repeat, physical keyboard/timing, rendering, pointer/accessibility, production behavior, or inference about internal consumers of unchanged edges.
