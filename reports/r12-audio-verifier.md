# Round 12 — named non-author audio verifier (LEAF)

**Verdict: HOLD — do not admit the audio coverage move yet.** The functional assertion and no-play control work, and the requested combined battery passes 35/35, but the positive run emits a reproducible Godot ObjectDB leak warning while the no-play control does not. Cleanup changes and an independent minimal WAV reproduction did not remove it. This prevents treating the positive fixture as clean; it is not evidence that the leak is merely a harmless headless backend warning.

## Scope / non-author status

I acted as the named verifier only. I did not delegate, commit, push, edit fixtures/runner, alter engine/editor files, or write outside this report. Inputs read: `LOG.md` Round 12 mission plus `reports/r12-audio-scout.md`, `r12-audio-executor.md`, and `r12-audio-critic.md`. Critic correctly said its then-current review was provisional; I independently inspected and executed the final workspace artifacts. Godot reported `4.7.2.stable.arch_linux.ed1daf0bf`.

## Independent battery replays

Command:

```text
python .shokunin/game-dev-2d/corpus/fixtures/run_battery.py --probe-failing --probe-unrelated-error --probe-export-launch --probe-godot-error
```

Exit **0**, overall `PASS battery`, **35/35**. This comprises the 29 original feature/mutant cases (including audio positive + negative, replacing zero audio cases), four calibration cases (`--probe-unrelated-error`), one export-launch probe, and one real-Godot diagnostic probe. Machine record: `.shokunin/game-dev-2d/corpus/live/runs/20261012T180117210908Z/verdicts.json`. The audio records show:

- `audio_playback`: exit 0; `in_tree=true`, `playing=true`, `position_before=0.00580498855561`, `position_after=0.09868481010199` (delta ≈0.09288 s), generated 44,100 bytes. This is actual player state/position, not an inferred print marker.
- `audio_no_play`: exit 2 at the **same** `AUDIO ASSERTION FAILED: expected in-tree player playback to advance` check; raw assertion values `in_tree=true playing=false position_before=0.0 position_after=0.0`. It differs only by omitting `play()` and completes without a leak warning.

Raw positive diagnostic lines, as captured in the run's JSON:

```text
WARNING: 2 ObjectDB instances were leaked at exit (run with `--verbose` for details).
   at: cleanup (core/object/object.cpp:2536)
```

The generic runner classifies this case PASS by the expected marker/exit and does not fail on that WARNING. Therefore 35/35 is functional battery success, not warning-clean audio admission. `audio_no_play` raw output contains the intended assertion ERROR and backtrace, no WARNING.

Fault replay:

```text
python .shokunin/game-dev-2d/corpus/fixtures/run_battery.py --fault-injection
```

Exit 0, meta `PASS fault injection` (`corpus/live/runs/20261012T180150607032Z/fault-verdicts.json`). Expected injected results: actual hang killed at 0.251 s / TIMEOUT after 0.25 s (inner FAIL); clean expected negative exit 2 accepted (inner PASS); same expected signature plus unrelated engine ERROR rejected (inner FAIL). The intentional inner FAILs are expected fault-test outcomes, not harness failures.

## Leak isolation (scratch-only; no repo edits)

I wrote scratch scripts only under `/tmp/r12-audio-isolation` and ran the same installed Godot headless binary. Results:

| Scratch case | Result |
|---|---|
| SceneTree baseline, no player/stream | exit 0; no leak warning |
| `AudioStreamGenerator` player, play/stop, clear stream, free player, wait four frames | exit 0; no leak warning |
| same minimal AudioStreamGenerator script with a bounded 2048-frame buffer push and real position advancement | exit 0; `playing=true`, position `0.09287979453802`; **one** ObjectDB leaked warning |
| Round 12's AudioStreamWAV pattern, play, 12 frames, stop, set player stream null, free player, null stream, clear samples, wait four frames | exit 0; **two** leaked warning |
| same WAV pattern, no `play()` | exit 0; no leak warning |
| WAV cleanup followed by 120 additional process frames | exit 0; no leak warning (instead of the warning) |
| WAV cleanup with `AudioServer.lock()` / `unlock()` around stop | exit 0; still two leaked warning |

Running WAV reproduction with `--verbose` identifies the leaked objects exactly:

```text
Leaked instance: AudioStreamWAV:... - Reference count: 1
Leaked instance: AudioStreamPlaybackWAV:... - Reference count: 1
Hint: Leaked instances typically happen when nodes are removed from the scene tree (with `remove_child()`) but not freed (with `free()` or `queue_free()`).
```

