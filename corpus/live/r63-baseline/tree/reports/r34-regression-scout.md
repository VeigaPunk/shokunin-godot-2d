# Round 34 regression scout — prior UI and battery caveats

Read-only review of the proposed RadioButton/ButtonGroup coverage move, current in-tree UI fixtures and battery registration, and prior reports. I ran no engine or battery command and changed no fixture or runner. This report is my only artifact.

## Existing UI baseline and proposed contrast

The current UI battery rows cover Button activation/focus (including disconnected and unfocused negative controls) and CheckBox state/signal behavior. `button_activation.gd` connects `pressed`, sends focused `ui_accept` edges and checks Label/receipt effects. `checkbox_toggle.gd` connects `toggled(bool)` and observes press/release edges over two actions; the disconnected arm still completes both property changes before its intended final signal assertion. They do not cover selection exclusivity across two controls in a shared `ButtonGroup`.

The declared RadioButton candidate is therefore a distinct control/property behavior, not merely another CheckBox boolean transition: two in-tree RadioButtons sharing one actual ButtonGroup should start in a measured, asserted selection state, then focused `ui_accept` on B and A should produce mutually exclusive state transitions. To keep the signal claim precise, assert the exact connected `toggled(bool)` receipt sequence and Label after each action, not just final values. Godot's signal ordering matters when selecting B deselects A and selects B; record actual callback values/order and encode only source-backed observed behavior. Do not emit signals manually or assign selection state as a substitute for routed input. Confirm focus is on the intended button before each action and ensure the second target is focused through an actual `grab_focus()`/focus assertion, rather than assuming focus moved.

In the disconnected arm, make the same two selections and assert both property transitions/exclusivity while receipts stay empty and the Label stays at its initial value. Only after both actions should the arm exit via the deliberate missing-signal diagnostic. This distinguishes the control's own group behavior from signal-consumer behavior and avoids an early expected failure masking whether both selections happened. A separate observer/scratch can help establish exact semantics, but the tracked test should remain self-checking and minimal.

## Prior baseline and regression comparison

Round 33's admitted baseline is 45 ordinary cases, 56 full default-path records (45 ordinary + 2 mutants + 9 opt-in/probe records). Its named non-author verifier compared all 54 non-CheckBox result triples to r32; both CheckBox rows remained PASS with connected exit 0 and disconnected expected-negative exit 2. Round 34's declared expectation is +2 ordinary rows (47 ordinary/58 full) with all 56 prior `(case, verdict, actual_exit, signature)` records unchanged. In a full replay compare the raw maps, not only totals; permit changes only to the two new RadioButton records. Existing Button/CheckBox records are the closest regressions to inspect. No current runtime conclusion is possible from this read-only review.

## Export, timeout, and fault-injection caveats

The default-path command's `--probe-export-launch` is a bounded Linux/X11 scratch export-and-launch check, not cross-platform export readiness. `--probe-timeout` checks a few bounded child-process scenarios and direct-child cleanup; it does not establish universal hang or process-tree cleanup guarantees. Keep these opt-in probe results distinct from ordinary seeded cases.

The separate `--fault-injection` mode is a harness self-test, not part of the default seeded battery. Its intentionally adverse inner classifications (for example timeout or unrelated diagnostic rejects) may be FAIL while the outer fault-injection meta-probe is PASS. Report outer verdict and inner outcomes separately; do not describe those intentional inner FAILs as seeded regressions. Any scratch signal-disconnection/mutation probe likewise is not a replacement for the tracked paired disconnected arm or named non-author full replay.

## Bounded conclusion

The proposed shared-ButtonGroup RadioButton pair fills a currently unrepresented exclusive-selection behavior, provided real-Godot evidence confirms the initial-selection and `toggled(bool)` callback sequence and both focused actions in connected and disconnected arms. It can support only synthetic headless `root.push_input(ui_accept)` behavior and the tested ButtonGroup configuration. It does not establish pointer/rendered interaction, physical timing, accessibility, arbitrary group configurations, or production UI behavior. No engine/editor source or seeded controls were changed; no commit, push, or merge.
