# Round 57 baseline regression report — read-only

## Scope

This lane independently measured the pre-round baseline and its opt-in classifications. I did not edit the runner, fixtures, engine/editor source, or any other report. No save/load fixture existed at the declared baseline (`HEAD c9a610d247425e759a50b69ca0831e8852b75b52`; runner SHA-256 `d546405ef2dcd18b5308cb81877b93905fb77102a364321bcc3a98c88c68c11d`). The r56 raw receipt records 70 ordinary cases plus two scratch mutants and nine opt-in records: 81 total. It has no save/load-named case. Seven opt-in flags account for nine records because unrelated-error probes emit four individual rows.

## Independent baseline replay

Godot available on this host: `/usr/bin/godot` (`godot --version` → `4.7.2.stable.arch_linux.ed1daf0bf`). I ran the seven declared opt-in flags in a dedicated scratch location:

```text
python .shokunin/game-dev-2d/corpus/fixtures/run_battery.py --probe-failing --probe-unrelated-error --probe-export-launch --probe-godot-error --probe-stream-attribution --probe-crash-exit --probe-timeout --runs .shokunin/game-dev-2d/corpus/live/r57-save-regression/full
```

Result: exit 0, `PASS battery`, 81/81 (70 ordinary + 2 mutants + 9 opt-in records). Raw output: `.shokunin/game-dev-2d/corpus/live/r57-save-regression/full/20261013T112523507522Z/verdicts.json`, SHA-256 `0f1e4808f10d52c26f1d7f33b57e9c0c84a26c74c8f2bbda39cd297683a31e61`. Every one of 70 ordinary records passed; six expected exit-1 rows and 32 expected exit-2 rows were accepted with their declared signatures. Both mutants passed classification with exit 2 and intended signatures (`chain incomplete`; `LEVEL ASSERTION FAILED: loaded level cell lacks collision geometry`).

The old baseline receipt `.shokunin/game-dev-2d/corpus/lessons/r56-pushframe-non-author.json` (SHA-256 `6b979618d730848499fba2c038c4a16c692518ce7b189e9130938c85ad52fdd5`) and this replay agree on all 72 tuple-bearing rows `(case, verdict, actual_exit, signature)`: 72/72 exact, no missing or changed tuples. Nine opt-in record verdicts are all PASS in both. Paired inner classifications are stable: unrelated-error export/mutant rows reject the injected diagnostic while their outer probes pass; Godot error `[true,false]`; stream attribution `[true,false]`; crash exit `[true,false]`; timeout `[false,true,false]`; export launch PASS. The printed `FAIL` for expected reject arms is an inner classification, not a battery failure.

## Interpretation and limits

This establishes a clean 70/81 pre-change baseline and stable tested classifications on this host/runtime. It is not evidence about the new save fixture or its corrupted-data behavior. The run occurred in a unique scratch directory; no pre-existing live artifacts were modified. By the time of report writing, the executor's additive runner/fixture edits were visible in the worktree, but this baseline replay's raw has no save rows and is not a post-change verification. I made no tracked edits and did not run mutations. No engine/editor source or existing artifacts were changed.
