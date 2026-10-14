# Round 29: headless Button focus control

Sources: `corpus/fixtures/button_activation.gd`, `run_battery.py`, named non-author `corpus/lessons/r29-focus-verifier.json`, `reports/r29-focus-verifier.md`. Godot 4.7.2 headless synthetic `root.push_input(ui_accept)` only.

| Control | Focus owner before input | After action | Expected result |
|---|---|---|---|
| Focused positive | Button owns GUI focus, has_focus true | owner/has_focus true after each complete pair; receipts 1 then 2, text Activated 1 then Activated 2 | Exit 0 |
| `--no-focus` | null GUI focus owner, Button.has_focus false | still false after first complete pair; receipts0, Ready | Exit 2, intended step1 assertion (not setup) |
| `--disconnect-signal` | Button focus | callback missing; receipts0, Ready | Exit 2, intended step1 assertion |

Named replay: 53/53 (42 ordinary +2 mutants +9 opt-ins), previous 52 verdict/exit/signature triples identical. Separate fault-injection outer PASS has intentional inner FAIL. Baseline-scout initially authored executor-named report and claimed a no-focus scratch PASS without preserved successful raw output; the same saved scratch source and exact path now repeatedly exit2 on intended step1 (parent, executor, named verifier). Claim is preserved as nonreproducible adverse telemetry, not reclassified as verified PASS or silently dropped. The tracked no-focus case stops at first-step assertion; it does not check a second no-focus pair. No pointer, rendered UI, accessibility, production focus behavior, or arbitrary mutation-resistance implication.
