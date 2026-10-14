# Round 36 regression scout — read-only

## Scope

Read-only review of prior UI/health-gauge coverage and export/timeout/fault caveats, plus an isolated scratch check of the proposed `HSlider` input semantics. No fixture, runner, engine/editor, or seeded control was edited. Probe files are confined to `corpus/live/r36-regression-scout/`.

## HSlider runtime measurement

Runtime: Godot 4.7.2.stable.arch_linux.ed1daf0bf, headless. A scratch `SceneTree` attached an `HSlider` to an in-tree `Control`, set range 0..10, step 1, value 5, `FOCUS_ALL`, awaited a frame, and confirmed `has_focus() == true` after `grab_focus()`.

Important input distinction: `Input.action_press("ui_right")` / `action_release` and the equivalent `ui_left` calls did **not** adjust this focused slider (value remained 5; no signal receipts). This is not evidence that the proposed action works; do not use these methods as the fixture stimulus. Repeating with synthetic `InputEventAction` instances passed through `Input.parse_input_event` did work: right press changed 5→6 and emitted exactly `[6.0]`; release caused no duplicate. Left press changed 6→5 and emitted exactly `[6.0, 5.0]`; release caused no duplicate. This supports the proposed two-transition behavior only with parsed input events and should be reported precisely. Raw scratch script/output: `corpus/live/r36-regression-scout/probe.gd`; Godot command `godot --headless --path .shokunin/game-dev-2d/corpus/live/r36-regression-scout --script res://probe.gd`.

## Prior UI coverage / distinction

`health_gauge.gd` is programmatic: an emitted `health_changed(float)` signal's connected handler assigns `TextureProgressBar.value`; it tests observed gauge value changes, clamping at 0/100, repeated-value suppression, and `value_changed` receipts. It does not exercise keyboard focus or user-input-driven adjustment of a `Range` control. `ui_signal_hud.gd` similarly emits `score_changed(int)` programmatically and checks a `Label` update. Thus an in-tree focused HSlider action sequence is distinct at the narrow mechanism level, assuming the fixture uses `Input.parse_input_event` rather than `Input.action_press`.

The paired disconnected arm must be interpreted carefully: slider adjustment is itself performed by the Range input handling; a consumer disconnected from `value_changed` should not prevent value transitions. It can establish absence of consumer updates / receipts under those same actions, not that input processing is signal-driven. Ensure Label's unchanged text and an empty receipt array are asserted separately from the actual slider values.

## Regressions and caveats retained

- **Export:** prior r16/r17 captures preserve a real `Prepare Template: The given export path doesn't exist` failure; later r25 evidence isolated relative export-target paths as failing in this Godot environment while absolute targets passed. Do not weaken fail-closed export checks, retry away adverse evidence, or claim export reliability. The r20 explicit-relative-`--runs` `StopIteration` caveat is also not erased by later passing runs.
- **Timeout:** r22 real-Godot timeout probe supports only its specific timed hold/direct child: same marker before 0.75s timeout, explicit timeout classification, bounded kill/reap, and no surviving direct child. It does not prove descendant/process-tree cleanup, arbitrary hang detection, or general timeout safety. The positive startup margin is load-sensitive; failure to start in time is a false negative, not evidence to relax checks.
- **Fault injection:** Python fault-injection harness outcomes (including expected inner FAILs for injected hang/unrelated-error arms) are harness regression evidence, not real-Godot UI or general game-runtime coverage. Keep their per-case outcomes and meta PASS distinction honest; they do not establish process-tree behavior.

## Finding

Proposed focused keyboard coverage is feasible on the tested runtime only when the synthetic action is delivered as `InputEventAction` via `Input.parse_input_event`. The tempting `Input.action_press` API did not stimulate the GUI control in this test. The paired connected/disconnected interpretation should center on Range value transitions versus consumer receipts/Label updates. No prior UI or operational caveat identified here supports broadening claims beyond that narrow headless fixture.
