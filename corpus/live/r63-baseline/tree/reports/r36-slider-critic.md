# Round 36 slider critic — actual input semantics

**Result: proposed focused-action behavior is observed in Godot 4.7.2; no falsifying input-route/focus/callback-count issue found.** This is read-only scratch evidence, not fixture admission or a battery replay.

Scratch project and script are under `.shokunin/game-dev-2d/corpus/live/r36-slider-critic/project/` (`slider_probe.gd`). Ran `godot --headless --path <scratch> --script <scratch>/slider_probe.gd`.

- An in-tree `HSlider` configured min=0, max=10, step=1, value=5 received focus (`has_focus=true`, viewport focus owner was that HSlider).
- A complete synthetic `InputEventAction` press+release for `ui_right`, injected with `root.push_input` and separated by process frames, changed value to 6.0 and delivered exactly one `value_changed(6.0)` receipt.
- The same `ui_left` sequence changed value back to 5.0 and delivered exactly one more receipt; accumulated order `[6.0,5.0]`.
- Disconnected-signal scratch variant, same focused HSlider and same actions, produced values 6.0 then 5.0 with receipts `[]`.
- Importantly, a scratch **programmatic** `slider.value=6; slider.value=5` variant also produced receipts `[6.0,5.0]`. `value_changed` receipts/value/Label alone therefore do not establish that keyboard input caused the changes. The fixture must retain explicit `InputEventAction` press/release injections (and preferably verify focus owner before them); it must not use `set_value` or manually emit the signal as its stimulus. The proposed fixture flow as logged does use explicit actions, so this overlap does not falsify that causal stimulus, but it is a real diagnostic confound if relying on receipts alone.
- This is distinct from `health_gauge.gd`: that fixture uses a `TextureProgressBar` and intentionally programmatic health-signal updates/clamping. Both employ a Range-derived value_changed signal, so signal callback behavior is not novel by itself; coverage here is specifically focused keyboard action adjustment on an HSlider, with connected/disconnected consumers.

No action mapping correction needed for tested `ui_right`/`ui_left`; observed exactly one step and one callback per action. Evidence is limited to headless synthetic input on Godot 4.7.2 and does not establish physical keyboard, rendered pointer, or broader slider behavior. No seeded fixture, engine/editor code, runner, or controls changed.
