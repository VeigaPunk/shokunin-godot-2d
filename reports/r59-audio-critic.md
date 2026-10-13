# R59 audio critic — missing/invalid bus control

## Result: proposed control is falsified as a routing discriminator

Godot **4.7.2.stable.arch_linux.ed1daf0bf** silently falls back to `Master` when an `AudioStreamPlayer.bus` is assigned a nonexistent bus name. `AudioServer.get_bus_index("MissingBus")` returns `-1`, and reading `player.bus` after assignment returns `Master`. No warning or error was emitted. The player still reports `is_playing() == true` and advances playback position. Therefore, an invalid-bus control paired only with the current playback-state assertions would PASS just like the valid explicit non-Master route; it does not causally distinguish correct routing from fallback.

### Scratch reproduction

Own isolated project/script: `corpus/live/r59-audio-critic/project.godot`, `probe.gd`, and `setter.gd`. Ran:

```sh
godot --headless --path .shokunin/game-dev-2d/corpus/live/r59-audio-critic --script .shokunin/game-dev-2d/corpus/live/r59-audio-critic/probe.gd
godot --headless --path .shokunin/game-dev-2d/corpus/live/r59-audio-critic --script .shokunin/game-dev-2d/corpus/live/r59-audio-critic/setter.gd
```

The probe added a real `Effects` bus (index 1), used an in-memory generated WAV with each route, called `play()`, observed 12 process frames, and drained 120 frames after cleanup. Captured results:

- `Effects`: index `1`, getter `Effects`, playing `true`, position `0.00580498855561 → 0.09868481010199`.
- `MissingBus`: index `-1`, getter `Master`, playing `true`, position `0.00580498855561 → 0.09868481010199`.
- Empty bus assignment also reads as `Master`; in this run playback stayed true but the sampled position did not advance. This is not evidence that invalid nonempty names fail playback.
- No bus-related warning/error appeared in either run.

This falsifies an assertion that missing/invalid names themselves make playback fail. A *separate explicit resolution check* (`AudioServer.get_bus_index(player.bus) == expected_index`, plus asserting `player.bus == requested_bus`) would distinguish the invalid route from the valid route, but that would test route-name resolution/fallback behavior, not audibility or actual signal flow. This scratch did not measure mixed output or prove sound reaches a device. No tracked fixtures or runner were changed.
