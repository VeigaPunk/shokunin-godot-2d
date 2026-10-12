# r19 hash scout (BEFORE executor)

- role: hash scout (L2 leaf)
- round: game-dev-2d r19
- branch: craft/game-dev-2d-r1
- git HEAD: fa31bef6c02b3ffb1cd2f8b98d60f4375f8ad776 (short fa31bef)
- timestamp_utc: 2026-10-12T23:18:38.584241+00:00
- godot_path_note: parent measured /usr/bin/godot 4.7.2 (not re-probed here)
- fixtures_root: `.shokunin/game-dev-2d/corpus/fixtures/`
- excluded: any path segment `live` under fixtures (none present)
- file_count: 43
- rehash: second pass matched first; no drift while hashing
- fixtures edited by this leaf: none (read-only except this report)

## Command used

Python `hashlib.sha256` over every file under fixtures (exclude `live`), sorted by path:

```python
from pathlib import Path
import hashlib
fix = Path('.shokunin/game-dev-2d/corpus/fixtures')
files = sorted(p for p in fix.rglob('*') if p.is_file() and 'live' not in p.relative_to(fix).parts)
for p in files:
    print(hashlib.sha256(p.read_bytes()).hexdigest(), p.stat().st_size, p.as_posix())
```

Equivalent intent to `sha256sum` on the same file set.

## BEFORE snapshot (SHA-256, size_bytes, path)

