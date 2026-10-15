# Round 33 CheckBox release-omission mutation review

## Scope
Scratch-only review of the CheckBox edge-depth mutation. No tracked fixture or runner edits. Scratch project: `.shokunin/game-dev-2d/corpus/live/r33-checkbox-mutation-reviewer/scratch-project`; unmodified baseline: `.shokunin/game-dev-2d/corpus/live/r33-checkbox-mutation-reviewer/baseline-project`.

## Evidence
- Sampled tracked `corpus/fixtures/checkbox_toggle.gd` unchanged from the initial read; baseline SHA-256: `a6971f7e1089177e3e7ed8923e95aa8dd1021bf0ac8c1a4856a257d3665f79bb`.
- Unmodified focused headless baseline, `godot --headless --path <baseline-project> --script res://checkbox_toggle.gd`: exit 0. Observed `state=true receipts=[true] label=On`, then `state=false receipts=[true, false] label=Off`, then PASS.
- In scratch only, inserted explicit press-only check after first press/frame (expected unchecked, empty receipts, Ready label), and omitted only the first release event while retaining the release1 state assertion. Mutation SHA-256: `ba1495b221d87a08979ad36e0e2d87d674af070e240d1c6d8d93144adbc4eced`.
- Mutant command: `godot --headless --path <scratch-project> --script res://checkbox_toggle.gd`: exit 2. It passed setup and printed `CHECKBOX_PRESS_ONLY state=false receipts=[] label=Ready`; then failed `CHECKBOX state assertion failed: expected checked=true got=false` after the release1 observation. Thus failure is at the intended release1 state assertion, not setup or press1. No receipt/Label release transition occurred.

## Conclusion
The focused CheckBox action distinguishes press-only old state/receipts/Label from release-only next state under the scratch first-release omission: press1 remains unchecked with no receipt and Ready, while the retained release1 state expectation fails when the release is removed. This supports the proposed edge attribution for this mutation only; it does not establish arbitrary mutation resistance or broader UI semantics. No engine/editor source or seeded controls changed.
