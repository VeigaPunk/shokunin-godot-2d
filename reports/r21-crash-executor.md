# Round 21 crash-exit executor report

Implemented the opt-in real-Godot paired signal-termination probe in the assigned scope only:
- Added `corpus/fixtures/crash_exit_probe.gd`.
- Added `--probe-crash-exit` and its isolated execution/classification/artifact path in `corpus/fixtures/run_battery.py`; ordinary `CASES` were not edited.

Replay: `python .shokunin/game-dev-2d/corpus/fixtures/run_battery.py --probe-crash-exit` (Godot 4.7.2 on Linux), exit 0. Battery verdict artifact: `corpus/live/runs/20261013T010046105008Z/verdicts.json`; probe raw artifact: `corpus/live/runs/20261013T010046105008Z/crash-exit-verdicts.json`. All 35 ordinary cases and the probe passed (36 records). The probe result records:
- Same `res://crash_exit_probe.gd` in both arms and exact marker `CRASH_EXIT_PROBE: expected signature` in each.
- Accept normally exited with expected/actual code 1 and classified true.
- Reject marker was observed while `process.poll()` confirmed the process still live; parent sent POSIX `SIGTERM`; return code was -15; classifier rejected it. `error` is null and the probe verdict is PASS.
- Signal wait is bounded at 8s; process cleanup is bounded at 3s, with forced kill on cleanup timeout. Unsupported platform, missing marker, non-live process, wrong signal exit, or timeout fails the probe.

No engine/editor mutation, seeded fixture edits, ordinary CASES edits, publication, push, or merge. This is only one Linux/Godot 4.7.2 signal contrast, not a general crash or process-tree guarantee. Targeted command did not run unrelated opt-in probes; the 35 ordinary outcomes held.
