# Round 22 timeout feasibility scout

## Scope
Read-only feasibility probe; no delegation and no edits to engine/editor, seeded controls, or battery runner. Godot binary: `/usr/bin/godot`; version emitted by the executable: `Godot Engine v4.7.2.stable.arch_linux.ed1daf0bf (2026-08-17 01:18:38 UTC)`. Python: `3.11.17`.

## Scratch probe
Created only `.shokunin/game-dev-2d/corpus/live/r22-timeout-scout/project.godot` (copy of the fixture project config) and `timeout_probe.gd` under my scratch directory. One SceneTree script prints the exact marker `TIMEOUT_PROBE: same signature`; for `--hold-open`, it awaits a 30-second SceneTree timer before normal quit. No other fixture touched.

Both commands used `[godot, --headless, --path, <scratch>, --script, res://timeout_probe.gd, --]` (reject arm adds `--hold-open`). Normal arm: `subprocess.run(..., capture_output=True, text=True, timeout=8)` returned exit **0**, `error=None`, marker present once in stdout. Hold-open arm used timeout **2 s**: raised `subprocess.TimeoutExpired` after **2.0045 s**, with `stdout` containing the engine banner and the exact same marker once, `stderr=None`; no return code exists, so expected wrapper representation is `code=None`, explicit timeout error. This is sufficient to show signature alone is not enough and the contrast is reproducible.

## Python timeout output detail
In this environment (`text=True`), `TimeoutExpired.stdout` was a **str** (not bytes) and held output through the marker. CPython documents/commonly exposes partial output as bytes even in text mode, so production handling must support both, as the existing `run_process` helper does at lines 95–98. Do not assume `.decode()` unconditionally. The observed normal and timed-out arms share script and marker.

## Limits / handoff
This was a direct `subprocess.run` timeout behavior probe, not a test of runner integration, forced cleanup, child liveness after timeout, arbitrary hangs, process trees, cross-platform semantics, or a full battery. `subprocess.run` timeout path is intended to kill and wait for its direct child before raising; this scout did not independently record post-timeout child liveness. For round admission, executor/verifier should capture returned timeout record/classification and demonstrate no direct child survives. Scratch files are under `corpus/live/r22-timeout-scout/`.
