# Round 35 baseline reviewer — immutable r34 replay

## Baseline identity

The working HEAD is `4f83d1d8fdd51a86b16abf3bc0743bc8e77087fb` (`game-dev-2d r34: report ButtonGroup coverage`), matching the declared immutable r34 baseline. The tracked worktree currently has uncommitted edits to `corpus/fixtures/button_group_selection.gd` and `run_battery.py` from the executor lane; I did not inspect their contents or alter them. To keep the replay isolated from those edits, I exported the fixture tree from HEAD into my own scratch area `corpus/live/r35-baseline-reviewer/` and ran only that archived copy.

HEAD baseline SHA-256: `run_battery.py` = `15c9c9f81d03e55f3ef0bca835e8406018adb07e2f0b9f78dc85150efd911f87`; `button_group_selection.gd` = `3657aaeed63dbc6f6ea6454d8e36fa21f395d27b2df312dc0fd3446614a5140e`. Committed r34 raw verifier receipt SHA-256 = `3e705bd77ae4cb62b70c2cf18b9f9f2364122d462256211095ad1e598e3974ce`; fault receipt SHA-256 = `cd49178d1f70d6a05dc89abffb6d9f756f22cb258b9f1854133597e4592849de`.

## Independent replay

From the archived HEAD copy, ran:

```text
python <scratch>/.shokunin/game-dev-2d/corpus/fixtures/run_battery.py --probe-failing --probe-unrelated-error --probe-export-launch --probe-godot-error --probe-stream-attribution --probe-crash-exit --probe-timeout
```

Exit 0: **58/58 PASS** (47 ordinary, 2 mutants, 9 probe rows). The new raw run is `corpus/live/r35-baseline-reviewer/.shokunin/game-dev-2d/corpus/live/runs/20261013T053105376837Z/verdicts.json`. All 58 `(case, verdict, actual_exit, signature)` tuples match `corpus/lessons/r34-button-group-verifier.json` exactly. The opt-in probes preserve expected inner adverse classifications (`godot_error_unrelated`, `stream_reject`) under their outer probe PASS results. Existing r34 grouped/disconnected ButtonGroup outcomes were reproduced from the committed baseline; no r35 ungrouped claim is made here.

## Scope

This is baseline/regression evidence only, not a review of the r35 causal contrast or executor changes. No tracked file, engine/editor source, or seeded fixture was edited; no commit, push, or merge was performed. Constants unchanged: baseline 47 ordinary / 58 full.
