# Round 40 repeat/focus absence scout

## Scope and setup
Scratch-only copy: `.shokunin/game-dev-2d/corpus/live/r40-repeat-focus-scout/`. Tested with Godot `4.7.2.stable.arch_linux.ed1daf0bf` headless. I made only scratch `slider_adjust.gd` changes to add a seven-edge no-focus mode; no seeded fixture or harness source was edited.

The same seven parsed events were used in order: right press, right press, right release, left press, left release, left press, left release. The focused run used `--repeat-right`; the no-focus run used `--repeat-right --no-focus`. In the no-focus scratch mode, focus owner was required to differ from slider before every edge, and value/receipts/Label were checked after every event frame.

## Raw result
Focused positive:
```
$ godot --headless --path .shokunin/game-dev-2d/corpus/live/r40-repeat-focus-scout --script res://slider_adjust.gd -- --repeat-right
exit=0
PASS slider_adjust_repeat focused=true range=0..10 step=1 values=6,7,7,6,6,5,5 receipts=6,7,6,5 Labels=Value 6,Value 7,Value 6,Value 5
```

No-focus paired run:
```
$ godot --headless --path .shokunin/game-dev-2d/corpus/live/r40-repeat-focus-scout --script res://slider_adjust.gd -- --repeat-right --no-focus
exit=2
SLIDER_REPEAT_NO_FOCUS values=[5, 5, 5, 5, 5, 5, 5] receipts=[] label=Value 5 focus_owner=<Object#null>
ERROR: SLIDER REPEAT NO-FOCUS ASSERTION FAILED: expected seven focus-dependent adjustment edges
```

The exit-2 diagnostic is emitted only after the loop completes all seven edge checks. For each edge, the focus owner check passed (owner was null, not the slider); value stayed 5, receipts stayed empty, and Label stayed `Value 5`.

## Admission / caveat
The real-engine paired observation supports proceeding: same seven synthetic parsed edges and connected signal/Label consumer, with focus as the varied condition; focus assigned in positive yields seven-edge adjustments, absent focus yields no changes. This is a headless synthetic event/process-frame result only, not OS auto-repeat, physical keyboard/timing, rendered/pointer UI, accessibility, or production guarantee. A first scratch invocation omitted `--no-focus` and correctly failed the no-focus owner assertion; the paired run above used the intended flag and passed all assertions before the expected terminal diagnostic. No source-level causal claim is made beyond this measured setup.
