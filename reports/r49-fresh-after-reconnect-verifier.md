# Round 49 named non-author verifier — fresh press after late reconnect

## Verdict: PASS; scoped synthetic evidence reproduced

I am the named non-author verifier. I did not delegate, edit tracked fixtures/runner, commit, push, or merge. I read the standing mission, r49 LOG declaration, wave-1 reports, and tracked `slider_adjust.gd` / `run_battery.py`. The r49 scout stopped responding after scratch creation and was canceled; it produced no verifier result. Record this as adverse lane telemetry, not evidence. Executor evidence was treated as author evidence only; I preserved its raw file unchanged.

## Named replay and preservation

Ran the requested full default path:

```text
python .shokunin/game-dev-2d/corpus/fixtures/run_battery.py --probe-failing --probe-unrelated-error --probe-export-launch --probe-godot-error --probe-stream-attribution --probe-crash-exit --probe-timeout --runs .shokunin/game-dev-2d/corpus/live/r49-fresh-after-reconnect-verifier/runs
```

Godot 4.7.2, run `20261013T084246724914Z`, outer battery PASS, 74/74. This comprises 63 ordinary cases, 2 mutants, and 9 opt-in probes. The new candidate row passed exit 0 with signature `PASS slider_adjust_repeat_second_focus_restore_press_after_late_reconnect values=6,6,6,5,5,5,5,4,4,3 receipts=6,3 Labels=Value 6,Value 3`.

The runner's raw is byte-identical at `corpus/lessons/r49-fresh-after-reconnect-non-author.json` (SHA-256 `45eace51453b307458cc441c85aa8ebe2e6a63c584f6187fbc2f043f578a2751`). The executor-author file `corpus/lessons/r49-fresh-after-reconnect-verifier.json` was restored/preserved byte-identically (SHA-256 `298a17bcee81020e6a7eb22bb917e65bc8c0d189fb59a3089e49e8d78555f12a`). Comparing the 64 prior tuple-bearing `(case, verdict, actual_exit, signature)` records with r48: all 64 remain exactly identical; one new tuple is present, the expected r49 PASS/exit0. The 9 opt-in classifications remained stable; paths are excluded from that comparison.

Separate `--fault-injection` run outer PASS: deliberate hang was inner FAIL/TIMEOUT, unrelated-error fault inner FAIL, and clean expected-negative inner PASS (exit 2). Raw preserved at `corpus/lessons/r49-fault-non-author.json`.

## Targeted sabotage

Three isolated copies of the candidate script were run directly under Godot 4.7.2:

- Omitted edge9 dispatch: failed at edge9 state assertion (exit 2), before positive marker.
- Disconnected callback before edge9 dispatch: failed at edge9 state assertion (exit 2), before positive marker.
- Omitted edge7 reconnect: failed at reconnect assertion (exit 2), before positive marker.

Scratch artifacts are under `corpus/live/r49-fresh-after-reconnect-verifier/sabotage/`. Fixture and runner hashes before/after were unchanged: fixture `0a21283fafed64f5a1653aa5e29ba9a1f76be848fe48f8e256b6cc05783c58f5`; runner `0cc168fdb16ff3dbbc0f16dddde4698183881365612d45c49e4d7a35f90d6cd0`.

## Scope and axis assessment

This supports the narrow depth move: a fresh parsed `ui_left` press after callback reconnection changes 4 to 3 and updates receipt/Label after the prior nine-edge history. The recorded owner/value/receipt/Label and callback transitions match the candidate's asserted sequence. Depth improved; coverage and calibration unchanged; no harm observed in this bounded replay. Evidence is synthetic parsed events plus process frames only. It does not establish OS repeat, physical timing/input, rendered or pointer behavior, accessibility, production behavior, generic replay, or internal consumer behavior on unchanged edges.
