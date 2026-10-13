# Round 27 independent button verifier

**Result: PASS, narrowly.** I am a fresh named non-author verifier. I inspected current `HEAD` (`a25ca36abcf4ae92ea42549d5cb464e2988761d9`) and the working-tree fixture/runner; no unreachable worker scratch was used. `HEAD` runner AST contains 39 ordinary cases; current runner has 41. I independently reviewed the new fixture and then ran the full requested default-path battery.

## Source inspection

`button_activation.gd` creates an in-tree `Button` and `Label`, checks initial `Ready`, focuses the button, and sends pressed and released `InputEventAction("ui_accept")` events via `root.push_input()`. The connected callback increments `pressed_receipts` and changes the label to `Activated`. The fixture contains no direct `_on_button_pressed()` call (the sole textual occurrence is its function declaration) and no manual `.pressed.emit()` call. The disconnected arm uses the same input sequence, then fails the final Activated/one-receipt assertion with the expected `UI BUTTON ASSERTION FAILED` diagnostic and exit 2. This is not a setup failure.

## Replay evidence

Command (default run path):

```text
python .shokunin/game-dev-2d/corpus/fixtures/run_battery.py --probe-failing --probe-unrelated-error --probe-export-launch --probe-godot-error --probe-stream-attribution --probe-crash-exit --probe-timeout
```

Exit 0; raw full verdict `corpus/lessons/r27-button-verifier.json` is a byte-identical copy of the run at `corpus/live/runs/20261013T041932364085Z/verdicts.json` (SHA-256 `8bf40f84dd3b85d815785a1eeddc13d10825f6c7a955a31d599fe7fa7de1a651`). Battery verdict is **52/52 PASS = 41 ordinary + 2 mutants + 9 opt-in records**. Both button cases passed their expected classifications; the disconnected row has actual exit 2 and no classifier error. Existing rows also passed. Expected inner diagnostics `FAIL godot_error_unrelated` and `FAIL stream_reject` are reject-arm results, while their paired meta-probes pass; they are not outer battery failures.

Separately ran `python .shokunin/game-dev-2d/corpus/fixtures/run_battery.py --fault-injection`: exit 0, top-level fault-injection verdict PASS. Its hang and unrelated-error inner rows intentionally FAIL. Byte-identical raw copy: `corpus/lessons/r27-fault-verifier.json`, SHA-256 `9fb8388bc6cd89a1f0234fa7403268d0b29d0290827fee98c324ded2652b5a4a`.

Fixture SHA-256 remained `1a9109bd08efc196c24761a7a64dee7d84160efe417611d0fefc3265bfa2b0f8`; runner remained `f29898f0cb603546705e9aadcb4aaae8a9df1dfcfc9bb91afe3eebe511a40e4d` across both runs.

## Scope and caveats

This replay supports the narrow headless UI action/signal/label behavior and the tracked disconnected control. The critic's scratch-only mutation that directly called the receiver in the disconnected arm did pass; therefore this is **not** evidence of arbitrary mutation resistance or proof that a spoofed fixture cannot pass. That direct call is absent from the tracked fixture. No pointer hit-testing, rendered UI, accessibility, or production-scene claim. Four wave-1 lanes were unreachable and their scratch is excluded from evidence. No engine/editor source changes were made by this verifier.
