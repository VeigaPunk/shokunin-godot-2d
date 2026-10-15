# Round 57 save/load scout report

Scope: read-only mapping of Godot 4.7.2 APIs and current battery; no tracked fixture/runner edits. Scratch: `.shokunin/game-dev-2d/corpus/live/r57-save-scout/api-probe/` (`project.godot`, `probe.gd`).

## Existing runner / baseline

- `.shokunin/game-dev-2d/corpus/fixtures/run_battery.py`: `CASES` has 70 entries by AST inspection; it runs each case serially via `godot --headless --path <scratch> --script res://<fixture> -- <flags>`, default per-script timeout 8s. It copies fixture tree into timestamped run scratch, then writes `verdicts.json`. Existing `execute()` requires expected exit, signature, no unrelated `ERROR:`/script/parse errors. Current cases contain no save/JSON case (search of source for save/JSON finds only Python runner bookkeeping and export `savepack` strings).
- `find` over `.shokunin/game-dev-2d/corpus/fixtures` found no filename containing `save` or `json`; no existing save/load fixture. Runner's CASES count matches LOG baseline of 70 ordinary.

Commands/evidence:
- `godot --version` → `4.7.2.stable.arch_linux.ed1daf0bf`.
- `python` AST parse of runner → `CASE entries 70`; literal source scan → no save/load case.
- `find` equivalent Python recursive fixture filename scan → `[]`.

## API behavior measured

A minimal scratch-only `SceneTree` script invoked with:
`godot --headless --path .shokunin/game-dev-2d/corpus/live/r57-save-scout/api-probe --script res://probe.gd`

Initial attempt compared decoded JSON directly to an integer-valued input dictionary and exited 1: decoded numeric values are floats (`7.0`, nested array `3.0`), even though output showed correct values. This is an important exact-value comparison pitfall; construct expected decoded values with numeric floats or compare intentionally typed fields.

After correcting expected values, exact output (exit 0):
```
PASS save_load reopened=true structured=true path=user://r57-save-scout-probe.json
EXPECTED_NEGATIVE corrupt-json-rejected parse_error=Unknown error getting token line=0
```
The scratch script used `FileAccess.open(path, FileAccess.WRITE)`, `store_string(JSON.stringify(payload))`, released the file reference, reopened using `FileAccess.READ`, and read `get_as_text()`. `JSON.new().parse(text)` returned `OK`; `JSON.data` held dictionary/array/bool/string/float structure. It then wrote the original bytes to a distinct `user://...-corrupt.json`, reread them, appended `
{broken`, reopened and parsed; parse returned non-OK and the positive structured comparison was not used as the corruption classifier. This is evidence for API feasibility, not a full battery fixture or isolated-battery verdict.

API/design notes:
- `FileAccess.open` returns null on open failure; check for null and report `FileAccess.get_open_error()` (static) rather than dereferencing. `WRITE` replaces/truncates, so negative mutation should use a separate copied scratch file, never overwrite the positive source/fixture. Release/close writers before reopening (the probe drops its refs).
- `store_string` and `get_as_text` are sufficient for a tiny JSON fixture. `JSON.stringify(value)` serializes; `JSON.new().parse(text)` returns an `Error` code and exposes decoded `data`, `get_error_message()`, `get_error_line()`. Do not use only `JSON.parse_string`/null as rejection evidence: valid JSON `null` is itself null-like; explicit parser error status distinguishes malformed data.
- Ensure malformed bytes differ from known-good copied bytes, and that the negative branch emits its own stable `EXPECTED_NEGATIVE ...` signature, exits with the intended expected code, and cannot also satisfy the positive PASS signature. In the probe, the parser's message was generic (`Unknown error getting token`) but `parse()` status differentiated it; avoid depending on specific engine error prose.

## Risks / boundary

- A save/reopen test only shows this process can persist and decode a small `user://` file in its isolated project user-data location. It does not establish crash durability, fsync behavior, platform persistence, migration, concurrency, security, or production save semantics.
- `user://` storage is project/user-data scoped; runner's per-run scratch project is the right containment for generated data. Keep all write/corruption operations in that runtime scratch, not tracked seed fixtures. Runner currently makes its own scratch copy, so cases should target runtime user storage, not fixture paths.
- To keep classification causal, positive must assert values after reopening from disk, not only the in-memory payload. Negative should copy then alter its scratch bytes and assert parse rejection with a distinct marker; a nonzero process exit alone can be confused with crashes/parse errors.

No changes made to tracked paths, runner, fixtures, LOG/SCORECARD, or other reports. No engine/editor source changed. No claims beyond observed API behavior above.
