# Round 40 independent repeat-focus reviewer

Independent paired Godot 4.7.2.stable headless scratch replay, in `.shokunin/game-dev-2d/corpus/live/r40-repeat-focus-reviewer/paired.gd`; no tracked fixture/runner edits. Both arms use the same in-tree HSlider (min=0, max=10, step=1, initial=5), `value_changed` callback and Label consumer, and seven fresh parsed `InputEventAction` edges (ui_right true, ui_right true, ui_right false, ui_left true, ui_left false, ui_left true, ui_left false), each followed by one process frame. The only arm difference is calling `grab_focus()`.

Focused arm exited 0. Before each edge, slider was GUI focus owner. Values by edge were `6,7,7,6,6,5,5`; cumulative receipts were `[6]`, `[6,7]`, `[6,7]`, `[6,7,6]`, `[6,7,6]`, `[6,7,6,5]`, `[6,7,6,5]`; signal-driven Label tracked `Value 6, Value 7, Value 7, Value 6, Value 6, Value 5, Value 5`.

No-focus arm exited 2 only at the deliberately expected terminal negative diagnostic, after all seven edges. Before every event, `has_focus()` was false and GUI focus owner was not slider. Value remained 5, receipts remained `[]`, and Label remained `Value 5` on all seven checks. This supports the proposed paired focus-absence control with same wiring and exact synthetic history. It is not evidence about OS auto-repeat or physical keyboard timing.

Scratch telemetry: my first probe attempt had a GDScript typed-array assignment error and was terminated (exit 143); it was corrected by initializing typed arrays then assigning conditionally. That failed attempt is not evidence; the two corrected arm results above are the evidence. No tracked source changes were made.
