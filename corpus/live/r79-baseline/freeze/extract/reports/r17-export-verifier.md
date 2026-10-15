# Round 17 export verifier — HOLD

Date: 2026-10-12. Named non-author LEAF verifier; no delegation, fixture/runner/source edits, commit, or push.

## Decision

**HOLD / no calibration improvement and no causal fix admitted.** The Round 16 `Prepare Template: The given export path doesn't exist` failure remains a genuine adverse result. Repeated successful exports do not explain or repair it; do not claim repeat-pass reliability. Keep export classification fail-closed and preserve the missing-preset negative.

## Independent reproduction

Using Godot `4.7.2.stable.arch_linux.ed1daf0bf`, copied the seeded fixtures to fresh `/tmp/r17-leaf-UzHoja/{project,missing}` projects (no inherited `.godot` or output cache), created empty output directories, and directly invoked real Linux/X11 exports.

- Positive: `godot --headless --path /tmp/r17-leaf-UzHoja/project --export-debug 'Linux/X11' /tmp/r17-leaf-UzHoja/project/out/fixture.x86_64` exited 0. Godot emitted `[ DONE ] savepack`; output contained a 73,703,800-byte executable, `.pck`, and `.sh`. Only observed warning was the pre-existing nested `controls/project.godot` warning; no `ERROR:`.
- Negative: same invocation in the independent `missing` copy with preset `Missing preset` exited 1 and emitted `ERROR: Invalid export preset name: Missing preset.`. This remains a genuine fail-closed negative.
- Also independently ran the unmodified runner with `--probe-failing --runs /tmp/r17-leaf-UzHoja/battery`: exit 0, **33/33** records PASS (31 base cases + 2 scratch mutations), including positive export and missing-preset negative. Raw record: `/tmp/r17-leaf-UzHoja/battery/20261012T185340940242Z/verdicts.json` (`verdict: PASS`). This is not the full seven-opt-in-probe command and does not erase or resolve the prior adverse export.

The direct positive log and negative log are under `/tmp/r17-leaf-UzHoja/` (`positive.log`, `missing.log`). Products were generated only in `/tmp`; no publishing.

## Causal and contract review

The proposed relative-versus-absolute output-path explanation is **not causally tested**. Round 16 adverse and passing captures differ across separate runs and scratch roots; their paths are confounded with other run/environment differences. Round 17 scout/executor/critic evidence and my successful absolute-path reproduction add more controls, but no paired experiment varied only relative vs absolute output path while holding project, cwd, destination state, and other relevant conditions fixed. No observed control reproduced the error. There is therefore no supported path fix, timing fix, retry rule, or other causal intervention. Nested-project warning appears on successful as well as failed captures and is not evidence of cause.

Contract remains fail-closed in unchanged runner: positive export requires successful process classification, `[ DONE ]`/`savepack` evidence and a nonempty executable; missing preset requires its expected nonzero result/diagnostic. My fresh negative reproduced the invalid-preset diagnostic; no weakening or masking was observed.

## Integrity / verdict

Before/after SHA-256 over **41 tracked fixture files** matched exactly. `git diff -- .shokunin/game-dev-2d/corpus/fixtures/run_battery.py` is empty. No tracked fixture or runner changes were made. Constants changed: none. Axis verdict: calibration **unchanged** (no causal repair); no new admission. Preserve r16 adverse evidence and make no export reliability claim.
