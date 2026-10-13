# Round 33: CheckBox press/release states

Sources: `corpus/fixtures/checkbox_toggle.gd`, `run_battery.py`, named non-author `corpus/lessons/r33-checkbox-edge-verifier.json`, `reports/r33-checkbox-edge-verifier.md`.

| After edge + awaited frame | Connected checked | `toggled(bool)` receipts | Label | Disconnected checked / receipts / Label |
|---|---|---|---|---|
| Initial | false | [] | Ready | false / [] / Ready |
| Press1 | false | [] | Ready | false / [] / Ready |
| Release1 | true | [true] | On | true / [] / Ready |
| Press2 | true | [true] | On | true / [] / Ready |
| Release2 | false | [true,false] | Off | false / [] / Ready; exit2 final signal assertion |

Independent scratch omission of first release retains release-state assertion: setup and press1 pass, exit2 at expected checked=true/got=false. Full named replay 56/56 PASS (45 ordinary +2 mutants +9 opt-ins); all 54 non-CheckBox verdict/exit/signature triples unchanged (9 probe summaries lack signatures); CheckBox connected PASS signature intentionally names `edge_states=[false,true,true,false]`; disconnected PASS/exit/signature unchanged. Separate fault-injection outer PASS includes deliberate inner FAILs. This is synthetic headless Godot 4.7.2 `root.push_input(ui_accept)` after-frame state, not pointer/rendered UI, physical timing, accessibility or production behavior.
