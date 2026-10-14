# Round 30 edge-scribe: paired evidence and verdict checklist

Read-only scribe checklist for the declared depth move. I did not run Godot, edit fixtures/runner, or create raw evidence. Treat this as a checklist; do not promote any item to observed until raw output and exit receipts exist.

## Positive focused action sequence

For the one tracked focused `button_activation` path, require focus owner=`ActivateButton` and `button.has_focus()==true` before action 1, and confirm focus remains intact at the observations. Capture both edges of each action separately, with a frame boundary after each input:

| Observation | Expected receipts | Expected Label text | Meaning |
|---|---:|---|---|
| Initial/setup | 0 | `Ready` | Baseline before first input |
| Action 1 press + frame | 0 | `Ready` | Press alone did not activate |
| Action 1 release + frame | 1 | `Activated 1` | First release edge activated once |
| Action 2 press + frame | 1 | `Activated 1` | Second press alone did not activate |
| Action 2 release + frame | 2 | `Activated 2` | Second release edge activated once |

A passing raw record should make each point attributable to the same action: ordered step/edge labels, receipts, focus observations, final PASS, and actual process exit 0. The assertion should check both receipt count and text at each point, not just final state. Use explicit expected diagnostics so a negative run can be distinguished from setup failure.

## Paired controls and mutation check

- Re-run the existing disconnected-signal control through the same sequence. It must fail at the first intended activation assertion (press-state assertions remain at 0/Ready); classify it by the battery's declared negative expectation, not as a setup failure.
- Re-run the existing no-focus control with verified null focus owner / `has_focus()==false` before input. It must remain at 0/Ready and fail at the intended first release assertion, not setup. Preserve its expected negative exit/classification.
- In an isolated scratch copy only, suppress the first release while retaining setup and press observation. Confirm press assertion passes at 0/Ready and the first release-state assertion fails with the intended diagnostic (still 0/Ready). Preserve scratch source, exact command, stdout/stderr, exit receipt, and source hash. Do not alter seeded inputs or tracked fixture for this test.

## Raw/verdict integrity checklist

- Keep raw command, Godot version, stdout, stderr, process exit, and source hashes for the focused case and each control; report raw paths and byte/hash relationship to any copied lesson artifact.
- Run named verifier against the committed candidate, independently of executor. Confirm the ordinary/full battery remains **42 ordinary / 53 full** (assuming no separate authorized count correction), and all 52 pre-round-30 cases retain `(verdict, actual_exit, signature)`; new edge assertions should change no case count.
- Preserve the separate fault-injection outer result and its intentional inner adverse cases if the established verifier protocol requires it; do not conflate those with ordinary battery failures.
- Compare fixture/runner hashes before and after verifier replay. Attribute every source change to the executor; this scribe makes none.
- A release-suppression mutation is a scratch diagnostic, not a seeded fixture or ordinary-case count change. Keep raw mutation evidence distinct from tracked verification.

## Bounds / adjudication

This can support only deeper per-edge assertions in the headless synthetic `root.push_input(ui_accept)` focused Button path if all paired raw evidence passes and the prior 53 outcomes remain intact. It does not establish pointer/mouse behavior, rendered UI, production scene behavior, user-level debounce/timing guarantees, accessibility behavior, arbitrary mutation resistance, or a general Godot Button contract. If the input ordering or focus changes, an assertion fails at setup, raw evidence is missing, or prior cases regress, mark the round HOLD / unprovable rather than claiming depth improvement. No axis verdict is made by this checklist alone.
