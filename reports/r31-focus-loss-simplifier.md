# Round 31 focus-loss simplifier

## Minimal causal contrast

Use the existing focused positive as the reference and add one opt-in focus-loss arm in the same `button_activation.gd` execution. Keep the current initial focused-owner assertion and first press/release pair unchanged. Immediately after the existing successful release1 assertion (receipt 1, `Activated 1`, focus still owned), conditionally call `button.release_focus()`, await `process_frame`, and assert both `button.has_focus() == false` and `gui_get_focus_owner() == null`. Then send the exact existing press2/release2 edges with no other changes. For the intervention arm, retain the press2 and release2 edge checks, expecting receipt 1 and `Activated 1` at both; also assert focus remains absent after the pair. The unmodified focused arm continues expecting `[0,1,1,2]` / `[Ready, Activated 1, Activated 1, Activated 2]`.

A single explicit opt-in argument (e.g. `--release-focus-after-first`) is justified to select that causal intervention; add just one ordinary runner case using it and its expected successful diagnostic. Do not add switches for skipping assertions, synthesizing receipts, weakening focus checks, or changing edge delivery. Keep disconnected and initial-no-focus rows and their existing release1 diagnostics unchanged. This yields 43 ordinary / 54 full only if the new arm actually stays at one receipt after focus is demonstrably lost; otherwise preserve raw evidence and HOLD rather than adding a purported focus-dependence control.

## Attribution and bounds

The intervention belongs strictly between the already-verified first complete pair and the second press. This preserves initial focus as a matched precondition and changes only continued focus before action2. Check owner and `has_focus` after release1, after the explicit release, and after action2; otherwise automatic refocus would make a non-activation result uninterpretable. Keep the same Button, signal connection, `root.push_input(ui_accept)` event edges, and awaited frames. Do not use another Control, manually invoke `pressed`, suppress the signal, omit an edge, or change input/action configuration.

This isolates only the synthetic headless Godot focus prerequisite for the second `ui_accept` pair; it does not establish rendered/pointer interaction, real-user event behavior, or production UI policy. No files beyond this assigned report were changed, and I did not execute a Godot probe.
