# Round 7 fault executor evidence

Implemented in `corpus/fixtures/run_battery.py` only. No seeded fixtures modified; no new fixtures required. CLI remains backwards compatible; `--fault-injection` is an independent mode using scratch runs.

## Checks

- `python .shokunin/game-dev-2d/corpus/fixtures/run_battery.py --probe-failing` — exit 0, **25/25 PASS**, including both existing scratch mutants. Raw verdict: `corpus/live/runs/20261012T170302499179Z/verdicts.json`.
- `python .shokunin/game-dev-2d/corpus/fixtures/run_battery.py --fault-injection` — exit 0, machine verdict PASS, deliberately separate from seeded battery. Raw verdict: `corpus/live/runs/20261012T170319264915Z/fault-verdicts.json`.
  - Hanging subprocess printed its start marker, timed out after 0.25 s, and production process classifier returned FAIL.
  - Clean expected negative diagnostic with exit 2 classified PASS.
  - Same expected diagnostic and exit 2 plus unrelated `ERROR:` classified FAIL.

Shared subprocess execution and classification are used by ordinary cases and fault probes. Known negative classes use case-specific expected error lines; dynamic animation/chain errors use narrow, one-`ERROR:` matching. Mutant checks also pass through classifier and retain explicit signatures. Timeout is recorded as error and cannot satisfy a normal expected case. Standard behavior remains 25/25.
