# Round 37 focus absence critic — HOLD / causal premise falsified

## Scope
Read-only critic; no tracked fixture or runner edits. This report records a scratch-only paired test of the proposed HSlider focus-absence calibration arm. Godot version: `4.7.2.stable.arch_linux.ed1daf0bf`.

## Paired measurement
- Positive: copied tracked `slider_adjust.gd` plus `project.godot` into `.shokunin/game-dev-2d/corpus/live/r37-focus-critic-positive/`; ran `godot --headless --path <dir> --script slider_adjust.gd`. Exit 0; exact result: `PASS slider_adjust focused=true range=0..10 step=1 values=6,5 receipts=6,5 Labels=Value 6,Value 5`.
- Candidate absence arm: copied the fixture into `.shokunin/game-dev-2d/corpus/live/r37-focus-critic/`; removed `slider.grab_focus()` and made setup assert `gui_get_focus_owner() != slider`, value=5, receipts=[], Label `Value 5`. The same connected `value_changed` callback / Label, same parsed synthetic ui_right pressed+released then ui_left pressed+released events, same waits; it performs owner checks before each action and additionally prints owner/value after each pair. Real output:
  ```text
  OBS right owner_is_slider=false focus_owner=<Object#null> value=5.0
  OBS left owner_is_slider=false focus_owner=<Object#null> value=5.0
  OBS no_focus values=5.0,5.0 receipts=[] label=Value 5
  ERROR: SLIDER NO-FOCUS CONTROL ASSERTION FAILED after both actions: expected no value change without focus
  ```
  Exit 2, from the intentionally requested negative assertion after both actions. The same programmatic action routing did not adjust value; no callback fired, Label unchanged.

## Falsification / finding
This supports the proposed focus counterfactual for this precise headless Godot 4.7.2 `Input.parse_input_event(InputEventAction)` path: actual viewport focus owner remains null during both actions, while the tracked focused positive moves 5→6→5. No automatic focus acquisition occurred, and no other Control owned focus. This directly answers the primary input-routing/focus attribution concern. Signal attribution is controlled: same connection and Label handler in both arms; only the focused arm transitions values and produces receipts. This does **not** prove general GUI routing, physical keyboard behavior, or focus behavior outside the isolated fixture.

However, the assigned instruction says HOLD if observed engine behavior is contrary. It was not contrary, but this remains a critic-only measurement: do not admit without executor's separate implementation/report and the required non-author full replay. There is no case count change from my work. The negative exit2 is expected/intended and after both actions, not a setup failure.

## Reproduction and files
Scratch source is only under `.shokunin/game-dev-2d/corpus/live/r37-focus-critic/` and `.../r37-focus-critic-positive/`; no tracked source was edited. Tracked fixture SHA-256: `099bef37e61342d371d77bcd750106ceddb686b0f20ef36fed80e1b759a1449e`; runner SHA-256: `9c6ed5e6b9f1283427e6be6d0ecd9eae512cf776641c9585a377fa4e1f4507cd`.