- `6760ee1a44bcc1a1dc2cfb5d91e5ecd2ad9be56e15cd3a38704655b77a7e691d`  1267  `.shokunin/game-dev-2d/corpus/fixtures/animation_property.gd`
- `be6e74f41db0f96202a4b274e4707bd6b42242197b20b1c9e8b796d87e3ae418`  378  `.shokunin/game-dev-2d/corpus/fixtures/area_pickup.tscn`
- `41293c477c14b42943b4c6663fc566b6467e24a56125b8b714e24353433fb512`  1823  `.shokunin/game-dev-2d/corpus/fixtures/audio_playback.gd`
- `945a491d5db13ebebe9253f3bdad1d9e96382612a05d2d60760d3acda758f46f`  453  `.shokunin/game-dev-2d/corpus/fixtures/baseline_actor.gd`
- `04a7403e1a93979dded0a7e9188a2a6fd1b944ebf2dd59c323789b5d8d7c2d90`  1170  `.shokunin/game-dev-2d/corpus/fixtures/camera_follow.gd`
- `f305622fa6305842d8507b9a7ec9a584459d4ddf969c8d1345754ccfb6f0c3ec`  2349  `.shokunin/game-dev-2d/corpus/fixtures/camera_limit.gd`
- `f21c888db6b21e9eaa1c417fb9a94db59646cde78804fc4fe86b23ee411eb640`  679  `.shokunin/game-dev-2d/corpus/fixtures/causal_actor.gd`
- `034618720d6f755515e6d862459ac2cc637aac492562b5b94c27828751a983d7`  8292  `.shokunin/game-dev-2d/corpus/fixtures/causal_chain.gd`
- `bcaf8e11f358620b3cb4395de147a41166e9b196ad24a1d68248a39dd12041f2`  233  `.shokunin/game-dev-2d/corpus/fixtures/causal_pickup.gd`
- `c6979325ae49983bb4cbd70a2c870be5f81c69e7094d04040f64bfb4a3e6925d`  3708  `.shokunin/game-dev-2d/corpus/fixtures/contact_probe.gd`
- `be6e74f41db0f96202a4b274e4707bd6b42242197b20b1c9e8b796d87e3ae418`  378  `.shokunin/game-dev-2d/corpus/fixtures/controls/area_pickup.tscn`
- `cfd48819de5b63ec2ab1a1df922fe33d7452808e4ddbdf1afd49df6dc85bdac4`  1435  `.shokunin/game-dev-2d/corpus/fixtures/controls/input_route.gd`
- `8801a55f917030c2d323135a2db400e9ac5473b73ddb62ea520ccd0672f61371`  1606  `.shokunin/game-dev-2d/corpus/fixtures/controls/input_route_negative.gd`
- `5da3ddf557366ce0f4ea51898ca96f46efbfb78563a41d40a70615c2548f15b3`  116  `.shokunin/game-dev-2d/corpus/fixtures/controls/input_route_receiver.gd`
- `4a5d993ebdf3de13184aa0e7f148e17e7d8dc05ddcb9039d5a717e806adf642e`  2473  `.shokunin/game-dev-2d/corpus/fixtures/controls/input_route_toggle.gd`
- `edbdffe2d1f22b99d0348e982d7ece33d63d725d59fa35e6e322ac52c1bc8390`  507  `.shokunin/game-dev-2d/corpus/fixtures/controls/mechanic_test.gd`
- `c8a9c076dead4a2808e7d4e7cda5277b1f9168449a66c8ddc0554f22092519fd`  251  `.shokunin/game-dev-2d/corpus/fixtures/controls/negative_test.gd`
- `c33f7d0ef112469e6c754f1713dd6068b2832bffffa5dd8c676dcca421a7af4d`  855  `.shokunin/game-dev-2d/corpus/fixtures/controls/overlap_negative.gd`
- `6dd75053c1357629f64d23d605564391c010fcd58e49a23cef8cfe9f2eb69b04`  1332  `.shokunin/game-dev-2d/corpus/fixtures/controls/overlap_probe.gd`
- `74cc07b9bc07a2f76685b5a04f8e41160b5b90d18f793554dee003e95283604d`  435  `.shokunin/game-dev-2d/corpus/fixtures/controls/pickup.gd`
- `f9b2de750e9fe08c7c2b50b5890a6992700c061da9ed5d8911c049a92eccbdf6`  155  `.shokunin/game-dev-2d/corpus/fixtures/controls/pickup.tscn`
- `8de8b3af9cc737edc3e5969b76bf049720266537ec366e03aa42702aa15406e9`  89  `.shokunin/game-dev-2d/corpus/fixtures/controls/project.godot`
- `63ea91ac4edb855802b925e47ff0bd67a57dacd49881e215a24be667e4a9dd8f`  172  `.shokunin/game-dev-2d/corpus/fixtures/controls/scene_a.tscn`
- `ca4c30efa4ca5c336a7737011cae44e3ad50b839bc689421a622a2655a616c35`  172  `.shokunin/game-dev-2d/corpus/fixtures/controls/scene_b.tscn`
- `fa72c254a5f635ef8aa70e7f07432f29f31ca3473490da2144a18bda273140ac`  38  `.shokunin/game-dev-2d/corpus/fixtures/controls/scene_marker.gd`
- `e1c881bc397b000970fcebc36b0483bad6694f2fc8b9750a6c06ef550754680f`  1247  `.shokunin/game-dev-2d/corpus/fixtures/controls/scene_transition_negative.gd`
- `93f781f27ec84b4bcbd0cbd81c0ec7bb79d92c70c76d2d51901bcc47a54c2118`  1583  `.shokunin/game-dev-2d/corpus/fixtures/controls/scene_transition_probe.gd`
- `eb113be690098bac16ce8bc08e9efc0ff353e99cc5bfeb1d8bca5fee8cbbad9a`  999  `.shokunin/game-dev-2d/corpus/fixtures/controls/test_scene_signal.gd`
- `27b106e73e905e47f8580667a04c55d8e6e6d7cddb08c6a5813eb8ec1d01c018`  835  `.shokunin/game-dev-2d/corpus/fixtures/controls/test_scene_signal_negative.gd`
- `0b321c1c866e5d61e5e4fe8842fe8552f8d6cac3c9b7659f285f2c15b59ba694`  265  `.shokunin/game-dev-2d/corpus/fixtures/export_presets.cfg`
- `b89e2ef78f23dacb32766073c6a7719f01e969ceaaa9f8f634575e30ae8d8956`  339  `.shokunin/game-dev-2d/corpus/fixtures/godot_error_probe.gd`
- `195d754beee358b1ac8d3f3e94b28f131079b9475bbfcf47def1200bd98ddf0f`  2062  `.shokunin/game-dev-2d/corpus/fixtures/health_gauge.gd`
- `81a76c3f3ceef1da14e79c185b8a02d1a4c57d89a811f6726372dcac410db5cd`  1262  `.shokunin/game-dev-2d/corpus/fixtures/level_collision/level_probe.gd`
- `1ce6c933f38f341a4fcee8e411bad184e67d038ec2a28ce11f77e771898398c8`  5975  `.shokunin/game-dev-2d/corpus/fixtures/level_collision/level_scene.tscn`
- `74cc07b9bc07a2f76685b5a04f8e41160b5b90d18f793554dee003e95283604d`  435  `.shokunin/game-dev-2d/corpus/fixtures/pickup.gd`
- `8de8b3af9cc737edc3e5969b76bf049720266537ec366e03aa42702aa15406e9`  89  `.shokunin/game-dev-2d/corpus/fixtures/project.godot`
- `b92ffce246d03e6ffd1bae63ebb5f66992d80be0b6a0116cca3ceb506d20a713`  42384  `.shokunin/game-dev-2d/corpus/fixtures/run_battery.py`
- `63ea91ac4edb855802b925e47ff0bd67a57dacd49881e215a24be667e4a9dd8f`  172  `.shokunin/game-dev-2d/corpus/fixtures/scene_a.tscn`
- `ca4c30efa4ca5c336a7737011cae44e3ad50b839bc689421a622a2655a616c35`  172  `.shokunin/game-dev-2d/corpus/fixtures/scene_b.tscn`
- `fa72c254a5f635ef8aa70e7f07432f29f31ca3473490da2144a18bda273140ac`  38  `.shokunin/game-dev-2d/corpus/fixtures/scene_marker.gd`
- `97143ad367a66e5f625208947c4d479a48d1aa7ce519d0e2de13b4751d288ebe`  330  `.shokunin/game-dev-2d/corpus/fixtures/stream_attribution_probe.gd`
- `e37bd03dd8801ba2379a1275eed3b9cab0b2767cf310ebb8c92a31892ebbdd81`  1560  `.shokunin/game-dev-2d/corpus/fixtures/tween_flash.gd`
- `3d0ccaede72670d59b63bab3c7cd2a49db18b1cbcfc1f9ec4d487ee93fb4804d`  1082  `.shokunin/game-dev-2d/corpus/fixtures/ui_signal_hud.gd`

