# Round 12 — independent audio re-verification

**Decision: RELEASE (narrowly scoped coverage admission).** The repaired fixture now passes the requested functional and warning checks in the combined regression battery and in two additional direct positive replays. The previously blocking ObjectDB leak warning did not recur. This supports only headless Godot playback-state advancement for the generated in-memory WAV after a bounded 120-frame cleanup drain; it does not prove audible output or production audio integration.

## Independent replay

I read the Round 12 mission and prior verifier HOLD and cleanup report, then ran:

```text
python .shokunin/game-dev-2d/corpus/fixtures/run_battery.py --probe-failing --probe-unrelated-error --probe-export-launch --probe-godot-error
```

Exit **0**, `PASS battery`, **35/35**. Every earlier feature/mutant case remained PASS, including export launch and the Godot diagnostic probe. As expected, within the diagnostic probe the clean expected-negative case classifies true and the unrelated-error case classifies false; the probe itself passes.

The battery's audio records are in `corpus/live/runs/20261012T180821838450Z/verdicts.json`:

- `audio_playback`: exit 0; `in_tree=true`, `playing=true`; position advanced from `0.00580498855561` to `0.09868481010199` (about 0.09288 s); 44,100 generated sample bytes. No `WARNING` or `ObjectDB` text appears in captured output.
- `audio_no_play`: exit 2 at the same expected `AUDIO ASSERTION FAILED: expected in-tree player playback to advance` assertion; `in_tree=true`, `playing=false`, positions both `0.0`. This is the required negative-control rejection, not a battery failure; no `WARNING` or `ObjectDB` text appears.

I then directly replayed the positive command twice against that run's scratch project:

```text
godot --headless --path <run scratch> --script res://audio_playback.gd
```

Both exited 0 and printed the same positive state/advanced-position evidence. For both replays, separately captured stdout and stderr contained **zero `WARNING` lines and zero `ObjectDB` mentions** (stderr was empty). Thus the original leak warning did not recur across either direct positive repetition. The fixture's bounded post-cleanup drain is 120 process frames; this evidence does not establish why that drain resolves the warning seen with the earlier four-frame cleanup.

Fault replay:

```text
python .shokunin/game-dev-2d/corpus/fixtures/run_battery.py --fault-injection
```

Exit **0**, `PASS fault injection`, record `corpus/live/runs/20261012T180848789062Z/fault-verdicts.json`. The injected hang was correctly classified as TIMEOUT/inner FAIL, the clean expected negative as PASS, and the unrelated-error case as inner FAIL; those are the expected fault outcomes.

## Immutability and limits

SHA-256 checked all **38 tracked** paths under `corpus/fixtures` immediately before and after the replays. No tracked path changed. Ordered manifest digest was identical before/after: `c2a4eedb49b091bcac5eb6d0be5284e12eb2176c197d6564cb4bbcc09cedf261`.

The positive result proves Godot's headless player state and playback-position bookkeeping advanced for this generated stream under the local Godot 4.7.2 runtime. It does **not** establish audible sound, mixer/output-device behavior, sound quality, asset rights, gameplay integration, or that the 120-frame wait is the only or general remedy for retained audio references. No fixture/runner mutation, delegation, commit, or push was performed. This report is the only repository write from this re-verification.
