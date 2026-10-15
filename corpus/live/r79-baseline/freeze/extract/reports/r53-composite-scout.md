# Round 53 composite-route scout

## Result: composite counterexample observed; candidate signal supported

LEAF scout; no delegation and no tracked fixture/runner edits. Godot `4.7.2.stable.arch_linux.ed1daf0bf`. Used three independent scratch project copies under `/tmp/r53-composite-scout/{parsed,push_only,composite}` based on the current r52 fixture. Earlier ten edges, focus transfers, callback disconnect/reconnect, owner/callback preconditions, one-frame boundary, and per-edge numeric/full receipt/Label checks were retained. Only edge10 dispatch varied. Added a scratch-only edge10 diagnostic for observer before/after, action state, value, receipts, Label, focus owner, and callback connection.

| edge10 path | observer releases | `ui_left` pressed after | numeric / receipts / Label | owner / callback | outcome |
|---|---:|---:|---|---|---|
| Normal parsed `_action` (`Input.parse_input_event`) | 3→4 | false | 3.0 / `[6.0, 3.0]` / `Value 3` | true / true | all eleven checks; existing terminal marker then expected exit 2 |
| r52 push-only (`root.push_input` matching release) | 3→4 | true | stopped at retained r51 pressed-state guard, before terminal | n/a after early guard | distinct expected-state ERROR, exit 2 |
| Composite `root.push_input` matching release, then `Input.action_release("ui_left")` in same edge/frame | 3→4 | false | 3.0 / `[6.0, 3.0]` / `Value 3` | true / true | all eleven checks; existing terminal marker then expected exit 2 |

Composite diagnostic: `R53_EDGE10 mode=composite observer=3->4 pressed=false value=3.0 receipts=[6.0, 3.0] label=Value 3 owner=true callback=true`. The parsed control gave the same measured state; push-only reproduced r52's observer increment but left the action pressed. The composite path therefore satisfies the combined observer-plus-global-state checks while deliberately not using `Input.parse_input_event` at edge10. It is a bounded counterexample to treating those measured signals as proof of parse-route provenance.

Raw scratch GDScript and complete stdout are in `/tmp/r53-composite-scout/`; commands used `godot --headless --path <variant-dir> --script slider_adjust.gd -- --repeat-right --second-focus-restore --observe-parsed-release`. Each process exited 2 as expected: the two reaching eleven edges printed `SLIDER_PARSED_RELEASE_OBSERVER ...` before the existing intentional terminal error; push-only exited earlier on the unchanged post-release action-state assertion. This is causal scratch evidence only, not a battery case or named non-author replay.

## Scope and recommendation

Recommend parent/executor consider the bounded dedicated expected-negative control exactly as mission specifies, only after checking scratch and preserving paired r51/r52 branches byte-exact. No tracked changes or constants changed by this scout. Evidence covers only this synthetic Godot 4.7.2 route composition and the existing focused/reconnected eleven-edge fixture. It does NOT establish HSlider internal consumption, OS/physical input or timing, rendering, pointer/accessibility behavior, production behavior, or generic event provenance.
