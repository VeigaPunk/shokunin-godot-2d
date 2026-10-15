# Round 13 juice scout — LEAF

## Finding
Godot 4.7.2 headless supports a narrow, testable `Tween` → `CanvasItem.modulate` transient property change. A scratch-only `SceneTree` probe used a `Sprite2D` with baseline white `(1,1,1,1)`, then `create_tween()` with a 0.20 s color tween to `(1.0,0.2,0.2,1.0)` and a 0.20 s tween back to baseline. It sampled the actual `target.modulate` after `await process_frame` and detected a non-baseline intermediate state followed by return to baseline after 62 frames. A 90-frame cap is a reasonable conservative bounded wait for this exact 0.40 s sequence on the tested runtime; require both observations and fail if the cap expires. Do not use a single assumed frame count as proof of duration.

The same scratch script had a `--no-start` branch skipping only tween creation/start. Over the same 90-frame observation window it stayed at baseline, never changed, and the control passed its expected unchanged-state assertion (exit 0). This is a credible skip-start negative if kept in the same fixture/script and classified as the expected mutant failure by the battery.

Runtime: `/usr/bin/godot --version` → `4.7.2.stable.arch_linux.ed1daf0bf`. Scratch script was `/tmp/r13_tween_probe.gd`; no repository fixture/source was edited and no commit made.

## Fixture recommendation
- Keep observations on the actual `CanvasItem.modulate` value, not a print-only marker, `Tween.is_running()`, or a requested target value.
- Capture baseline after attaching the target and a process-frame yield. Assert observed change differs from baseline (prefer an approximate color comparison) and record at least one observed intermediate value; then assert return to baseline (approximate comparison) before a finite frame cap.
- Make the no-start argument skip only creation/start, retaining the same target setup, baseline capture, sample loop, and assertions. Its expected outcome is an unchanged baseline and a nonzero feature assertion; do not make the negative pass by changing the property manually.
- Use a fresh target and tween per process; no rendered image or screen capture is needed for this property-state claim.

## Overlap and limits
Existing `corpus/fixtures/animation_property.gd` tests `AnimationPlayer` driving `Node2D.position.x` with a direct `player.advance(0.5)` and checks `x=60`; its stuck mutant sets speed scale to zero. It does not exercise `Tween`, `CanvasItem.modulate`, a frame-observed transient state, return-to-baseline, or a no-start control. There is conceptual overlap in “animation changes a property,” but the proposed case adds a distinct runtime API/property/effect shape and a transient-return assertion. Scope it to that narrow executable coverage.

This establishes only a headless observed property transition. It does **not** establish that anything was rendered, that perceived brightness/flash occurred, that the effect is attractive/readable, or that it works with project art, gameplay timing, or production integration. Scratch timing is a feasibility result, not a battery result.
