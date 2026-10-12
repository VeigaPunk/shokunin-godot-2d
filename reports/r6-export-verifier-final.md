# Round 6 export — final named non-author verifier

## Verdict: PASS for the declared narrow readiness probe

I independently ran the corrected battery from the repository root:

    python .shokunin/game-dev-2d/corpus/fixtures/run_battery.py --probe-failing

It exited 0. The unedited raw verdict JSON is [`.shokunin/game-dev-2d/corpus/live/runs/20261012T165341021057Z/verdicts.json`](../corpus/live/runs/20261012T165341021057Z/verdicts.json). It records exactly 25 cases, all PASS; the output contains a final `PASS battery`. The prior 23 cases remain present and PASS. Neither export invocation timed out; the runner records no case error/timeout.

### Positive Linux/X11 export

The positive raw record reports actual Godot 4.7.2 Linux/X11 `--export-debug` exit 0, a nonempty executable of 73,703,800 bytes, SHA-256 `1a291d3d15e4180b60b0af96cf6458f11fe143636d76575ddf1e23d1a3f24f2e`, and all products inventoried: `fixture.pck`, `fixture.sh`, and `fixture.x86_64`. The runner records deletion of all inventoried products. I inspected the battery scratch `out/` after completion: it exists and is empty. The positive log has no `ERROR:` or `SCRIPT ERROR:`. It does contain this warning:

    WARNING: Detected another project.godot at res://controls. The folder will be ignored.

### Negative missing-preset case

The negative test uses a separate `missing-preset-scratch` tree. The raw record shows exact diagnostic `ERROR: Invalid export preset name: Missing preset.`, process exit 1, and PASS. The runner copies with `out` excluded, then asserts output dir empty before invocation and checks the entire dir remains empty after. I inspected that separate negative `out/`: it exists and is empty. There are no leftover sidecars (the earlier verifier's issue is resolved).

### Integrity, warning, and limits

This verifier made no fixture edits. The fixture tree contains 35 tracked files; the observed worktree changes in that area are the corrected runner and the new export preset, not verifier changes. The execution's scratch copy isolates generated files; positive products were deleted and both output dirs are empty. No publishing or asset-rights claim is made.

The nested `controls/project.godot` warning means Godot ignores that nested project while scanning the export project. Therefore this proves only that this host's Godot 4.7.2 Linux/X11 preset/template can produce and clean up an export for the scanned scratch project under that behavior. It does not establish that nested controls were included, that the exported program launches or functions, production project readiness, other platform readiness, distributability, publishing permission, or asset rights.
