# Round 25 independent paired export-path review

## Method
Used the existing `run_battery.py` unchanged (no fixture/runner edits), four bounded full-battery trials in alternating order relative, absolute, absolute, relative for `--runs`. Each trial used a new empty run root and the same repository cwd, seed fixture, Godot binary `/usr/bin/godot` (`4.7.2.stable.arch_linux.ed1daf0bf`), export preset, and runner command apart from `--runs` path spelling. Every trial copies fixtures into unique scratch. Each invocation had 180s bound (actual ~27–29s). Raw commands, stdout/stderr, exit, and complete verdict JSON are in this directory (`battery-{1..4}-output.txt`, `battery-{1..4}-verdicts.json`).

## Paired observations
| order | --runs form | exit | export_readiness | bytes | missing preset |
|---:|---|---:|---|---:|---|
| 1 | relative `.shokhin…/runner-runs-relative-0` | 1 | FAIL (actual exit 1; `Prepare Template: The given export path doesn't exist.`) | 0 | PASS (exit 1, expected missing-preset diagnostic) |
| 2 | absolute `/home/vgpnk/…/runner-runs-absolute-1` | 0 | PASS (exit 0) | 73,703,800 | PASS |
| 3 | absolute `/home/vgpnk/…/runner-runs-absolute-2` | 0 | PASS (exit 0) | 73,703,800 | PASS |
| 4 | relative `.shokhin…/runner-runs-relative-3` | 1 | FAIL (actual exit 1; same missing export-target diagnostic) | 0 | PASS |

This is two alternating matched comparisons: both relative trials failed and both absolute trials passed, with matching per-form outcomes. This reproduces a strong causal association between relative `--runs` spelling and export failure for this runner/Godot environment, not merely intermittence. The run-root absolute location is equivalent to its relative spelling from the identical cwd; underlying project seed, generated fixture copies, output location semantics, preset, and executable are otherwise constant. All four export outputs include the same benign nested `project.godot` warning; only relative-target attempts additionally report the export-path error. Missing-preset fail-closed behavior passed in all four.

## Additional direct Godot path probe
I also tried four raw exports using the same project copy and export target paths: relative target, absolute target, absolute target, relative target. Relative targets fail (exit 1/zero artifact) and absolute targets succeed (exit 0, 73,703,800-byte artifact). Full data/output is `direct-godot-path-experiment.json`. This corroborates but does not replace the runner `--runs` pairing. The raw probe confirms no project-path change was required to produce the target-path contrast.

## Evidence limits / recommendation
Retain the relative `--runs` failure outputs; do not reclassify as a pass or claim general Godot export reliability. The evidence justifies executor evaluation of one narrow absolute-path normalization at the export target (not suppression of diagnostics or a retry). The independent reviewer did not edit code. No engine/editor files, seeded fixture inputs, or tracked runner were modified.
