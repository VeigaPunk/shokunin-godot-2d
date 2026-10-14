# Round 25 executor — paired relative/absolute `--runs` exports

## Scope and immutable baseline

Read-only HEAD: `1482c9311047a1a78cadb41c6818254fe9fcdcbe` (`r24` report). No runner or fixture edits. HEAD runner SHA-256: `d7bd449d2a351e8adcd2a0cac2b5caf14e60ab9c50d0f48a75b032d9a8088ebb`; fixture `export_presets.cfg` SHA-256: `0b321c1c866e5d61e5e4fe8842fe8552f8d6cac3c9b7659f285f2c15b59ba694`. Preset is Linux/X11 with `export_path=""`; export target is explicitly `<scratch>/out/fixture.x86_64`, and the runner creates/validates an empty `out` directory before invoking Godot. Missing-preset negative row remains in every run.

## Controlled bounded replay

Executed four unmodified full battery invocations serially from repository cwd `/home/vgpnk/Projects/prymeagnt/game-dev-2d`, with the same `godot` executable (captured output identifies Godot 4.7.2.stable.arch_linux.ed1daf0bf), HEAD seed, preset, and runner. Alternated relative and absolute `--runs` forms; each gets its own fresh run root and unique timestamp. Console outputs and complete verdict JSONs are retained below the two owned scratch roots.

| order | `--runs` argument form | raw verdict JSON | full battery | export readiness |
|---|---|---|---|---|
| 1 | relative `.shokunin/game-dev-2d/corpus/live/r25-own-relative` | `corpus/live/r25-own-relative/20261013T012747419272Z/verdicts.json` | 38/39 PASS; battery exit 1 | FAIL, exit 1; `Prepare Template: The given export path doesn't exist.`; 0 bytes / no products |
| 2 | absolute `/home/vgpnk/Projects/prymeagnt/game-dev-2d/.shokunin/game-dev-2d/corpus/live/r25-own-absolute` | `corpus/live/r25-own-absolute/20261013T012829908977Z/verdicts.json` | 39/39 PASS; battery exit 0 | PASS, exit 0; 73,703,800 bytes, SHA-256 `1a291d3d15e4180b60b0af96cf6458f11fe143636d76575ddf1e23d1a3f24f2e` |
| 3 | absolute (same root) | `corpus/live/r25-own-absolute/20261013T012905598095Z/verdicts.json` | 39/39 PASS; battery exit 0 | PASS, exit 0; same size and SHA-256 |
| 4 | relative (same root) | `corpus/live/r25-own-relative/20261013T012938947823Z/verdicts.json` | 38/39 PASS; battery exit 1 | FAIL, exit 1; same diagnostic; 0 bytes / no products |

Corresponding stdout/stderr captures: `corpus/live/r25-own-relative/console-1.txt`, `console-2.txt`; `corpus/live/r25-own-absolute/console-1.txt`, `console-2.txt`. Relative form resolves to the same repository-local area as the absolute form. All four missing-preset rows PASS with the expected invalid preset diagnostic; no failure was retried or converted to PASS. The failure and success outputs both contain the nested `controls/project.godot` warning, so that warning alone does not distinguish outcomes. Raw results retain all case outputs; each runner invocation cleans exported products after recording.

Historical checks: `corpus/lessons/r16-export-adverse.json` is relative-root FAIL/0 products; `r16-parent-retry.json` is absolute `/tmp` PASS/73,703,800 bytes. `r24-export-adverse.json` is relative-root FAIL/0 products. `r17-export-path-hold.md` records earlier mixed bounded probes with no established cause. These older comparisons are not controlled pairs.

## Finding / recommendation

This is a repeated, alternating contrast under the same runner and machine: relative `--runs` yielded 2/2 export failures while absolute `--runs` yielded 2/2 successes; missing-preset behavior stayed fail-closed. It materially supports relative path form as a causal contributor in this environment, and it rules out a simple one-off export failure. It does **not** establish a general or production export cause: runs use distinct scratch directories/times and cannot isolate every cache, filesystem, template, or Godot state effect. No code correction was made. In particular, do not weaken the success predicate, suppress this failure, or auto-retry it. A minimal path normalization change may be considered only after independent paired re-execution confirms it; this executor's own runs do not constitute non-author verification. No engine/editor/seeded-control change, commit, push, or merge.
