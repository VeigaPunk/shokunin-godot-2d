# Round 17 export-path forensic scout (read-only)

## Scope and source evidence

Read the Round 17 mission/LOG entry, `r16-export-adverse.json`, `r16-parent-retry.json`, `r16-clamp-verifier.json`, the r16 executor/verifier reports, `corpus/fixtures/run_battery.py`, `export_presets.cfg`, and `project.godot`. No fixture, runner, or project configuration was edited. The only repository write is this report; all live reproduction was in `/tmp/r17-export-scout`.

Godot in all three captured r16 records is `godot` = Godot 4.7.2.stable.arch_linux.ed1daf0bf. The adverse run's recorded runner command (r16 executor report) was:

```text
python3 .shokunin/game-dev-2d/corpus/fixtures/run_battery.py --godot godot --probe-failing --runs .shokunin/game-dev-2d/corpus/live/runs
```

Parent retry and independent verifier instead supplied explicit `/tmp/...` `--runs` roots; verifier's exact command appears in `reports/r16-clamp-verifier.md`. The runner constructs each export as:

```text
godot --headless --path <scratch project> --export-debug "Linux/X11" <scratch>/out/fixture.x86_64
```

The export subprocess inherits the runner's current working directory (no `cwd=` override); `--path` and output are the scratch project's paths. The adverse JSON records its scratch path as a relative path `.shokunin/game-dev-2d/corpus/live/runs/20261012T184136853021Z/scratch`; parent and verifier records use absolute `/tmp/.../scratch` paths. The initial executor command was issued at the repository root per the relative script/run paths in its report. Exact wall times and process cwd were not persisted in the JSON records, so they cannot be recovered from those files. Runner's export timeout is 60 seconds; it does not record per-case timings.

## Comparison and scratch configuration

- Adverse `20261012T184136853021Z`: `export_readiness` exit 1, 0-byte/missing artifact. Godot completed `first_scan_filesystem` and `update_scripts_classes`, then emitted the nested-project warning followed by `ERROR: Prepare Template: The given export path doesn't exist.` and `ERROR: Project export for preset "Linux/X11" failed.` The runner had created `scratch/out` and asserted it empty before launching Godot; captured `export_artifact` says no products and artifacts deleted. The subsequent missing-preset test correctly emitted `ERROR: Invalid export preset name: Missing preset.`
- Parent retry `20261012T184247849282Z`: export exit 0, 73,703,800-byte executable (plus `.pck` and `.sh`); completed `savepack`. Same nested-project warning, no export-path error. Export products were deleted by runner.
- Independent verifier `20261012T184507298936Z`: likewise export exit 0 and 73,703,800-byte executable, same warning, no path error; the export-launch opt-in also passed. Export products deleted.

The seed preset is identical in these scratch copies: `export_path=""` (the runner supplies an explicit CLI output path), preset `Linux/X11`, x86_64. Each scratch project has top-level `project.godot`, `export_presets.cfg`, and `out/`; it also contains `controls/project.godot`. Godot warns `Detected another project.godot at res://controls. The folder will be ignored.` This warning occurs on both failures/passes and is not itself evidence of causation. No preset output-path difference is recorded. The nested `controls` project collision is a real layout warning, but its significance for the export-path error is unproven.

The r16 evidence is asynchronous in time and supports an intermittent observed outcome: one failure, then two fresh successes. It does **not** establish a race, filesystem timing issue, relative-path defect, nested-project cause, cache issue, or any other root cause. The distinction between relative adverse path and absolute passing paths is confounded with separate runs/roots; no controlled paired test of that single variable exists. The target directory existed in the adverse run per runner control flow, but no filesystem trace/timestamp proves its existence at the exact failing operation.

## Bounded real-Godot reproduction/control in isolated copies

Copied the seed fixtures to three separate `/tmp/r17-export-scout/copyN` projects, excluding runner and generated `.godot`/`out`, created a fresh empty `out/` in each, and ran Godot's real headless Linux/X11 export directly. All three commands used an absolute `--path` and absolute output path; they were started in parallel in distinct project copies. Each exited 0, emitted `[ DONE ] savepack`, and produced a 73,703,800-byte executable. Timings reported by Bash were 1.607s, 1.721s, and 1.752s. Each produced only the same nested-project `controls` warning, with no `ERROR` lines.

Then deleted the first copy's generated output artifacts, leaving its output directory empty, and reran the same export as a warm-cache repeat. It exited 0 in 1.567s, again emitted `[ DONE ] savepack` and the same warning only. This gives four successful fresh/warm real-Godot control attempts. It does not reproduce the r16 failure. These tests differ from the adverse invocation in using explicit absolute paths, direct rather than battery invocation, and `/tmp`; they are not a controlled isolation of why the prior run failed. I did not alter preset, destination, cwd, or project structure as an adverse manipulation because no supported causal hypothesis was established.

## Finding

**Unresolved / HOLD.** The error is real in the retained r16 adverse capture; three later battery/direct captures succeeded, and four bounded isolated repeats here succeeded. No falsifiable cause was isolated, so no repair or runner/config edit is supported. Keep the original failure visible and do not claim export-path reliability or that the scratch-path change fixed it. The existing missing-preset negative remains a distinct expected error; do not relax its classification or suppress export errors.
