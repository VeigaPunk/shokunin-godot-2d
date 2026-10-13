# Round 28 named non-author repeat verifier

## Result: PASS

Independent replay on 2026-10-13 using Godot 4.7.2 (`godot --headless`) and the tracked final fixture/runner. No tracked files were edited.

### Full default-path replay

Ran exactly:

```text
python .shokunin/game-dev-2d/corpus/fixtures/run_battery.py --probe-failing --probe-unrelated-error --probe-export-launch --probe-godot-error --probe-stream-attribution --probe-crash-exit --probe-timeout
```

Exit 0; outer battery verdict **52/52 PASS**: 41 ordinary cases + 2 mutants + 9 opt-in probe records. Previous verifier `r27-button-verifier.json` also had 52 records. All prior cases retained the same verdict and actual exit; the 50 non-button cases retained same verdict, exit, and signature. The two button case signatures changed intentionally from one activation to two; both retained expected status/exits (positive 0, disconnected negative 2). The battery's inner diagnostics intentionally include `FAIL godot_error_unrelated` and `FAIL stream_reject`; their parent probes classify these expected negative controls and are PASS. No other case status/exit changed.

Tracked fixture confirms two `_send_action(button)` calls, separated by process-frame waits, with exact per-step receipt/Label assertions (step 1: receipts=1 and `Activated 1`; step 2: receipts=2 and `Activated 2`). It has no tracked `--skip-second` branch, no direct `_on_button_pressed()` invocation, and no manual `pressed.emit()`. `button.pressed.connect(_on_button_pressed)` is the callback route. Ordinary CASES count is 41.

Raw full verdict was copied byte-for-byte to `corpus/lessons/r28-repeat-verifier.json` (SHA-256 `62737006cefb018cba78fa8987ef5a584b26ddfcf55cb1ca5a0568aac4bf27b6`).

### Omitted-second-action sabotage

Created own disposable script at `corpus/live/r28-repeat-verifier-scratch/button_activation.gd`, removing only the second `_send_action(button)` invocation while retaining the second-step assertion. Ran it with real Godot:

```text
godot --headless --path .shokunin/game-dev-2d/corpus/fixtures --script .shokunin/game-dev-2d/corpus/live/r28-repeat-verifier-scratch/button_activation.gd
```

Exit **2** at step 2: `expected step2 text=Activated 2 receipts=2, got receipts=1 text=Activated 1`. No setup error. Scratch source is not tracked.

### Separate fault injection

Ran `python .shokunin/game-dev-2d/corpus/fixtures/run_battery.py --fault-injection`; command exit 0 and top-level fault-injection verdict PASS. Raw cases: `fault_hang` intentionally FAIL / timeout at 0.25s; expected-negative control PASS / exit 2; unrelated-error control intentionally FAIL / exit 2. Copied raw fault verdict byte-for-byte to `corpus/lessons/r28-fault-verifier.json` (SHA-256 `68dbd098c882a2d09e688568201fbc335138d1553f5c8a909a6ff88e964d8620`).

### Scope and integrity

The observed release edge is specifically `Button.pressed` on **release** in the scout's Godot 4.7.2 probe (`0` receipts after press, then `1` after release; next pair advances to `2`). Tracked fixture asserts after complete press/release pairs; it does not assert per-edge state. This verifies two frame-separated focused headless `ui_accept` press/release pairs and the ordered step receipts/text, not pointer hit-testing, debounce/rate behavior, or arbitrary mutation resistance.

Tracked SHA-256 before and after replay was unchanged: `run_battery.py` `c178aea2cfdfd16f31f3c4c0d192ab82988bfd31faba96dc2f053b4ca8d60260`; `button_activation.gd` `9373e361e4adaf20d6ef012c883799522f700846e672889f589596ad91983c22`.
