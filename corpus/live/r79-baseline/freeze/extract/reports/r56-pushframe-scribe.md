# Round 56 push-frame scribe — read-only evidence checklist

## Scope and current status

Read-only scribe; no delegation, no tracked edits, no Godot run, and no seeded corpus changes. This report records the required evidence and the inspected baseline. I have not observed a Round 56 causal run or any Round 56 setup failures in this workspace at report time; do not interpret the checklist as a PASS or proof. Record every later setup failure (command, exit/status, output/raw path) as adverse, never as a successful measurement.

Claim under test is only the synthetic edge-10 substep pattern: push a matching `ui_left` release, await a process frame, then `Input.action_release("ui_left")` and await another frame. Required direct checks: at first substep observer 3→4 and action still pressed=true; after second substep observer stays 4 and pressed=false; numeric value 3, receipts `[6,3]`, Label `Value 3`, slider focus/owner and callback-connected remain true throughout. Preserve parsed edges 0–9, two focus handoffs/restores, late callback reconnect, and owner/callback prechecks before every edge plus numeric/full receipts/Label checks after each edge. Compare r52 push-only, r53 same-frame push+clear, and r55 clear-frame+push controls. Do not infer frame necessity (r55 omit-await sabotage was ineffective), physical timing, HSlider internal consumption, OS/render/pointer/accessibility/production, or general event provenance.

## Evidence checklist for executor / eventual verifier

- [ ] Unique scratch per role/run; Godot version and exact command recorded; all setup failures/adverse retries retained.
- [ ] Read-only tracked baseline hashes captured before and after non-author work; no editing committed lesson raws.
- [ ] Before any tracked edit: causal scratch run directly exhibits both requested substeps, all eleven history checks, expected values/receipts/Label/focus/callback, with comparison to controls. If not, HOLD; no tracked candidate row.
- [ ] If causal and executor proceeds: only executor edits `slider_adjust.gd` and `run_battery.py`; strictly additive new `--push-frame-then-clear-release` branch, one CASE, exact expected-negative allowance; r51–r55 tracked content byte-exact.
- [ ] Author ordinary/full results and denominator reported; expected proposal ordinary 70/full 81, but only report actual measured totals.
- [ ] Named non-author replay on fresh unique scratch: seven-flag full battery and separate fault-injection raw; capture unique source raw and copy once only after validation. No delegation. Verify expected-negative terminal and both edge10 substep assertions.
- [ ] New branch omit-push and omit-clear sabotage each fails early at its targeted assertion, before the exact terminal and rejected by production classifier. Retain any ineffective sabotage as adverse, not support.
- [ ] Compare all 71 prior tuple-bearing rows exact `(case, verdict, actual_exit, signature)` against r55; verify all nine opt-in classifications unchanged. Report row counts from raw, not inferred totals.
- [ ] Compare source/copy SHA-256; report tracked fixture/runner hashes unchanged during verifier; never overwrite committed r51–r55 lesson raws.
- [ ] Keep verdict bounded to the directly measured synthetic substeps. Parent makes admission decision; no commit/push/merge by this lane.

## Inspected immutable baseline

- r55 verifier reports Godot 4.7.2, full 80/80 (69 ordinary + 2 mutants + 9 opt-ins), 70/70 prior r54 tuple matches, 9/9 opt-ins stable, and separate fault outer PASS. Its r55 record explicitly says omitting intermediate await still reaches terminal, so frame necessity is unsupported.
- Current r55 full raw has 80 result records and verdict PASS. SHA-256: `ecaa7807e1eb7d01914ac8b3e9837c349c1e80f4032978ac727a2e20037c3e51`.
- Current r55 fault raw SHA-256: `2e11424fa1ed88086de6c92c4080eaa5aa508a6d5bc46127b64a7f5581d00e1c`.
- Current tracked fixture SHA-256: `0b287ea2a687e48045359949cd83ef222c2255bf67ecd2c472e688cc90480035`; runner: `d57b8f477c3507122dfb1d7d35040487c8d54598c75b6587a45484e710f3875d`. These are scribe observations only; capture fresh hashes at actual run time.
- r52–r54 lesson/report evidence aligns with the LOG summary: push-only observer advances while action remains pressed; same-frame push+clear and reversed clear+push share final measured state; r55 separated clear-frame then push shows intermediate clear-only state. Their conclusions are synthetic post-state observations, not route uniqueness or HSlider internal behavior.

No constants changed. No assumptions beyond the supplied round claim and preceding records; no engine/editor/seeded changes, commit, push, or merge.
