# Round 6 export — named non-author verifier

## Verdict: conditional / negative control needs repair

I independently ran the requested command from the repository root:

```text
python .shokunin/game-dev-2d/corpus/fixtures/run_battery.py --probe-failing
```

It exited 0 and printed `PASS battery`; its raw verdict is [`corpus/live/runs/20261012T164942179119Z/verdicts.json`](../corpus/live/runs/20261012T164942179119Z/verdicts.json). The raw JSON records 25/25 PASS, including the previously existing 23 cases and both additional scratch-only mutants. I checked the export case streams and outcome, not only the summary.

### Positive export

The runner's actual command is `godot --headless --path <scratch> --export-debug "Linux/X11" <scratch>/out/fixture.x86_64`. The raw positive record has Godot 4.7.2.stable.arch_linux.ed1daf0bf, exit 0, no timeout, no `ERROR:` or `SCRIPT ERROR:`, and a 73,703,800-byte executable SHA-256 `1a291d3d15e4180b60b0af96cf6458f11fe143636d76575ddf1e23d1a3f24f2e`; the executable was deleted by the runner. I independently repeated that exact command against the battery scratch copy and confirmed the same exit, byte count, and hash. I then removed the resulting `.x86_64`, `.pck`, and `.sh` export products from scratch. Its sole warning was `WARNING: Detected another project.godot at res://controls. The folder will be ignored.` There were no unrelated errors or timeout.

The nested-project warning is material: Godot skipped `res://controls` as another project root. The successful result proves only that this host's Godot 4.7.2 Linux/X11 preset/template path can package the selected scratch project inputs under that behavior. It does not prove every nested fixture was packaged, that an exported app launches or behaves correctly, production-project readiness, other platforms, or any publishing/asset rights.

### Negative export

The runner's `export_preset_missing` raw record has the expected exact diagnostic, `ERROR: Invalid export preset name: Missing preset.`, exit 1, and no executable at its expected `fixture.x86_64` path. I independently ran the missing-preset command on a fresh, separate scratch copy; it emitted that same diagnostic (plus the nested-project warning), exited 1, and created no files in the separately inspected output directory.

However, the battery's own negative scratch output directory contained `fixture.pck` (23,456 bytes) and `fixture.sh` (131 bytes), even though `fixture.x86_64` was absent. I removed those scratch outputs after inspection. The runner checks only that the expected executable path is absent, so its negative PASS is not evidence of “no output artifact.” This is a runner assertion gap / incomplete negative evidence; do not accept the stated negative no-output claim until the case checks the whole output directory or otherwise isolates these side effects. The clean independent negative replay did produce no output, but does not repair the battery's weaker assertion.

### Integrity and scope

SHA-256 before/after comparison of all 35 tracked paths under `corpus/fixtures` found no changes. No fixture or code was edited by this verifier; no output remains in either battery `out/` directory. Export output was generated only in ignored scratch and deleted; nothing was published. The positive evidence is valid for the narrow local export operation. Overall round acceptance should remain conditional on correcting and independently replaying the negative output check.
