# Round 10 launch executor

## Scope and result
Implemented `--probe-export-launch` in `.shokunin/game-dev-2d/corpus/fixtures/run_battery.py`. It makes isolated positive/control projects, writes a startup scene/script and `run/main_scene` setting to each scratch project, exports Linux/X11 builds, then runs each executable with `--headless` from its `out/` directory. That working directory contains only the exported `.x86_64`, `.pck`, and `.sh` products—no `project.godot`, source scene, or source script—so the event must come from packaged export content. Each process has a 5-second timeout. Seeded fixture settings/scenes and engine/editor files were not changed. No delegation, commit, push, or tracked executable.

Both variants have the same startup scene and project main-scene setting. The negative scratch script omits only the print event. The assertion requires exit 0, no process error, no script/parse/unexpected `ERROR:` diagnostics, and exactly one stdout line equal to `EXPORT_LAUNCH_READY scene=fixture`. Thus the clean negative must fail the same assertion, not merely fail to launch.

## Probe output and evidence
Latest corrected combined replay: `python .shokunin/game-dev-2d/corpus/fixtures/run_battery.py --probe-failing --probe-unrelated-error --probe-export-launch` → exit **0**, **32/32 PASS**. Raw battery and launch JSON: `.shokunin/game-dev-2d/corpus/live/runs/20261012T173644453195Z/{verdicts.json,export-launch-verdicts.json}`.

Both exports used `godot --headless --path <variant-scratch> --export-debug 'Linux/X11' <variant-scratch>/out/fixture-launch.x86_64`; each export exit **0**, observed `[ DONE ]` and `savepack`, executable nonempty (~73.7 MB), products `fixture-launch.pck`, `fixture-launch.sh`, and `fixture-launch.x86_64`.

- Positive: direct launch `<out>/fixture-launch.x86_64 --headless`, cwd `<positive-scratch>/out`, exit **0**, no timeout/error, exact event line observed once; assertion **true**. PCK: 28,020 bytes, SHA-256 `8598c8cd5cfac41c19ce4b7b2855a4b6ad48b6cabf0072acbdc9a9679a99e1ce`.
- Negative: direct launch `<out>/fixture-launch.x86_64 --headless`, cwd `<negative-scratch>/out`, exit **0**, no timeout/error or `ERROR:`/script/parse error, no event line; same assertion **false**. Export exit **0** and nonempty executable. PCK: 27,956 bytes, SHA-256 `75673af40e28d272c165050f13d1843f591f7c70a280b7d82f620600d231f069`.
- Executable template hashes match as expected: SHA-256 `1a291d3d15e4180b60b0af96cf6458f11fe143636d76575ddf1e23d1a3f24f2e`. PCK sizes and hashes differ across variants. All three products were deleted after each launch; both `products_after_cleanup` arrays are empty.

Preserved regressions: final baseline-only run `python .../run_battery.py` exited **0**, **25/25 PASS**; `--probe-unrelated-error` exited **0**, **27/27 PASS**; `--fault-injection` exited **0**, meta PASS. The latest combined replay also includes mutants and unrelated-error controls while exercising launch behavior (32/32).

An initial draft run failed with a timeout-output bytes/string TypeError and created incomplete disposable scratch; that scratch was removed. The final control preserves the same startup scene and main-scene setting, removing only the event-print line. A prior code draft accidentally described the control as missing its main scene; that claim was corrected. The actual final control exports and launches successfully without emitting the event.

## Limits
This proves only this host's Godot 4.7.2 Linux/X11 synthetic export startup, packaged event, and clean control behavior. It is not a production-game launch, visual check, cross-host/platform verification, or published build.
