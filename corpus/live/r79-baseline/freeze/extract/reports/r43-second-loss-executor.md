# Round 43 executor — second focus loss

## Claim and result
Real Godot 4.7.2 scratch reproduced the proposed sequence. The second Button focus handoff suppresses the final left press: values were `6,6,6,5,5,5,5`, receipts `[6,5]`, and Labels remained `Value 6` / `Value 5` after their corresponding transitions. The seventh check completed and only then the dedicated expected-negative branch exited 2. This supports the stated bounded calibration claim; no discrepancy observed.

## Direct scratch evidence
- Engine: `Godot Engine v4.7.2.stable.arch_linux.ed1daf0bf` (`godot --version` reported `4.7.2.stable.arch_linux.ed1daf0bf`).
- Baseline positive `--repeat-right --focus-restore`: exit 0; values `6,6,6,5,5,4,4`, receipts `[6,5,4]`, labels `Value 6`, `Value 5`, `Value 4`.
- Candidate `--repeat-right --second-focus-loss`: exit 2 after all seven owner/state/receipt/Label assertions; output `SLIDER_REPEAT_SECOND_FOCUS_LOSS values=6,6,6,5,5,5,5 receipts=6,5 Labels=Value 6,Value 5`, followed by the distinct expected-negative diagnostic `SLIDER REPEAT SECOND-FOCUS-LOSS ASSERTION FAILED: expected final restored-focus adjustment after seven checks`.
- Scratch project and engine output: `.shokunin/game-dev-2d/corpus/live/r43-second-loss-executor/scratch/` (locally created, not seeded).

## Candidate edits
After scratch evidence, added `--second-focus-loss` mode to `corpus/fixtures/slider_adjust.gd`. It asserts the GUI focus owner before every fresh parsed action, dispatches one event and awaits one process frame per edge, then checks expected value, cumulative `value_changed` receipts, and Label after each edge. Button owns focus for edges 1–2 and 5–6; slider owns it for edges 0 and 3–4. Its terminal expected-negative diagnostic is distinct and occurs after all seven assertions.

Added one ordinary negative case to `corpus/fixtures/run_battery.py`: `slider_adjust_repeat_right_second_focus_loss`, expected exit 2 with that exact diagnostic. Added an empty diagnostic allowance for the expected case, matching existing negative-control classification. No other files edited by executor.

## Validation and scope
Direct candidate scratch replay after edit returned exit 2 with the expected seven-edge evidence and terminal diagnostic. Full one-run default battery replay recognized the new row with the expected exit/signature; this initial integrated run ended `1/20261013T071456617101Z/verdicts.json` because the ordinary battery includes `export_readiness`, which returned PASS but its preset-missing negative returned exit 1 (shown as `FAIL export_preset_missing` in this run). Thus this is not a full-battery PASS and must not be cited as such. The new slider row itself was correctly recognized as an expected negative. No engine/editor/seeded fixture edits, commits, push, or merge.

Scope is a synthetic parsed-event/frame sequence, not OS repeat, physical keyboard timing, rendering/pointer behavior, accessibility, production, or a generic slider guarantee.
