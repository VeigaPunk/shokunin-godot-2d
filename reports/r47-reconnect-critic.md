# Round 47 reconnect calibration — adversarial review

## Verdict: measured candidate matches the declared synthetic expectation, with one adverse scratch attempt retained

Independent direct scratch used installed Godot `4.7.2.stable.arch_linux.ed1daf0bf`, an in-tree `HSlider` initialized to 5, fresh `InputEventAction` parsed events, one frame after each action, and the same nine-edge focus pattern. The first scratch path (`corpus/live/r47-reconnect-scratch`) failed to parse/run cleanly: a conditional array expression assigned to `Array[float]` caused a GDScript type error; the invocation was terminated (exit 143, 278s). This is adverse telemetry, not evidence. A bounded 30-second retry in a separate unique scratch (`corpus/live/r47-reconnect-retry-20261013T0809`) corrected that scratch-only typing issue and returned exit 0 with:

```
PASS SLIDER_R47_RECONNECT values=6,6,6,5,5,5,5,4,4 receipts=[6,4] Label=Value 4
```

The scratch asserts the expected GUI focus owner before each event and numeric value, full callback receipt history, and label after each event/frame. It asserts callback connected at start and after edge0; verifies disconnected after edge0 removal; verifies disconnected after edge3 action before reconnect; and verifies connected immediately after reconnect. The callback is reconnected after edge3's `ui_left` press and frame, before edge4. Measured numeric history is `6,6,6,5,5,5,5,4,4`; receipts stay `[6]` through edge6 and become `[6,4]` at edges7–8; label is `Value 6` through edge6, then `Value 4`.

## Adversarial checks / limitations

- The positive terminal is reachable only after the nine-loop checks; early ownership, value, receipt, label, or signal-state assertion failures quit nonzero first.
- Focus transfer schedule matches the declared r44 history: Button owns before edges1–2 and 5–6; slider before the others. Owner is asserted before all nine events.
- The callback transition is explicitly tested with `Signal.is_connected` around both disconnect and reconnect. No `value_changed` emission occurs on no-change edges, so `[6,4]` is consistent with the actual two numeric changes whose callback was connected.
- The first run's type error/long termination is retained; only the bounded unique-path retry yielded usable direct-engine evidence. Scratch files are untracked and the tracked fixture/runner were not edited by this reviewer.
- I did not perform a full battery replay or independently rerun the r44/r45/r46 paired modes; no claim about battery classifications or preservation is made here.

Scope is parsed synthetic input plus frames in headless Godot only. This does not establish OS key repeat, physical input/timing, rendered or pointer interaction, accessibility, production behavior, generic slider behavior, or internal consumption of unchanged edges.
