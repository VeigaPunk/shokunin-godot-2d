# Round 56 named non-author verifier — push-frame then clear

## Verdict: PASS (bounded synthetic observation)

LEAF, no delegation. Runtime: Godot `4.7.2.stable.arch_linux.ed1daf0bf`. Read the standing mission, r56 LOG/declaration, all six wave1 reports, r52–r55 reports and committed lesson raws. The candidate is the additive `--push-frame-then-clear-release` branch. No tracked files were edited by this verifier.

## Full battery and immutable lesson receipt

Command:

```text
python .shokunin/game-dev-2d/corpus/fixtures/run_battery.py --probe-failing --probe-unrelated-error --probe-export-launch --probe-godot-error --probe-stream-attribution --probe-crash-exit --probe-timeout --runs .shokunin/game-dev-2d/corpus/live/r56-named-verifier-20261013T105550Z/full
```

PASS **81/81**: 70 ordinary cases + 2 mutants + 9 opt-in classifications. Source raw: `.shokunin/game-dev-2d/corpus/live/r56-named-verifier-20261013T105550Z/full/20261013T105550668723Z/verdicts.json` (SHA-256 `6b979618d730848499fba2c038c4a16c692518ce7b189e9130938c85ad52fdd5`). Copied once to `corpus/lessons/r56-pushframe-non-author.json`; verified byte-identical, SHA-256 `6b979618d730848499fba2c038c4a16c692518ce7b189e9130938c85ad52fdd5`. Compared with immutable `corpus/lessons/r55-frame-non-author.json`: all **71/71** tuple-bearing `(case, verdict, actual_exit, signature)` records match exactly by case and value. The single new tuple-bearing row is `slider_adjust_repeat_right_second_focus_restore_push_frame_then_clear_release`, expected-negative exit 2 with exact terminal `SLIDER PUSH FRAME THEN CLEAR RELEASE ASSERTION FAILED: expected no new receipt after eleven checks`. Nine opt-in classifications remain stable: export positive/negative `[true,false]`, Godot error `[true,false]`, stream `[true,false]`, crash `[true,false]`, timeout `[false,true,false]`. Intentional inner unrelated-error and stream-reject remain FAIL beneath their outer probe PASS.

Separate command:

```text
python .shokunin/game-dev-2d/corpus/fixtures/run_battery.py --fault-injection --runs .shokunin/game-dev-2d/corpus/live/r56-named-verifier-20261013T105550Z/fault
```

Outer fault-injection verdict PASS. Source raw: `.shokunin/game-dev-2d/corpus/live/r56-named-verifier-20261013T105550Z/fault/20261013T105639727230Z/fault-verdicts.json` (SHA-256 `2e11424fa1ed88086de6c92c4080eaa5aa508a6d5bc46127b64a7f5581d00e1c`); copied once to `corpus/lessons/r56-fault-non-author.json`, verified byte-identical, SHA-256 `2e11424fa1ed88086de6c92c4080eaa5aa508a6d5bc46127b64a7f5581d00e1c`. Inner outcomes: hang TIMEOUT/FAIL, clean expected-negative exit 2 PASS, unrelated-error exit 2 FAIL.

## Direct candidate and targeted sabotages

Unique direct scratch: `.shokunin/game-dev-2d/corpus/live/r56-named-verifier-20261013T105550Z/direct/project`; command `godot --headless --path . --script slider_adjust.gd -- --repeat-right --second-focus-restore --push-frame-then-clear-release`. Exit 2 at the exact intentional terminal after all eleven checked edges. The candidate measured edge10 after push + awaited frame: observer 3→4, action pressed=true, numeric 3, receipts `[6,3]`, Label `Value 3`, focus owner and callback true. After `Input.action_release("ui_left")` + second awaited frame: observer remained 4, action pressed=false, numeric/receipts/Label/focus/callback remained unchanged. Parsed edges 0–9, handoffs/restores, late reconnect and per-edge checks remain in the candidate.

- Omit-push scratch `.shokunin/game-dev-2d/corpus/live/r56-named-verifier-20261013T105550Z/sabotage-omit-push-fresh/project`: exit 2 early at push-frame intermediate assertion (observer 3, pressed=true); no candidate terminal.
- Omit-clear scratch `.shokunin/game-dev-2d/corpus/live/r56-named-verifier-20261013T105550Z/sabotage-omit-clear-fresh/project`: exit 2 early at clear-frame final assertion (observer 4, pressed=true); no candidate terminal.
- Omitted-await sabotage was not rerun in this named verification. r55’s omitted-await sabotage reached its terminal, so frame necessity is not established.

## Adverse telemetry and integrity

Verifier setup attempts retained under `.shokunin/game-dev-2d/corpus/live/r56-named-verifier-20261013T105550Z`: initial direct run failed before Godot because relative log redirection did not resolve from the scratch working directory; corrected unique direct run succeeded. First sabotage setup aborted on an overbroad snippet-count assertion; the next attempted directory collided with that scratch. Fresh uniquely named sabotage projects then ran as above. These are setup errors, not evidence.

Wave1 adverse attempts were read and retained in their reports: executor initial candidate run lacked observer registration (nil access/exit 143) and initial author replay timed out; corrected observer registration, fresh direct replay and corrected author replays supersede them. Critic’s initial wrong-guard/assertion replay is explicitly superseded by corrected causal replay. No adverse attempt is counted as PASS.

Tracked fixture/runner SHA-256 before and after verifier: `slider_adjust.gd` `9c7e21509b415fcbdfa0799e78897fd13e50edcad28e680075808ec5d212d77f`; `run_battery.py` `d546405ef2dcd18b5308cb81877b93905fb77102a364321bcc3a98c88c68c11d`. No constants changed. No committed r51–r55 receipt was changed; r56 lesson copies were verified byte-identical to the source raws. No commit, push, or merge.

**Scope:** only the synthetic Godot 4.7.2 substep observations in this fixture. No claim of frame necessity, physical timing, HSlider internals, OS input, rendering, pointer/accessibility, production behavior, or general event provenance.
