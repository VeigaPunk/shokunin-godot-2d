# Round 42 focus-restore named verifier

## Verdict

**PASS, with the required bounded interpretation.** I am the named non-author verifier. On the executor's proposed `--repeat-right --focus-restore` candidate, the full required default-path replay passed, both targeted sabotage mutations failed at the intended early checks, and the isolated fault-injection harness classified its intentional faults correctly. No HOLD condition was found.

## Direct paired evidence

Real Godot 4.7.2 headless, connected in-tree HSlider (0..10, step 1, initial 5), signal-driven Label, separate in-tree focusable Button. Direct scratch artifacts are in `corpus/live/r42-focus-restore-executor/scratch/`; scout/reviewer scratch reports independently record the same sequence. Each fresh parsed action was followed by one process frame. Owner was asserted before each edge; numeric value, accumulated signal receipts, and Label were asserted afterward:

| Edge | Focus owner before | Action | Value | Receipts | Label |
|---:|---|---|---:|---|---|
| 0 | slider | right press | 6 | [6] | Value 6 |
| 1 | Button | right press | 6 | [6] | Value 6 |
| 2 | Button | right release | 6 | [6] | Value 6 |
| 3 | slider restored | left press | 5 | [6,5] | Value 5 |
| 4 | slider | left release | 5 | [6,5] | Value 5 |
| 5 | slider | left press | 4 | [6,5,4] | Value 4 |
| 6 | slider | left release | 4 | [6,5,4] | Value 4 |

The in-tree fixture positive row exits 0 only after all checks, with its expected PASS signature and no error diagnostics.

Sabotage evidence used disposable copies of the scratch script. Omitting restoration exited 2 at `focus-restore owner assertion failed before edge 3` (before remaining edges); omitting the first dispatch exited 2 at `focus-restore edge assertion failed: edge=0` (value/receipt mismatch). These did not falsely produce PASS.

## Required full battery and comparison

Command (default PATH):
`python .shokunin/game-dev-2d/corpus/fixtures/run_battery.py --probe-failing --probe-unrelated-error --probe-export-launch --probe-godot-error --probe-stream-attribution --probe-crash-exit --probe-timeout --runs .shokunin/game-dev-2d/corpus/live/r42-focus-restore-verifier`

Exit 0; outer verdict **67/67 PASS**. Raw byte-identical lesson: `corpus/lessons/r42-focus-restore-verifier.json`, SHA-256 `e483882c1f39963388a48791500cb78bf37c4216d5e3e97b3258ad3e04561ed5`. Baseline `r41-focus-handoff-verifier.json` had 66 results, including 57 tuple-bearing cases and nine opt-ins. All 57 prior `(case, verdict, actual_exit, signature)` tuples are unchanged; all nine opt-ins retain their outer PASS and their available stable inner classifications match (including Godot error `[true,false]`, stream attribution `[true,false]`, crash-exit `[true,false]`, timeout `[false,true,false]`). Exactly one new tuple row is added: `slider_adjust_repeat_right_focus_restore`, PASS, exit 0. No prior rows changed.

Separate `--fault-injection` replay exited 0, outer verdict PASS. Raw byte-identical fault lesson: `corpus/lessons/r42-fault-verifier.json`, SHA-256 `cc50beaf84dfdc2010358eafda5dbb50e217ed6327d8e39fd7b3538cc612fd8f`. deliberate hang classified FAIL after 0.25s timeout, unrelated-error probe classified FAIL, and clean expected-negative classified PASS. This is harness classification behavior, not evidence that intentional inner cases are clean.

Tracked fixture/runner SHA-256 before and after replay matched: `slider_adjust.gd` `2fcc98b4c5363d121effdb0accaa63118a42fdb32f82ccd1d593581063f5ed21`; `run_battery.py` `948f6ca23abd8f2b8dd81424d7dd0d81061df18db75895fee39d40f56be6ed18`.

## Limits and adverse telemetry

Retain the scout's initial incorrect expectation of a new receipt on unchanged edge 1 as probe-setup telemetry; corrected run expected cumulative `[6]`. Earlier r41 timeout telemetry remains adverse; this replay does not erase it. State/receipt observations and owner checks do not independently prove which internal Control consumed unchanged edges. Evidence is bounded to synthetic parsed actions plus one process frame per edge in headless Godot 4.7.2—not OS auto-repeat, physical timing, rendered/pointer/accessibility behavior, production, generic slider behavior, or internal consumption of unchanged edges. No engine/editor or seeded controls were changed; no commit, push, or merge.
