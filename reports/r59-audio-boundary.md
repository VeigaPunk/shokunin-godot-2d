# Round 59 boundary probe — headless audio

## Scope

Tested one boundary only: whether headless Godot 4.7.2 can establish explicit non-Master bus routing and whether an invalid bus name causally rejects instead of falling back. This is an isolated scratch probe, not a fixture or battery change.

## Method and observed output

Godot reported `4.7.2.stable.arch_linux.ed1daf0bf`. Scratch is `.shokunin/game-dev-2d/corpus/live/r59-audio-boundary/probe/` (`project.godot`, `probe.gd`). The script creates a generated 1-second WAV, adds a bus named `ProbeNonMaster`, and sequentially plays the same stream from players with `bus` set to `ProbeNonMaster` and nonexistent `ProbeMissing`. After 12 process frames it prints the player bus and playback state/position.

Command: `godot --headless --path . --script probe.gd --quit-after 60` from the scratch project. Exit 0; observed:

```text
RESULT bus=ProbeNonMaster effective_bus=ProbeNonMaster playing=true before=0.00580498855561 after=0.09868481010199
RESULT bus=ProbeMissing effective_bus=Master playing=true before=0.00580498855561 after=0.09868481010199
WARNING: 2 ObjectDB instances were leaked at exit ...
```

An additional `--verbose` invocation produced the same results and the same resource-leak warning. There was no invalid-route error or warning. The non-Master case resolves and advances. Crucially, nonexistent route is silently mapped to `Master` and also plays/advances. Thus this control does **not** causally reject and cannot distinguish intended routing from fallback by playback advancement alone. It falsifies the proposed missing/invalid-bus rejection expectation for this API/runtime; use a different control/assertion (for example, verify resolved `get_bus()` equals the requested name) if the fixture needs to test route correctness.

## Boundary: no audible/mixing claim

This process has no audible listener or human hearing, and the probe does not capture or compare output samples from the audio mixer. Player state and playback position are logical playback observations; they do not establish that sound was audible, that the configured bus mix/effects/gain are correct, or that speakers/device output work. No rendered-output, mixer-fidelity, production-sound, platform, or rights claim follows. The ObjectDB leak warning is also present, so do not treat this scratch script as a clean resource-lifecycle fixture.
