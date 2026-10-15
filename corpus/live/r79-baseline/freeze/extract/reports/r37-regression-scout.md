# Round 37 regression scout — read-only

## Scope

Measured the requested focus-absence counterfactual in an isolated scratch project using Godot 4.7.2 headless. Same in-tree `HSlider` setup as r36 (range 0..10, step 1, initial value 5), connected `value_changed(float)` callback updating a `Label`, and parsed synthetic `InputEventAction` press/release for `ui_right` then `ui_left`, with frames between events. Did not call `grab_focus()`. No tracked fixture/runner, engine/editor, or seeded control was edited.

## Actual focus owner and action result

Raw output: `corpus/live/r37-regression-scout/godot-raw.txt`; script: `corpus/live/r37-regression-scout/probe.gd`.

- Before `ui_right`: `gui_get_focus_owner()` was `<Object#null>`, `slider.has_focus()` false. After its press/release and frame waits: value 5, receipts `[]`, Label `Value 5`, focus owner remained null.
- Before `ui_left`: same null owner / `has_focus=false`. After its press/release and waits: value 5, receipts `[]`, Label `Value 5`, focus owner remained null.

This matches the proposed focus-absence observation; no contradiction requiring HOLD. Keep the intended negative exit2 after both complete actions (not on the first untouched value), and assert no slider focus before each action, values 5 after each, receipts empty, and Label unchanged. Since the callback is connected, this arm distinguishes focus-routed adjustment from mere action injection without conflating absence of a signal consumer.

## Prior coverage and operational caveats retained

- r36 `slider_adjust` is focused and checks parsed actions, focus owner, values 6 then 5, receipts `[6,5]`, and Label changes. Its disconnected control still adjusts 6 then 5 with no receipts and unchanged Label; it is not an unfocused control. `health_gauge` remains programmatic `TextureProgressBar` coverage, not input/focus evidence.
- Do not substitute `Input.action_press`/`action_release`: r36's measured scout found those did not adjust the focused HSlider, while parsed `InputEventAction` worked. This probe used the latter.
- Preserve prior export caveats: r36 notes relative export-target paths failed in this environment while absolute paths passed, and r20 explicit-relative `--runs` hit `StopIteration`; no export test was run here.
- Preserve timeout boundary: r22 establishes only the specific direct-child hold/timeout/kill/reap behavior, not descendant cleanup or generic timeout safety. Fault-injection inner failures remain distinct from real-Godot UI evidence. No export, timeout, or fault replay was done here.

## Bounded recommendation

The requested unfocused negative control is causally plausible on this measured runtime: no owner before either parsed action and no numeric transition or consumer receipt afterward. This is scratch evidence only; it does not replace the named non-author full replay or focus sabotage. Scope is headless synthetic focus routing only, not pointer/rendered input, physical timing, OS window focus, accessibility, production behavior, or general slider assurance. No changes to fixture/runner are recommended by this read-only scout.
