# Round 45 adversarial critic — signal disconnect paired-history claim

## Direct scratch result

Read-only critic used a fresh scratch copy at `.shokunin/game-dev-2d/corpus/live/r45-double-restore-disconnect-critic/` with the in-tree `project.godot` and `slider_adjust.gd`; only the scratch copy received a branch to assert the proposed disconnected nine-edge history. Real Godot reported `4.7.2.stable.arch_linux.ed1daf0bf`.

Commands run from the repository root:

```sh
godot --headless --path .shokunin/game-dev-2d/corpus/live/r45-double-restore-disconnect-critic --script slider_adjust.gd -- --repeat-right --second-focus-restore
godot --headless --path .shokunin/game-dev-2d/corpus/live/r45-double-restore-disconnect-critic --script slider_adjust.gd -- --repeat-right --second-focus-restore --disconnect-signal
```

Connected paired case exited 0 after the original nine checks with values `6,6,6,5,5,5,5,4,4`, receipts `[6,5,4]`, and final Label `Value 4`. The disconnected scratch case asserted owner before every edge (HSlider at 0,3,4,7,8; Button at 1,2,5,6), and numeric value, empty receipts, and `Value 5` Label after every fresh parsed event plus frame. It completed all nine checks, then emitted `SLIDER_DOUBLE_RESTORE_DISCONNECTED values=6,6,6,5,5,5,5,4,4 receipts=[] Label=Value 5` and exited 2 as the expected negative. Thus the observed numeric trace is invariant under disconnect in this paired scratch; the signal receipts and callback-owned Label are not.

## Wiring and falsification review

In the existing fixture, `disconnected` is derived from `--disconnect-signal`; the only signal wiring is `if not disconnected: slider.value_changed.connect(_on_value_changed)`. The new scratch branch kept the same nine actions, focus handoffs/restorations, per-edge focus-owner assertions, and value expectation array as r44. It checks receipts and Label independently after every edge, and gives exit 2 only after the nine checks. No production/in-tree edit was made by this critic.

The current in-tree r44 branch already checks disconnected-vs-connected receipts and Labels per edge, but its disconnected expectation is not yet `receipts=[]`, `Label=Value 5` (it currently expects the connected prefixes in that path). Therefore this scratch evidence supports the hypothesis but is **not** proof that the integrated candidate or its runner classification is correct. If integrated, disconnected assertions must be explicit per edge; do not simply turn off the callback while retaining connected expectations. Confirm the runner expects exit 2 and the unique disconnected diagnostic, and preserve the existing r44 connected positive branch.

No numerical/focus difference was found. This is not evidence of internal consumption of unchanged edges: owner assertions identify GUI owner before dispatch, not which control consumed an action. No claim about OS repeat, physical input/timing, rendered/pointer behavior, accessibility, production, or generic HSlider behavior. No engine/editor or seeded files changed; no commit/push/merge.
