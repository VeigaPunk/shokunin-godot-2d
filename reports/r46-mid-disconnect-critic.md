# Round 46 mid-run callback-disconnect critic

## Adversarial review (read-only)

The proposed contrast is causally coherent if the scratch confirms it: keep the existing same in-tree `HSlider` (`0..10`, step `1`, initial `5`) and the exact nine fresh parsed edges/focus transfers from r44. Let edge 0 run while `_on_value_changed` remains connected. After its frame and assertions establish numeric `6`, cumulative receipts `[6]`, and Label `Value 6`, disconnect only that callback before edge 1. Then the expected nine numeric values remain `6,6,6,5,5,5,5,4,4`, while receipt history and Label remain `[6]` / `Value 6` from edges 1–8 onward. This discriminates callback timing within one history from r45's disconnect-at-start empty-receipt/initial-label control.

## Conditions that would falsify or weaken the claim

- Do not treat an expected-state table as measurement: run Godot 4.7.2 scratch first, and HOLD if either focus ownership or numeric values differ. Check GUI owner immediately before *each* action (slider edges 0,3,4,7,8; Button edges 1,2,5,6) and verify value, complete receipt array, and exact Label after each action/frame.
- The edge-0 connected observation must be asserted before disconnect. Otherwise a wrong setup or already-disconnected callback could still produce a later terminal error that looks like the target case.
- Verify the callback is connected immediately before disconnect and absent immediately after. Disconnect exactly `value_changed` → `_on_value_changed`; do not disable signal emission, alter actions/focus, clear receipts, or reset Label. The condition must be a separate `--disconnect-after-first` branch gated by both `--repeat-right` and `--second-focus-restore`, and must not reuse/alter r44 or r45 branches.
- Edges 3 and 7 are the numeric decrement presses after focus restoration, so they are the key checks that numeric movement continues after callback removal while receipt/Label state does not. Releases and Button-owned events still need all nine checks to reject edge omission/order/focus sabotage.
- Emit one unique mid-disconnect marker only after all nine checks; use a unique expected-negative terminal error/signature and exit 2 only after that marker. Any per-edge/setup/focus failure exits before it. The battery must classify the exact marker plus expected exit, reject unrelated errors/parse failures, and avoid accepting a marker produced by an earlier failure.
- The branch ordering must precede the existing connected r44 and start-disconnected r45 exact predicates without broadening either predicate. Runner addition should be one opt-in case with flags in the requested order and exact signature; preserve every previous case tuple and classifier.

## Interpretation boundary

A successful paired run supports only this synthetic Godot parsed-action-plus-frame observation: after the first connected adjustment, removing the Label/receipt callback did not prevent subsequent numeric HSlider changes in this same double-restoration sequence. It does not establish internal consumption details, physical key repeat/timing, OS input, rendered or pointer behavior, accessibility, production UI behavior, or a general HSlider guarantee. No source edits or engine runs were performed for this read-only critique.
