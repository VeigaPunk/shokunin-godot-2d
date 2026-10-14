# R53 — composite release route counterexample (Godot 4.7.2)

## Decision and evidence

| Route at edge 10 of the same focused/reconnected eleven-edge HSlider history | `_input` observer release count | `Input.is_action_pressed("ui_left")` after frame | value / callback receipts / Label | What it establishes |
|---|---|---|---|---|
| `Input.parse_input_event(InputEventAction(ui_left,false))` (r51) | 3→4 | false | 3 / `[6,3]` / `Value 3` | Parsed event reaches observer and clears global state. |
| `root.push_input(matching release)` alone (r52) | 3→4 | true | 3 / `[6,3]` / `Value 3` | Pushed event reaches observer but does not clear global state. |
| `root.push_input(matching release)` then `Input.action_release("ui_left")` before one frame (r53) | 3→4 | false | 3 / `[6,3]` / `Value 3` | Observer receipt plus global state clear do **not** uniquely prove parsed route provenance. |

The dedicated `--composite-push-and-clear` branch preserves ten earlier parsed edges, two focus transfers/restorations, callback disconnection/reconnection, owner and connection checks before every edge, and numeric/full receipt/Label assertions after every frame. One exact expected-negative exit 2 occurs after all eleven checks. In separate scratch, omitting the push leaves the observer unchanged and fails before the terminal; omitting direct clear leaves action pressed and fails before the terminal. Both fail the production classifier. The terminal diagnostic is a negative-control marker, not independent state evidence.

Named non-author full opt-in raw `r53-composite-non-author.json`: 78/78, all 68 prior tuple-bearing r52 rows exact and nine opt-in classifications stable. Separate `r53-fault-non-author.json`: outer PASS, expected inner timeout/negative/unrelated-error outcomes. See `../../reports/r53-composite-verifier.md`; author and adverse scratch are detailed in `../../reports/r53-composite-executor.md`, `../../reports/r53-composite-critic.md`, and `../../reports/r53-regression-scout.md`. The executor first tested against the wrong push-only guard and failed; other nil-observer scratch timeouts and the initial malformed verifier command are setup adversity, not PASS evidence. Initial verifier arithmetic was corrected in its superseding report.

This is only a synthetic Godot 4.7.2 route counterexample. It does not establish HSlider internal event consumption, OS or physical input/auto-repeat/timing, rendering, pointer/accessibility, production behavior, or general event provenance.
