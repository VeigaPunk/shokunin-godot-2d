# Round 28: repeated headless Button activation

Sources: `corpus/fixtures/button_activation.gd`, `run_battery.py`, named non-author `corpus/lessons/r28-repeat-verifier.json` and `reports/r28-repeat-verifier.md`; timing scout `reports/r28-repeat-scout.md`.

| Step | Focused `ui_accept` path | Label after full pair | Receipts after full pair |
|---|---|---|---:|
| Initial | in-tree Button and Label | Ready | 0 |
| First press/release | routed via `root.push_input`, signal connected | Activated 1 | 1 |
| Second press/release after frame | same route | Activated 2 | 2 |
| Disconnected control | first pair, no signal connection | Ready, exit 2 intended step1 assertion | 0 |
| Disposable scratch removal of second action | first pair only, step2 assertion retained | Activated 1, exit 2 intended step2 assertion | 1 |

Godot 4.7.2 scratch scout observed `Button.pressed` fires on **release**: after first press count0, release count1, next press remains1, release count2. The tracked fixture asserts after each complete pair only; do not claim it separately checks event edges. Named full default-path replay 52/52 PASS, 41 ordinary unchanged; separate fault meta top-level PASS with deliberate inner failures. A baseline-scout child briefly self-identified as executor, but subsequently wrote only assigned baseline report; code attribution is based on diff and non-author replay. No pointer hit-testing, real-user debounce/rate, rendered UI or arbitrary mutation-proof provenance.
