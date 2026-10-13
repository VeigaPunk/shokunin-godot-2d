# Round 36 baseline reviewer — immutable r35 replay

## Baseline identity

Working HEAD: `de4d3410ee1e41eda5178f4b73eb217c979c8979` (`game-dev-2d r35: report ButtonGroup absence calibration`), matching the declared r35 baseline. I archived committed fixture/lesson files from HEAD into my own scratch copy at `.shokunin/game-dev-2d/corpus/live/r36-baseline-reviewer/`; replay was isolated from the uncommitted LOG update and did not inspect or change executor work.

HEAD SHA-256: `run_battery.py` `78072024d092964c9e214be418df10933092caf3f73168cbc27ef189f43ebc87`; `button_group_selection.gd` `bc9f4aadfcfb2ea4930985ca4acb4d440ad3fd3c99411c891ca434e748053957`; committed r35 raw verifier `corpus/lessons/r35-group-absence-verifier.json` `09a44a1004cbc52d3b8bd60b0bbe6902cdc7f6271d3c5f80f20eeec00b75a3ed`.

## Independent baseline replay

Ran the default full battery on the archived HEAD copy:

```text
python <scratch>/.shokunin/game-dev-2d/corpus/fixtures/run_battery.py --probe-failing --probe-unrelated-error --probe-export-launch --probe-godot-error --probe-stream-attribution --probe-crash-exit --probe-timeout
```

Exit 0; **59/59 PASS** = 48 ordinary +2 mutants +9 opt-ins. Raw receipt: `.shokunin/game-dev-2d/corpus/live/r36-baseline-reviewer/.shokunin/game-dev-2d/corpus/live/runs/20261013T054126551733Z/verdicts.json`, SHA-256 `82f4cfbaa43bb61605dc0664dd8743c098e7a225ee7327433df435387a15fa94`. All 50 result rows carrying `(case, verdict, actual_exit, signature)` are unchanged versus committed r35 receipt. Opt-in probes preserve expected inner adverse classifications, including `godot_error_unrelated` and `stream_reject`, under their outer probe PASS results. The ButtonGroup absence row reproduces expected exit 2 at the after-B→A exclusivity assertion.

This is baseline/regression evidence only; it makes no claim about r36 HSlider input semantics or causal coverage. No tracked file, engine/editor source, or seeded fixture was edited; no commit, push, or merge. Constants unchanged: baseline 48 ordinary / 59 full.
