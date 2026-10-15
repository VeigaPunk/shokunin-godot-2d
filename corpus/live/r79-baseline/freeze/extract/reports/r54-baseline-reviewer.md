# Round 54 baseline reviewer — reverse composite order

## Baseline and audit

Read the standing mission, the r51–r53 LOG declarations/adjudications, r51 parsed-release and r52 push-route lessons, r53 composite lesson, non-author/fault raw artifacts, and r53 baseline/executor/reviewer/critic/simplifier/scribe/verifier reports. r53 baseline is Godot 4.7.2, 67 ordinary / 78 full, 69 tuple-bearing rows and nine opt-ins. Its named replay reports all 68 comparable r52 tuples and nine opt-in classifications stable, plus separate fault outer PASS. r53 records the composite edge10 order as push matching release then `Input.action_release`, before one frame. Existing adverse evidence remains adverse: wrong-control and nil-observer scratch attempts, malformed verifier invocation, corrected arithmetic, and the critic's hardcoded `pressed=true` diagnostic are not evidence; rely on explicit assertions/raw and corrected reports. No tracked file was changed here.

The r51 parsed edge10 baseline is observer 3→4 and global action true→false, numeric3 / receipts `[6,3]` / `Value 3`, focus and callback true. The r53 push-then-clear composite recorded the same measured state. The r52 push-only route instead has observer 3→4 and action still pressed. Prior full-path tuple/opt-in results are baseline evidence, not rerun in this read-only reviewer task.

## Reverse-order scratch probe

Unique scratch: `.shokunin/game-dev-2d/corpus/live/r54-baseline-reviewer-scratch/project/slider_adjust.gd`; output `../reverse-order-measured.log`. I copied current `slider_adjust.gd` and changed only edge10 order in the composite branch to `Input.action_release("ui_left")` followed by `root.push_input(matching InputEventAction(ui_left, pressed=false))`; both occur before the same `process_frame`. Edges 0–9 remain parsed. The fixture's owner and callback preconditions, per-edge value/full receipt/Label checks, observer and action-state checks, focus transfers, callback disconnect/reconnect, and eleven-edge terminal are preserved. I added a scratch-only diagnostic after edge10's frame to print the exact observed state.

Command: `godot --headless --path . --script slider_adjust.gd -- --repeat-right --second-focus-restore --composite-push-and-clear` (from the scratch project). Godot `4.7.2.stable.arch_linux.ed1daf0bf`; exit 2 at the existing unique expected-negative terminal after all eleven edge checks. Direct edge10 output:

```text
R54_REVERSED edge10 observer=3->4 pressed=false value=3.0 receipts=[6.0, 3.0] label=Value 3 focus=true callback=true
SLIDER_COMPOSITE_PUSH_AND_CLEAR values=6,6,6,5,5,5,5,4,4,3,3 receipts=6,3 Labels=Value 6,Value 3 callback_connected=true
ERROR: SLIDER COMPOSITE PUSH AND CLEAR ASSERTION FAILED: expected no new receipt after eleven checks
```

The reversed ordering satisfies the existing composite branch's observer and cleared-state assertions and reproduces the measured r51/r53 state in this same synthetic sequence. It differs in **order only**, not measured postconditions. Therefore the r53 push-then-clear order is not necessary to produce those observations. The action release precedes the matching pushed event here; the result does not establish any broader order/timing property.

## Reviewer conclusion and limits

Causal scratch supports one additive exact expected-negative case for the dedicated `--clear-then-push-release` route, if the sole executor implements it without altering r51–r53 branches/rows and the named verifier confirms full-path, fault, sabotage, and prior tuple/opt-in stability. This review did not edit tracked files, run the battery, verify a classifier row, or establish admission. Preserve prior 69 tuple-bearing rows and nine opt-ins byte/semantic stable as applicable; any failed scratch is adverse, not a pass.

Scope is this synthetic Godot 4.7.2 routed-action sequence only. No inference about HSlider internal event consumption, OS/physical input, timing, rendering, pointer behavior, accessibility, production, or general event provenance. No engine/editor/seeded edits, commit, push, or merge.
