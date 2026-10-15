# Round 15 gauge scout

## Finding

Godot 4.7.2 headless can instantiate a `TextureProgressBar`, observe its `value`, and receive its `value_changed` signal when a health-like signal handler assigns a different value. The range setter clamps an out-of-range assignment and reports the clamped value. This is distinct from `ui_signal_hud.gd`, which asserts Label text (`Score: 7`) after a signal; it does not exercise a range Control or its value-change receipt.

## Scratch evidence

Ran a disposable `/tmp/r15-gauge-e191mw7r` project with `/usr/bin/godot --headless --path <scratch> --script res://probe.gd` (installed engine identified itself as Godot 4.7.2.stable). Setup used `TextureProgressBar.new()`, `min_value=0`, `max_value=100`, `step=1`, and initial `value=100`; connected a `health_changed(float)` handler that assigns `bar.value`, and a `value_changed(float)` callback that appends receipts. After adding the bar under `root` and awaiting `process_frame`, verified in-tree and initial value. Emitting `health_changed(63)` gave `value=63`, receipts `[63]`. Emitting `health_changed(140)` gave clamped `value=100`, receipts `[63, 100]`. Process exited 0 with `PASS gauge in_tree=true value=100 receipts=[63.0, 100.0]` and no stderr.

The paired disconnection control conditionally omitted `health_changed.connect(_on_health_changed)` and otherwise ran the same assertions. It exited 2 at the positive assertion: `value=100.0 receipts=[]` (reported `positive failed`), confirming that the control does not accidentally pass without the health-to-gauge connection. This scratch control fails on the same value/receipt assertion; production fixture should likewise use an identical assertion and expected negative classifier signature/exit.

## Bounded fixture recommendation

- Build the bar entirely at runtime; add it to the SceneTree and wait one `process_frame` before asserting `is_inside_tree()` and initial value.
- Set the range and initial value before connecting/clearing the receipt collector, to avoid counting setup as gameplay.
- Connect a typed health signal to a handler that assigns `TextureProgressBar.value`; connect `value_changed` to collect actual emitted values.
- Positive: emit an in-range changed health value (e.g. 63), assert exact bar value and exactly one corresponding receipt. Then emit an above-maximum health value (e.g. 140), assert clamp to 100 and the receipt reports 100. Keep the out-of-range check distinct from initial setup and avoid same-value assignments, which need not produce a change signal.
- Negative: command-line flag skips only the health-to-bar connection; emit the same health update and fail on the same value/receipt assertion with a stable expected error and nonzero exit. The observer connection to `value_changed` remains in place.
- Use a bounded one-frame setup wait; no rendering loop, assets, timers, or visual inspection are needed.

## Claim limits

This establishes runtime Control property and signal behavior in the installed headless Godot 4.7.2 build, plus a synthetic disconnected-signal contrast. It does not establish rendered fill pixels, theme/texture correctness, visual appearance, player readability, or production health integration. Scratch values demonstrate numeric range clamping; they are not evidence about a visible gauge.
