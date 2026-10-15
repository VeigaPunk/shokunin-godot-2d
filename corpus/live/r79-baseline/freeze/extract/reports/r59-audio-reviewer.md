# Round 59 audio reviewer — read-only regression risks

## Scope and method

Read `.shokunin/game-dev-2d/LOG.md`, `corpus/fixtures/audio_playback.gd`, `project.godot`, and `run_battery.py`; did not edit tracked files or launch Godot. Re-executed the current production `classify_process` and `classify_audio_process` definitions extracted from the runner AST against the two retained Godot 4.7.2 `audio_playback` outputs. Results are in `corpus/live/r59-audio-reviewer/classifier-review.json`.

## Findings

- Existing positive audio fixture is a `SceneTree` script that generates an in-memory WAV, adds an `AudioStreamPlayer` to `root`, awaits a frame, starts playback, then checks `is_playing()` and position advance after 12 frames. It never sets `player.bus`, and the in-tree project has no declared audio bus configuration; this covers default routing only, not explicit non-Master routing.
- Preserve the existing baseline as an unchanged `audio_playback`/`audio_no_play` pair. Existing positive cleanup (`stop`, clear stream, free player, then bounded frames) is important: retained historical positive output includes both a clean PASS and a separate PASS-shaped output with `WARNING: 2 ObjectDB instances were leaked at exit`. `classify_audio_process` correctly classifies the latter as false and clean one as true. Avoid weakening/replacing that filter when adding route cases.
- The audio-specific classifier is used only when `name == "audio_playback"`; other cases use `classify_process`, which rejects unexpected `ERROR:` diagnostics, parse errors, and script errors but does not reject arbitrary `WARNING:` lines. If the new case uses another name, it will not inherit the ObjectDB leak guard unless the runner explicitly dispatches it to the audio classifier. Keep any exception tightly scoped to audio.
- The warning filter is targeted to the known ObjectDB-leak warning. AST-extracted probes confirm the exact known warning and its verbose suffix reject; unrelated/malformed warning text does not. Do not broaden the work to generic warning policy.
- For a missing bus, do not assume Godot emits an error or that playback stops: the existing classifier can accept exit 0 plus the expected signature even if the engine logs a non-ERROR warning or silently falls back. A meaningful negative must assert route semantics (for example, the requested route is not reported as resolved/accepted) and prove the paired positive reached its configured non-Master route. Process exit/signature alone is insufficient.
- Keep expected negative diagnostics exact and case-scoped. The global `classify_process` only excludes errors outside supplied `allowed_errors`; a broad allowed prefix could mask an unrelated engine error. Parse/script errors remain unconditionally disqualifying.
- The runner copies fixture project files into each run scratch and serializes cases. New bus declarations/fixtures must be staged only in scratch during runs; avoid modifying global engine audio settings. The seven existing opt-in flags are independent of fixture rows, and Round 59 must retain exact prior 87 `(case, script, flags, expected/actual exit, signature, verdict, error)` classifications.

## Boundary

No claim about audible/rendered output, mixer fidelity, production sound, exported audio, or platform behavior follows from headless playback-position and route-property checks. No audio engine process was run in this read-only review.
