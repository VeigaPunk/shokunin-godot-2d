# Round 54 independent reverse-order reviewer — causal match

- LEAF reviewer; no delegation and no tracked edits. Runtime: Godot `4.7.2.stable.arch_linux.ed1daf0bf`.
- Copied the seeded fixture to `.shokunin/game-dev-2d/corpus/live/r54-order-reviewer-scratch/project/`. In scratch only, swapped edge10 of `--composite-push-and-clear`: `Input.action_release("ui_left")` first, then matching `root.push_input(InputEventAction(action="ui_left", pressed=false))`, before the same `process_frame`. Edges 0–9 remain parsed. Existing script checks owner and callback connection before each edge and numeric value, complete receipt history, and Label after each edge frame; edge10 checks observer increment and action state.

## Evidence

Reverse-order command:
`godot --headless --path <scratch>/project --script slider_adjust.gd -- --repeat-right --second-focus-restore --composite-push-and-clear`

Godot output:
```
R54_REVERSE edge10 observer=3->4 pressed=false value=3.0 receipts=[6.0, 3.0] label=Value 3 owner=true callback=true
SLIDER_COMPOSITE_PUSH_AND_CLEAR values=6,6,6,5,5,5,5,4,4,3,3 receipts=6,3 Labels=Value 6,Value 3 callback_connected=true
ERROR: SLIDER COMPOSITE PUSH AND CLEAR ASSERTION FAILED: expected no new receipt after eleven checks
```
Exit 2 is the expected unique negative terminal after all eleven checks, not an early assertion failure. Before editing the scratch sequence, I also ran the existing parsed control (`--observe-parsed-release`) and push-then-clear control (`--composite-push-and-clear`); both reached their respective unique terminal after checks. The original push-then-clear confirms the r53 measurement; the parsed control confirms the r51 comparator. Reverse order retains the measured edge10 observer 3→4, global action false, value 3, receipts `[6,3]`, Label `Value 3`, focus owner true, and callback connected true. It therefore matches both controls on these measured fields; the order reversal is not distinguishable by this fixture's asserted receipt/state.

## Conclusion and limits

Causal scratch supports the bounded claim that reverse order also mimics parsed r51 and push-then-clear r53 on the measured synthetic route. This is evidence for an additive, dedicated expected-negative row only if the sole executor integrates it while preserving prior r51–r53 branches/rows byte-exact and validates battery/classifier receipts. I made no tracked change, so no battery admission claim. Scope is only the synthetic route in Godot 4.7.2; no inference about HSlider internal consumption, OS/physical input or timing, rendering, pointer/accessibility, production, or general event provenance. No engine/editor/seeded changes, commit, push, or merge.
