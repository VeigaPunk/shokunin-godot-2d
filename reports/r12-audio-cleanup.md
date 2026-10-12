# Round 12 — bounded audio cleanup repair

Edited only `corpus/fixtures/audio_playback.gd`.

- Before: after stopping/freeing the player, detaching/nulling the stream, and clearing samples, the fixture waited 4 `process_frame`s.
- After: that same post-stop/free drain waits 120 `process_frame`s. The existing 12-frame playback observation, playback-position assertion, and identical no-play assertion are unchanged. No warning filtering or runner changes.

Validation: `python .shokunin/game-dev-2d/corpus/fixtures/run_battery.py --probe-failing --runs .shokunin/game-dev-2d/corpus/live/runs/20261012T181000000000Z` exited 0: battery PASS, 29/29. Both audio cases are recorded in:

`.shokunin/game-dev-2d/corpus/live/runs/20261012T181000000000Z/20261012T180542323188Z/verdicts.json`

Raw audio results in that file:

- `audio_playback`: exit 0; `position_before=0.00580498855561`, `position_after=0.09868481010199`; no `WARNING` line (including no ObjectDB leak warning).
- `audio_no_play`: exit 2 at the same expected `AUDIO ASSERTION FAILED` check; `in_tree=true`, `playing=false`, both positions 0.0; no `WARNING` line.

This confirms the bounded drain suppressed the reported leak warning in both direct battery cases; it does not establish audible output or broader audio behavior.
