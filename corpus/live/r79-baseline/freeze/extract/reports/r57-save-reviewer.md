# Round 57 read-only save/load semantics review

## Scope and baseline inspection

Read-only review of `.shokunin/game-dev-2d/corpus/fixtures/run_battery.py` and existing `.gd` fixtures; no fixture/runner or engine/editor source edits. At review time, `corpus/fixtures/*save*` matched no files. The runner's `CASES` begins at line 18 (currently the baseline is expected to be 70 ordinary cases per the round declaration); its scratch staging at lines 108–118 copies fixture inputs into a run directory before invoking Godot. No existing fixture uses `user://` (`rg`-equivalent Python scan over fixture `.gd` files returned no matches). Existing fixtures mostly assert emitted signatures and exit status through `classify_process` (lines 138–155); this alone would not prove a file was reopened or structured data matched.

## Independent semantic probes (Godot 4.7.2)

1. `godot --version` → `4.7.2.stable.arch_linux.ed1daf0bf`.
2. Created only under `.shokunin/game-dev-2d/corpus/live/r57-save-reviewer/` a minimal `project.godot` and `probe.gd`; ran:
   `godot --headless --path ".shokunin/game-dev-2d/corpus/live/r57-save-reviewer" --script res://probe.gd`
   → exit 0. Probe wrote JSON with `FileAccess.open("user://slot.json", WRITE)`, `JSON.stringify`, closed it, reopened it with `READ`, read text, and `JSON.parse`d it. Output: `ROUNDTRIP { "player": { "health": 7.0, "items": ["key", "potion"] }, "position": "(12.5, -3.0)", "schema": 1.0 }`; types: `pos=4 items=28` (`TYPE_STRING`, `TYPE_ARRAY`). Therefore JSON round-trip turns numeric values into floating point and Vector2 into its string representation; compare JSON-compatible values deliberately, not original Variant types or exact textual formatting.
3. Wrote malformed UTF-8/JSON bytes to the same unique scratch, copied only that probe byte file into Godot's app-user directory for this test, then ran:
   `godot --headless --path ".shokunin/game-dev-2d/corpus/live/r57-save-reviewer" --script res://read_corrupt.gd`
   → exit 0 for my diagnostic harness; Godot emitted `Unicode parsing error ... Invalid UTF-8 leading byte (ff)` and `CORRUPT bytes=32 parse_error=43 line=0 message=Expected key`. This demonstrates `JSON.parse` exposes a non-OK error code for these bytes, but an expected-negative fixture must itself turn that into an expected-negative test result (e.g. internal assertion plus the runner's distinct expected error/exit signature). A zero process exit with a printed parse error is not evidence that the battery rejected the data.

## False-positive risks / review recommendations

- The positive must explicitly close the writer, reopen the *same* `user://` path via a new `FileAccess`, parse the bytes read from that handle, and compare each nested expected value/type (allowing JSON's numeric float conversion). Merely checking in-memory state, `FileAccess.file_exists`, a PASS marker, or parsing the original input would not establish load behavior.
- `user://` belongs to Godot's per-project user-data location, not the copied scratch tree. Existing runner scratch projects copy the same `project.godot` (including its `config/name`, see staging lines 108–118), so their user-data location can be shared across run invocations. A stale file can produce a false positive. The fixture should overwrite a unique filename and verify current expected values; stronger isolation is a unique project name or explicit per-case user-data path if supported. Never mutate existing user data as a negative control.
- Corruption must be applied to a **copied scratch save**, after the positive save, not the fixture source or a shared `user://` file. Verify the bytes differ from the valid save and that the malformed bytes are actually what the negative opens. Otherwise an omitted mutation, stale/alternate file, or negative branch that skips loading can masquerade as rejection.
- On parse failure, do not inspect `JSON.data` as though it were valid. Avoid treating the mere occurrence of an expected diagnostic substring as sufficient: the normal classifier requires expected exit and signature and rejects unexpected `ERROR:`/script/parse diagnostics (lines 138–155), but a deliberately negative case should pin its own unique expected-negative signature and exit code so a setup/IO error cannot satisfy it.
- This test can establish one-process close/reopen and structured JSON parsing only. It does not establish app-restart persistence, atomic writes, flush/fsync durability, power-loss recovery, schema migration, tamper resistance, or platform-independent `user://` behavior. `FileAccess.close()` is not a durability guarantee.

Scratch paths created: `.shokunin/game-dev-2d/corpus/live/r57-save-reviewer/{project.godot,probe.gd,corrupt.json,read_corrupt.gd}`. No fixture or runner was changed. No baseline battery was run; this lane reviewed semantics and existing behavior, not admission verification.
