# Round 31 focus-loss scout — independent scratch contrast

## Result
**Causal contrast reproduced** on Godot 4.7.2.stable.arch_linux.ed1daf0bf headless. The second synthetic `ui_accept` pair activated the Button in the uninterrupted focused path, but did not activate after explicit focus release between pairs. Both runs had the same scene, signal connection, input edge helper, and pair sequence apart from the `release_focus()` operation and corresponding expected receipt assertion.

## Method
Created an independent scratch project in `corpus/live/r31-focus-loss-scout/`, based on the r30 edge-scout project config, with `focus_loss.gd`. Both paths verified initial focus owner, then pressed/released action 1 and required receipts=1 / `Activated 1`. The treatment called `button.release_focus()`, awaited a frame, and checked `button.has_focus()==false` and viewport focus owner is null. Both paths then issued identical action-2 press/release edges with a frame after each edge. Focused positive expected second pair to increment to 2; focus-loss treatment expected unchanged 1 at both second edges. No tracked fixture/runner changes.

## Raw outcomes
- Focused positive: exit 0. Pair1 press: focused/owner true, receipts 0, Ready; pair1 release: focused/owner true, receipts 1, Activated 1; pair2 press: still receipts 1 / Activated 1; pair2 release: receipts 2 / Activated 2.
- Focus-loss treatment: exit 0. Pair1 matched positive. Immediately after release_focus: `has_focus=false owner_null=true`. Pair2 press and release remained receipts 1 / Activated 1, with no Button focus.
- Complete captured stdout: `focused.stdout.txt`, `focus-loss.stdout.txt`. Exact commands: `godot --headless --path .shokunin/game-dev-2d/corpus/live/r31-focus-loss-scout --script focus_loss.gd`; same plus `-- --drop-focus` for treatment.
- Scratch hashes: `project.godot` SHA-256 `823a355b748ad21cdc7657b59c51817d5ac6b277e2c9e18e1b31cb8caf2abcfb`; `focus_loss.gd` SHA-256 `79f98172281de52843ad4957b2c662c0adf9910404e8716b750bd183d6e1fa58`.

## Scope/caveats
This establishes headless synthetic `root.push_input(InputEventAction)` behavior for this Button in this isolated project: continued GUI focus is required for the second activation under these conditions. It does not establish physical keyboard or real-user timing, pointer activation, rendered UI, accessibility, or broader production focus behavior. Focus-loss path remains a valid fixture candidate; parent executor/verifier should independently evaluate integration and regressions.
