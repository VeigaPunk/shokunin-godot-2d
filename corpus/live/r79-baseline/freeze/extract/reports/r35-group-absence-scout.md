# Round 35 group-absence scout

## Result
Measured paired Godot 4.7.2 scratch runs using native `Button` controls with `toggle_mode=true`, initial A selected, identical signal connections, and focused B then A `ui_accept` actions. In the control run A and B share one `ButtonGroup`; in the treatment only B's `button_group` assignment is omitted. Both start from the same fixture source copied to the scout scratch project; only that membership assignment is conditionalized. No tracked fixture or runner was edited.

- **Grouped:** setup A=true/B=false, Label=A. After focused B action: A=false/B=true, receipts `[A:false, B:true]`, Label=B. After focusing A and the same action: A=true/B=false, receipts `[A:false, B:true, B:false, A:true]`, Label=A.
- **B ungrouped:** setup A=true/B=false, Label=A. After focused B action: A=true/B=true, receipts `[B:true]`, Label=B. After focusing A and the same action: A=true/B=true, receipts `[B:true, A:true]`, Label=A. A was already pressed, but the focused native Button still emits `toggled(true)` on `ui_accept`; importantly no A:false or B:false event occurs.

The observable difference already exists after B: grouped A is cleared and emits `A:false`; ungrouped A remains selected and has no such receipt. The second action confirms the ungrouped pair remains simultaneously selected; Label tracks the last `toggled(true)` receiver in both arms. Thus a sound negative assertion should check **after B** that ungrouped A remains true and exact receipts are `[B:true]` (and Label B), contrasted against grouped A=false/B=true and `[A:false,B:true]`. Do not expect the ungrouped after-A state to match grouped behavior or expect a B:false callback.

## Raw evidence / limits

Raw command outputs and exit codes are in `corpus/live/r35-group-absence-scout/{grouped,ungrouped}.{stdout,exit}.txt`; scratch project is alongside them. Both probes exited 0 after scout-only assertion relaxation so both actions and states were observed. Godot version: `4.7.2.stable.arch_linux.ed1daf0bf`. This is a bounded native behavior probe, not an engine guarantee. I did not edit `button_group_selection.gd` or `run_battery.py` and make no fixture-admission recommendation beyond the measured causal distinction.