## Battery case counts (from `run_battery.py` CASES)

- `CASES` tuple length (authored ordinary cases): **33**
- authored case names (33): mechanic, scene_signal, input_route, route_toggle, overlap, transition, causal, wrong_key, release, keyup, negative_route, negative_overlap, negative_transition, negative_signal, camera_follow, camera_no_follow, camera_limit, camera_far_bound, ui_signal_hud, ui_signal_disconnected, health_gauge, health_gauge_disconnected, level_collision, contact_runtime, contact_no_collision, animation_property, animation_stuck, tween_flash, tween_no_start, audio_playback, audio_no_play, export_readiness, export_preset_missing

### Mutation (opt-in `--probe-failing`)

When `--probe-failing` is set, runner adds **2** mutation executes (not in `CASES`):
- `mutant_broken_scene_route`
- `mutant_level_collision_removed`

### Opt-in probe flags currently defined (`store_true`)

1. `--probe-failing`
2. `--fault-injection` (isolated fault mode; separate from seeded battery results list)
3. `--probe-unrelated-error`
4. `--probe-export-launch`
5. `--probe-godot-error`
6. `--probe-audio-warning`

No `--probe-stream-attribution` yet (pre-executor).

### Ordinary-record count matching r18 lesson framing

Parent/r18 lesson framing: **33 authored + 2 mutation + 7 opt-in** when all current probe flags are on.

Grounding at HEAD fa31bef:
- authored ordinary = `len(CASES)` = **33**
- mutation records from `--probe-failing` = **2**
- additional opt-in result rows when battery probe flags fire together (from code structure + prior full-battery artifacts): typically
  - `probe_audio_warning_captured_r12` (1)
  - `probe_unrelated_error_export_readiness` (1)
  - `probe_unrelated_error_export_preset_missing` (1)
  - `probe_unrelated_error_mutant_broken_scene_route` (1)
  - `probe_unrelated_error_mutant_level_collision_removed` (1)
  - `probe_export_launch` (1)
  - `probe_godot_error` (1)
  → **7** opt-in probe result rows (distinct from the 2 mutant case rows themselves)

So full battery with all listed probe flags (and probe-failing mutants) yields ordinary 33 + mutation 2 + opt-in 7 = **42** result rows in the main battery payload shape (fault-injection remains a separate mode).

## Refused / out of scope for this leaf

- Did not edit fixtures, `run_battery.py`, MANIFEST, sibling books, or any path outside this report.
- Did not commit, push, spawn subagents, or judge the round.
- Did not create `stream_attribution_probe.gd` (executor job).

## Leaf deliverable

- this file only: `.shokunin/game-dev-2d/reports/r19-hash-scout.md`
