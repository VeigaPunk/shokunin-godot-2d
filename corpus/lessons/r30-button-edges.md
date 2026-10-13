# Round 30: headless Button press/release edges

Sources: `corpus/fixtures/button_activation.gd`, `run_battery.py`, named non-author `corpus/lessons/r30-edge-verifier.json`, `reports/r30-edge-verifier.md`; scratch omission reports `reports/r30-edge-mutation-reviewer.md` and named verifier.

| Edge after one frame | Focused positive receipts | Label | Absent first release scratch |
|---|---:|---|---|
| Initial | 0 | Ready | Setup passes |
| Press 1 only | 0 | Ready | Press1 assertion passes |
| Release 1 | 1 | Activated 1 | Omitted release: exit2 intended release1, 0/Ready |
| Press 2 only | 1 | Activated 1 | Not reached |
| Release 2 | 2 | Activated 2 | Not reached |

The disconnected and no-focus controls use the same press/release action path but fail at release1 with 0/Ready, exit2; no-focus establishes Button unfocused and null GUI owner. Named full replay 53/53 PASS (42 ordinary +2 mutants +9 opt-ins); prior 50 non-Button verdict/exit/signature triples unchanged, three Button PASS/exits preserved with intentionally changed edge signatures. Separate fault-injection outer PASS contains deliberate inner failures. This establishes only synthetic headless `root.push_input(ui_accept)` edge state after awaited frames, not pointer/physical timing, debounce, rendered UI, accessibility or production focus.
