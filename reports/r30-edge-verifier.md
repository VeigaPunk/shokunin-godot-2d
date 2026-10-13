# Round 30 named non-author edge verifier

## Verdict: verified bounded edge-depth evidence

I independently replayed the final tracked fixture and runner without editing them. The required full default-path command was:

```text
python .shokunin/game-dev-2d/corpus/fixtures/run_battery.py --probe-failing --probe-unrelated-error --probe-export-launch --probe-godot-error --probe-stream-attribution --probe-crash-exit --probe-timeout
```

Exit **0**; **53/53 PASS** (42 ordinary cases and 11 probe/mutant records, including nine opt-in probe rows). The battery reported Godot 4.7.2. Raw `verdicts.json` was copied byte-for-byte to `corpus/lessons/r30-edge-verifier.json`; both SHA-256 `890042e23e8533f27b50f9758517ed3e448cfd5472dc0addf86a93872532829f`. All 53 results were PASS. Probe records can contain intentional nested adverse diagnostics; the battery classified them as expected.

Compared with `corpus/lessons/r29-focus-verifier.json`, all **50 non-Button** results have unchanged `(verdict, actual_exit, signature)`. The three Button rows retain PASS and their actual exits; only their expected signatures changed: focused positive now reports `edge_texts=[Ready,Activated 1,Activated 1,Activated 2] receipts=[0,1,1,2]`, and disconnected/unfocused expected-negative diagnostics moved from `step1` to `release1`.

Direct Godot 4.7.2 replays independently confirm the focused positive exits 0 with focus owner/button focus true at release1 and release2 and observed receipt/text sequence `[0,1,1,2]` / `Ready, Activated 1, Activated 1, Activated 2`. No manual signal emission or callback invocation is present; the fixture connects `Button.pressed` to its receipt handler and routes `ui_accept` through `root.push_input`. The disconnected run exits 2 at intended release1 with setup and press1 checks passing, receipt 0 and `Ready`. The no-focus run also exits 2 at intended release1, with receipt 0/`Ready`; its setup establishes both `button.has_focus() == false` and null viewport focus owner. Neither negative produced a setup error.

For the scratch-only mutation, I copied the fixture project under `corpus/live/r30-edge-verifier/omit-release/project`, omitted only the first release event, and left release1 assertion intact. Godot exited **2** at intended release1 (`receipts=0`, `text=Ready`); setup and press1 passed and focus remained true. The tracked fixture/runner hashes before and after all verifier runs were unchanged: fixture `edb777640fe19bdd62960ef18898f8fb181fcb28db57f20025f4430d1cbb68af`; runner `38a27c76ceb18a8b5e14b90504ca8010856b305929487ccef18252f96c6bc0eb`.

Separate `--fault-injection` run exited 0 and was copied byte-identically to `corpus/lessons/r30-fault-verifier.json` (SHA-256 `cc50beaf84dfdc2010358eafda5dbb50e217ed6327d8e39fd7b3538cc612fd8f`). Its outer harness verdict is PASS with the intentional inner `fault_hang` and `fault_unrelated_error` rows FAIL, and `fault_clean_expected_negative` PASS. This is deliberate fault-injection evidence, not a full-battery failure.

## Limits

Evidence is limited to synthetic headless Godot `root.push_input(ui_accept)` Button behavior and these two press/release pairs. It does not establish pointer/rendered UI behavior, physical event timing, debounce, accessibility, or general production focus behavior. No tracked source edits, commits, push, or merge were made by this verifier.
