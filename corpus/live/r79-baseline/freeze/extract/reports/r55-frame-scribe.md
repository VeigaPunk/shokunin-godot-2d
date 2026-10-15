# Round 55 frame-scribe — read-only causal scratch

## Scope and baseline

LEAF/no delegation. Read `/tmp/mission-game-dev-2d-standing.md`, the r55 declaration in `.shokunin/game-dev-2d/LOG.md`, r53/r54 lessons, named verifier reports and raw lesson receipts. Baseline is r54 `f8b3e99` / `15419b3`: 68 ordinary, 79 full, 70 tuple-bearing rows and nine opt-ins. The r53 lesson describes push-then-clear; r54 shows same-frame clear-then-push matches its measured postconditions. This test isolates a frame gap between those latter operations.

Tracked `slider_adjust.gd` SHA-256 before/after: `da84345352fc60637f35fcb94d4adf8ebf36be1c06f5a1cf10d83b36b65421cd`; `run_battery.py`: `6652003110eec0936fb6272c5d4dbcb2560bfbab168339af06a1ca724ff638e8`. Both remained unchanged. Unique scratch project: `.shokunin/game-dev-2d/corpus/live/r55-frame-scribe-20261013T1028Z/project`; no engine/editor or seeded fixture edits.

## Read-only checklist and operation

- Copied current fixtures into scratch and changed only the candidate r54 edge-10 block there. Edges 0–9 remain parsed and retain both focus transfers/restorations, callback disconnect/reconnect, owner and callback prechecks before every edge, and numeric/value receipt/Label postchecks after each earlier frame.
- At edge10 retained input-state precondition (`ui_left` pressed), sampled release count, called `Input.action_release("ui_left")`, then awaited `process_frame`.
- After that frame directly asserted observer count unchanged at 3, action pressed false, numeric value 3, full receipts `[6.0,3.0]`, Label `Value 3`, slider focus owner, and callback connected. The conjunction passed.
- Then delivered the matching `InputEventAction(ui_left, pressed=false)` with `root.push_input`, awaited another `process_frame`, and asserted observer count 3→4, action still false, numeric value 3, receipts `[6.0,3.0]`, Label `Value 3`, focus owner unchanged, and callback connected. The conjunction passed. This distinguishes substep checks from only observing the final branch terminal.
- Command: `godot --headless --path <unique scratch project> --script slider_adjust.gd -- --repeat-right --second-focus-restore --clear-then-push-release`.

Godot `4.7.2.stable.arch_linux.ed1daf0bf`; exit 2 at the branch's exact expected-negative terminal **after** the eleven-edge checks. Output:

```text
SLIDER_CLEAR_THEN_PUSH_RELEASE values=6,6,6,5,5,5,5,4,4,3,3 receipts=6,3 Labels=Value 6,Value 3 callback_connected=true
ERROR: SLIDER CLEAR THEN PUSH RELEASE ASSERTION FAILED: expected no new receipt after eleven checks
```

This bounded two-frame sequence therefore matches the same-frame r54 clear-then-push measurements at the postconditions requested, with an additional directly checked intermediate state after clear-only. It does not show internal event equivalence. Controls/claims are only synthetic frames and this exact focused/reconnected HSlider scenario; not physical timing, HSlider internal consumption, OS, rendered UI, pointer, accessibility, or production.

## Adversity and recommendation

One initial shell invocation mistakenly quoted the full command as an executable (exit 127); it did not start Godot and is not evidence. Corrected command ran as above. No full battery or fault battery was run by this read-only lane; no tracked edits, engine/editor/seeded changes, commit, push, or merge. Scratch change only. This is causal scratch evidence for the executor to consider; it is not independent verification or an axis verdict.
