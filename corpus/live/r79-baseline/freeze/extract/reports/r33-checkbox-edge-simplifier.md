# Round 33 — CheckBox edge simplifier review

**Scope:** Read-only review of `corpus/fixtures/checkbox_toggle.gd` and its two `checkbox_toggle` runner signatures, against the declared r33 press-only/release-only depth move. No source, runner, engine, or seeded-control edits; no Godot run. No delegation.

## Minimal edge assertions

Keep the existing focused CheckBox setup, two `ui_accept` press/release pairs, and final disconnected-signal failure. Split each pair at its existing frame waits, using the previous pair's state as the press-edge expectation and the loop's `expected` value as the release-edge expectation:

| Edge | Checked state | Connected receipts / Label | Disconnected receipts / Label |
|---|---|---|---|
| Press 1 | false (unchanged) | `[]` / `Ready` | `[]` / `Ready` |
| Release 1 | true | `[true]` / `On` | `[]` / `Ready` |
| Press 2 | true (unchanged) | `[true]` / `On` | `[]` / `Ready` |
| Release 2 | false | `[true,false]` / `Off` | `[]` / `Ready` |

At each press edge, assert the old checked value, the full expected receipt sequence, and corresponding label. At each release edge, assert the next checked value, receipt sequence and label. For the disconnected arm, assert only state plus empty receipts/`Ready`; retain its existing final signal diagnostic after both pairs. This is sufficient to distinguish no press-edge transition from one release-edge transition per action without adding another row, control, or fixture mode.

## Simplification / integration notes

- Preserve one input route and one focus setup; there is no need for another focus assertion or generic event abstraction to establish this edge split.
- Avoid checking only receipt count: compare the boolean sequence too, so `[false,true]` cannot masquerade as the intended `[true,false]` path.
- Keep release assertions before advancing to the next press. A missing first release should fail the first release state assertion, while its preceding press assertion still passes.
- Reuse the existing state/signal diagnostic families where feasible. If new exact error strings are introduced for press-edge or intermediate signal failures, the runner's expected-diagnostic allowlist/signatures must be updated in scope; the disconnected arm should still exit 2 at its final missing-signal assertion, not at setup.
- Existing tracked fixture currently checks only after complete pairs, so the table is a recommendation, not observed edge evidence. Named non-author replay remains required for any admission claim.

**Assessment:** The proposed four edge checkpoints add the intended depth with no broader generalization. This review does not establish Godot runtime semantics or round outcome.
