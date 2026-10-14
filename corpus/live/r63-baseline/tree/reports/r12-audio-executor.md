# Round 12 audio executor report

Implemented only new `corpus/fixtures/audio_playback.gd` and the two `audio_*` cases plus their case-scoped expected-error allowance in `corpus/fixtures/run_battery.py`.

- `audio_playback`: generates a one-second mono 16-bit 22.05 kHz WAV in memory, adds an `AudioStreamPlayer` under the SceneTree root, records playback position immediately after `play()`, then observes for 12 process frames. Assertion requires in-tree membership, `is_playing()`, and position advance >1 ms. Observed `0.00580498855561 -> 0.09868481010199`; generated audio buffer is 44,100 bytes.
- `audio_no_play`: `--no-play` skips only `play()` and evaluates the exact same assertion. It exits 2 on the intended diagnostic, and the narrow classifier allowance requires the assertion's own `ERROR:` prefix. It does not allow parse/setup failures.
- Cleanup follow-up: stopped/freed player, detached stream, nulled stream reference, cleared sample array after copying its byte count, and awaited four bounded process frames. Direct raw positive replay still reports `WARNING: 2 ObjectDB instances were leaked at exit`; negative replay has no warning. The cleanup attempt is not treated as resolving or suppressing the warning.
- Final raw battery replay after cleanup attempt: `python .shokunin/game-dev-2d/corpus/fixtures/run_battery.py --godot godot --runs /tmp/r12-audio-cleanup-final` exited 0, 27/27 PASS, including both audio cases. Raw verdicts: `/tmp/r12-audio-cleanup-final/20261012T175858561195Z/verdicts.json`. The positive warning is explicitly visible in that JSON.
- Earlier `--probe-failing` run was 29/29 PASS at `/tmp/r12-audio-final/20261012T175659991280Z/verdicts.json`, but it preceded the cleanup experiment and contained the positive leak warning. It is not claimed warning-clean or a clean final replay.

Headless playback-position evidence does not establish audible sound or mix quality. No seeded fixture mutation, delegation, commit, push, or engine/editor source edits.
