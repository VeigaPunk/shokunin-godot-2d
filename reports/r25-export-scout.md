# Round 25 export-path scout

## Scope and finding
Read-only comparison of the r16/r20/r24 evidence plus bounded scratch Godot exports. No runner edit. Godot `/usr/bin/godot` (4.7.2.stable.arch_linux.ed1daf0bf), fixture source `.shokunin/game-dev-2d/corpus/fixtures`, same preset (`Linux/X11`), export target name `out/fixture.x86_64`, clean copied project and empty output directory for every attempt. The result strongly supports a path-form cause: when both `--path` project root and export target are supplied as cwd-relative paths, all three relative trials fail with exit 1 and `ERROR: Prepare Template: The given export path doesn't exist.`; paired absolute trials succeed with the same 73,703,800-byte artifact and SHA-256 `1a291d3d15e4180b60b0af96cf6458f11fe143636d76575ddf1e23d1a3f24f2e`. An extra mixed trial (relative `--path`, absolute target) succeeds. This narrows the failure to the relative export target, rather than relative project root alone. It is controlled evidence for Godot CLI path interpretation, not yet a changed battery-runner reproduction nor a production-export reliability claim.

## Historical comparison
- `corpus/lessons/r16-export-adverse.json`: explicit `scratch` is relative (`.shokunin/.../runs/20261012T184136853021Z/scratch`); `export_readiness` FAIL, exit 1, zero bytes, exact missing export-path diagnostic. The separate missing-preset control PASSes with its expected diagnostic.
- r20 LOG entry records an explicit relative `--runs .shokunin/game-dev-2d/corpus/live/runs` run that stopped at export with `StopIteration` looking for `savepack`; this is an exception, not a recorded export-readiness verdict. The recorded default-path `corpus/lessons/r20-top-verifier.json` passes export: exit 0, 73,703,800 bytes.
- `corpus/lessons/r24-export-adverse.json`: explicit relative scratch under `.shokunin/...`; export readiness FAIL, exit 1, zero bytes, same diagnostic. `corpus/lessons/r24-bottom-verifier.json` default absolute scratch passes, exit 0, 73,703,800 bytes.
- Historical runs were not matched/alternated, so alone they were confounded. They are consistent with the scratch controlled result. Neither successful default export nor a matching executable hash establishes general export reliability.

## Scratch paired trials and raw evidence
CWD for every command: `/home/vgpnk/Projects/prymeagnt/game-dev-2d`. Project copies, complete stdout/stderr, command arrays, exit, elapsed duration, product existence/size/hash are preserved in each `record.json`; each project and output directory is retained under `corpus/live/r25-export-scout/`.

| trial | project `--path` form | export target form | exit | artifact |
|---|---|---|---:|---|
| pair1 relative-root comparison | relative | relative | 1 | absent, 0 bytes |
| pair1 relative-root comparison | absolute | absolute | 0 | 73,703,800 bytes, hash above |
| pair2 (reverse order) | absolute | absolute | 0 | same size/hash |
| pair2 (reverse order) | relative | relative | 1 | absent, 0 bytes |
| pair3 target isolation | absolute | absolute | 0 | same size/hash |
| pair3 target isolation | absolute | relative | 1 | absent, 0 bytes |
| pair4 target isolation | relative | absolute | 0 | same size/hash |

Commands (paths are per-trial roots/targets, as recorded verbatim in raw JSON):
`/usr/bin/godot --headless --path <project> --export-debug 'Linux/X11' <target>`.
Relative is relative to the recorded CWD; each trial uses a distinct fresh copy, with no inherited `.godot` cache or `out`. Relative failure diagnostic includes `Prepare Template` and then `Project export ... failed`; absolute success prints the benign nested-project warning only. No retry of a failing attempt; the reverse ordering reduces run-order/cache explanation. The battery's intended relative `--runs` option makes its derived scratch and export target relative, so this supports that mechanism, but we did not invoke or alter the runner here.

## Assessment
Causal evidence is strong for Godot export target path form in this environment: 3/3 relative-target failures, 3/3 absolute-target successes; relative-root alone does not fail when target is absolute. Thus the prior intermittent battery pattern is plausibly explained by whether a relative `--runs` was passed, not by a stochastic export-template outage. The smallest prospective correction would normalize the runner's run root (or export target) to absolute before constructing Godot arguments, while keeping preset checks and empty/nonempty artifact validation fail-closed. Do not implement from this scout alone; have executor/verifier reproduce through the actual battery and verify the unchanged missing-preset case before admission. Calibration axis: improved diagnosis evidence; no correction or runner claim. Coverage/depth unchanged. No engine/editor/seeded controls edit, no commit/push/merge.
