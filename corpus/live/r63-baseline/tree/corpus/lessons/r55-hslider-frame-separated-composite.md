# R55 — frame-separated clear then push (Godot 4.7.2)

## Decision and evidence

| Edge10 substep in focused/reconnected eleven-edge history | `_input` observer release count | Global `ui_left` | numeric / callback receipts / Label | Meaning |
|---|---|---|---|---|
| Pre-edge, after ten parsed edges | 3 | true | 3 / `[6,3]` / `Value 3` | Baseline before release. |
| Direct `Input.action_release("ui_left")`, then **one awaited process frame** | 3 | false | 3 / `[6,3]` / `Value 3` | Clear changes global action state but does not deliver `_input` release. |
| Matching `root.push_input(ui_left,false)`, then **another awaited process frame** | 4 | false | 3 / `[6,3]` / `Value 3` | Push supplies one observer receipt, leaving state cleared. |

Owner/focus and callback connection remain true at both substeps. The dedicated `--clear-frame-then-push-release` control checks owner/callback before all eleven edges, numeric/full receipts/Label per edge, both edge10 intermediate/final states, then reaches one exact expected-negative exit2 terminal. Same-frame r54 clear-then-push has the same measured *final* state; the extra frame does not demonstrate a final-state difference or physical timing. Omitting clear fails intermediate pressed-state assertion; omitting push fails final observer assertion; neither reaches the terminal. Omitting the intermediate await, however, **still reaches terminal**: this sabotage is ineffective, so these checks do not prove that the extra frame is necessary.

Named non-author repaired fresh full opt-in raw `r55-frame-non-author.json`: 80/80, all 70 prior r54 tuple-bearing rows and nine opt-in classifications unchanged. Separate `r55-fault-non-author.json` outer PASS with expected intentional inner failures. See `../../reports/r55-frame-verifier.md` and wave reports. Initial r54 old-branch marker overwrite was restored before fresh author and verifier replays; pre-repair runs are tainted. The verifier improperly delegated to a child (cancelled, no child result used); malformed shell attempt exit127 launched no battery. These are adverse telemetry, not PASS evidence.

This is only a synthetic Godot 4.7.2 two-frame substep observation, not HSlider internal event consumption, OS/physical timing/input, rendered or pointer UI, accessibility, production, or general event-provenance evidence.
