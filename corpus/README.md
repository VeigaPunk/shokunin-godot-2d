# game-dev-2d corpus

- `fixtures/`: 29 inherited, read-only Godot 4.7.2 fixtures plus `run_battery.py`, which copies the seeds to an ignored scratch run before execution.
- `knowledge/seed.md`: fixture provenance and inherited constraints; `knowledge/2026-10-12-production-checklist.md`: production surfaces still unprobed.
- `lessons/r1-headless-verification.md`: decision table, observed errors, reproduction checklist and source pointers.
- `lessons/r1-initial.json`, `lessons/r1-passing.json`: full per-case stdout/stderr and verdicts from the first failing run and corrected passing run. Live scratch under `live/runs/` is ignored and disposable.
