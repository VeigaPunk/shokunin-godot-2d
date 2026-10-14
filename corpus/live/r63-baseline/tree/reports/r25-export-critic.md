# Round 25 export critic — path attribution and falsification

## Scope and result

Read-only review of r16/r20/r24 records plus one bounded, sequential relative/absolute full-battery pair. No runner/fixture/preset/engine edits. No delegation. **Result: independently reproduced the target-path-form contrast, isolating the relative export-target string as a cause in this Godot environment; this is not yet the executor-owned battery fix validation.** Counts below distinguish individual export rows from full battery outcomes.

## Historical record review

- `corpus/lessons/r16-export-adverse.json`: Godot 4.7.2, `godot: "godot"`, relative scratch `.shokunin/.../live/runs/20261012T184136853021Z/scratch`; export failed exit 1 with `ERROR: Prepare Template: The given export path doesn't exist.`, 0 bytes, no products. Its `--runs` command was the default relative `HERE.parent / live / runs` (runner code), not a controlled path comparison.
- `corpus/lessons/r24-export-adverse.json`: same Godot/preset and exact failure/no product; relative scratch `.shokunin/.../live/r24-bottom-executor/.../scratch`. This was a relative explicit `--runs` invocation. `reports/r24-bottom-executor.md` confirms command and failure.
- `reports/r20-baseline-scout.md`: one explicit relative `--runs` run, but it reports **StopIteration** as a separate exception, not the export-template signature; not an export-path replicate. Default-path r20 replay succeeded (73,703,800 bytes), as did r20 verifier and r24 verifier, but they differ in time/order/cache state and are not paired counterfactuals.
- Current tracked runner at inspected `HEAD` `1482c9311047a1a78cadb41c6818254fe9fcdcbe`; runner SHA256 `d7bd449d2a351e8adcd2a0cac2b5caf14e60ab9c50d0f48a75b032d9a8088ebb`; preset SHA256 `0b321c1c866e5d61e5e4fe8842fe8552f8d6cac3c9b7659f285f2c15b59ba694`; Godot `4.7.2.stable.arch_linux.ed1daf0bf`; cwd `/home/vgpnk/Projects/prymeagnt/game-dev-2d`.

## Bounded pair (author critic)

Commands used the same runner, cwd, Godot lookup, fixture tree and preset, sequentially; no concurrent run was launched. Full batteries each had 39 cases. Raw stdout/stderr and complete JSON retained in own scratch:

| Order | `--runs` | overall | export row | artifact |
|---|---|---:|---|---|
| 1 | relative `.shokunin/game-dev-2d/corpus/live/r25-export-critic/relative` | exit 1; 38/39 PASS | FAIL, exit 1; exact Prepare Template error; 0 bytes/no products | `corpus/live/r25-export-critic/relative.stdout`; `.../relative/20261013T012748035456Z/verdicts.json` |
| 2 | absolute `/home/vgpnk/Projects/prymeagnt/game-dev-2d/.shokunin/game-dev-2d/corpus/live/r25-export-critic/absolute` | exit 0; 39/39 PASS | PASS, exit 0; 73,703,800 bytes; SHA256 `1a291d3d15e4180b60b0af96cf6458f11fe143636d76575ddf1e23d1a3f24f2e`; products `.pck`, `.sh`, `.x86_64` before runner cleanup | `corpus/live/r25-export-critic/absolute.stdout`; `.../absolute/20261013T012822419759Z/verdicts.json` |

Both presets are `Linux/X11`; fixture hash and runner were not changed. Runner removes export products after recording them, and raw result records cleanup.

## Falsification / confounds

The pair is directionally consistent with the hypothesized path issue but **not a clean `--runs`-only intervention**. In this runner, `scratch = run_dir / "scratch"`, `export_project = scratch`, and the Godot export command passes both `--path str(export_project)` and `str(export_path)`. Relative `--runs` therefore propagates relative project and export output paths to Godot; absolute `--runs` propagates absolute paths. We cannot identify which path argument (or their interaction) is causal from this pair. The run roots were distinct fresh project copies, sequential (relative first), so project-cache/scan warmup and order are confounded. The first pair's relative failure and second success could also reflect export-template availability/timing, cache state, or nondeterministic template preparation. `first_scan_filesystem` completed in both; both scanned same files, and both emitted the nested `controls/project.godot` warning, which is not evidence it caused failure. Cwd was held constant. Preset content, Godot binary and fixture source were held constant. Artifact existence tracks the observed success/failure, but does not identify cause.

No alternating replicate, same-scratch path-only crossover, cache-state control, or template/cache inventory was performed. Historical successes and failures are not randomized pairs. Thus one FAIL/PASS pair (1/1 per arm) cannot rule out scan timing, template state, project cache, concurrency outside our observation, or relative export artifact path as alternatives. The overall battery difference is only export readiness; other 38 case outcomes match at PASS.

## Verdict

Do **not** attribute the issue specifically to relative `--runs`; do not alter `run_battery.py`. No causal paired evidence justifies the executor correction gate. Calibration is **unprovable-but-better** only as diagnostic evidence: this controlled-commands pair records the association while exposing the path propagation confound, but does not establish a repairable cause. Coverage/depth unchanged; no axis improvement claim suitable for admission and no harm established beyond the recorded export failure. Round should HOLD unless non-author follow-up independently resolves these confounds. No export reliability claim.


## Independent target-path isolation follow-up

After reviewing scout's raw trials/report, I ran an independent two-case target-isolation pair on fresh fixture copies, sequentially in the same cwd with `/usr/bin/godot` 4.7.2, same Linux/X11 preset and empty `out` directories. Reversed the path factors: relative project root + **absolute target** succeeded (exit 0; 73,703,800 bytes; SHA256 `1a291d3d15e4180b60b0af96cf6458f11fe143636d76575ddf1e23d1a3f24f2e`); absolute project root + **relative target** failed (exit 1; no artifact; exact Prepare Template diagnostic). Raw complete command/output/product records are `corpus/live/r25-export-critic/target-isolation/relroot_abstarget.json` and `absroot_reltarget.json`; script is `.../pair.py`. This establishes that relative project root alone is insufficient to trigger and that relative target is sufficient in this pair. Together with scout's report/raw trial table (relative target 3/3 failure, absolute target 3/3 success, plus both mixed-factor contrasts), attribution to target path form is strong in this environment, not mere association with the `--runs` root.

The battery itself directly propagates relative `--runs` into `export_path` (`run_dir / scratch / out / fixture.x86_64`) and the Godot command passes that path unchanged. Our own sequential full-battery pair had relative `--runs`: 38/39 PASS, export exit 1/no product; absolute `--runs`: 39/39 PASS, export exit 0, same 73,703,800-byte artifact/hash; raw JSON/stdout paths are listed above. This ties the isolated Godot target-path behavior to the actual adverse battery mechanism. It does not establish universal Godot behavior or production export reliability.

## Revised assessment

The causal premise is now supported: normalize the export target path to absolute before constructing the Godot command (not necessarily the run root/project path). This critic did not edit the runner. Executor must make the smallest target-only normalization after its own paired evidence and validate actual battery with relative `--runs` plus fail-closed missing-preset case; verifier should replay independently. Keep output directory empty checks, export success criteria, and artifact checks intact. Calibration diagnosis improved; no coverage/depth change.
