# Round 29 regression scout — read-only Button, export, timeout review

Reviewed the declared r29 focus-dependence question, tracked Button fixture/runner, r28 verifier raw, r28 fault-injection raw, and the existing r29 scratch focus scout's paired script/raw output. This scout made no fixture/runner edits and ran no engine process. No seeded controls or engine/editor files were touched.

## Focus pairing and current Button boundary

The r28 tracked positive `button_activation.gd` still calls `button.grab_focus()` in `_send_action()` before each of two `ui_accept` press/release deliveries. It checks step states `Activated 1`/`Activated 2` and receipt counts `[1,2]`; disconnected flag fails the intended first-step assertion with `Ready`/0. It does not itself check the focus owner. The r29 scratch scout `corpus/live/r29-focus-scout/focus_pair.gd` uses the same Button/Label/signal and action helper for focused and then unfocused inputs. Its saved Godot 4.7.2 raw says:

- focused owner `@Button@2`, `has_focus=true`; first action ends at receipt 1 / `Activated 1`;
- after `button.release_focus()`, owner `<none>`, `has_focus=false`; same action leaves the totals at receipt 1 / `Activated 1`.

This is a positive observed contrast in callback delta (focused +1; unfocused +0), not merely a different setup. The raw is `corpus/live/r29-focus-scout/godot-4.7.2-paired-raw.txt`; script is in the same scratch directory. It supports the bounded headless `ui_accept` focus-dependence claim if the named independent reviewer/verifier confirms the paired run. Caveat: this is one press/release pair per arm in a scratch-only script, not a second repeated action in the unfocused arm, and not pointer/window/rendered focus behavior. No speculative edit is indicated by my review.

## Export and timeout boundaries (prior-run evidence only)

The r28 full raw `corpus/lessons/r28-repeat-verifier.json` has top-level PASS, 52 records, including `export_readiness` and `export_preset_missing` PASS. The positive export used Linux/X11 and created a 73,703,800-byte executable (`fixture.x86_64`, plus `.pck`/launcher) before cleanup; the missing-preset control exited 1 with `ERROR: Invalid export preset name: Missing preset.`. Opt-in unrelated-error export probes detected injected unrelated diagnostics and rejected same-line spoofing. `probe_export_launch` is PASS with positive launch assertion true and negative assertion false. These establish r28 health, not fresh r29 replay or a broader export guarantee.

The same r28 run's `probe_timeout` is PASS with inner classifications `[false, true, false]`: old bound rejects delayed clean startup, new bound accepts it, hold-open times out. Script cases use 8s and export 60s per prior source review; timeout control tests direct-child cleanup only. `corpus/lessons/r28-fault-verifier.json` is separately labeled `fault_injection`, not seeded battery: top-level meta PASS while intentional `fault_hang` and `fault_unrelated_error` inner cases correctly FAIL, and clean expected-negative inner case PASS. This must not be counted as Button/fault-free fixture evidence. No r29 export, timeout, or fault replay was done here.

## Bounded recommendation

No Button/export/timeout regression is apparent from source/read-only raw review, but I cannot certify r29 regression-free behavior without a fresh named full replay. Preserve existing two Button row contracts, 41 ordinary rows and prior 52-record run shape; do not alter export, timeout, executor, or unrelated fixtures for this focus test. Focus contrast supports calibration only at the explicitly headless routed-input boundary, pending independent re-execution. No claim about pointer hit-testing, OS window focus, rendering, real users, or production UI behavior.
