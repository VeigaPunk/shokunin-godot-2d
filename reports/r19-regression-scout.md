# r19 regression scout (leaf)

Role: regression scout (read-only except this report).
Repo: `/home/vgpnk/Projects/prymeagnt/game-dev-2d` branch `craft/game-dev-2d-r1` HEAD fa31bef (as tasked).
Source read: `.shokunin/game-dev-2d/corpus/fixtures/run_battery.py` only.
Did not run the full battery. Did not edit fixtures, MANIFEST, or other paths.

## Command under audit

```text
python .shokunin/game-dev-2d/corpus/fixtures/run_battery.py \
  --probe-failing --probe-unrelated-error --probe-export-launch --probe-godot-error
```

(`--probe-audio-warning` and `--fault-injection` are **not** in this command, so their `results.append` paths are inactive.)

## Every `results.append` case name for that command

Order follows control flow in `run_battery.py`: always-on `CASES` loop, then opt-in blocks.

### A. Ordinary seeded battery (`CASES` → `execute` → `results.append(record)` with `"case": name`) — 33

1. `mechanic`
2. `scene_signal`
3. `input_route`
4. `route_toggle`
5. `overlap`
6. `transition`
7. `causal`
8. `wrong_key`
9. `release`
10. `keyup`
11. `negative_route`
12. `negative_overlap`
13. `negative_transition`
14. `negative_signal`
15. `camera_follow`
16. `camera_no_follow`
17. `camera_limit`
18. `camera_far_bound`
19. `ui_signal_hud`
20. `ui_signal_disconnected`
21. `health_gauge`
22. `health_gauge_disconnected`
23. `level_collision`
24. `contact_runtime`
25. `contact_no_collision`
26. `animation_property`
27. `animation_stuck`
28. `tween_flash`
29. `tween_no_start`
30. `audio_playback`
31. `audio_no_play`
32. `export_readiness`
33. `export_preset_missing`

While `--probe-unrelated-error` is set, the two export cases also each append a **meta** row inside `execute` (still part of this command):

34. `probe_unrelated_error_export_readiness` (after successful `export_readiness` export path)
35. `probe_unrelated_error_export_preset_missing` (after `export_preset_missing` path)

### B. `--probe-failing` mutants → `execute` → ordinary `results.append` for the mutant name

36. `mutant_broken_scene_route`
37. `mutant_level_collision_removed`

And, because `--probe-unrelated-error` is also set and `mutate=True`, each mutant appends a meta row:

38. `probe_unrelated_error_mutant_broken_scene_route`
39. `probe_unrelated_error_mutant_level_collision_removed`

### C. `--probe-export-launch` → single top-level append

40. `probe_export_launch`  
   (inner `launch_results.append` rows use labels inside `export-launch-verdicts.json`; they are **not** top-level `results.append` case names. Labels observed in source: positive/negative launch variants only as nested JSON.)

### D. `--probe-godot-error` → single top-level append

41. `probe_godot_error`  
   (inner `probe_results` labels `godot_error_expected_negative` and `godot_error_unrelated` live in the artifact / nested list, not as separate top-level `results` case strings.)

### Not produced by this command

- `probe_audio_warning_captured_r12` (needs `--probe-audio-warning`)
- fault-injection mode cases (`fault_hang`, `fault_clean_expected_negative`, `fault_unrelated_error`) (needs `--fault-injection`; early-return path)

**Total top-level `results` case names for the audited flag set: 41** (33 ordinary + 2 export unrelated metas + 2 mutants + 2 mutant unrelated metas + `probe_export_launch` + `probe_godot_error`).

## What must stay byte-identical in outcome if a new opt-in flag is added and **not** passed

Parent contract: new flag is `--probe-stream-attribution` (opt-in only). When that flag is **absent**, behavior of the audited command must not change.

Must remain **byte-identical in outcome** (same case names, same PASS/FAIL verdicts, same classifier decisions for those rows; nested probe artifacts for export-launch / godot-error likewise unchanged):

1. **All 33 ordinary `CASES` outcomes** — parent contract explicitly: “Prior 33 ordinary outcomes must stay unchanged.”
2. **All existing probe rows produced by the audited flags**, because the new flag must not alter them when not passed:
   - `probe_unrelated_error_export_readiness`
   - `probe_unrelated_error_export_preset_missing`
   - `mutant_broken_scene_route`
   - `mutant_level_collision_removed`
   - `probe_unrelated_error_mutant_broken_scene_route`
   - `probe_unrelated_error_mutant_level_collision_removed`
   - `probe_export_launch` (and its nested export-launch artifact content under the same inputs)
   - `probe_godot_error` (and its nested godot-error artifact content under the same inputs)
3. **Unrelated-error rejection strength** must not be weakened (export / mutant / process classifiers still fail on injected unrelated `ERROR:` lines).

When `--probe-stream-attribution` **is** passed, the only **allowed** delta is **additional** result row(s) for the stream-attribution meta probe (plus any new fixture file under the contract path). Existing case names above must still match prior outcomes.

## BEFORE / AFTER measurement commands (parent contract)

**BEFORE** (baseline without stream probe; matches this scout’s audited flag set):

```bash
python .shokunin/game-dev-2d/corpus/fixtures/run_battery.py \
  --probe-failing --probe-unrelated-error --probe-export-launch --probe-godot-error
```

**AFTER** (same flags **plus** the new opt-in):

```bash
python .shokunin/game-dev-2d/corpus/fixtures/run_battery.py \
  --probe-failing --probe-unrelated-error --probe-export-launch --probe-godot-error \
  --probe-stream-attribution
```

Compare: the 33 ordinary cases and all pre-existing probe case outcomes must be identical; AFTER may add stream-attribution meta coverage only.

## Notes for integrator (not executed here)

- `run_process` still concatenates stdout+stderr today; stream attribution is unprobed until the fixture + flag land.
- Scout refused: running full battery, editing any code, commits/pushes, MANIFEST/sibling books.

## Files written

- `.shokunin/game-dev-2d/reports/r19-regression-scout.md` (this file only)
