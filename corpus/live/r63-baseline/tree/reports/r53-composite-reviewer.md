# Round 53 independent composite-route scratch review — causal result

- Role: LEAF reviewer, read-only tracked-file scope, no delegation. Godot `4.7.2.stable.arch_linux.ed1daf0bf`. Read the standing mission, r53 claim/plan and r52/r51 lessons and reviews.
- Scratch project: `.shokunin/game-dev-2d/corpus/live/r53-composite-reviewer-scratch/project/`; copied the fixture and modified only scratch `slider_adjust.gd`. Kept the exact eleven-edge r52 parsed-release sequence, focus transfers, owner and callback-connected preconditions before each edge, and per-edge numeric/full receipt/Label checks. At edge10 only, used `root.push_input` with matching `InputEventAction(action="ui_left", pressed=false)`, then `Input.action_release("ui_left")` in the same frame boundary; no `Input.parse_input_event` for edge10. Added one diagnostic line.

## Evidence

Command: `godot --headless --path <scratch>/project --script slider_adjust.gd -- --repeat-right --second-focus-restore --observe-composite`

Godot 4.7.2 output at edge10:
```
R53_COMPOSITE edge10 observer=3->4 pressed=false value=3.0 receipts=[6.0, 3.0] label=Value 3 focus_owner=true callback_connected=true
ERROR: SLIDER COMPOSITE PUSH AND CLEAR ASSERTION FAILED: expected no new receipt after eleven checks
```
Exit 2 followed all eleven checks and reached its unique negative terminal. The existing composite assertions independently enforce observer +1, action pre-state pressed, action post-state clear, and edge numeric/receipts/Label; owner/callback assertions run before every edge. This matches the r51 parsed edge10 measurements, while r52 push-only had observer 3→4 and action state still pressed (see `reports/r52-route-reviewer.md` and r52 lesson). Thus the proposed composite is a direct counterexample to interpreting observer receipt plus cleared action state as proof that edge10 used the parsed route.

## Verdict and limits

Causal scratch supports the bounded hypothesis; candidate additive exact-negative case is technically justified if runner/classifier integration preserves paired modes and all prior evidence. I did not edit tracked files, runner, or constants, and make no claim about HSlider internal consumption, OS/physical input or timing, rendering, pointer/accessibility, production, or generic event provenance. Scratch-only changes; no engine/editor/seeded edits, commit, push, or merge. Initial scratch invocation ran before observer initialization was extended to the new scratch flag and timed out/was terminated (exit143); after correcting scratch-only initialization, the successful run above is the evidence.
