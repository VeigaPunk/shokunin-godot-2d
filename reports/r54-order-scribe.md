# Round 54 order scribe — read-only causal evidence

## Scope and result

LEAF, no delegation; tracked `slider_adjust.gd` and `run_battery.py` were read-only in this lane. Using Godot `4.7.2.stable.arch_linux.ed1daf0bf`, the reverse edge-10 ordering **does mimic** the parsed r51 measured postconditions and the r53 push-then-clear postconditions in this synthetic fixture. This is causal scratch evidence for the bounded candidate; it does not itself authorize tracked edits. The sole executor may decide whether to add a dedicated branch/one exact expected-negative row and allowance.

## Read-only checklist

- Read `/tmp/mission-game-dev-2d-standing.md`, r54 declaration in `.shokunin/game-dev-2d/LOG.md`, r51 named-verifier evidence, r52 route verifier/report, and r53 composite verifier/report plus fixture and runner.
- Kept independent scratch under `.shokunin/game-dev-2d/corpus/live/r54-order-scribe-scratch/{parsed,push,composite,reverse}`. Each is a copy of the current fixture plus `project.godot`; no engine/editor or seeded fixture edits.
- Compared controls with the same repeat-right/second-focus-restore sequence and Godot 4.7.2. r51 parsed control: `--observe-parsed-release`; r52 push-only control: `--observe-push-input-release`; r53 order: `--composite-push-and-clear`; reverse scratch changes only edge-10 statement order.
- Edges 0–9 remain parsed via `_action` in all cases. At every edge the candidate branch checks expected focus owner/slider focus and callback connection before action; after each frame compares numeric value, full receipts, and Label. At edge10 it also checks release observer delta and global pressed state. The route branch checks expected press state before edge10.
- No tracked fixture/runner changes were made. No full battery, fault-injection battery, branch allowance, commit, push, or merge was run/performed by this read-only lane.

## Direct Godot replay

All four commands were invoked with `godot --headless --path <scratch> --script slider_adjust.gd -- --repeat-right --second-focus-restore <flag>`. The three existing branch controls terminated at their expected-negative terminal (exit 2), indicating the eleven-edge checks completed. Their outputs retained `values=6,6,6,5,5,5,5,4,4,3,3`, `receipts=6,3`, `Labels=Value 6,Value 3`, callback connected true. Push-only additionally reports `observer_delta=1 pressed=true`; parsed and r53 composite each passed their respective route assertions.

For the reversed r53 scratch, the only route-order change is:

```gdscript
Input.action_release("ui_left")
root.push_input(composite)
```

Raw edge10 print before the frame: `observer=3->4 pressed=false value=3.0 receipts=[6.0, 3.0] label=Value 3 focus_owner=true callback_connected=true`. The route checks then completed all eleven edges and reached the same unique expected-negative terminal, `SLIDER_COMPOSITE_PUSH_AND_CLEAR_ASSERTION FAILED: expected no new receipt after eleven checks` (exit 2). Thus reverse order still gives observer 3→4, action state false, numeric value 3, receipts `[6,3]`, Label `Value 3`, slider focus owner true, callback connected true. It is not distinguishable from the measured parsed and push-then-clear states by these observations.

Two initial shell attempts used malformed quoting and exited 127 before starting Godot; they produced no application execution and are retained as setup adversity, not evidence. The corrected commands above ran successfully.

## Bounded interpretation / recommendation

Order is not necessary for these measured synthetic postconditions: `action_release` then `push_input` mimics `push_input` then `action_release`, while both also match the measured parsed edge10 state. This supports exactly one additive expected-negative row for the reversed sequence if the executor proceeds, with an exact allowance for its terminal signature; keep prior r51–r53 branches/rows byte-exact. Parent/executor should verify that change and compare all 69 prior tuple-bearing rows plus nine opt-in classifications before admission. No HSlider internal event consumption, OS/physical timing/input, render/pointer/accessibility, production, or general provenance inference.
