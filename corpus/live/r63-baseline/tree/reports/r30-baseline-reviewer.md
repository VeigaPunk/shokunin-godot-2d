# Round 30 immutable r29 baseline review

## Verdict: immutable baseline established from committed r29 evidence

Reviewed immutable `HEAD` before the r30 executor change: `511b2493b1b06352e6b85215197af7f28976e3a2` (`game-dev-2d r29: report Button focus calibration`). Its Button fixture SHA-256 is `d42ebb11bdc07a007d7a85eaf0399c594fc76ca8e0fdab0b4d145d36e82bae3`; runner SHA-256 is `097058b23fb53f38dd8cbede34559d7ef6a2999c8568ea598d7a2c57d1b3ff38`. I did not edit fixture or runner. During my review, shared worktree showed an executor modification to `button_activation.gd`; consequently I treat HEAD hashes as the authoritative baseline, not a claim that the live fixture remained untouched through my run.

Committed r29 named-verifier evidence (which ran before the r30 executor change) is the authoritative immutable baseline: its report says 53/53 PASS = 42 ordinary +2 mutants +9 opt-ins, and records byte-identical raw output at `corpus/lessons/r29-focus-verifier.json`, SHA-256 `593c2b25a16f1c40e1a49a04172da12639087bd24e3f742a8054dac0f179c9af`. Its 52 prior cases matched r28, and r29 adds `button_activation_unfocused`. The r29 report gives the same fixture/runner hashes listed above.

I also ran the following command during review, but the shared working tree had already acquired executor edits to the fixture. Therefore this is only a contemporaneous sanity replay, **not** the requested HEAD-baseline reproduction; it must not be used to attribute baseline outcomes to HEAD:

`python .shokunin/game-dev-2d/corpus/fixtures/run_battery.py --probe-failing --probe-unrelated-error --probe-export-launch --probe-godot-error --probe-stream-attribution --probe-crash-exit --probe-timeout --runs .shokunin/game-dev-2d/corpus/live/r30-baseline-reviewer/full`

Exit 0, raw verdict aggregate PASS, 53 records. The output identifies Godot `4.7.2.stable.arch_linux.ed1daf0bf`. Comparison with committed r28 full replay `corpus/lessons/r28-repeat-verifier.json` (SHA-256 `62737006cefb018cba78fa8987ef5a584b26ddfcf55cb1ca5a0568aac4bf27b6`) finds all 52 prior case names present with identical `(verdict, actual_exit, signature)` and no missing or changed outcomes. This live replay contains one additional record named `probe_unrelated_error_export_preset_missing` (the battery emits probe records as well as cases); it reports 53 PASS records overall. Because the fixture was modified by the executor, its Button results are not HEAD baseline evidence. The probe-level intentional adverse classifications (`godot_error_unrelated`, `stream_reject`) are controlled diagnostics nested under PASS probe records, not battery-level failures.

Raw output: `.shokunin/game-dev-2d/corpus/live/r30-baseline-reviewer/full/20261013T044348842225Z/verdicts.json`, SHA-256 `dc4542226b92a4258e634322a1a7b163bef2410cdae2f0ca88ad9b4fe8eb46c1`. Raw record count includes probe metadata; the previous comparable r28 verifier report calls the baseline 52 cases as 42 ordinary +2 mutants +9 opt-ins. This is a replay of the contemporaneous modified fixture, not a regression comparison against immutable HEAD.

No engine/editor source, seeded fixture, controls, runner or Button fixture was edited by me; no commit, push or merge. Scope is only the synthetic headless Godot battery; this report does not establish press/release edge behavior.
