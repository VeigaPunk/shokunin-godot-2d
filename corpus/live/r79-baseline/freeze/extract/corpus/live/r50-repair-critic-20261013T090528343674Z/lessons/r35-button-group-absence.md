# Round 35: ButtonGroup absence control

Sources: `corpus/fixtures/button_group_selection.gd`, `run_battery.py`, named non-author `corpus/lessons/r35-group-absence-verifier.json`, `reports/r35-group-absence-verifier.md`.

| Same focused action | Grouped A/B membership | Grouped A/B selected and receipts | B ungrouped A/B membership | Ungrouped selected and receipts |
|---|---|---|---|---|
| Setup | true/true | true/false, [] | true/false | true/false, [] |
| After B press/release | true/true | false/true, [A:false,B:true], Label B | true/false | true/true, [B:true], Label B |
| After A press/release | true/true | true/false, [A:false,B:true,B:false,A:true], Label A | true/false | true/true, [B:true,A:true], Label A; exit2 intended non-exclusive diagnostic |

The only treatment change is withholding B's ButtonGroup association; same focus owner B then A, routed `root.push_input(ui_accept)` actions, signal connections, and initial A selected setup. A scratch sabotage that keeps B grouped in treatment fails its after-B expected ungrouped state assertion. Early executor drafts stopped after B or failed classifier allowlist; final named replay 59/59 PASS (48 ordinary +2 mutants +9 opt-ins) with old 58 result triples unchanged. Separate fault-injection outer PASS contains deliberate inner FAILs. This is a headless synthetic causal control, not RadioButton coverage (class absent), pointer/rendered UI, physical timing, accessibility or production/group-general assurance.
