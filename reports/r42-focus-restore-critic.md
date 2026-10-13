# Round 42 focus-restoration critic (read-only)

## Finding
No falsifier found for the declared focus/value/receipt hypothesis in the supplied real-Godot scratch evidence. The observed sequence supports the bounded claim: after a focused adjustment, a distinct in-tree Button receives focus and the next right press/release leave the slider at 6; restoring HSlider focus before the first left press yields 5, then the next left press yields 4.

## Independent checks
- Inspected the tracked `corpus/fixtures/slider_adjust.gd` and scout's disposable scratch `corpus/live/r42-focus-restore-scout/scratch/slider_adjust.gd`, plus `godot.log`. The in-tree fixture adds the `--repeat-right --focus-restore` path; scratch independently exercises the same handoff/restoration history. Neither relies on changing slider value or manually emitting `value_changed`.
- On each of seven loop iterations, focus changes (Button before edge 1, HSlider before edge 3) are followed by a process frame. Then `gui_get_focus_owner()` and `slider.has_focus()` are checked immediately before dispatch. This covers both edges while Button owns focus, and all four edges after restoration. The Button is a distinct focusable Control added to the in-tree UI.
- Each `_action` constructs a new `InputEventAction` with the requested action/pressed state and calls `Input.parse_input_event`; every event is followed by one process frame. The fresh right-press event on edge 1 is distinct, though it is not an OS repeat or proof of physical-key timing.
- Per-edge assertions compare numeric value, the full accumulated `value_changed` receipt array, and Label text. In scratch, the checked states are: edge 0 `6/[6]/Value 6`; edges 1–2 `6/[6]/Value 6`; edge 3 `5/[6,5]/Value 5`; edge 4 unchanged; edge 5 `4/[6,5,4]/Value 4`; edge 6 unchanged. This verifies receipt chronology, not merely final receipt count. Callback appends the actual signal argument and updates Label; no synthetic receipt is injected.
- Raw `godot.log` records edge indices 0–6, expected owner, values, receipts, and labels. It reports the hypothesized observations. The scout notes one initial local assertion expected a receipt on edge 1; that erroneous probe expectation was corrected, and the successful run's expected history is [6] on edges 1–2. Treat the failed probe as telemetry, not candidate evidence.

## Limits / residual caveat
A focus-owner assertion plus the observed unchanged state does not independently prove which internal Godot Control consumed each no-change action; the bounded claim is about the resulting state under the verified focus sequence, not detailed event-consumer internals. The scratch's edge lines print expected owner names after assertions, but those assertions query the actual owner and compare it to the expected Control. This is headless synthetic parsed input plus process frames only—not OS auto-repeat, physical timing, rendered/pointer UI, accessibility, production, or a generic HSlider guarantee.

Verdict: hypothesis survives this read-only falsification pass; no correction requested.
