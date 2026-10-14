# Round 24 — named non-author bottom verifier

**Result: coverage replay PASS; export caveat retained.** Independently ran the requested real Godot battery from the default path:

```text
python .shokunin/game-dev-2d/corpus/fixtures/run_battery.py --probe-failing --probe-unrelated-error --probe-export-launch --probe-godot-error --probe-stream-attribution --probe-crash-exit --probe-timeout
```

Exit 0; aggregate `PASS`; raw result has 50/50 passing rows: 39 ordinary, 2 scratch mutants and 9 opt-in probes. This preserves the previous 48 cases with no failures. Godot reported 4.7.2. Raw full JSON was copied byte-for-byte from `corpus/live/runs/20261013T012300240590Z/verdicts.json` to `corpus/lessons/r24-bottom-verifier.json` (98,725 bytes).

## Bottom edge evidence

- Positive `camera_bottom_limit`: exit 0, PASS. Fixture uses authored bottom limit 1000, target `(0, 2000)`, and dynamic visible viewport half-height. Observed expected active center y=968 (64px viewport, half-height 32), distinct from target.
- `camera_far_bottom_bound`: exit 2, expected PASS classification. With camera limit changed to 100000, center followed target y=2000 and failed the *same authored boundary* assertion (`camera limit assertion failed: expected active center within bottom boundary and distinct from target`). It was not setup failure.
- Disposable scratch sabotage changed the authored `camera.limit_bottom` from 1000 to 100000, then invoked the positive `--bottom-bound` probe. It exited 2 with the intended bottom-bound assertion, center y=2000/target y=2000, expected clamp y=968; no setup error. Scratch is under `corpus/live/r24-bottom-verifier-scratch/sabotage`.

## Separate fault injection

Ran `python .shokunin/game-dev-2d/corpus/fixtures/run_battery.py --fault-injection` separately; command exit 0 means harness completed, not that every probe passed. Raw output copied byte-for-byte to `corpus/lessons/r24-fault-verifier.json`: top-level fault mode, seeded_battery_run=false; deliberate `fault_hang` and `fault_unrelated_error` FAIL, clean expected negative PASS. Not included in battery 50/50.

## Adverse author export record and limits

Preserved and inspected `corpus/lessons/r24-export-adverse.json`: author replay was 38/39, with `export_readiness` FAIL and `ERROR: Prepare Template: The given export path doesn't exist.` The independent default-path replay's export-readiness row passed (nonempty executable, 73,703,800 bytes), but this one subsequent success does **not** erase the committed adverse failure or prove export reliability. Cause of discrepancy remains unresolved; no reliability claim is made.

Tracked fixture/runner Git blob hashes before and after this verifier were identical: `camera_limit.gd` `d981f5a0ca7cb251ec66cc8099ea95ca763c0f92`; `run_battery.py` `1a36adbe74e0c103fd7390383d561a146811eab9`. No tracked fixture/runner edits were made by verifier. No commit, push or merge.
