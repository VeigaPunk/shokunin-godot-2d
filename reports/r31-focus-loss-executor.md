# Round 31 focus-loss executor report

## Result: admit bounded calibration contrast

The baseline focused Button path activates twice with the existing signal wiring and identical `root.push_input(ui_accept)` press/release pairs. A new ordinary case releases Button focus only after release1, verifies the viewport has no focus owner before action2, and verifies both no-focus state and unchanged `Activated 1`/one receipt after press2 and after release2. It exits 0 with a distinct PASS signature; this is a genuine causal contrast in headless Godot 4.7.2: continued focus is required for the second activation in this fixture.

Tracked fixture and runner changed only to add `--lose-focus-after-first` behavior and one ordinary row. The control does not suppress/skip an event or disconnect signals. Existing focused positive, disconnected negative, and initially unfocused negative remain.

Full command:

```text
python .shokunin/game-dev-2d/corpus/fixtures/run_battery.py --probe-failing --probe-unrelated-error --probe-export-launch --probe-godot-error --probe-stream-attribution --probe-crash-exit --probe-timeout
```

Exit 0; 54/54 PASS = 43 ordinary + 11 probe/mutant records. Raw verdicts copied to `corpus/live/r31-focus-loss-executor/r31-focus-loss-verdicts.json` (SHA-256 `ccbb7f31387e5ecbd70e1827dfff7bddf424f5dd513c1240078ddb682922fcd7`). New case raw output:

```text
BUTTON_FOCUS edge=release1 focused=true button_has_focus=true receipts=1 text=Activated 1
BUTTON_FOCUS mid_sequence focused=false button_has_focus=false
BUTTON_FOCUS step=2 focused=false button_has_focus=false receipts=1 text=Activated 1
PASS button_activation_focus_loss initial=focused release1=Activated1 mid_sequence=no_focus release2=Activated1 receipts=1
```

The `step=2` focus diagnostic is after release2; code also asserts null GUI focus owner and `button.has_focus() == false` after press2. Both edge checks rule out transient focus reacquisition. The positive remains receipts/text `[0,1,1,2]`; disconnected and initial no-focus negatives still fail at release1 as intended. Full-run nested adverse classifications for Godot error and stream attribution probes are expected diagnostics; outer battery and probe rows PASS.

## Scope and limits

Calibration improved (mid-sequence focus precondition for second action now isolated); depth unchanged (same two action pairs/edge assertions); coverage unchanged as an axis (one additional calibration ordinary row). 53 prior case verdicts/exits/signatures retained; new count 43 ordinary/54 full. Claim is limited to headless synthetic Godot 4.7.2 `ui_accept` routing in this fixture, not rendered UI, pointer, timing, accessibility, or all production focus behavior. No engine/editor, seeded-control edits, commit, push, or merge.
