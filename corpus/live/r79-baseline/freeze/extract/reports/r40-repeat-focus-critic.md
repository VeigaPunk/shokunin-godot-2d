# Round 40 repeat-focus critic (read-only)

## Verdict: candidate supports the declared causal contrast; diagnostic must be intentionally terminal

Scratch used installed Godot 4.7.2.stable.arch_linux.ed1daf0bf, headless, a private copied project under `corpus/live/r40-repeat-focus-critic-scratch/project`, and seven deliberate `InputEventAction` events each followed by `process_frame`. No tracked fixture or battery was edited. Scratch candidate retained the existing slider, signal connection, Label callback, actions and event order; it changed only repeat-mode expectations/diagnostics for the no-focus branch.

Focused baseline replay (`--repeat-right`) exited 0 with values `6,7,7,6,6,5,5`, receipts `6,7,6,5`, and corresponding Label values. It confirms the focused positive path as currently tracked.

Important caveat: invoking the **currently tracked** fixture with `--repeat-right --no-focus` exits 2 immediately at `SLIDER repeat focus assertion failed before edge 0`. That is expected from the existing repeat branch's unconditional focus assertion and does not measure absent-focus behavior; the new mode needs its own per-edge `not slider.has_focus()` and `gui_get_focus_owner() != slider` assertions.

Adapted scratch candidate made exactly those per-edge no-focus assertions, expected value 5 at every edge, expected receipts `[]`, Label `Value 5`, and after all seven assertions reported the terminal expected failure. It exited 2 only after the seventh edge, printing `SLIDER_REPEAT_NO_FOCUS values=[5.0, ...] receipts=[] label=Value 5 focus_owner=<Object#null>` followed by `SLIDER REPEAT NO-FOCUS ASSERTION FAILED: expected focus-dependent repeat adjustment values=6,7,7,6,6,5,5`. This is the intended control result. No event assigned focus or adjusted value.

The early `repeat focus assertion failed` diagnostic is a blocker only if reused for the no-focus candidate. The terminal assertion must be distinct and classified exactly by battery row, after all seven checks; add a stdout receipt or otherwise ensure row signature captures the expected no-focus evidence. Same signal/Label wiring is preserved. Do not claim OS auto-repeat or physical keyboard/timing behavior.

Raw logs: `corpus/live/r40-repeat-focus-critic-scratch/focused-positive.{stdout,stderr}`, `focused-mixed.{stdout,stderr}`, `candidate.{stdout,stderr}`; candidate script/project also retained under that scratch directory.
