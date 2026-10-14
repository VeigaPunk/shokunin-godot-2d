# Round 36 slider scribe — evidence and admission checklist

## Scope and baseline

Read-only scribe assignment. LOG proposes one coverage move: focused `HSlider` with `ui_right` then `ui_left`, values 5→6→5, observed `value_changed(float)` receipts and Label; paired signal-disconnected consumer traverses the same actions and values but has no receipts/Label updates. Before-state is 48 ordinary / 59 full from r35. `health_gauge` is programmatic `TextureProgressBar` coverage, not input-driven HSlider adjustment. Intended scope is headless synthetic input on the stated Godot runtime only.

I found no r36 wave artifacts or named verifier artifacts at inspection time. The r35 verifier report says the previous full default-path battery was 59/59 (48 ordinary +2 mutants +9 opt-ins), with prior r34 triples retained. This is context, not a fresh baseline replay or r36 admission evidence. No source or runner was read/changed for this scribe report.

## Required evidence before admission

- First scratch execution on Godot 4.7.2 must measure that the actual focused HSlider receives `ui_right`/`ui_left` from complete synthetic pressed/released actions; do not use direct `value` assignment as stimulus or manually emit signals. Preserve script, command, stdout, exit, focus-owner/action diagnostics in the scribe/executor scratch corpus.
- Record actual `min_value`, `max_value`, `step`, initial value, value after each action, signal argument/order/count, and Label after each action. Confirm exactly 5→6→5, `[6,5]`, and `Value 6`→`Value 5`; identify frames and action release boundaries. If actual mapping differs, revise the claim and LOG before implementation, or HOLD. If doubled/auto-repeat receipts occur, characterize them rather than masking them.
- In paired disconnected run, use same setup and two actions. Confirm values still change 5→6→5, receipts remain empty, Label remains `Value 5`, then classify exit 2 only at the intended missing-signal assertion after both actions—not during setup or after first input. This control distinguishes Range property behavior from signal-driven observer effects.
- Read-only critic must exclude direct property writes, manual emissions, signal wiring differences beyond intentional disconnect, focus/action mismatch, and observer/Label conflation. Scratch positive and disconnected arm must have same action sequence and control setup.
- Named non-author verifier must run default-path full battery, retain the raw byte-identical `verdicts.json`, report command/exit/counts and compare all prior 59 `(case, verdict, actual_exit, signature)` triples. Check new connected positive and disconnected expected-negative row signatures/exits, plus fault-injection outer/inner classification separately. Verify tracked source hashes remain stable during replay.
- Verify only assigned tracked scope is new `slider_adjust.gd` and causal runner edits; no engine/editor or seeded fixture change. No commit/push/merge by this scribe.

## Provisional disposition / limits

No axis verdict is supportable from this read-only note alone. If scratch does not show the declared mapping and exact receipts, HOLD—no speculative fixture. If verified, coverage may improve for bounded focused keyboard-driven numeric HSlider adjustment and its signal-disconnected contrast; depth and calibration remain unchanged unless evidence demonstrates otherwise. Do not claim rendered/pointer behavior, physical timing, accessibility, production behavior, broad Range/HSlider reliability, or general action-map guarantees. Constants proposed by LOG are ordinary 48→50 and full 59→61, only if both rows and prior-result preservation verify.
