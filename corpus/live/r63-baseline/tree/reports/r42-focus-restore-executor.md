# Round 42 executor — focus restore

## Scratch-first evidence
Used system `godot` 4.7.2.stable.arch_linux.ed1daf0bf (headless) against a dedicated scratch project at `corpus/live/r42-focus-restore-executor/scratch/`. The scratch created a connected in-tree HSlider (min0/max10/step1/initial5), Label, and separate focusable Button. The seven parsed actions were fresh right press, right press, right release, left press, left release, left press, left release, each followed by one process frame. Focus owner was asserted before each: HSlider for edge 0, Button for edges 1–2, HSlider restored for edges 3–6. All state checked after every edge.

Raw scratch output: `EDGE 0 ... value=6.0 receipts=[6.0] label=Value 6`; edges 1–2 remained 6/[6]/Value 6; edge3 became 5/[6,5]/Value 5; edge4 held; edge5 became 4/[6,5,4]/Value 4; edge6 held. Summary values `[6.0,6.0,6.0,5.0,5.0,4.0,4.0]`. Hypothesis confirmed; no forced value or signal.

## Candidate implementation
Only after the scratch run, added the dedicated `--repeat-right --focus-restore` branch to `corpus/fixtures/slider_adjust.gd` and one ordinary positive row to `run_battery.py`. The branch asserts expected owner before each edge, plus value/receipt/label after each edge; Button owns focus before second right press and release; slider focus is restored before first left press. Real fixture replay exit 0:
`PASS slider_adjust_repeat_focus_restore focused=true range=0..10 step=1 values=6,6,6,5,5,4,4 receipts=6,5,4 Labels=Value 6,Value 5,Value 4`.

No engine/editor or seeded control edits. Scope is synthetic parsed events and process frames, not OS auto-repeat, physical keyboard timing, rendered/pointer/accessibility behavior, production, or generic slider guarantees. Full non-author battery replay is pending parent orchestration.
