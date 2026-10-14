# Round 50 repaired release-edge named non-author verifier

- Role: named non-author leaf; no delegation and no tracked source edits.
- Godot: `4.7.2.stable.arch_linux.ed1daf0bf`.
- Tracked repair was already present before this verification: before/after hashes `slider_adjust.gd` `abf833021df686f01d6778646a9d1a96bbabab00905bcb554ac7f8e2d68e7434`, `run_battery.py` `4afc03127ecd13d274eb6bfe8f569bbdd849108558b3884c8d7247775ad3d77c`.
- Full default path: `python .shokunin/game-dev-2d/corpus/fixtures/run_battery.py --probe-failing --probe-unrelated-error --probe-export-launch --probe-godot-error --probe-stream-attribution --probe-crash-exit --probe-timeout --runs .shokunin/game-dev-2d/corpus/live/r50-release-repaired-verifier/runs`
- Result **75/75 PASS = 64 ordinary + 2 mutants + 9 opt-ins**. Raw `corpus/lessons/r50-release-repaired-non-author.json`, byte-identical to run output. Compared by case against `r49-fresh-after-reconnect-non-author.json`: all **65** prior `(case, verdict, actual_exit, signature)` tuples match; one new expected-negative exit2 tuple for the repaired release branch. Nine opt-in outer classifications pass and inner classifications remain intentional: Godot-error `[True,False]`, stream `[True,False]`, crash `[True,False]`, timeout `[False,True,False]`. Export-launch probe PASS.
- Separate `--fault-injection` outer PASS, raw `corpus/lessons/r50-release-repaired-fault-non-author.json`; inner hang and unrelated-error FAIL, clean expected-negative PASS.

## Direct fresh scratch sabotage

Copied the repaired tracked fixture to a new scratch directory. Clean invocation of `--repeat-right --second-focus-restore --release-after-late-reconnect-press` reached the eleven-check marker and the exact intended terminal negative, exit2. The new `Input.is_action_pressed("ui_left")` assertions see pressed before edge10 and unpressed after the actual release.

For actual no-dispatch sabotage, retained focus/connection prechecks, skipped only `_action(...)` for `i == 10`, and retained frame wait plus edge10 numeric/receipt/Label assertions. Invocation:

`timeout 15s godot --headless --path .shokunin/game-dev-2d/corpus/live/r50-release-repaired-verifier/sabotage-omit-edge10 --script res://slider_adjust.gd -- --repeat-right --second-focus-restore --release-after-late-reconnect-press`

Result exit2 at `ERROR: SLIDER input-state post-release assertion failed: ui_left remains pressed` (fixture line 109), before the eleven-check marker and before exact terminal expected-negative diagnostic. That early `ERROR:` is not the row's exact expected signature, so production `classify_process` rejects it; by direct application of classifier conditions, the expected terminal signature is absent and the unrelated `ERROR:` is disallowed. **This corrected sabotage is detected**, unlike the earlier pre-repair no-dispatch false-PASS (adverse historical result retained; old `r50-release-non-author.json` not overwritten).

The earlier separate replace-release-with-press sabotage also fails at edge10 state assertion, but is not used as evidence for no-dispatch detection. Omit-edge9 dispatch still fails at edge9 numeric/receipt/Label assertion before terminal marker. A prior direct clean invocation was first attempted with a quoted full command string and shell returned 127 (invalid command invocation); rerun with normal `bash("""...""")` syntax succeeded. This setup failure is telemetry only.

No engine/editor/seeded edits, tracked changes, commit, push, or merge. Scope remains synthetic parsed `InputEventAction` events and process frames only; not OS repeat, physical input/timing, rendered/pointer behavior, accessibility, production, generic slider behavior, or internal consumption of unchanged edges.
