# Round 59 audio scout

## Scope and method
Read `.shokunin/game-dev-2d/corpus/fixtures/audio_playback.gd`, `project.godot`, and the battery case table. No tracked fixture or runner was changed. Created isolated project and probe under `corpus/live/r59-audio-scout/`; executed with `/usr/bin/godot --headless` (Godot 4.7.2.stable.arch_linux.ed1daf0bf).

## Existing fixture
`audio_playback.gd` synthesizes one second of mono 22050-Hz PCM, adds an `AudioStreamPlayer` to root, plays unless `--no-play`, observes `is_playing()` and playback position over 12 process frames, stops/frees, and asserts in-tree + playing + position advanced. It does not assign or inspect `player.bus`, nor interrogate `AudioServer`; default is Master. Runner currently has `audio_playback` (exit 0) and `audio_no_play` (expected exit 2), with no bus coverage.

## API / scratch observation
Godot 4.7.2 `AudioServer` exposes the relevant runtime bus surface: `bus_count`, `add_bus(at_position=-1)`, `set_bus_name(bus_idx,name)`, `get_bus_name(bus_idx)`, `get_bus_index(bus_name)`. `AudioStreamPlayer.bus` is a bus-name string. A simple ephemeral bus can be added and named `FixtureSfx`; it is index 1, distinct from Master index 0. My scratch creates it at runtime (avoids project audio-bus asset edits), assigns it before playback, and checks the player's bus name and `AudioServer.get_bus_index(player.bus)` alongside playback advancement.

Command: `godot --headless --path .shokunin/game-dev-2d/corpus/live/r59-audio-scout --script probe.gd`.

Observed output:
```
BUS_SETUP count=2 idx=1 name=FixtureSfx lookup=1 master=0
POSITIVE bus=FixtureSfx idx=1
POSITIVE playing=true before=0.00580498855561 after=0.09868481010199
INVALID bus=Master lookup=0 playing=true pos=0.09868481010199
```

Crucial control behavior: assigning `DefinitelyMissingBus` to `AudioStreamPlayer.bus` silently normalizes the property to `Master` (index 0), rather than preserving the invalid name or rejecting playback. Player remains `is_playing() == true`. Thus `playing` alone is not a causal bus-routing assertion. A useful negative case must assert mismatch/rejection of the requested bus, and report actual normalization (do not expect process failure or stopped playback). Positive must assert requested named non-Master bus exists and is the player's resolved bus, plus position advances. A shared assertion/route invariant can require `AudioServer.get_bus_index(player.bus) == requested non-Master index`; the invalid-name case should detect `player.bus != requested invalid name` and/or resolved index 0. Separate fixture invocations make dynamic bus setup deterministic.

## Boundary / recommendation
Headless evidence covers Godot's bus-name resolution and player transport cursor, not audible output, signal/mix level, actual acoustic routing, mixer fidelity, or production sound. Scratch had a shutdown ObjectDB-leak warning because it omitted complete teardown; this does not alter the observed API behavior and should be cleaned up in any final fixture. Recommendation: feasible and narrowly testable as a bus identity/resolution assertion paired with existing cursor advancement, but phrase claim as resolved bus assignment, not measured audio reaching that bus. I made no tracked edits and did not run the full battery.
