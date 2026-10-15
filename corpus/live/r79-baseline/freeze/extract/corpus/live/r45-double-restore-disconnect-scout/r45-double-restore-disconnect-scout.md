# Round 45 paired scratch scout — double restoration, disconnected signal

**Claim under test:** With only the `value_changed` callback disconnected, the r44 nine-edge sequence should retain its numeric HSlider trajectory while receipts stay empty and the Label remains at its initial `Value 5`. Connected control should retain receipts `[6,5,4]` and update the Label.

## Method
Used a fresh scratch project under `corpus/live/r45-double-restore-disconnect-scout/scratch`, copied the current in-tree `slider_adjust.gd` and `project.godot` without changing tracked files, and ran the existing script directly with `/usr/bin/godot --headless` (Godot 4.7.2.stable.arch_linux.ed1daf0bf). Both commands used the same fixture path and nine-event `--repeat-right --second-focus-restore` scenario; disconnected run added only `--disconnect-signal`.

Connected command:
```
godot --headless --path <scratch> --script <scratch>/slider_adjust.gd -- --repeat-right --second-focus-restore
```
Observed exit 0, stdout `PASS slider_adjust_repeat_second_focus_restore focused=true values=6,6,6,5,5,5,5,4,4 receipts=6,5,4 Labels=Value 6,Value 5,Value 4`.

Disconnected command adds `--disconnect-signal` to user args. **Observed exit 0 and the same connected PASS line/receipts/Label.** Thus the hypothesized disconnected result did not occur. Inspection shows the existing `--second-focus-restore` branch unconditionally prints PASS/quit(0) after per-edge checks; it only adjusts per-edge expected receipts/Label when disconnected, but does not check that the connected callback is actually absent and does not assert the final disconnected negative outcome. The direct test therefore exposes a branch bug, not evidence for calibration: disconnected path passed falsely because the final `quit(0)` bypasses the negative terminal assertion.

The r44 connected control reproduced its expected path. The disconnected run does *not* satisfy the round-45 hypothesis (no observed `receipts=[]` or `Label Value 5`). Per instructions HOLD; no fixture/runner edit performed. Needed correction: in this branch, after all nine edge checks, branch on `disconnected`; require final value 4, empty receipts, `Value 5`, then emit expected-negative diagnostic and `quit(2)`; connected branch remains PASS exit0 with `[6,5,4]` / `Value 4`. Before any edit, verify callback disconnection and per-edge expected values/owner assertions in real Godot scratch.

Scope: headless synthetic parsed actions + process frames only; does not test OS key repeat, physical timing/input, rendered or pointer UI, accessibility, production, or internal consumer of unchanged edges.
