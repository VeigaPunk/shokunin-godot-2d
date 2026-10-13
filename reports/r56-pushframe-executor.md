# Round 56 push-frame-then-clear executor

## Causal scratch (before tracked edits)

Unique scratch: `.shokunin/game-dev-2d/corpus/live/r56-pushframe-executor/scratch/project/`, copied from the tracked fixture. Godot 4.7.2.stable.arch_linux.ed1daf0bf. The scratch branch preserved parsed edges 0–9, focus transfers/restores, callback disconnect/reconnect, owner/connection prechecks, and per-edge numeric/receipt/Label checks. At edge10 it pushed the matching `InputEventAction(ui_left,false)` then awaited `process_frame`; assertions passed for observer 3→4, action pressed=true, numeric 3, receipts `[6,3]`, Label `Value 3`, focus and callback true. It then called `Input.action_release("ui_left")`, awaited `process_frame`; observer stayed 4, pressed=false, numeric3/[6,3]/Value3/focus/callback remained true. The unique expected-negative terminal was reached after all eleven checks (exit2). This directly establishes the bounded complementary intermediate result. Same-frame r53 push-then-clear and r55 clear-frame-then-push code paths were also run in this isolated scratch with their existing checks and terminal expectations; both reached their expected terminal. Push-only r52 control observed observer delta1 and pressed=true.

A first scratch launch occurred before observer registration was widened for this candidate flag and timed out; it is setup failure/adverse, not evidence. Fresh corrected scratch run above passed. No tracked changes preceded causal evidence.

## Additive tracked work

After scratch, the sole executor added one `--push-frame-then-clear-release` branch and one exact expected-negative battery case/allowance. Prior branches remain byte-exact; no constants changed. The branch checks owner and callback before every edge, all eleven edge values/receipts/Labels, and both substeps: first-frame observer 3→4 and pressed true, then second-frame observer remains4 and pressed false, preserving numeric3, receipts `[6,3]`, Label `Value 3`, focus/callback.

## Scope

Synthetic Godot 4.7.2 substeps only. Not a claim about frame necessity, physical timing, HSlider internals, OS input, rendering, pointer/accessibility, production, or generic provenance. No engine/editor/seeded changes, commit, push, or merge. Author batteries and prior tuple comparisons will be appended after execution.

Initial direct candidate launch lacked observer registration, nil-accessed and was terminated (exit143); battery replay before correction then timed out the added case under that setup and is excluded. Observer registration was extended additively to include the new flag; a fresh copied direct project then produced the expected exact terminal with all assertions. These are adverse setup attempts, not PASS evidence.

## Author battery and comparisons

- Fresh ordinary author replay: **70/70 PASS**; raw live source `.shokunin/game-dev-2d/corpus/live/r56-pushframe-executor/runs-author-corrected/20261013T105207256016Z/verdicts.json`. No author raw was written to `corpus/lessons/` (reserved for named verifier).
- Fresh full seven-flag author replay: **81/81 PASS** (70 ordinary + 2 mutants + 9 opt-in classifications); raw live source `.shokunin/game-dev-2d/corpus/live/r56-pushframe-executor/runs-full-corrected/20261013T105247366189Z/verdicts.json`.
- All **71/71** prior r55 tuple-bearing `(case, verdict, actual_exit, signature)` records match by case and values. Existing **9/9** opt-in classifications remain PASS. New case `slider_adjust_repeat_right_second_focus_restore_push_frame_then_clear_release` is expected-negative PASS, exit2, exact terminal signature after the eleven measured edges. Intentional inner unrelated-error and stream-reject conditions remain FAIL under their outer probe PASS.
- The first ordinary author run with missing observer setup failed added case (`actual_exit=None`); preserved at `.shokunin/game-dev-2d/corpus/live/r56-pushframe-executor/runs-author/20261013T104846933538Z/verdicts.json`, excluded. Fresh corrected run above is the author evidence.
- Current candidate is additive: only new branch and observer-registration flag in `slider_adjust.gd`, plus one case and exact allowance in `run_battery.py`. Tracked hashes: slider `9c7e21509b415fcbdfa0799e78897fd13e50edcad28e680075808ec5d212d77f`; runner `d546405ef2dcd18b5308cb81877b93905fb77102a364321bcc3a98c88c68c11d`. No further tracked edits by executor.