Thus this is audio-path-associated in the minimal reproduction, and with generator playback there is also a warning when advancing a stream. But I **cannot** conclude that this is only a known/benign headless backend artifact: the baseline is clean, the no-play case is clean, the generator-without-buffer case is clean, and verbose identifies retained stream/playback objects. Extra waiting suppresses the WAV warning in the standalone repro, but does not establish cleanup within the fixture's bounded lifetime or explain the retained refs; the executor's four-frame cleanup attempt and explicit AudioServer locking did not fix it. I found no justified fixture-only remedy that can be certified without changing scope. No backend lock/workaround or warning filter was applied. Warning remains admission-blocking pending diagnosis/remedy or an explicit policy decision supported by evidence.

## Fixture/runner immutability

Hashed all **38 tracked** paths from `git ls-files .shokunin/game-dev-2d/corpus/fixtures` immediately before and after the verification commands, using SHA-256. **All 38 path digests are unchanged**; changed paths: none. The aggregate SHA-256 of the ordered `path + per-file digest` manifest is `6b57f18b7d38b39e99fb022b2f90527edbc5054bea5a54f19f62ded6caa69a46` before and after.

- `.shokunin/game-dev-2d/corpus/fixtures/animation_property.gd` — `6760ee1a44bcc1a1dc2cfb5d91e5ecd2ad9be56e15cd3a38704655b77a7e691d` (before = after)
- `.shokunin/game-dev-2d/corpus/fixtures/area_pickup.tscn` — `be6e74f41db0f96202a4b274e4707bd6b42242197b20b1c9e8b796d87e3ae418` (before = after)
- `.shokunin/game-dev-2d/corpus/fixtures/baseline_actor.gd` — `945a491d5db13ebebe9253f3bdad1d9e96382612a05d2d60760d3acda758f46f` (before = after)
- `.shokunin/game-dev-2d/corpus/fixtures/camera_follow.gd` — `04a7403e1a93979dded0a7e9188a2a6fd1b944ebf2dd59c323789b5d8d7c2d90` (before = after)
- `.shokunin/game-dev-2d/corpus/fixtures/causal_actor.gd` — `f21c888db6b21e9eaa1c417fb9a94db59646cde78804fc4fe86b23ee411eb640` (before = after)
- `.shokunin/game-dev-2d/corpus/fixtures/causal_chain.gd` — `034618720d6f755515e6d862459ac2cc637aac492562b5b94c27828751a983d7` (before = after)
- `.shokunin/game-dev-2d/corpus/fixtures/causal_pickup.gd` — `bcaf8e11f358620b3cb4395de147a41166e9b196ad24a1d68248a39dd12041f2` (before = after)
- `.shokunin/game-dev-2d/corpus/fixtures/contact_probe.gd` — `c6979325ae49983bb4cbd70a2c870be5f81c69e7094d04040f64bfb4a3e6925d` (before = after)
- `.shokunin/game-dev-2d/corpus/fixtures/controls/area_pickup.tscn` — `be6e74f41db0f96202a4b274e4707bd6b42242197b20b1c9e8b796d87e3ae418` (before = after)
- `.shokunin/game-dev-2d/corpus/fixtures/controls/input_route.gd` — `cfd48819de5b63ec2ab1a1df922fe33d7452808e4ddbdf1afd49df6dc85bdac4` (before = after)
- `.shokunin/game-dev-2d/corpus/fixtures/controls/input_route_negative.gd` — `8801a55f917030c2d323135a2db400e9ac5473b73ddb62ea520ccd0672f61371` (before = after)
- `.shokunin/game-dev-2d/corpus/fixtures/controls/input_route_receiver.gd` — `5da3ddf557366ce0f4ea51898ca96f46efbfb78563a41d40a70615c2548f15b3` (before = after)
- `.shokunin/game-dev-2d/corpus/fixtures/controls/input_route_toggle.gd` — `4a5d993ebdf3de13184aa0e7f148e17e7d8dc05ddcb9039d5a717e806adf642e` (before = after)
- `.shokunin/game-dev-2d/corpus/fixtures/controls/mechanic_test.gd` — `edbdffe2d1f22b99d0348e982d7ece33d63d725d59fa35e6e322ac52c1bc8390` (before = after)
- `.shokunin/game-dev-2d/corpus/fixtures/controls/negative_test.gd` — `c8a9c076dead4a2808e7d4e7cda5277b1f9168449a66c8ddc0554f22092519fd` (before = after)
- `.shokunin/game-dev-2d/corpus/fixtures/controls/overlap_negative.gd` — `c33f7d0ef112469e6c754f1713dd6068b2832bffffa5dd8c676dcca421a7af4d` (before = after)
- `.shokunin/game-dev-2d/corpus/fixtures/controls/overlap_probe.gd` — `6dd75053c1357629f64d23d605564391c010fcd58e49a23cef8cfe9f2eb69b04` (before = after)
- `.shokunin/game-dev-2d/corpus/fixtures/controls/pickup.gd` — `74cc07b9bc07a2f76685b5a04f8e41160b5b90d18f793554dee003e95283604d` (before = after)
- `.shokunin/game-dev-2d/corpus/fixtures/controls/pickup.tscn` — `f9b2de750e9fe08c7c2b50b5890a6992700c061da9ed5d8911c049a92eccbdf6` (before = after)
- `.shokunin/game-dev-2d/corpus/fixtures/controls/project.godot` — `8de8b3af9cc737edc3e5969b76bf049720266537ec366e03aa42702aa15406e9` (before = after)
- `.shokunin/game-dev-2d/corpus/fixtures/controls/scene_a.tscn` — `63ea91ac4edb855802b925e47ff0bd67a57dacd49881e215a24be667e4a9dd8f` (before = after)
- `.shokunin/game-dev-2d/corpus/fixtures/controls/scene_b.tscn` — `ca4c30efa4ca5c336a7737011cae44e3ad50b839bc689421a622a2655a616c35` (before = after)
- `.shokunin/game-dev-2d/corpus/fixtures/controls/scene_marker.gd` — `fa72c254a5f635ef8aa70e7f07432f29f31ca3473490da2144a18bda273140ac` (before = after)
- `.shokunin/game-dev-2d/corpus/fixtures/controls/scene_transition_negative.gd` — `e1c881bc397b000970fcebc36b0483bad6694f2fc8b9750a6c06ef550754680f` (before = after)
- `.shokunin/game-dev-2d/corpus/fixtures/controls/scene_transition_probe.gd` — `93f781f27ec84b4bcbd0cbd81c0ec7bb79d92c70c76d2d51901bcc47a54c2118` (before = after)
- `.shokunin/game-dev-2d/corpus/fixtures/controls/test_scene_signal.gd` — `eb113be690098bac16ce8bc08e9efc0ff353e99cc5bfeb1d8bca5fee8cbbad9a` (before = after)
- `.shokunin/game-dev-2d/corpus/fixtures/controls/test_scene_signal_negative.gd` — `27b106e73e905e47f8580667a04c55d8e6e6d7cddb08c6a5813eb8ec1d01c018` (before = after)
- `.shokunin/game-dev-2d/corpus/fixtures/export_presets.cfg` — `0b321c1c866e5d61e5e4fe8842fe8552f8d6cac3c9b7659f285f2c15b59ba694` (before = after)
- `.shokunin/game-dev-2d/corpus/fixtures/godot_error_probe.gd` — `b89e2ef78f23dacb32766073c6a7719f01e969ceaaa9f8f634575e30ae8d8956` (before = after)
- `.shokunin/game-dev-2d/corpus/fixtures/level_collision/level_probe.gd` — `81a76c3f3ceef1da14e79c185b8a02d1a4c57d89a811f6726372dcac410db5cd` (before = after)
- `.shokunin/game-dev-2d/corpus/fixtures/level_collision/level_scene.tscn` — `1ce6c933f38f341a4fcee8e411bad184e67d038ec2a28ce11f77e771898398c8` (before = after)
- `.shokunin/game-dev-2d/corpus/fixtures/pickup.gd` — `74cc07b9bc07a2f76685b5a04f8e41160b5b90d18f793554dee003e95283604d` (before = after)
- `.shokunin/game-dev-2d/corpus/fixtures/project.godot` — `8de8b3af9cc737edc3e5969b76bf049720266537ec366e03aa42702aa15406e9` (before = after)
- `.shokunin/game-dev-2d/corpus/fixtures/run_battery.py` — `8ee95facdb203fd56dfeb499695d2f124ac7052b2adc512a24a0c2f6f9eb185e` (before = after)
- `.shokunin/game-dev-2d/corpus/fixtures/scene_a.tscn` — `63ea91ac4edb855802b925e47ff0bd67a57dacd49881e215a24be667e4a9dd8f` (before = after)
- `.shokunin/game-dev-2d/corpus/fixtures/scene_b.tscn` — `ca4c30efa4ca5c336a7737011cae44e3ad50b839bc689421a622a2655a616c35` (before = after)
- `.shokunin/game-dev-2d/corpus/fixtures/scene_marker.gd` — `fa72c254a5f635ef8aa70e7f07432f29f31ca3473490da2144a18bda273140ac` (before = after)
- `.shokunin/game-dev-2d/corpus/fixtures/ui_signal_hud.gd` — `3d0ccaede72670d59b63bab3c7cd2a49db18b1cbcfc1f9ec4d487ee93fb4804d` (before = after)

## Decision boundary

The narrow functional claim is supported for Godot playback bookkeeping under this local headless configuration; it says nothing about audible output. However, because the positive produces the warning while the paired no-play path does not, and scratch controls did not establish the cause as harmless backend noise, verdict is **HOLD**, not coverage improved/admitted. Keep the 35-case output as evidence, preserve the warning verbatim, and do not claim a resolved leak based on the extra-wait scratch observation.
