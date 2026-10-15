# Round 20 baseline scout — HEAD evidence

Scope: read-only baseline; no fixture/runner edits. All baseline content was extracted from immutable Git `HEAD` (`3d19377a604df726377e53b8007b284a3607875d`), not the concurrently modified working tree. `LOG.md` has an uncommitted round-20 declaration at the time of inspection; it was not used as fixture evidence.

## Commands and results

- `git rev-parse HEAD` → `3d19377a604df726377e53b8007b284a3607875d`.
- `godot --version` → `4.7.2.stable.arch_linux.ed1daf0bf`.
- Parsed `CASES` from `git show HEAD:.shokunin/game-dev-2d/corpus/fixtures/run_battery.py` → **33** base cases. Includes `camera_limit` PASS and `camera_far_bound` negative (along with `camera_follow` and `camera_no_follow`).
- Ran the HEAD fixture snapshot in `/tmp/r20-baseline-head.eu0wuQ`, command: `python run_battery.py --probe-failing --runs /tmp/r20-baseline-head.eu0wuQ/runs` from its extracted `.shokunin/game-dev-2d/corpus/fixtures` directory. Exit **0**. Battery printed PASS for all 33 base cases and both scratch mutants (`mutant_broken_scene_route`, `mutant_level_collision_removed`); raw verdict file: `/tmp/r20-baseline-head.eu0wuQ/runs/20261013T005257093733Z/verdicts.json`. The output included `EXPORT PASS` (73,703,800 bytes) and expected missing-preset diagnostic; this is one replay, not evidence of export reliability.
- HEAD SHA-256: runner `eacaa2842d22cfe4a1d1663438bb254a1f2f90a460771c1cb15d6afcff0cedde`; `camera_limit.gd` `f305622fa6305842d8507b9a7ec9a584459d4ddf969c8d1345754ccfb6f0c3ec`.
- Hashed all **43** tracked fixture-tree files (HEAD; excluding `.import` files). Full manifest follows.

## Fixture-tree SHA-256 (HEAD)

