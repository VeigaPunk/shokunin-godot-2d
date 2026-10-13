# Round 32: stateful CheckBox toggle under headless input

Sources: `corpus/fixtures/checkbox_toggle.gd`, `run_battery.py`, named non-author `corpus/lessons/r32-checkbox-verifier.json`, `reports/r32-checkbox-verifier.md`.

| After action | Connected CheckBox state | `toggled(bool)` receipts | Label | Disconnected state / receipts / Label |
|---|---|---|---|---|
| Initial | unchecked | [] | Ready | unchecked / [] / Ready |
| First focused `ui_accept` pair | checked | [true] | On | checked / [] / Ready |
| Second focused `ui_accept` pair | unchecked | [true,false] | Off | unchecked / [] / Ready; exit2 intended final signal assertion |

Both arms execute both action pairs and check widget state independently from callback receipts. No manual property toggle or `toggled.emit` is used. The scratch positive signal-disconnection sabotage exits2 on first signal assertion, **not** after two toggles; the tracked disconnected paired case is the proof of two state transitions without callback. Named full replay 56/56 PASS (45 ordinary +2 mutants +9 opt-ins), prior 54 case verdict/exit/signature triples unchanged. Separate fault injection outer PASS includes deliberate inner FAILs. Scout's first scratch typed-Array error hung until parent terminated PID 1530630; raw error remains in `corpus/live/r32-checkbox-scout/initial-typed-array-error.log`, not PASS evidence. Later corrected scout and independent reviewer/verifier runs passed. Scope is synthetic headless Godot 4.7.2 action routing, not pointer/rendered UI, physical timing, accessibility or production behavior.
