# Round 26 timeout executor report

Implemented the opt-in three-arm timeout contrast in the assigned `timeout_probe.gd` and `run_battery.py` only. The fixture now emits the exact marker immediately before either a deliberate clean delay or the existing hold-open wait. Both slow-positive arms therefore expose the same marker before process completion/timeout.

## Replay

Command: `python .shokunin/game-dev-2d/corpus/fixtures/run_battery.py --probe-timeout --runs .shokunin/game-dev-2d/corpus/live/r26-executor-final`

Exit 0; ordinary fixture/export rows PASS and the timeout meta row PASS. Raw details: `.shokunin/game-dev-2d/corpus/live/r26-executor-final/20261013T014502499619Z/timeout-verdicts.json`; outer verdicts in sibling `verdicts.json`.

- `slow_clean_old_bound`: old 0.75s bound, elapsed 0.753s; marker observed, timed out, inner false, direct child gone after cleanup.
- `slow_clean_new_bound`: 1.5s deliberate post-marker wait; elapsed 1.877s; marker observed, exit 0, inner true.
- `hold_open_new_bound`: new 3.0s bound, elapsed 3.006s; marker observed, timed out, inner false, direct child gone after cleanup.

The 1.5s delay is explicitly encoded in the test fixture, not a random value. 3.0s new bound is twice that measured deliberate wait and leaves observed ~0.377s margin in this Godot 4.7.2 run. This is one host/run measurement, not a cross-platform guarantee. Runner records actual elapsed time. Constants: old timeout 0.75s (unchanged baseline), fixture delay 1.5s (new), new timeout 3.0s (new), cleanup 3s (unchanged). Ordinary `CASES` and existing CLI flags are unchanged; new arm flags are fixture-internal. No engine/editor/seeded control mutation.

Tracked fixture SHA-256: `4994893281fea8221d980f5c551f2e0541464530e3e542ac97b2cabe97a61462`; runner SHA-256: `431f922421af2780529860151347a7146204952d55e09607779b34632bc682cc`. No commit/push/merge.

This executor replay supports the requested calibrated contrast; independent non-author verification remains required before round admission.
