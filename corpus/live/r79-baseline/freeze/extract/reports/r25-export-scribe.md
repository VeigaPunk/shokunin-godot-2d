# Round 25 export scribe — relative/absolute path diagnosis checklist

Scope: read-only synthesis of the standing mission, Round 25 declaration, prior raw lessons/reports, and current runner. This is not a Godot replay and does not diagnose the failure. No runner/fixture/control edits or export runs were performed. This report is the only file written.

## Question and admission bar

The hypothesis under test is narrow: does relative versus absolute `--runs` root cause the intermittent `ERROR: Prepare Template: The given export path doesn't exist.` during otherwise identical real-Godot fixture exports? A historical adverse run plus successful runs with different roots are confounded, not a paired causal contrast. The round declaration requires at least one controlled pair in which relative fails and absolute passes, plus non-author re-execution, before any attribution or runner fix. If bounded pairs do not produce that differential, diagnosis is unproved and the round remains HOLD. Preserve export fail-closed behavior and the Missing preset negative.

## Historical observations (not causal pairs)

| Evidence | Runs root form / relevant path | Godot / result | Interpretation limit |
|---|---|---|---|
| r16 adverse `corpus/lessons/r16-export-adverse.json` | Runner invoked with relative `.shokunin/game-dev-2d/corpus/live/runs`; recorded scratch path relative | Godot 4.7.2; export exit 1, zero products, `Prepare Template: The given export path doesn't exist.` | Adverse is real, but not paired to an absolute run under controlled conditions. |
| r16 parent retry `corpus/lessons/r16-parent-retry.json` | Explicit absolute `/tmp/r16-parent-retry`; scratch absolute | Same Godot; export exit 0, 73,703,800-byte executable | Separate run/time/environment; does not show root form caused r16 failure. |
| r16 named verifier `corpus/lessons/r16-clamp-verifier.json` | Explicit absolute `/tmp/...`; scratch absolute | Same Godot; export passed | Independent pass, still confounded with adverse. |
| r24 adverse `corpus/lessons/r24-export-adverse.json` | Explicit relative `.shokunin/game-dev-2d/corpus/live/r24-bottom-executor`; scratch recorded relative | Same Godot; exit 1, zero products, same Prepare Template diagnostic | Repeats correlation, not causal proof; runner's CWD and output target must be controlled. |
| r24 named verifier `corpus/lessons/r24-bottom-verifier.json` | Default runs root resolves from `HERE`; scratch absolute | Same Godot; export passed | Different run and scratch context; not a paired intervention. |
| r17 historical isolation (`corpus/lessons/r17-export-path-hold.md`, `reports/r17-export-scout.md`) | Multiple relative-adverse vs absolute-pass observations; scratch copies and timing differed | Bounded scratch exports passed; no failure reproduced | Prior investigation explicitly concluded cause unestablished; not evidence to override. |

The runner resolves `HERE = Path(__file__).resolve().parent`, defaults `--runs` to `HERE.parent / "live" / "runs"`, and constructs `run_dir = args.runs / stamp`. It creates `scratch/out`, then passes Godot `--path <scratch>` and an explicit `<scratch>/out/fixture.x86_64` target. The export subprocess inherits the Python runner's CWD (`subprocess.run` has no `cwd=` override). Therefore a valid paired test must distinguish the `--runs` spelling while ensuring both export project and target resolve to equivalent locations and that CWD does not inadvertently change. Do not treat a relative scratch path in JSON alone as proof the Godot export target was relative: inspect exact argv and resolve it against recorded CWD.

## Pairing table to fill from raw live evidence

Use fresh, equivalent fixture copies and empty `out/` directories for each arm; keep Godot binary/version, project/preset hashes, CWD, environment, target path semantics, and command content fixed. Alternate order across pairs (R→A, then A→R) to reduce time/order confounding. Keep bounded pair count; preserve every attempt, including failures. No retry may overwrite/replace an adverse attempt.

| Pair / order | Relative `--runs` exact argv + CWD | Absolute `--runs` exact argv + CWD | Same project/preset and resolved output? | Relative outcome (exit / diagnostic / product bytes+hash) | Absolute outcome (exit / diagnostic / product bytes+hash) | Raw stdout/stderr + metadata paths |
|---|---|---|---|---|---|---|
| 1 (R→A) | pending | pending | pending | pending | pending | pending |
| 2 (A→R), only if needed | pending | pending | pending | pending | pending | pending |

For each cell capture UTC start/end, pair ID, order, runner command, `pwd`, absolute and literal `--runs`, Godot resolved executable/version, fixture and preset SHA-256, exact Godot argv, output-directory existence/emptiness before launch, return/timeout/error, stdout and stderr separately, savepack presence, output listing/size/SHA-256, and raw `verdicts.json`. Keep raw artifacts under the assigned scratch area; do not copy away or mutate seeded fixtures. Record counts as attempts and paired contrasts, not a reliability rate from a tiny sample.

## Falsification and admission checklist

- [ ] The failure is reproduced in a relative arm under preserved raw evidence; a historical adverse is not enough for this controlled claim.
- [ ] Its same-pair absolute arm succeeds, and each contrast uses fresh/equivalent fixture copies, same Godot executable/version, preset bytes, relevant environment, CWD, and output-path semantics.
- [ ] Reverse order in a bounded second pair if resources permit; retain all outcomes. A lone relative-fail/absolute-pass pair is the minimum hypothesis signal, not proof of general reliability.
- [ ] If both arms fail, both pass, or the absolute arm fails while relative passes, reject attribution to relative-vs-absolute based on these observations; report HOLD/unprovable rather than rationalizing a fix.
- [ ] Check and report alternative explanations: CWD changed; output/scratch paths differ beyond spelling; missing/unclean output directory; permission/ownership; preset/template availability; cache state; concurrent Godot/template activity; time/order effects; filesystem mount/path behavior; timeout or unrelated project scan errors. Do not claim ruled out without measurements.
- [ ] Do not infer that “Prepare Template” names the runner's `--runs` root. Capture Godot's exact absolute `--path` and export target as resolved at invocation.
- [ ] Do not auto-retry a failed positive export and report only the later pass. Export readiness stays accepted only with expected process exit, savepack evidence, and a nonempty artifact; retain the `Missing preset` expected-failure control.
- [ ] Any proposed runner change is limited to `run_battery.py`, follows only a reproduced cause, preserves fail-closed checks and missing-preset behavior, and receives named non-author paired replay plus ordinary/full regression replay before admission.
- [ ] Report axis verdicts categorically (calibration/depth/coverage), identify adverse evidence and constants changed, and make no production-export-reliability claim. With no causal paired evidence, no code edit is the correct outcome and calibration is unchanged/HOLD.

## Scribe assessment

At the time of this report, evidence consists of historical adverse and passing runs with correlated path-form differences, no controlled paired replay, and no causal runner change. Conclusion: **relative `--runs` contribution remains unproved**. This scribe does not satisfy causal attribution or round admission; the executor/verifier raw pairing and independent review are still required.
