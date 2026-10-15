# Round 59 audio bus probe — minimal design

## Recommendation

Add one additive fixture and two battery rows: a positive explicit non-Master route and a paired invalid-name control. Keep the existing `audio_playback` cases unchanged. The probe should synthesize its short WAV as the existing fixture does; do not depend on an audio asset or audible output.

In each fresh headless invocation, add one `FixtureBus` to `AudioServer` (after Master), set its name, and verify `get_bus_index("FixtureBus")` is a valid index distinct from Master. Create/in-tree an `AudioStreamPlayer`, assign the requested bus (`FixtureBus` positive, a unique nonexistent name negative), and start playback. After a bounded number of process frames, record the requested `player.bus`, `AudioServer.get_bus_index(player.bus)`, the effective bus name/index if exposed by the engine, `is_playing()`, and playback positions. Stop/free before exit.

The positive passes only if its named bus resolves to the exact non-Master index and playback is active with position advancement. The negative must be judged by observed effective route, not by assuming assignment throws or exits nonzero: Godot may warn and fall back to Master. It passes as a negative control only if it does **not** resolve to `FixtureBus` (ideally record/require Master fallback); playback alone is not evidence of routing. Fail the fixture if invalid input unexpectedly resolves to the target bus or if observations cannot establish the route. Print explicit structured markers for both outcomes.

## Causal contrast / limits

Use the same script and setup with only the requested bus name varied (user argument or two fixed case arguments). Assert the positive and negative independently so the invalid-name behavior is measured rather than inferred from stderr. For causal sensitivity, scratch-test a sabotage that substitutes `Master` in the positive arm: it must fail the positive assertion. Preserve raw stdout/stderr and actual exit for both arms; do not make warnings the sole oracle.

This establishes only headless Godot 4.7.2 bus-name resolution/routing metadata plus synthetic playback progression. It does not establish audible output, mixer fidelity, device output, production sound, or platform behavior. Before fixture integration, run the two arms in unique scratch and capture actual invalid-bus semantics; if `get_bus_index(player.bus)` only reflects the requested string, use the engine's effective route API (e.g. `get_bus()`, after confirming availability/semantics) or hold rather than claiming effective routing. A mere property echo is insufficient.

## Scope

Read-only design; no fixture/runner edits or engine execution performed. Existing seven opt-in battery flags and 87 prior classifications must remain untouched/stable; run-local scratch only. Parent's named non-author replay remains required before admission.
