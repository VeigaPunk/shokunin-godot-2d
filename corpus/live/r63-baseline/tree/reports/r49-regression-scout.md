# Round 49 regression scout — post-late-reconnect press

Read-only regression scout for the bounded r49 candidate. I read `/tmp/mission-game-dev-2d-standing.md`, the r49 declaration and r44–r48 outcome entries in `.shokunin/game-dev-2d/LOG.md`, and prior r46–r48 regression-scout reports. I did not edit tracked fixtures/runner, seeded fixtures, engine/editor files, or prior reports; made no commit, push, or merge. My unique scratch is `.shokunin/game-dev-2d/corpus/live/r49-regression-scout-20261013/scratch/`.

## Direct bounded Godot 4.7.2 evidence

Godot reports `4.7.2.stable.arch_linux.ed1daf0bf`. I copied the fixture `project.godot` and `slider_adjust.gd` into my scratch and added only the candidate branch there. Command:

```text
timeout 15s godot --headless --path .shokunin/game-dev-2d/corpus/live/r49-regression-scout-20261013/scratch --script res://slider_adjust.gd -- --repeat-right --second-focus-restore --press-after-late-reconnect
```

The first scratch attempt failed to parse/type at a conditional expression assigning an untyped Array to `Array[float]`, then the outer timeout returned 124. It is retained as adverse telemetry, not candidate evidence. I changed only the scratch expression to construct a typed Array and reran. The successful command exited **0** in about 0.7s and emitted:

```text
SLIDER_PRESS_AFTER_LATE_RECONNECT values=6,6,6,5,5,5,5,4,4,3 receipts=[6,3] Label=Value 3 connected=true
PASS slider_adjust_repeat_second_focus_restore_press_after_late_reconnect
```

The branch preserved the nine r48 events and added one fresh `ui_left` pressed=true event (edge9). It asserted the expected focus owner before every event and value/receipts/Label after each frame. Callback was verified connected before edge0; after edge0's numeric6/receipt `[6]`/Label `Value 6`, disconnected, remained disconnected through edge7 numeric4/receipt `[6]`/Label `Value 6`, then reconnected after edge7 checks. Edge8 release retained 4/`[6]`/`Value 6`; edge9 press changed numeric value to3, appended receipt3, and updated Label to `Value 3`. The success marker and exit0 occur after all ten checks. This is scratch candidate evidence only, not tracked integration or independent named-verifier certification.

## Read-only prior-branch / regression caveats

- r44 connected nine-edge baseline: numeric `6,6,6,5,5,5,5,4,4`, receipts `[6,5,4]`, Label ends `Value 4`.
- r45 start-disconnected control: same nine numeric values, receipts `[]`, Label `Value 5`, expected exit2 only after nine checks.
- r46 disconnect-after-edge0: same numeric values, receipts `[6]`, Label `Value 6`, expected exit2 after nine checks.
- r47 reconnect-after-edge3: same nine values; receipts `[6]` through edge6 then `[6,4]` at edges7–8, Label changes to `Value 4`; positive exit0.
- r48 disconnect after edge0, reconnect only after edge7 value4 check: same nine values, receipts `[6]` and Label `Value 6` throughout including connected edge8 release; expected exit2 after nine checks. Its row/branch is a distinct adverse counterfactual and must remain unchanged beside r49's new positive arm.
- Keep r47's additive reconnect row/branch intact (r47 report records an earlier replacement caught/restored); preserve r48 nine-edge expected-negative row byte-exact. This scout did not run the battery or establish historical tuple stability.
- Fault caveat: prior fault-injection outer/meta PASS wraps deliberate inner hang/timeout and unrelated-error FAILs; only the clean expected-negative inner case is PASS. Timeouts bound tested child invocation, not general descendant cleanup.
- Export caveat: historical export launch failure for relative target (`Prepare Template: The given export path doesn't exist.`) is separate; no export, timeout or fault path was exercised here.

Evidence scope is headless Godot 4.7.2, synthetic parsed events and process-frame waits. No OS key-repeat, physical input/timing, rendered/pointer UI, accessibility, production/generic slider behavior, generic signal replay, or internal consumption of unchanged edges is claimed. No engine/editor/seeded mutation, tracked code edit, commit, push, or merge.
