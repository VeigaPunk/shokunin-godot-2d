# R54 order scout — independent scratch

## Result

In Godot `4.7.2.stable.arch_linux.ed1daf0bf`, the reversed edge-10 sequence **mimicked both controls** on all measured assertions. In an isolated scratch copy, the eleven-edge history kept edges 0–9 parsed and changed edge 10 to `Input.action_release("ui_left")` followed by `root.push_input(matching ui_left release)`, then awaited the same `process_frame`. It passed pre-edge owner/connection and edge-10 pressed-state checks, observer-count increment exactly 3→4, global `ui_left` state true→false, and numeric value 3 / receipts `[6,3]` / Label `Value 3`; the callback remained connected. All per-frame edge checks completed before the fixture's intentional exact-negative terminal diagnostic/exit 2.

Independent scratch controls also completed their corresponding checked edge histories: r51 parsed edge10 and r53 push-then-clear. Both produced observer 3→4, action false, numeric3 / `[6,3]` / `Value 3`, focus/callback true; each ended on its expected-negative terminal diagnostic/exit 2. Thus the reverse ordering differs in ordering but not in the measured synthetic route state; r53's push-then-clear order is not necessary to obtain these measurements. This is causal scratch evidence supporting the executor's separate additive `--clear-then-push-release` expected-negative branch/row/allowance proposal. I made **no tracked edits**.

## Scratch and commands

Unique scratch root: `corpus/live/runs/r54-order-scout-independent/` (reverse under `scratch/`, controls under `r51-parsed/` and `r53-push-clear/`). Each was copied from the fixture tree; only scratch `slider_adjust.gd` was changed for the reverse branch, and the standard scratch-only two-frame readiness adjustment was applied to `causal_chain.gd`. Commands used Godot 4.7.2 headless with `--repeat-right --second-focus-restore` and the respective mode flag. Reverse output marker: `SLIDER_COMPOSITE_PUSH_AND_CLEAR values=6,6,6,5,5,5,5,4,4,3,3 receipts=6,3 Labels=Value 6,Value 3 callback_connected=true`; control outputs have corresponding parsed/composite markers. Each process exits 2 because these modes intentionally assert an expected negative after their positive measured checks; this is not a battery PASS.

Adverse setup attempt retained in the same scratch: first reverse attempt had a nil observer because I did not initially add the new mode to the scratch-only observer initialization condition; it hung/was terminated (exit143). I corrected that scratch-only condition and reran successfully. Do not count the failed attempt as evidence. A malformed shell invocation also returned exit127 before launching Godot; no fixture ran. No engine/editor or seeded edits, and no tracked source changes.

## Boundary

This only concerns this synthetic Godot 4.7.2 action-routing sequence and its observed node/state/value/callback receipts. It makes no claim about HSlider internal consumption, OS or physical input/timing, rendering, pointer/accessibility behavior, or production behavior.
