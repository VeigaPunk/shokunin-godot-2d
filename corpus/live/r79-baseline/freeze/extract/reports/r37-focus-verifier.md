# Round 37 named non-author verifier — HSlider focus absence

## Scope and independent measurement

I independently replayed the r37 focus-absence control in Godot `4.7.2.stable.arch_linux.ed1daf0bf` using the tracked in-tree `slider_adjust.gd` and runner. The focused positive uses an HSlider (min=0, max=10, step=1, initial=5), grabs and checks focus before both fresh parsed `InputEventAction` pairs (`ui_right`, then `ui_left`, pressed/released with frame waits), and uses the connected `value_changed(float)` callback/Label. Observed values were 5→6→5, callback receipts `[6,5]`, Label `Value 6` then `Value 5`. The disconnected row kept the same actions and focus, moved 5→6→5, had no receipts, retained `Value 5`, then emitted its intended negative diagnostic and exited 2.

For `--no-focus`, the fixture does not call `grab_focus`; before each action it checks the slider is not focus owner. Both complete parsed actions leave the value at 5, receipts `[]`, and Label `Value 5`. Only after both does it print `SLIDER_NO_FOCUS values=5.0,5.0 receipts=[] label=Value 5 focus_owner=<Object#null>` and emit the exact final `ERROR: SLIDER NO-FOCUS ASSERTION FAILED: expected focus-dependent adjustment values=6,5` (exit 2). This is the expected negative, not an observed-state-only classification.

## Full default-path replay

Ran exactly:

```text
python .shokunin/game-dev-2d/corpus/fixtures/run_battery.py --probe-failing --probe-unrelated-error --probe-export-launch --probe-godot-error --probe-stream-attribution --probe-crash-exit --probe-timeout
```

Exit 0; 62/62 overall PASS = 51 ordinary + 2 mutants + 9 opt-in probe groups. Raw stdout and JSON are retained at `corpus/live/runs/20261013T060220331134Z/` (`verdicts.json`; export, Godot-error, stream-attribution, crash-exit, and timeout probe artifacts alongside it). I copied `verdicts.json` byte-identically to `corpus/lessons/r37-focus-verifier.json` (SHA-256 `aa14fc53eadb717b3f66475a22c424961cceb0257b60cd0e6332dd421da09b05`). All 61 prior r36 result-row `(verdict, actual_exit, signature)` triples are unchanged; the only new result row is `slider_adjust_no_focus`, PASS with expected/actual exit 2 and the exact final intended signature above. The Godot-error and stream-reject inner FAIL classifications remain expected probes; their outer groups PASS.

The executor's earlier full replay with a classifier/signature draft mismatch is preserved in its scratch run directory as telemetry, not treated as passing evidence. My clean replay above independently verifies the final classifier.

## Separate fault injection and sabotage

Ran fault injection separately from the seeded battery. Raw `fault-verdicts.json` is retained at `corpus/live/r37-focus-verifier-fault/20261013T060333668772Z/` and copied byte-identically to `corpus/lessons/r37-fault-verifier.json`. Outer fault-injection verdict is PASS while the deliberate inner results remain visible: timeout FAIL, clean expected-negative PASS (exit 2), and unrelated-error FAIL. These are fault detections, not battery rows.

In disposable scratch `corpus/live/r37-focus-verifier-sabotage/`, I forced `grab_focus()` even under `--no-focus`. The run exited 2 at `SLIDER no-focus setup assertion failed: slider owns GUI focus`, before action injection; this does not false-PASS as an absence control. No tracked source was edited for sabotage.

## Integrity and bounded verdict

Tracked source SHA-256 before and after verification: `slider_adjust.gd` `099bef37e61342d371d77bcd750106ceddb686b0f20ef36fed80e1b759a1449e`; `run_battery.py` `69d94dd63f0a32769731d7942b831a3d7e7ad84a5ce571153df2abe231a1914f`. No engine/editor or seeded controls changed. Calibration evidence supports the paired focus-presence/focus-absence contrast; prior result triples are preserved. Scope is headless-only synthetic parsed-action GUI focus routing in Godot 4.7.2. No rendered/pointer input, physical keyboard/timing, OS window focus, accessibility, production UI, or general slider assurance is claimed. No commit, push, or merge.
