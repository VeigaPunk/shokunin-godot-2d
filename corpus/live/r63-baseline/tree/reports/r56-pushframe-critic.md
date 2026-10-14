# Round 56 push-frame-first critic — corrected causal replay

- Role: LEAF critic, no delegation; tracked files read-only. Read the standing mission, Round 56 declaration, and Round 52–55 reports/lesson records. Runtime: Godot 4.7.2.stable.arch_linux.ed1daf0bf.
- Unique corrected scratch: `.shokunin/game-dev-2d/corpus/live/r56-pushframe-critic-corrected-scratch/project/`, copied from fixture. Modified only the scratch branch derived from r55 to test the declared order: matching pushed release + awaited frame; then `Input.action_release("ui_left")` + awaited frame. Both substeps assert observer/action/numeric/receipts/Label/focus/callback. No tracked, seeded, engine/editor files or constants changed.

## Corrected two-substep measurement

Command: `godot --headless --path . --script slider_adjust.gd -- --repeat-right --second-focus-restore --push-frame-then-clear-release`.

- After `root.push_input(matching ui_left=false)` + `await process_frame`: observer **3→4**, `Input.is_action_pressed("ui_left")=true`, numeric **3.0**, receipts `[6.0,3.0]`, Label `Value 3`, slider focus owner true, callback connected true.
- After `Input.action_release("ui_left")` + `await process_frame`: observer remains **4**, pressed=false, numeric **3.0**, receipts `[6.0,3.0]`, Label `Value 3`, focus owner true, callback connected true.
- Every explicit scratch assertion passed, as did the existing eleven-edge history/terminal assertions. Process exits 2 at its established exact expected-negative terminal after all eleven checks; this is fixture's intentional terminal, not a failed substep assertion.

This matches Round 56's declared hypothesis and demonstrates bounded complementary synthetic substeps. It adds no evidence about necessity of awaits, physical timing, HSlider internals, OS/render/pointer/accessibility/production.

## Prior wrong-control run retained adverse

The prior scratch run `.shokunin/game-dev-2d/corpus/live/r56-pushframe-critic-scratch/project/` incorrectly asserted pressed=false after the first pushed-release frame, though LOG r56 explicitly predicts pressed=true. It measured observer 3→4 and pressed=true, then stopped before direct clear. Its report wording incorrectly treated that as claim falsification. This was a wrong-control/assertion setup error, not adverse evidence against the declared hypothesis; its attempted test and prior report classification are superseded by this corrected report. No tracked file was edited in either run.

No battery, fixture/runner edits, constants, commits, push or merge. No setup failures in corrected run.
