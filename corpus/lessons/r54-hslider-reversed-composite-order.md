# R54 — reversed composite release order (Godot 4.7.2)

## Decision and evidence

| Edge 10 route, after identical ten parsed history edges | `_input` observer releases | Global `ui_left` after one frame | Numeric / callback receipts / Label | Inference |
|---|---|---|---|---|
| r51 parsed release | 3→4 | false | 3 / `[6,3]` / `Value 3` | Reference postconditions. |
| r52 pushed release only | 3→4 | true | 3 / `[6,3]` / `Value 3` | Push alone does not clear action state. |
| r53 push then direct `Input.action_release` | 3→4 | false | 3 / `[6,3]` / `Value 3` | Composite counterexample. |
| r54 direct `Input.action_release` then push matching release, before same frame | 3→4 | false | 3 / `[6,3]` / `Value 3` | The r53 call order is not necessary for these measured postconditions. |

The dedicated `--clear-then-push-release` branch retains focus transfers, signal disconnect/reconnect, owner/callback prechecks on every edge, numeric/full callback receipts/Label after every edge, and the unique exact expected-negative exit2 terminal after all eleven checks. In separate scratch, omitting clear leaves pressed=true and fails before terminal; omitting push leaves observer delta zero and fails before terminal. Both are rejected under the production classifier.

Named non-author full opt-in `r54-order-non-author.json`: 79/79, all 69 prior r53 tuple-bearing rows unchanged and nine opt-in classifications stable. Separate `r54-fault-non-author.json` outer PASS with expected intentional inner failures. See `../../reports/r54-order-verifier.md`; wave scratch and author runs in `../../reports/r54-order-executor.md` and peer reports. Initial malformed command and missing-observer scratch run, plus scribe/scout malformed setup attempts, are adverse and not evidence of PASS.

This is a bounded synthetic Godot 4.7.2 post-state comparison, not proof of route uniqueness, HSlider internal consumption, OS or physical input/timing, rendered UI, pointer/accessibility, production behavior, or generic event provenance.
