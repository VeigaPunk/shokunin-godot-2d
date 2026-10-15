# Round 31 named non-author focus-loss verifier

## Verdict: verified; no discrepancy found

I independently replayed the working-tree candidate without editing either tracked source file. The requested exact default-path command exited **0**, with **54/54 PASS = 43 ordinary + 11 probe/mutant records**. Raw output copied byte-for-byte from `.shokunin/game-dev-2d/corpus/live/runs/20261013T045836789733Z/verdicts.json` to `corpus/lessons/r31-focus-loss-verifier.json` (SHA-256 `e0f59818e105537ce800fec3d7c62f68123fe0c952db35e7f87b6eed7288c30b`). Against committed r30 raw `.shokunin/game-dev-2d/corpus/lessons/r30-edge-verifier.json`, all **53 prior cases** have identical `verdict`, `actual_exit`, and `signature`; the sole added case is `button_activation_focus_loss` with expected/actual exit 0 and PASS. The output's two inner intentional negative classifications are not battery failures.

The separate `--fault-injection` command exited 0 as a harness, with intentional inner FAILs for `fault_hang` (timeout, exit null) and `fault_unrelated_error` (exit 2); `fault_clean_expected_negative` PASSed. Its raw artifact was copied byte-for-byte to `corpus/lessons/r31-fault-verifier.json` (SHA-256 `cc50beaf84dfdc2010358eafda5dbb50e217ed6327d8e39fd7b3538cc612fd8f`). This is separate from, and not conflated with, the 54-row seeded battery.

## Direct Godot checks

Godot: `4.7.2.stable.arch_linux.ed1daf0bf`. Direct focused replay exited 0 and produced first completed pair receipts/text `1 / Activated 1`, then second pair `2 / Activated 2`. The `--lose-focus-after-first` treatment exited 0 on **two independent repetitions**. Both logged first pair `focused=true`, receipts 1 / `Activated 1`; after release-focus the viewport owner was null and `button.has_focus()` false; after press2 and release2 both remained unfocused, receipts remained 1 / `Activated 1`. Thus both edges were sent, and second-action suppression is not being used to produce the expected result. `--disconnect-signal` and `--no-focus` each still exited 2 at intended release1 with zero receipts / `Ready`; the initially-unfocused case reported no focus.

I also ran a disposable sabotage copy in `corpus/live/r31-focus-loss-verifier/button_activation_sabotage.gd`: removed only `button.release_focus()` while retaining the null-owner / no-focus mid-sequence assertion. The treatment failed with exit 2 at `UI BUTTON mid-sequence focus loss setup assertion failed` (observed focus remained true), rather than passing. No tracked file was changed for this check.

## Integrity, scope, and limits

Before and after replay, working-tree source hashes were stable: `button_activation.gd` `08b6447773bfaeaa2398e402b5c6506a7607914720b0ef27461b8d7a0a9cb645`; `run_battery.py` `3b8d400479e9efb55f8983dfb508c4ad75b55d0c658e5c8bf10738013e2e8928`. Their only tracked diffs from r30 are the assigned focus-loss fixture behavior and one battery row; no callback/manual signal emit or action-edge suppression was introduced. I wrote only this verifier report, the two requested lesson JSON files, and my own scratch/live verifier area. I did not edit tracked source, commit, push, or merge.

This evidence is limited to **headless synthetic `root.push_input(ui_accept)` in this fixture**. It does not test rendered UI, pointer input, physical keyboard/user timing, or production focus behavior.
