# Round 31 immutable r30 baseline reviewer

## Verdict: r30 baseline verified; no r31 execution performed

The immutable baseline is repository `HEAD` `be1f5e4bf7827a3b978ad88c0fdb2bd9f4a2b75d` (`game-dev-2d-shokunin <game-dev-2d@shokunin.local>`, `game-dev-2d r30: report Button edge depth`). This review used the committed r30 named non-author verifier artifacts, not the mutable working-tree LOG or any fixture execution. At that HEAD, fixture `corpus/fixtures/button_activation.gd` blob is `a18518ca40bfa4a561f4d6b58d9181dcfeac03b3`; runner `run_battery.py` blob is `576ec3b4ab2ee35c33a4fbde096f9cbd319510b2`. Their SHA-256 values reported by the r30 verifier are respectively `edb777640fe19bdd62960ef18898f8fb181fcb28db57f20025f4430d1cbb68af` and `38a27c76ceb18a8b5e14b90504ca8010856b305929487ccef18252f96c6bc0eb`.

Committed evidence `reports/r30-edge-verifier.md` records named full default-path replay exit 0, **53/53 PASS = 42 ordinary + 11 probe/mutant records** (nine opt-in probe rows included); the raw `corpus/lessons/r30-edge-verifier.json` is byte-identical to replay output, SHA-256 `890042e23e8533f27b50f9758517ed3e448cfd5472dc0addf86a93872532829f`. Godot reported 4.7.2. The three Button baseline result signatures are:

- `button_activation`: expected/actual exit 0, PASS; `PASS button_activation in_tree=true initial=Ready edge_texts=[Ready,Activated 1,Activated 1,Activated 2] receipts=[0,1,1,2]`.
- `button_activation_disconnected`: expected/actual exit 2, battery PASS as expected-negative; signature `UI BUTTON ASSERTION FAILED: expected release1 text=Activated 1 receipts=1`.
- `button_activation_unfocused`: expected/actual exit 2, battery PASS as expected-negative; same release1 signature.

Per the committed verifier report, direct focused positive replay observed Button focus at both releases and receipts/text `[0,1,1,2]` / `[Ready, Activated 1, Activated 1, Activated 2]`. The disconnected and initially-unfocused controls fail at intended release1 with zero receipts/Ready, without setup errors; the latter precondition is null focus owner and `button.has_focus() == false`. A scratch-only omitted-first-release mutation failed at intended release1 while setup and press1 passed. The verifier states all 50 non-Button results match r29 in verdict, actual exit and signature; fixture/runner hashes remained unchanged. The separate fault-injection replay is not part of the 53-row full battery and is deliberately not treated as a full-suite failure.

This establishes the declared pre-r31 baseline only. It does not answer whether focus loss between completed action1 and action2 prevents action2; no r31 fixture was run or modified here. No tracked files, shared report, engine/editor source, seeded controls, or commits were changed by this reviewer.
