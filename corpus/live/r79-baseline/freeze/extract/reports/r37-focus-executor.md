# Round 37 executor report — HSlider focus absence

## Measurement before edit
On Godot 4.7.2.stable.arch_linux, a scratch copy ran the same slider, parsed ui_right then ui_left press/release actions, signal connection, and Label as the positive fixture, omitting only `grab_focus()`. Before each action the GUI focus owner was `<Object#null>` and `slider.has_focus()` was false. After each action value remained 5; receipt list remained `[]`; Label stayed `Value 5`. Exit 2 came after both actions. This is a real contrast with focused 5→6→5 and disconnected-signal 5→6→5/empty-receipts. Scratch raw output and exploratory probe are in `corpus/live/r37-focus-executor-scratch/` (the early exploratory probe is not a battery test).

## Implementation
Added only `--no-focus` to `slider_adjust.gd` and one `slider_adjust_no_focus` negative row to `run_battery.py`. Positive focused path and disconnected path preserve their original actions/assertions. No-focus still connects the same `value_changed` callback; it confirms slider never owns focus, applies both complete parsed actions, records values/receipts/Label, then exits 2 at the intended `SLIDER NO-FOCUS ASSERTION FAILED` check. Runner classification requires that final exact intended diagnostic, not merely the observation line.

## Replay
Full command: `python .shokunin/game-dev-2d/corpus/fixtures/run_battery.py --runs .shokunin/game-dev-2d/corpus/live/r37-focus-executor-full --probe-failing --probe-unrelated-error --probe-export-launch --probe-godot-error --probe-stream-attribution --probe-crash-exit --probe-timeout`

Final replay artifact: `corpus/live/r37-focus-executor-full/20261013T055856271822Z/verdicts.json`; outer exit 0, 62/62 PASS = 51 ordinary +2 mutants +9 opt-ins. `slider_adjust_no_focus` is expected exit 2/PASS; raw stdout observation `SLIDER_NO_FOCUS values=5.0,5.0 receipts=[] label=Value 5 focus_owner=<Object#null>` followed by exact expected `ERROR:` diagnostic. Focused and disconnected rows retain PASS. Initial full run had a signature mismatch (runner expected observation instead of intended final error); subsequent classifier update fixed it. The initial failed replay at `20261013T055719890435Z` is retained as telemetry, as are earlier mutant experiments. Godot unrelated-error and stream reject inner FAILs are deliberately accepted detection outcomes and outer probe groups PASS.

Changes: `slider_adjust.gd` SHA-256 `099bef37e61342d371d77bcd750106ceddb686b0f20ef36fed80e1b759a1449e`; `run_battery.py` SHA-256 `69d94dd63f0a32769731d7942b831a3d7e7ad84a5ce571153df2abe231a1914f`. No engine/editor, seeded control, commit, push, or merge changes.
