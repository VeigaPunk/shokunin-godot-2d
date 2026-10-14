# Round 43 second-loss critic — adversarial replay

**Verdict: confirms the declared terminal negative behavior in an isolated scratch; no falsification found.**

I independently copied the r42 reviewer scratch project setup into `corpus/live/r43-second-loss-critic/` and altered only that scratch script. Ran real Godot `4.7.2.stable.arch_linux.ed1daf0bf`: `godot --headless --path .shokunin/game-dev-2d/corpus/live/r43-second-loss-critic --script slider_adjust.gd -- --repeat-right --focus-restore`.

The seven fresh `InputEventAction` dispatches each followed by `process_frame` produced values `6,6,6,5,5,5,5`, receipts `[6,5]`, and Labels `Value 6` then `Value 5`. The scratch asserted GUI focus owner and `slider.has_focus()` before each event: slider at edges 0,3,4; Button at 1,2,5,6. It explicitly restored slider focus before edge 3 and transferred focus to Button again before edge 5, awaiting a frame for both transfers. After each dispatch, it checked value, complete receipt list, and Label. All checks passed; terminal expected-negative assertion ran only after edge 6 and yielded exit 2 with `SLIDER REPEAT SECOND-LOSS ASSERTION FAILED: expected post-restoration adjustment`.

This supports calibration: the last pair is held at 5 after second focus loss, contrasting r42 restored-focus positive final `4/[6,5,4]`. It is synthetic parsed input/frame behavior only; not OS auto-repeat, physical timing, rendered/pointer UI, accessibility, production or generic slider guarantee. Does not establish internal consumption of unchanged edges. No seeded/engine/editor source edited. Scratch lives at `.shokunin/game-dev-2d/corpus/live/r43-second-loss-critic/`.
