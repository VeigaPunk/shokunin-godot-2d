# R12 audio scout — headless playback state (read-only)

## Finding

Godot **4.7.2.stable.arch_linux.ed1daf0bf** (local binary) can exercise `AudioStreamPlayer` playback state in `--headless`; no physical sound-output conclusion follows. A scratch-only `SceneTree` probe ran successfully with both default headless audio selection and explicit `--audio-driver Dummy` (exit 0). It generated an in-memory `AudioStreamWAV` (16-bit PCM) and an `AudioStreamGenerator`, assigned each to a player, and used `await process_frame` for bounded observation. `play()` made `is_playing()` true. The generator case obtained a non-null `AudioStreamGeneratorPlayback`, pushed bounded frames, and its playback position advanced from `0.0` to `0.0928798` after eight frames (dummy driver); the player remained playing. After `stop()` with a stream still assigned and eight bounded frames, the same player reported `is_playing() == false`, position `0.0`.

This establishes a feasible generated-stream positive and no-play control under this installed binary and headless dummy path. It does **not** establish audible sound, output-device operation, sound quality, or game integration.

## Probe shape / recommended assertion

- Use a minimal `SceneTree` script (no project/editor modifications), create an `AudioStreamPlayer`, add it to the tree, assign generated stream, then call `play()`.
- For `AudioStreamWAV`, populate valid PCM `data` bytes and set `format`, `mix_rate` and `stereo` consistently. `AudioStreamWAV` is finite; choose sufficient duration for the observation window or stop at a bounded point. Avoid asserting an exact position.
- For `AudioStreamGenerator`, configure `mix_rate` and `buffer_length`, call `play()`, then acquire `get_stream_playback()` (cast to `AudioStreamGeneratorPlayback`) and push bounded frames when available. Positive assertion should require `is_playing()`, non-null playback, and `get_playback_position() > 0.0` after bounded processing. In the local dummy-driver probe generator position was initially zero, then advanced after frames were supplied and processing continued.
- Use a finite number of `process_frame` awaits and a process timeout. Do not await `finished` for an intentionally continuing generator. Capture raw Godot output and process exit for attribution.
- Negative control: assign the same valid generated stream but **never call `play()`**; after the same bounded frame wait assert `not is_playing()` and position remains zero (or within a deliberately broad near-zero tolerance). Fail the probe if control unexpectedly plays. This is a no-play control, not a muted-output control.

## Pitfalls / qualifications

- Headless / Dummy audio still advances Godot's playback bookkeeping; it is not acoustic evidence. Do not call it audible playback.
- `AudioStreamPlayer.get_playback_position()` can be quantized/buffered and timing-sensitive. In this local probe, WAV position was already about `0.0058` immediately after `play()` and did not change across eight rapid frames; the generator began at `0.0` and later advanced. Avoid requiring a particular nonzero delta for WAV under an unspecified scheduler; generator with explicit frame supply was the stronger progress signal.
- Generator playback can exist while its buffer is empty; push frames before treating position movement as a meaningful positive. Bound both pushed frames and wait frames; don't use unbounded fill loops.
- Don't assume every `AudioStreamGeneratorPlayback` call or exact timing is identical across audio drivers/platforms. Keep thresholds coarse, record Godot version/driver, and check positive and negative on the same path.
- WAV PCM byte layout must match selected sample format/rate/channel count; malformed or too-short data can end before observation. Finite WAV may finish naturally, making `is_playing()` false if the wait is too long.

## Documentation

- [AudioStreamPlayer (Godot 4.7)](https://docs.godotengine.org/en/4.7/classes/class_audiostreamplayer.html): `play()`, `is_playing()`, `get_playback_position()`, `get_stream_playback()`.
- [AudioStreamWAV (Godot 4.7)](https://docs.godotengine.org/en/4.7/classes/class_audiostreamwav.html): runtime PCM `data`, `format`, `mix_rate`, and `stereo` properties.
- [AudioStreamGenerator (Godot 4.7)](https://docs.godotengine.org/en/4.7/classes/class_audiostreamgenerator.html): `mix_rate`, `buffer_length`; procedural stream.
- [AudioStreamGeneratorPlayback (Godot 4.7)](https://docs.godotengine.org/en/4.7/classes/class_audiostreamgeneratorplayback.html): available-frame / frame-push interface.
