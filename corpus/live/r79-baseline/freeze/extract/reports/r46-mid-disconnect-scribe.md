# Round 46 mid-disconnect scribe — read-only evidence/admission checklist

## Declared claim and baseline

Read the Round 46 claim in `.shokunin/game-dev-2d/LOG.md` before testing. It changes one condition within r44's same nine-edge, double-focus-restoration history: start connected, then disconnect only the `value_changed` callback after edge 0. Predicted history is numeric `6,6,6,5,5,5,5,4,4`; after edge 0 receipts are `[6]` and Label is `Value 6`; after edges 1–8 cumulative receipts remain `[6]` and Label remains `Value 6`. Baseline r45 is 59 ordinary / 70 full. This scribe did not modify tracked fixtures or runner.

## Godot 4.7.2 isolated scratch

Copied `.shokunin/game-dev-2d/corpus/fixtures` into `.shokunin/game-dev-2d/corpus/live/r46-mid-disconnect-scribe/` before execution. Engine reported `4.7.2.stable.arch_linux.ed1daf0bf`.

The scratch-only candidate branch uses `--repeat-right --second-focus-restore --disconnect-after-first`; its branch checks focus owner before every edge, performs the same nine parsed press/release actions with frame yields, asserts numeric value and state after every edge, disconnects the callback after the first edge's successful checks, and emits a unique expected-negative diagnostic only after all nine. The connected paired control completed with exit 0 and values `6,6,6,5,5,5,5,4,4`, receipts `6,5,4`, Labels `Value 6,Value 5,Value 4`. The candidate completed all nine checks and exited 2 with:

```text
SLIDER_REPEAT_SECOND_FOCUS_RESTORE_MID_DISCONNECTED values=6,6,6,5,5,5,5,4,4 receipts=[6] Label=Value 6
ERROR: SLIDER REPEAT SECOND-FOCUS-RESTORE MID-DISCONNECT expected-negative after nine checks
```

Thus the declared same-history observation is reproduced in this local scratch. This is not a full-battery or independent-verifier result.

## Checklist / verdict

- [x] Read Round 46 claim and recorded baseline.
- [x] Scratch copy made before Godot runs; no engine/editor or seeded source modified.
- [x] Connected same-history control: exit 0, expected values and cumulative consumer updates.
- [x] Candidate: per-edge focus-before/state-after checks; callback disconnect follows edge 0 state verification; expected-negative occurs only after nine checks.
- [x] Candidate numeric sequence and post-edge receipts/Label match the prediction.
- [ ] Tracked executor integration, unique ordinary row, preserved prior rows, named non-author full replay, fault/sabotage verification, and admission: pending; outside this read-only scribe's authority.

**Scribe verdict: scratch supports the calibration claim; admission remains pending.** Scope is headless Godot synthetic parsed action events plus process-frame yields and observed focus/value/receipt/Label state. No claim about OS repeat, physical timing/input, rendered/pointer UI, accessibility, production, generic HSlider behavior, or internal consumers of unchanged edges. No commit, push, or merge.