| SHA-256 | Path |
|---|---|
| `6760ee1a44bcc1a1dc2cfb5d91e5ecd2ad9be56e15cd3a38704655b77a7e691d` | `.shokunin/game-dev-2d/corpus/fixtures/animation_property.gd` |
| `be6e74f41db0f96202a4b274e4707bd6b42242197b20b1c9e8b796d87e3ae418` | `.shokunin/game-dev-2d/corpus/fixtures/area_pickup.tscn` |
| `41293c477c14b42943b4c6663fc566b6467e24a56125b8b714e24353433fb512` | `.shokunin/game-dev-2d/corpus/fixtures/audio_playback.gd` |
| `945a491d5db13ebebe9253f3bdad1d9e96382612a05d2d60760d3acda758f46f` | `.shokunin/game-dev-2d/corpus/fixtures/baseline_actor.gd` |
| `04a7403e1a93979dded0a7e9188a2a6fd1b944ebf2dd59c323789b5d8d7c2d90` | `.shokunin/game-dev-2d/corpus/fixtures/camera_follow.gd` |
| `f305622fa6305842d8507b9a7ec9a584459d4ddf969c8d1345754ccfb6f0c3ec` | `.shokunin/game-dev-2d/corpus/fixtures/camera_limit.gd` |
| `f21c888db6b21e9eaa1c417fb9a94db59646cde78804fc4fe86b23ee411eb640` | `.shokunin/game-dev-2d/corpus/fixtures/causal_actor.gd` |
| `034618720d6f755515e6d862459ac2cc637aac492562b5b94c27828751a983d7` | `.shokunin/game-dev-2d/corpus/fixtures/causal_chain.gd` |
| `bcaf8e11f358620b3cb4395de147a41166e9b196ad24a1d68248a39dd12041f2` | `.shokunin/game-dev-2d/corpus/fixtures/causal_pickup.gd` |
| `c6979325ae49983bb4cbd70a2c870be5f81c69e7094d04040f64bfb4a3e6925d` | `.shokunin/game-dev-2d/corpus/fixtures/contact_probe.gd` |
| `be6e74f41db0f96202a4b274e4707bd6b42242197b20b1c9e8b796d87e3ae418` | `.shokunin/game-dev-2d/corpus/fixtures/controls/area_pickup.tscn` |
| `cfd48819de5b63ec2ab1a1df922fe33d7452808e4ddbdf1afd49df6dc85bdac4` | `.shokunin/game-dev-2d/corpus/fixtures/controls/input_route.gd` |
| `8801a55f917030c2d323135a2db400e9ac5473b73ddb62ea520ccd0672f61371` | `.shokunin/game-dev-2d/corpus/fixtures/controls/input_route_negative.gd` |
| `5da3ddf557366ce0f4ea51898ca96f46efbfb78563a41d40a70615c2548f15b3` | `.shokunin/game-dev-2d/corpus/fixtures/controls/input_route_receiver.gd` |
| `4a5d993ebdf3de13184aa0e7f148e17e7d8dc05ddcb9039d5a717e806adf642e` | `.shokunin/game-dev-2d/corpus/fixtures/controls/input_route_toggle.gd` |
| `edbdffe2d1f22b99d0348e982d7ece33d63d725d59fa35e6e322ac52c1bc8390` | `.shokunin/game-dev-2d/corpus/fixtures/controls/mechanic_test.gd` |
| `c8a9c076dead4a2808e7d4e7cda5277b1f9168449a66c8ddc0554f22092519fd` | `.shokunin/game-dev-2d/corpus/fixtures/controls/negative_test.gd` |
| `c33f7d0ef112469e6c754f1713dd6068b2832bffffa5dd8c676dcca421a7af4d` | `.shokunin/game-dev-2d/corpus/fixtures/controls/overlap_negative.gd` |
| `6dd75053c1357629f64d23d605564391c010fcd58e49a23cef8cfe9f2eb69b04` | `.shokunin/game-dev-2d/corpus/fixtures/controls/overlap_probe.gd` |
| `74cc07b9bc07a2f76685b5a04f8e41160b5b90d18f793554dee003e95283604d` | `.shokunin/game-dev-2d/corpus/fixtures/controls/pickup.gd` |
| `f9b2de750e9fe08c7c2b50b5890a6992700c061da9ed5d8911c049a92eccbdf6` | `.shokunin/game-dev-2d/corpus/fixtures/controls/pickup.tscn` |
| `8de8b3af9cc737edc3e5969b76bf049720266537ec366e03aa42702aa15406e9` | `.shokunin/game-dev-2d/corpus/fixtures/controls/project.godot` |
| `63ea91ac4edb855802b925e47ff0bd67a57dacd49881e215a24be667e4a9dd8f` | `.shokunin/game-dev-2d/corpus/fixtures/controls/scene_a.tscn` |
| `ca4c30efa4ca5c336a7737011cae44e3ad50b839bc689421a622a2655a616c35` | `.shokunin/game-dev-2d/corpus/fixtures/controls/scene_b.tscn` |
| `fa72c254a5f635ef8aa70e7f07432f29f31ca3473490da2144a18bda273140ac` | `.shokunin/game-dev-2d/corpus/fixtures/controls/scene_marker.gd` |
| `e1c881bc397b000970fcebc36b0483bad6694f2fc8b9750a6c06ef550754680f` | `.shokunin/game-dev-2d/corpus/fixtures/controls/scene_transition_negative.gd` |
| `93f781f27ec84b4bcbd0cbd81c0ec7bb79d92c70c76d2d51901bcc47a54c2118` | `.shokunin/game-dev-2d/corpus/fixtures/controls/scene_transition_probe.gd` |
| `eb113be690098bac16ce8bc08e9efc0ff353e99cc5bfeb1d8bca5fee8cbbad9a` | `.shokunin/game-dev-2d/corpus/fixtures/controls/test_scene_signal.gd` |
| `27b106e73e905e47f8580667a04c55d8e6e6d7cddb08c6a5813eb8ec1d01c018` | `.shokunin/game-dev-2d/corpus/fixtures/controls/test_scene_signal_negative.gd` |
| `0b321c1c866e5d61e5e4fe8842fe8552f8d6cac3c9b7659f285f2c15b59ba694` | `.shokunin/game-dev-2d/corpus/fixtures/export_presets.cfg` |
| `b89e2ef78f23dacb32766073c6a7719f01e969ceaaa9f8f634575e30ae8d8956` | `.shokunin/game-dev-2d/corpus/fixtures/godot_error_probe.gd` |
| `195d754beee358b1ac8d3f3e94b28f131079b9475bbfcf47def1200bd98ddf0f` | `.shokunin/game-dev-2d/corpus/fixtures/health_gauge.gd` |
| `81a76c3f3ceef1da14e79c185b8a02d1a4c57d89a811f6726372dcac410db5cd` | `.shokunin/game-dev-2d/corpus/fixtures/level_collision/level_probe.gd` |
| `1ce6c933f38f341a4fcee8e411bad184e67d038ec2a28ce11f77e771898398c8` | `.shokunin/game-dev-2d/corpus/fixtures/level_collision/level_scene.tscn` |
| `74cc07b9bc07a2f76685b5a04f8e41160b5b90d18f793554dee003e95283604d` | `.shokunin/game-dev-2d/corpus/fixtures/pickup.gd` |
| `8de8b3af9cc737edc3e5969b76bf049720266537ec366e03aa42702aa15406e9` | `.shokunin/game-dev-2d/corpus/fixtures/project.godot` |
| `eacaa2842d22cfe4a1d1663438bb254a1f2f90a460771c1cb15d6afcff0cedde` | `.shokunin/game-dev-2d/corpus/fixtures/run_battery.py` |
| `63ea91ac4edb855802b925e47ff0bd67a57dacd49881e215a24be667e4a9dd8f` | `.shokunin/game-dev-2d/corpus/fixtures/scene_a.tscn` |
| `ca4c30efa4ca5c336a7737011cae44e3ad50b839bc689421a622a2655a616c35` | `.shokunin/game-dev-2d/corpus/fixtures/scene_b.tscn` |
| `fa72c254a5f635ef8aa70e7f07432f29f31ca3473490da2144a18bda273140ac` | `.shokunin/game-dev-2d/corpus/fixtures/scene_marker.gd` |
| `97143ad367a66e5f625208947c4d479a48d1aa7ce519d0e2de13b4751d288ebe` | `.shokunin/game-dev-2d/corpus/fixtures/stream_attribution_probe.gd` |
| `e37bd03dd8801ba2379a1275eed3b9cab0b2767cf310ebb8c92a31892ebbdd81` | `.shokunin/game-dev-2d/corpus/fixtures/tween_flash.gd` |
| `3d0ccaede72670d59b63bab3c7cd2a49db18b1cbcfc1f9ec4d487ee93fb4804d` | `.shokunin/game-dev-2d/corpus/fixtures/ui_signal_hud.gd` |
