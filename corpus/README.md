# game-dev-2d corpus

- `fixtures/`: 29 inherited, read-only Godot 4.7.2 fixtures plus `run_battery.py`, which copies the seeds to an ignored scratch run before execution.
- `knowledge/seed.md`: fixture provenance and inherited constraints; `knowledge/2026-10-12-production-checklist.md`: production surfaces still unprobed.
- `lessons/r1-headless-verification.md`: decision table, observed errors, reproduction checklist and source pointers.
- `lessons/r1-initial.json`, `lessons/r1-passing.json`: full per-case stdout/stderr and verdicts from the first failing run and corrected passing run.
- `lessons/r2-camera-headless.md`, `lessons/r2-camera-verifier.json`: camera-center decision boundaries and independent 17/17 replay; rendered viewport behavior remains unprobed.
- `lessons/r3-ui-headless.md`, `lessons/r3-ui-verifier.json`: synthetic UI signal-to-Label decision boundaries and independent 19/19 replay; production/rendered UI remains unprobed.
- `lessons/r4-level-headless.md`, `lessons/r4-level-verifier.json`: authored level tile collision metadata and independent 21/21 replay; runtime contact/rendering remain unprobed.
- `lessons/r5-animation-headless.md`, `lessons/r5-animation-verifier.json`: deterministic in-memory property animation and independent 23/23 replay; rendered motion remains unprobed.
- `lessons/r6-export-headless.md`, `lessons/r6-export-verifier.json`: actual scratch Linux/X11 export plus missing-preset control, independent 25/25; generated artifacts deleted, app launch and production project remain unprobed.
- `lessons/r7-fault-classification.md`, `lessons/r7-fault-verifier.json`, `lessons/r7-normal-verifier.json`: shared subprocess/classifier fault probes and independent 25/25 replay.
- `lessons/r8-runtime-contact.md`, `lessons/r8-contact-verifier.json`: finite CharacterBody2D contact at authored tile `(2,3)` and scratch polygon-removed pass-through; independent 27/27 replay.
- `lessons/r9-diagnostic-calibration.md`, `lessons/r9-diagnostic-verifier.json`, `lessons/r9-fault-regression.json`: captured-output export/mutant ERROR calibration, independent 27 + four probes and r7 fault regression.
- `lessons/r10-export-launch.md`, `lessons/r10-launch-verifier.json`, `lessons/r10-battery-verifier.json`, `lessons/r10-fault-regression.json`: direct scratch exported Linux/X11 executable startup event/control, independent 32/32 and fault regression. Live scratch under `live/runs/` is ignored and disposable.
