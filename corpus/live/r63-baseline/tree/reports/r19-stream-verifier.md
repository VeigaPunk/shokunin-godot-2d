# r19-stream-verifier (non-author)

- role: r19-stream-verifier (named non-author verifier)
- round: game-dev-2d r19
- worktree: `/home/vgpnk/Projects/prymeagnt/game-dev-2d` (branch `craft/game-dev-2d-r1`)
- git HEAD at verify: `fa31bef6c02b3ffb1cd2f8b98d60f4375f8ad776`
- did_not_author: `stream_attribution_probe.gd`, `run_battery.py` edits, parent `classify_streams` tighten
- did_not: edit those files, commit, push, spawn subagents, edit MANIFEST.json

## 1. Godot version

Command: `godot --version`  
Observed exit: **0**  
Observed output: `4.7.2.stable.arch_linux.ed1daf0bf`  
Expect 4.7.2: **PASS**

## 2. AFTER command (round claim)

Command:
```
python .shokunin/game-dev-2d/corpus/fixtures/run_battery.py \
  --probe-failing --probe-unrelated-error --probe-export-launch \
  --probe-godot-error --probe-stream-attribution
```
Observed exit: **0**  
Duration: ~25.7s  
Meta battery verdict (`verdicts.json`): **PASS**  
Artifact dir: `.shokunin/game-dev-2d/corpus/live/runs/20261012T232144802702Z/`

### Result counts (`verdicts.json` → `results`, n=42)

| bucket | count | notes |
|--------|------:|-------|
| ordinary authored cases (CASES + export pair, non-probe names) | 33 | mechanic … export_preset_missing; all verdict PASS |
| mutants (`--probe-failing`) | 2 | `mutant_broken_scene_route`, `mutant_level_collision_removed` |
| opt-in probe rows (unrelated-error×4, export-launch, godot-error) | 6 | plus stream below |
| stream attribution probe row | 1 | `probe_stream_attribution` verdict **PASS** |
| **total results** | **42** | |

Exact case list (case → verdict): all 42 rows **PASS**.

Ordinary 33 (all PASS): mechanic, scene_signal, input_route, route_toggle, overlap, transition, causal, wrong_key, release, keyup, negative_route, negative_overlap, negative_transition, negative_signal, camera_follow, camera_no_follow, camera_limit, camera_far_bound, ui_signal_hud, ui_signal_disconnected, health_gauge, health_gauge_disconnected, level_collision, contact_runtime, contact_no_collision, animation_property, animation_stuck, tween_flash, tween_no_start, audio_playback, audio_no_play, export_readiness, export_preset_missing.

Mutants (2, PASS): mutant_broken_scene_route, mutant_level_collision_removed.

Opt-in (6, PASS): probe_unrelated_error_export_readiness, probe_unrelated_error_export_preset_missing, probe_unrelated_error_mutant_broken_scene_route, probe_unrelated_error_mutant_level_collision_removed, probe_export_launch, probe_godot_error.

Stream (1, PASS): probe_stream_attribution → artifact `.../stream-attribution-verdicts.json`.

Console lines `FAIL stream_reject` and `FAIL godot_error_unrelated` are **expected inner classification prints**, not battery meta failures.

### Stream pair evidence (`stream-attribution-verdicts.json`)

- mode: `real_godot_stream_attribution`
- same_script: **true**
- script_paths both: `res://stream_attribution_probe.gd`
- meta verdict: **PASS**
- stdout_signature: `STREAM_STDOUT: expected attribution marker`
- stderr_diagnostic: `STREAM_STDERR: unrelated attribution diagnostic`

| arm | actual_exit | inner_classification | stdout marker present | stderr |
|-----|------------:|---------------------:|-----------------------|--------|
| stream_accept | 0 | **true** | yes (`STREAM_STDOUT: expected attribution marker`) | empty (`raw_stderr` `""`, lines `[]`) |
| stream_reject | 0 | **false** | yes (same stdout marker) | exactly `STREAM_STDERR: unrelated attribution diagnostic` (one line) |

