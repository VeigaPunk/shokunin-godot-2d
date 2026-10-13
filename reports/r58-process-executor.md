# Round 58 process executor

## Result
Implemented separate Godot writer and read-only reader invocations, plus a separate missing-file negative. Godot 4.7.2 headless battery passes **87/87** with the seven declared opt-in flags. This adds 3 fixture rows and one meta row (ordinary 72→76; full 83→87). The existing 83 case classifications match the r57 seven-flag receipt exactly for `script`, `flags`, expected/actual exit, signature, and verdict (0 differences).

- Raw full receipt: `corpus/live/r58-process-executor/runs/20261013T132430103538Z/verdicts.json`
- Process-specific evidence: `corpus/live/r58-process-executor/runs/20261013T132430103538Z/save-process-verdicts.json`
- Full run output was 87/87 PASS; opt-in classification arms intentionally include inner FAIL classifications as positive probe assertions.
- Previous receipt compared: `corpus/live/r57-save-verifier/corrected-seven-flag-runs/20261013T131017016504Z/verdicts.json`.

## Causal/process evidence
The writer process exited 0 and wrote `user://r58-process-save.json`. An independent subsequent Godot process exited 0, parsed the same JSON structure and matched all expected values without opening the save for writing. PID evidence: writer `3244255`, reader `3244332`. Both commands used the identical copied project path under this run, `res://save_process.gd`, and the same absolute run-local `XDG_DATA_HOME` `/home/vgpnk/Projects/prymeagnt/game-dev-2d/.shokunin/game-dev-2d/corpus/live/r58-process-executor/runs/20261013T132430103538Z/xdg-data`. Their globalized user paths are identical and inside the XDG root. A third invocation used `--missing`; it exited 2 with the expected `FILE_NOT_FOUND` diagnostic and distinct PID `3244408`. The meta record verifies PID inequality, command/project identity, XDG environment values, and path containment via `Path.is_relative_to`.

Causal baseline: `corpus/live/r58-process-executor/causal-scratch/causal-check.md` and `baseline-runner-sha256.txt` (runner before edit: `b3d721f923feda6b04b9cc9b78278f5b41c1e7a9df4e3215eb13e73505f982a8`). The fixture is `corpus/fixtures/save_process.gd`; runner change is confined to `corpus/fixtures/run_battery.py`. Existing r57 `save_roundtrip.gd` and negative remain intact.

## Scope and limitations
This demonstrates bounded headless Godot 4.7.2 JSON write, process exit, and read by a distinct process in this runner/project setup. It does **not** establish power-loss/crash durability, explicit filesystem flush guarantees, atomicity, arbitrary-corruption detection, production persistence, or cross-platform behavior. Existing absolute run-local XDG isolation was preserved; no prior receipts, log, scorecard, other lane, or source project files were edited. No commit/push/merge performed.
