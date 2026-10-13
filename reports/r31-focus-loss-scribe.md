# Round 31 focus-loss scribe report

## Evidence and preliminary verdict

**Preliminary HOLD pending tracked-control replay and named non-author verification.** The read-only paired probe supports the proposed bounded focus-dependence contrast, but it does not validate the executor's shared tracked fixture/runner changes.

On Godot 4.7.2, the scout's disposable probe at `corpus/live/r31-focus-loss-scout/focus_loss.gd` was replayed in both arms. Raw stdout is preserved under my scratch directory as `corpus/live/r31-focus-loss-scribe/focused.stdout.txt` and `focus-lost.stdout.txt`.

- Focused arm: `button.has_focus=true`, owner=Button at pair1 press/release and pair2 press/release; receipts `0,1,1,2`, text `Ready, Activated 1, Activated 1, Activated 2`.
- Focus-loss arm: pair1 completes at receipt 1 / `Activated 1`; explicit `release_focus()` is followed by `has_focus=false`, owner null; identical pair2 press/release leaves receipt 1 / `Activated 1`, with focus still absent. Both runs exit 0.
- Same Button, connected `Button.pressed` handler, `ui_accept` `root.push_input` press/release events, and frame waits are used in the two scratch arms. The distinction is the release of focus after pair1.
- My scratch copy of the tracked r30 positive fixture still exits 0 with `[0,1,1,2]`, preserved at `corpus/live/r31-focus-loss-scribe/tracked-positive.stdout.txt`.

This is evidence for a bounded synthetic headless Godot path only. It does not establish the tracked control or runner case, nor rendered, pointer, physical-input, accessibility, timing, or production focus behavior.

## Prior-case comparison and attribution

`corpus/lessons/r30-edge-verifier.json` records the prior named-verifier baseline: 53/53 PASS (42 ordinary plus 11 mutant/probe records). I ran the full default-path command with the seven specified probes into `corpus/live/r31-focus-loss-scribe/full-run/`; it exited 0, also with 53/53 PASS. The saved comparison `corpus/live/r31-focus-loss-scribe/r30-vs-r31-case-comparison.json` shows all 53 prior case names retained and unchanged in `(verdict, actual_exit, signature)`, with no additions or removals.

**Important timing/scope caveat:** this 53-case run did not include a new focus-loss row. It is a replay of the prior battery, not a verifier run of the executor's proposed change. During this task I observed shared tracked diffs adding `--lose-focus-after-first` and `button_activation_focus_loss`; I did not edit or stage either fixture or runner. Those changes need their own verification before admission. Direct pair outputs are raw stdout, not battery verdicts.

## Bounds checklist

- [x] Same input action and connected signal path in both disposable arms.
- [x] Focus ownership checked initially and after pair1; focus-loss arm checks null owner and `has_focus=false` before pair2, and remains unfocused after pair2.
- [x] Both complete press/release pairs are retained; no manual signal emission or receipt mutation.
- [x] Preserve the r30 53-case comparison separately; do not count the paired control as independent coverage-axis gain.
- [ ] Named non-author verifier replays the tracked focus-loss row and confirms runner count/signature and full-battery preservation.
- [ ] Fault-injection/meta result and tracked fixture/runner hashes captured before/after verifier replay.
- [x] No engine/editor source or seeded-control edits, no commit/push/merge by this scribe.

## Recommendation

Hold admission until a non-author verifier replays the tracked contrast and confirms the full battery preserves the 53 prior outcomes. If it does, the bounded calibration claim is that the second headless `ui_accept` activation in this fixture requires continued Button focus after the first completed activation. Do not generalize beyond that path. No constants changed by this scribe.