Flags: accept_emitted_stdout_marker true; reject_emitted_stdout_marker true; accept_lacks_stderr_diagnostic true; reject_emitted_stderr_diagnostic true; same_exit_zero true.

## 3. Fault injection (separate; not in battery count)

Command: `python .shokunin/game-dev-2d/corpus/fixtures/run_battery.py --fault-injection`  
Observed exit: **0**  
Artifact: `.shokunin/game-dev-2d/corpus/live/runs/20261012T232212537236Z/fault-verdicts.json`  
Meta verdict: **PASS**

| case | case-level verdict | notes |
|------|--------------------|-------|
| fault_hang | FAIL (expected) | TIMEOUT after 0.25s, exit null |
| fault_clean_expected_negative | PASS | exit 2, expected negative diagnostic only |
| fault_unrelated_error | FAIL (expected) | exit 2, extra `ERROR: unrelated engine failure` |

## 4. Hash stability

Recomputed SHA-256 for every file under `.shokunin/game-dev-2d/corpus/fixtures/` excluding `live` (43 files). Compared to BEFORE list in `.shokunin/game-dev-2d/reports/r19-hash-scout.md`.

- only_after / only_before: empty (same path set as scout’s 43, which already included `stream_attribution_probe.gd`)
- hash differences vs scout BEFORE:
  - `run_battery.py`: **changed** (allowed)  
    before `b92ffce246d03e6ffd1bae63ebb5f66992d80be0b6a0116cca3ceb506d20a713` (42384 bytes)  
    after  `eacaa2842d22cfe4a1d1663438bb254a1f2f90a460771c1cb15d6afcff0cedde` (42394 bytes)
  - `stream_attribution_probe.gd`: **unchanged vs scout BEFORE** (already present when scout hashed)
- every other fixture: **byte-identical to scout BEFORE**
- seeded fixtures other than runner: **0 mismatches** vs `git show HEAD:<path>` content hash

Hash check: **PASS** (only allowed runner change vs scout; probe already in BEFORE list and stable; no unexpected fixture drift).

## 5. classify_process / classify_streams

Command: `git diff -U0 HEAD -- .shokunin/game-dev-2d/corpus/fixtures/run_battery.py`  
- `classify_process` function body vs git HEAD: **unchanged? yes** (nested def extracted from HEAD and worktree; equal; 19 lines each). Diff adds only `classify_streams` + CLI flag + probe block; does not rewrite `classify_process`.
- New `classify_streams`: reads separate stdout/stderr; requires signature on stdout; rejects SCRIPT/Parse errors on either stream; for every non-empty stripped stderr line, returns False unless `line_allowed` (exact membership in `allowed_stderr`, or single-ERROR prefix form when allowed entry ends with `,`). Comment in body: any unexpected stderr line rejects (not prefix-only admit). **Confirms reject-any-non-allowed-stderr behavior. Did not edit.**

## 6. Refused claims

This verifier does **not** claim:
- crash classification
- process-tree timeout behavior beyond the isolated fault_hang TIMEOUT observation
- export reliability (r16 export-path failure remains an unresolved adverse observation even though this run’s `export_readiness` / export-launch probe rows passed)
- rendered output / visual correctness

Bounded claim aligned with stream artifact: one Godot 4.7.2 headless stream-attribution pair only.

## Deliverables written (only)

- `.shokunin/game-dev-2d/reports/r19-stream-verifier.md` (this file)
- `.shokunin/game-dev-2d/corpus/lessons/r19-stream-verifier.json` (copy of AFTER `verdicts.json`)
- `.shokunin/game-dev-2d/corpus/lessons/r19-fault-regression.json` (copy of `fault-verdicts.json`)

## Name

r19-stream-verifier (non-author)
