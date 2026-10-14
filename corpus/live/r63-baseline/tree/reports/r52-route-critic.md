# Round 52 route critic — SceneTree.push_input contrast

- Role: LEAF critic; no delegation and no tracked fixture/runner edits. Godot `4.7.2.stable.arch_linux.ed1daf0bf`.
- Scratch only: `.shokunin/game-dev-2d/corpus/live/r52-route-critic/scratch/project/slider_adjust.gd`. Copied the in-tree r51 fixture. Changed only edge10 dispatch in the `--observe-parsed-release` path to construct an `InputEventAction` with the same `action` and `pressed` fields and call `root.push_input(event)`; earlier ten edges still use `_action` / `Input.parse_input_event`. Added a scratch stdout line after the one-frame await to record observer, action state, numeric value, receipts, Label, focus, and callback.

## Direct result

Command: `godot --headless --path .shokunin/game-dev-2d/corpus/live/r52-route-critic/scratch/project --script slider_adjust.gd -- --repeat-right --second-focus-restore --observe-parsed-release`

Godot printed at edge10: `observer=3->4 pressed=true value=3.0 receipts=[6.0, 3.0] label=Value 3 focus=true callback=true`. The next existing post-release state assertion emitted `ERROR: SLIDER input-state post-release assertion failed: ui_left remains pressed` and exited 2. Thus `root.push_input` DOES deliver this matching release to the separate Node `_input` observer (same +1 receipt), but in this tested route it does NOT clear global `Input.is_action_pressed("ui_left")`. It fails before final eleven-edge summary/terminal assertion; it is not a successful clean route. This confirms the proposed contrast: observer receipt alone is not sufficient evidence of the combined parsed-event/state transition.

The comparable r51 named-verifier raw evidence reports the parsed route edge10 observer `3→4`, pressed `true→false`, numeric3/receipts `[6,3]`/Label `Value 3`, focus+callback true. R51 baseline itself completed the exact expected-negative terminal after all checks. The r52 alternate evidence above is a direct fresh scratch run; not an inference from API naming.

## Adversarial assessment / scope

- This disproves treating `_input` observer count by itself as a distinguishing signature of `Input.parse_input_event`: `root.push_input` also reached the observer. The additional `Input.is_action_pressed` postcondition is what discriminates these two routes here.
- The test shows delivery to this observer, not HSlider internal consumption or general event provenance. It exercises only synthetic action events and a headless Godot frame. No claim about OS input, physical timing, HSlider internals, rendering, pointer/accessibility, or production behavior.
- The exact alternate did not reach the expected terminal marker because the retained state assertion stopped the run. Therefore it is an adverse early ERROR, not a new expected-negative battery case unless an additive control intentionally expects this exact early failure and preserves the normal parse path.
- No tracked edits, seeded fixture changes, constants, commits, push, or merge. This scratch changes only the edge10 dispatch and adds diagnostic print; all prior owner/callback checks and value/full receipt/Label checks are retained.
