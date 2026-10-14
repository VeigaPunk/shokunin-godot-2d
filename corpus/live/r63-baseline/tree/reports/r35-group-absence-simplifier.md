# Round 35 — group-absence simplifier

**Recommendation:** use the smallest paired control: keep both native `Button(toggle_mode=true)` controls, A alone assigned to a `ButtonGroup`, and leave B unassigned. Keep initial A selection, connected `toggled(bool)` callbacks that append `A:<bool>` / `B:<bool>` and update the Label only on `true`, and the existing focused B then A `ui_accept` procedure unchanged. Compare exact state, callback receipts, and Label after each action. This isolates B's group membership; no other control or input mode changes.

**Scratch evidence (Godot 4.7.2, headless):** `.shokunin/game-dev-2d/corpus/live/r35-group-absence-simplifier/ungrouped_probe.gd` is the scratch-only probe. Output:

```text
setup A=true B=false receipts=[] label=A
after_B A=true B=true receipts=["B:true"] label=B
after_A A=true B=true receipts=["B:true", "A:true"] label=A
```

For the grouped arm, the existing `corpus/fixtures/button_group_selection.gd` was replayed unchanged with the same engine/input approach. It reports `after_B A=false B=true receipts=["A:false", "B:true"] label=B` and `after_A A=true B=false receipts=["A:false", "B:true", "B:false", "A:true"] label=A`. This matches the r34 recorded sequence. The paired observations show group membership—not action/focus/consumer wiring—distinguishes exclusive state. The ungrouped arm's B action leaves A selected; subsequent A action is already-selected and produces `A:true` in this engine, so measure rather than assume it is a no-op.

**Minimal assertion/admission guidance:** after each action assert and print the complete `(A pressed, B pressed, receipts, Label)` tuple. In an ungrouped arm, assert expected *non-exclusive* states `(true,true)` after B and after A, and exact receipts/Label as measured above. Do not turn the expected contrast into a generic group guarantee. Because the two-action signature has evidence and makes the pair stronger, retain both actions rather than stopping at the first contrast. Keep disconnection as a separate signal-consumer diagnostic; it is not needed in this causal negative. Scratch only; no tracked fixture, runner, seeded corpus, engine/editor change.

**Scope limit:** native toggle-mode `Button` with `ButtonGroup` membership only; not `RadioButton`, rendered/pointer behavior, physical timing, accessibility, or production-wide group semantics. This is design/evidence for the calibration move, not full battery admission or non-author verification.
