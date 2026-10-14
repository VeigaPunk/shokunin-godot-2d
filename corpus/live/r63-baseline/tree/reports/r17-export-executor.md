# Round 17 export executor — HOLD

Date: 2026-10-12. Scope: export-path diagnosis; no runner edits.

## Decision

**HOLD / no causal fix admitted.** The r16 adverse export is genuine and preserved, but its cause is not established. Retrying successfully is not a fix. I left `corpus/fixtures/run_battery.py` unchanged. Do not claim improved export reliability.

## Evidence reviewed

- `corpus/lessons/r16-export-adverse.json`: executor battery at `.shokunin/game-dev-2d/corpus/live/runs/20261012T184136853021Z/scratch` had export exit 1, zero-byte/missing artifact, `ERROR: Prepare Template: The given export path doesn't exist.`, followed by project-export failure. Ordinary fixture results and invalid-preset control passed. The record says `out/fixture.x86_64` is the target; no artifact products were made.
- `corpus/lessons/r16-parent-retry.json`: distinct scratch at `/tmp/r16-parent-retry/20261012T184247849282Z/scratch` exported successfully (73,703,800-byte executable; products included `.x86_64`, `.pck`, `.sh`) and the missing-preset negative still returned exit 1 with `ERROR: Invalid export preset name: Missing preset.`
- `corpus/fixtures/export_presets.cfg` has `[preset.0]`, `name="Linux/X11"`, `platform="Linux/X11"`, and empty `export_path`. The runner passes the explicit output path as the final `--export-debug` argument and creates an empty `out/` first. This is not evidence that the preset names a missing path.

## Bounded reproductions

- Copied the seeded fixture tree to `/tmp/r17-export-path-repro` (excluding `.godot`/`out`), staged the same `controls/pickup.tscn` root copy, created empty `out/`, then ran real Godot 4.7.2 `--headless --path ... --export-debug 'Linux/X11' <absolute out path>`. It passed and created a 73,703,800-byte executable.
- Three additional fresh copies `/tmp/r17-repeat-1` through `-3`, each with no `.godot` or `out` cache and a fresh empty output directory, all passed the same real export; each executable was 73,703,800 bytes.
- In the first bounded copy, invoking `--export-debug 'Missing preset'` produced exit 1 and the genuine invalid-preset diagnostic. Thus the negative control remains meaningful; a retry/success does not mask it.
- Ran the unmodified runner with `--probe-failing --runs /tmp/r17-battery-runs`. All 33 ordinary records (31 base + 2 mutations) passed, including real export readiness and invalid-preset rejection. The battery exited 0. Its positive export produced the same-sized artifact before runner cleanup.

## Causal assessment / limits

The observed adverse raw output reports Godot's export-path/template preparation failure, but does not distinguish a transient engine/template condition, filesystem state, timing, or any path-specific cause. Existing output directories and the configured preset path are not shown to be missing. Clean fresh `/tmp` copies and the original project-nested r16 scratch both have successful controls; only one adverse sample exists. We did not reproduce the failure under either bounded path, and therefore cannot attribute it to parent-vs-`/tmp` path dependence or to a runner defect. No retry policy, preset mutation, wait, or error suppression is justified by these data.

No seeded fixtures changed. No runner logic changed. Constants changed: none. This report records a HOLD, not a reliability claim.
