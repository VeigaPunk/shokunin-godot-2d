# Round 28 mutation reviewer

## Scope and method
Independently exercised the current button fixture's connected and disconnected controls, then made an isolated scratch copy under `corpus/live/r28-mutation-reviewer-scratch/project/` and removed only the second `_send_action(button)` invocation. The scratch retained its step-2 assertion. No tracked fixture/runner edits were made by this reviewer; no engine/editor or seeded controls were changed.

## Results
- Connected baseline: `godot --headless --path .shokunin/game-dev-2d/corpus/fixtures --script button_activation.gd --` exited 0 and printed `PASS button_activation in_tree=true initial=Ready step_texts=[Activated 1,Activated 2] receipts=[1,2]`.
- Disconnected control: same command with `-- --disconnect-signal` exited 2 at the intended first-step assertion: `expected step1 text=Activated 1 receipts=1, got receipts=0 text=Ready`. This is a real signal-disconnect failure, not setup failure.
- Scratch-only omitted-second-action mutant: `godot --headless --path .shokunin/game-dev-2d/corpus/live/r28-mutation-reviewer-scratch/project --script button_activation.gd` exited 2 at the retained step-2 assertion: `UI BUTTON ASSERTION FAILED: expected step2 text=Activated 2 receipts=2, got receipts=1 text=Activated 1`. The setup and step 1 succeeded; the failure specifically detects the absent second activation.

Actions were dispatched through the fixture's `ui_accept` input route, with press and release, and `process_frame` between separate activations. The positive aggregate receipt and final text are consistent with two sequential activations. This finite test does not establish pointer hit-testing, real-user debounce/rate behavior, or arbitrary mutation-proof provenance.

## Reviewer verdict
Both connected positive and disconnected control behaved as intended; suppressing the second action in a disposable copy triggers the intended second-step assertion. No unrelated outcomes assessed here. No constants changed by reviewer.
