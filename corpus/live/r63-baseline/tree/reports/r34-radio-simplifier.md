# Round 34 — RadioButton simplifier review

**Scope:** Read-only fixture-design review for two `RadioButton`s in one exclusive `ButtonGroup`, focused `ui_accept` on B then A, exact `toggled(bool)` receipts and Label behavior, plus a disconnected-consumer control. No source/runner/engine/seeded-control edits, no runtime probe, and no delegation.

## Minimal state and signal assertions

Build one in-tree UI with A and B both assigned to the same `ButtonGroup` configured exclusive. Set A selected before connecting the consumer (or otherwise explicitly account for any setup emission); await a frame, then assert A selected, B unselected, and Label `A`. Focus B and assert it owns GUI focus before sending input. Do not directly mutate either button after setup and do not manually emit `toggled`.

For each `ui_accept` press/release action, await the same frame boundary used by the existing focused-control fixtures, then assert **both** properties, not only the newly activated button:

| Checkpoint | A selected | B selected | Connected receipt suffix | Connected Label |
|---|---:|---:|---|---|
| Setup | true | false | `[]` | `A` |
| After focus/action B | false | true | `[(A,false),(B,true)]` | `B` |
| After focus/action A | true | false | `[(A,false),(B,true),(B,false),(A,true)]` | `A` |

Represent each callback as a pair `(control_id, bool)` in one shared ordered receipt array, with callbacks bound to the relevant control identity. This checks exact order and values and distinguishes the two controls; counts alone or a bool-only array cannot prove which RadioButton changed. A handler should update the Label only on `toggled(true)`, so the old control's false notification cannot overwrite the newly selected option. The exact ordering above is a **hypothesis to validate**, not runtime evidence: if Godot emits a different order, record the real order from an independent scratch probe and use that source-backed order consistently. Do not loosen to unordered membership.

## Disconnected consumer contrast

Run the same two-control setup, focus, and B-then-A input sequence, disconnecting only the consumer callbacks. Assert after B that A/B are false/true, then after A they are true/false; receipts remain `[]` and Label remains `A` at both checkpoints. Only after both property transitions, fail at the intended final missing-signal assertion (exit 2), rather than treating a setup/focus/input failure as the contrast. This establishes that the exclusive group transitions independently of the connected consumer. It does not establish signal delivery in the disconnected arm.

## Keep it small / caveats

- Use one group, two controls, two actions, one Label, and one shared receipt array. Avoid a general event framework or extra fixture modes.
- Make the group relationship observable by asserting mutual exclusion after **each** action; do not infer exclusivity merely because the expected selection became true.
- Connect after initial selection if setup should not count as a transition; assert the initial receipt list is empty. Otherwise make setup receipt semantics explicit rather than silently discarding callbacks.
- Compare exact callback identity/value sequence and exact Label at checkpoints. The paired disconnected case is a control for consumer side effects, not a second independent proof of signals.
- Keep setup assertions separate from the final intentional disconnected failure so its failure location is attributable.

**Assessment:** These are the minimal assertions for the requested exclusive-selection coverage and consumer contrast. Godot callback ordering, initial assignment semantics, and focus activation are unmeasured here; this report is design guidance only and cannot support admission or a coverage verdict. No constants changed.
