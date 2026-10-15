# Round 57 executor — save/load fixture

## Implementation

Added only `corpus/fixtures/save_roundtrip.gd` and additive runner rows/classification for `save_roundtrip` and `save_corrupt_negative` in `corpus/fixtures/run_battery.py`. Positive writes JSON containing nested dictionary, array, string, bool and float, closes it, reopens `user://r57-save.json`, parses with `JSON.parse_string`, and compares the structured result to expected values. Expected numeric value is `7.0`: Godot JSON decoding represents JSON numbers as floats. Negative copies the positive source bytes, checks the copy equals source before changing it, writes malformed `{` bytes only to the separate copy, verifies copied bytes differ, reopens/parses the copy with `JSON.new().parse()`, and requires a parse error. It also requires original saved source bytes remain unchanged. The expected-negative path emits exact `ERROR: SAVE EXPECTED NEGATIVE: malformed JSON rejected signature=JSON_PARSE_ERROR` and exits 2; false acceptance and other failed assertions exit 2 with distinct assertion diagnostics. This is deliberately a malformed-syntax rejection control only, not a claim of detecting valid-but-modified JSON.

The runner gives each copied scratch project a timestamp-suffixed `config/name`, so Godot's app userdata directory is distinct per invocation. Isolated smoke set `XDG_DATA_HOME` to this lane's `positive/xdg-data` and `negative/xdg-data`; observed globalized paths:
- `.shokunin/game-dev-2d/corpus/live/r57-save-executor/positive/xdg-data/godot/app_userdata/MechanicOneShotTest-r57-save-executor-smoke/r57-save.json`
- `.shokunin/game-dev-2d/corpus/live/r57-save-executor/negative/xdg-data/godot/app_userdata/MechanicOneShotTest-r57-save-executor-smoke/r57-save-corrupt-copy.json`

The full corrected battery used standard HOME app userdata with unique project name, observed under `/home/vgpnk/.local/share/godot/app_userdata/MechanicOneShotTest-20261013T113124907867Z/`; both outputs remained under this unique app userdata directory, not the preexisting `MechanicOneShotTest`. Ordinary replay similarly resolved to unique `MechanicOneShotTest-20261013T113248950917Z`. I did not write the existing app userdata directory.

## Exact commands and results

- `godot --version` → `4.7.2.stable.arch_linux.ed1daf0bf`.
- Isolated positive/negative invocations used `XDG_DATA_HOME=<unique scratch case directory>` and `godot --headless --path <unique scratch project> --script res://save_roundtrip.gd [-- --corrupt-negative]`; positive exit 0 with `PASS save_roundtrip structured=true reopened=true values_match=true`, negative exit 2 with the exact expected-negative ERROR marker. Both printed globalized paths, as above.
- Ordinary: `python3 .shokunin/game-dev-2d/corpus/fixtures/run_battery.py --runs .shokunin/game-dev-2d/corpus/live/r57-save-executor/ordinary` → exit 0, **72/72 PASS** (baseline 70 + two new cases), raw `.shokunin/game-dev-2d/corpus/live/r57-save-executor/ordinary/20261013T113248950917Z/verdicts.json`.
- Full: `python3 .shokunin/game-dev-2d/corpus/fixtures/run_battery.py --probe-failing --probe-unrelated-error --probe-export-launch --probe-godot-error --probe-stream-attribution --probe-crash-exit --probe-timeout --runs .shokunin/game-dev-2d/corpus/live/r57-save-executor/isolated-replay` → exit 0, **83/83 PASS** (81 prior full + two new cases), raw `.shokunin/game-dev-2d/corpus/live/r57-save-executor/isolated-replay/20261013T113124907867Z/verdicts.json`.
- Independently compared prior r56 raw `corpus/lessons/r56-pushframe-non-author.json` to corrected full raw for all 81 old case tuples `(case, expected_exit, actual_exit, signature, verdict)`: **81/81 identical, 0 mismatches**. Full underlying cases 79 (includes prior full's mutants); prior ordinary baseline is **70**, now **72**.

## Adverse attempts / caveats

- First isolated iteration found `7` vs decoded `7.0` equality mismatch; corrected fixture to expected float. First hand-built run command had shell quoting error (exit 127), no Godot process started.
- Earlier `full2` run is adverse and retained separately at `corpus/live/r57-save-executor/full2/20261013T112739614735Z`; it ran before final fixture/runner and showed stale old PASS/exit0 negative behavior. Do not use as evidence. A later `verify` run occurred after fixture correction but before all isolation changes; kept separate.
- An intermediate replay with relative XDG_DATA_HOME was invalid for isolation; do not rely on it. A subsequent replay used absolute XDG and exposed changed export-template lookup (the isolated XDG tree lacked installed templates), so the tracked runner does not globally override XDG. Final isolation is unique project `config/name`, validated by the full result paths. Thus existing export/preset behavior stayed unchanged.
- Full replay's extra unrelated-diagnostic and stream-rejection probe child cases intentionally report `FAIL` in their captured probe payloads; the enclosing probes and battery classify these expected rejection observations as PASS. Two earlier fault-injection invocations were standalone and not part of the accepted full battery; standalone `--fault-injection` records expected child failures under PASS meta. The accepted full command above exited 0.
- Corruption tests malformed JSON only; they do not detect valid semantic edits or promise checksums/authentication, crash durability, migration, or recovery.

## Changed paths

- `corpus/fixtures/run_battery.py` (add two case rows, expected malformed-JSON error classification, unique scratch project app name).
- `corpus/fixtures/save_roundtrip.gd` (new fixture).
- `corpus/live/r57-save-executor/` (this lane's scratch and raw evidence).
- `reports/r57-save-executor.md` (this report).
