# Round 25 simplifier review

Read the Round 25 declaration and standing mission brief, examined runner export path construction, and compared preserved r16/r24 failure records with the r16 retry and r20 verifier evidence. This was read-only: no Godot run or runner edit. No delegation.

## Recommendation: no fix on current evidence

The history does not isolate the `--runs` path form. `r16-export-adverse.json` is FAIL at relative scratch path `.shokunin/game-dev-2d/corpus/live/runs/20261012T184136853021Z/scratch`; its immediate `r16-parent-retry.json` PASS uses `/tmp/r16-parent-retry/20261012T184247849282Z/scratch`. The r24 adverse is another relative scratch path under `corpus/live/r24-bottom-executor/...` and fails. These are suggestive but not a controlled pair: run roots, timestamps, fixture revisions/content, caches, and other conditions differ. Recorded Godot identity is the same 4.7.2 build string. The r20 top verifier records successful export (73,703,800 bytes; SHA-256 `1a291d3d15e4180b60b0af96cf6458f11fe143636d76575ddf1e23d1a3f24f2e`), but is not a paired absolute/relative experiment. Earlier successful defaults likewise do not establish causation.

The runner passes `--runs` into `run_dir = args.runs / stamp`, then uses that scratch path for `--path` and constructs `out/fixture.x86_64` beneath it. The export failure says `Prepare Template: The given export path doesn't exist`, but the raw adverse records establish only zero products and exit 1; they do not show a malformed resolved path or establish that the CLI `--runs` spelling caused it. The output is consistent with multiple causes, including path resolution, export-template state/readiness, or transient environment/order effects. Do not infer a fix from the diagnostic text alone.

## Minimal correction gate

Keep `run_battery.py` unchanged unless a bounded, alternating paired real-Godot experiment holds constant executable/version, cwd, fixture tree and hashes, preset/config, destination structure, and export invocation, while recording both spelling and resolved paths, full commands/output, exit, artifact existence/size/hash, and timestamps—and produces at least one relative FAIL / absolute PASS contrast. A non-author must reproduce the contrast before any runner change. If met, first consider the smallest localized normalization of the runs root to an absolute path before building `run_dir`; preserve existing output/preset checks and fail-closed export classification. Do not retry a failure into a pass or weaken/remove export diagnostics. If relative and absolute behavior is alike, recommend no fix and classify path diagnosis unproven.

## Axis view

No calibration improvement is established by this review; coverage and depth are unchanged. This is not a production export-reliability claim. No engine/editor source, seeded control, or runner was changed; no export was run.
